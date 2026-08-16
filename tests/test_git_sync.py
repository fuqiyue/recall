import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
import git_sync


class GitSyncTests(unittest.TestCase):
    def test_hook_block_is_managed_and_non_interactive(self):
        block = git_sync._hook_block()
        self.assertIn(git_sync.HOOK_BEGIN, block)
        self.assertIn(git_sync.HOOK_END, block)
        self.assertIn("git config --bool recall.autoSync", block)
        self.assertIn("git_sync.py", block)

    def test_configure_sync_writes_safe_defaults_and_enables_hook(self):
        root = Path("D:/recall-test")
        calls = []

        def fake_run_git(args, cwd=None, timeout=60):
            calls.append(list(args))
            if args[:2] == ["remote", "get-url"]:
                return True, "https://example.invalid/recall.git", ""
            return True, "", ""

        with patch.object(git_sync, "run_git", side_effect=fake_run_git), patch.object(
            git_sync, "install_post_commit_hook", return_value=(True, "hooks/post-commit")
        ) as install:
            self.assertTrue(git_sync.configure_git_sync(root))

        install.assert_called_once_with(root)
        self.assertIn(["config", "--local", "recall.autoSync", "true"], calls)
        self.assertIn(["config", "--local", "recall.autoCommit", "true"], calls)
        self.assertIn(["config", "--local", "pull.rebase", "true"], calls)
        self.assertIn(["config", "--local", "fetch.prune", "true"], calls)
        self.assertIn(["config", "--local", "push.autoSetupRemote", "true"], calls)

    def _sync_calls(self, dirty, autocommit_config, autocommit_param=True):
        """跑一次 sync_repository，返回 (exit_code, git 调用列表)。"""
        root = Path("D:/recall-test")
        calls = []

        def fake_run_git(args, cwd=None, timeout=60):
            calls.append(list(args))
            if args[0] == "ls-remote":
                return True, "abc\trefs/heads/main", ""
            if args[:2] == ["config", "--bool"]:
                return (autocommit_config is not None), autocommit_config or "", ""
            return True, "", ""

        with patch.object(git_sync, "_git_root", return_value=root), patch.object(
            git_sync, "_remote_config", return_value="origin"
        ), patch.object(
            git_sync, "_remote_url", return_value="https://example.invalid/recall.git"
        ), patch.object(git_sync, "_is_dirty", return_value=dirty), patch.object(
            git_sync, "_current_branch", return_value="main"
        ), patch.object(git_sync, "run_git", side_effect=fake_run_git):
            code = git_sync.sync_repository(
                root, quiet=True, autocommit=autocommit_param
            )
        return code, calls

    def test_autocommit_default_commits_dirty_worktree(self):
        """自动保存默认开启：脏工作区被自动提交后同步（RULE-011）。"""
        code, calls = self._sync_calls(dirty=True, autocommit_config=None)
        self.assertEqual(code, 0)
        self.assertIn(["add", "-A"], calls)
        self.assertIn(["commit", "-m", git_sync.AUTOCOMMIT_MESSAGE], calls)
        self.assertIn(["pull", "--rebase", "--autostash", "origin", "main"], calls)
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)

    def test_manual_mode_dirty_worktree_not_committed_but_still_syncs(self):
        """手动模式（recall.autoCommit=false）：不自动提交，但不阻断已提交历史。"""
        code, calls = self._sync_calls(dirty=True, autocommit_config="false")
        self.assertEqual(code, 0)
        self.assertNotIn(["add", "-A"], calls)
        self.assertFalse(any(call[:1] == ["commit"] for call in calls))
        self.assertIn(["pull", "--rebase", "--autostash", "origin", "main"], calls)
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)

    def test_post_commit_hook_never_autocommits_dirty_files(self):
        """hook 场景（autocommit=False）：即使自动保存开启也不提交其他脏文件。"""
        code, calls = self._sync_calls(
            dirty=True, autocommit_config="true", autocommit_param=False
        )
        self.assertEqual(code, 0)
        self.assertNotIn(["add", "-A"], calls)
        self.assertFalse(any(call[:1] == ["commit"] for call in calls))
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)

    def test_internal_commit_guard_short_circuits_hook(self):
        """内部提交触发的嵌套 hook 直接退出，防止递归。"""
        with patch.dict(os.environ, {git_sync.INTERNAL_COMMIT_ENV: "1"}):
            with patch.object(git_sync, "sync_repository") as sync:
                self.assertEqual(git_sync.main(["--post-commit"]), 0)
                sync.assert_not_called()

    def test_manual_and_auto_flags_write_config(self):
        """--manual/--auto 切换 recall.autoCommit。"""
        calls = []

        def fake_run_git(args, cwd=None, timeout=60):
            calls.append(list(args))
            return True, "", ""

        with patch.object(
            git_sync, "find_project_root", return_value=Path("D:/recall-test")
        ), patch.object(git_sync, "run_git", side_effect=fake_run_git):
            self.assertEqual(git_sync.main(["--manual"]), 0)
            self.assertEqual(git_sync.main(["--auto"]), 0)

        self.assertIn(["config", "--local", "recall.autoCommit", "false"], calls)
        self.assertIn(["config", "--local", "recall.autoCommit", "true"], calls)

    def test_backfill_fills_placeholder_and_commits_only_that_file(self):
        """回填 HEAD 引用的记录，且内部提交只包含被回填的文件。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_rel = "logic_version/records/logic_version-20260811-009-demo.md"
            record = root / record_rel
            record.parent.mkdir(parents=True)
            record.write_text(
                "# VER-demo\n\n- after_commit: _待填写_\n", encoding="utf-8"
            )
            calls = []

            def fake_run_git(args, cwd=None, timeout=60):
                calls.append(list(args))
                if args[:2] == ["log", "-1"]:
                    return True, f"abc1234\nfeat: demo\n\nRef: {record_rel}\n", ""
                return True, "", ""

            with patch.object(git_sync, "run_git", side_effect=fake_run_git):
                self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))

            content = record.read_text(encoding="utf-8")
            self.assertIn("- after_commit: abc1234", content)
            self.assertNotIn("_待填写_", content)
            self.assertIn(["add", "--", record_rel], calls)
            commit_calls = [c for c in calls if c[:1] == ["commit"]]
            self.assertEqual(len(commit_calls), 1)
            self.assertIn(record_rel, commit_calls[0])
            self.assertNotIn(["add", "-A"], calls)

    def test_backfill_is_noop_without_ref_or_placeholder(self):
        """HEAD 无 Ref 行、或记录已回填时不产生任何提交。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_rel = "logic_version/records/logic_version-20260811-009-demo.md"
            record = root / record_rel
            record.parent.mkdir(parents=True)
            record.write_text("# VER-demo\n\n- after_commit: 5afe9bb\n", encoding="utf-8")
            calls = []

            def fake_run_git(args, cwd=None, timeout=60):
                calls.append(list(args))
                if args[:2] == ["log", "-1"]:
                    return True, f"abc1234\nchore: x\n\nRef: {record_rel}\n", ""
                return True, "", ""

            with patch.object(git_sync, "run_git", side_effect=fake_run_git):
                self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))
                calls.clear()
                with patch.object(
                    git_sync,
                    "run_git",
                    side_effect=lambda a, cwd=None, timeout=60: (
                        calls.append(list(a)) or (True, "abc1234\nchore: no ref\n", "")
                    ),
                ):
                    self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))

            self.assertFalse(any(c[:1] == ["commit"] for c in calls))

    def test_backfill_covers_records_committed_without_ref(self):
        """自动保存提交无 Ref 行：HEAD 提交文件清单里的记录也被回填。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_rel = "logic_version/records/logic_version-20260816-009-demo.md"
            record = root / record_rel
            record.parent.mkdir(parents=True)
            record.write_text(
                "# VER-demo\n\n- after_commit: _待填写_\n", encoding="utf-8"
            )
            calls = []

            def fake_run_git(args, cwd=None, timeout=60):
                calls.append(list(args))
                if args[:3] == ["log", "-1", "--format=%h%n%B"]:
                    return True, "abc1234\nchore(recall): 自动保存本地修改\n", ""
                if args[:3] == ["log", "-1", "--format="]:
                    return True, f"{record_rel}\nsrc/app.py", ""
                return True, "", ""

            with patch.object(git_sync, "run_git", side_effect=fake_run_git):
                self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))

            self.assertIn(
                "- after_commit: abc1234", record.read_text(encoding="utf-8")
            )
            self.assertIn(["add", "--", record_rel], calls)
            self.assertNotIn(["add", "-A"], calls)

    def test_fill_placeholder_only_matches_field_lines(self):
        """叙述文字里引用的占位符字符串不得被回填（曾污染不可变记录正文）。"""
        text = (
            "hook 只精确匹配 `- after_commit: _待填写_` 这个占位符。\n"
            "- after_commit: _待填写_\n"
        )
        new_text, filled = git_sync._fill_placeholder(text, "abc1234")
        self.assertTrue(filled)
        self.assertIn("- after_commit: abc1234\n", new_text)
        self.assertIn("`- after_commit: _待填写_`", new_text)

        # 只有叙述引用、没有字段行时：不回填、文本不变
        prose_only = "正文提到 `- after_commit: _待填写_`，但无字段行。\n"
        unchanged, filled = git_sync._fill_placeholder(prose_only, "abc1234")
        self.assertFalse(filled)
        self.assertEqual(unchanged, prose_only)

    def test_backfill_supports_legacy_commit_placeholder(self):
        """旧快速模板的 `- commit: _待填写_` 占位符同样被回填。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_rel = "logic_version/records/logic_version-20260816-010-legacy.md"
            record = root / record_rel
            record.parent.mkdir(parents=True)
            record.write_text(
                "# VER-legacy\n\n- commit: _待填写_\n", encoding="utf-8"
            )

            def fake_run_git(args, cwd=None, timeout=60):
                if args[:3] == ["log", "-1", "--format=%h%n%B"]:
                    return True, f"abc1234\nfeat: x\n\nRef: {record_rel}\n", ""
                return True, "", ""

            with patch.object(git_sync, "run_git", side_effect=fake_run_git):
                self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))

            self.assertIn("- commit: abc1234", record.read_text(encoding="utf-8"))

    def test_backfill_warns_when_ref_record_has_no_placeholder(self):
        """Ref 指向的记录既无占位符也无哈希：打印警告而非静默跳过，且不提交。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_rel = "logic_version/records/logic_version-20260816-011-broken.md"
            record = root / record_rel
            record.parent.mkdir(parents=True)
            record.write_text(
                "# VER-broken\n\n- after_commit: <pending-backfill>\n",
                encoding="utf-8",
            )
            calls = []

            def fake_run_git(args, cwd=None, timeout=60):
                calls.append(list(args))
                if args[:3] == ["log", "-1", "--format=%h%n%B"]:
                    return True, f"abc1234\nfeat: x\n\nRef: {record_rel}\n", ""
                return True, "", ""

            buffer = io.StringIO()
            with patch.object(git_sync, "run_git", side_effect=fake_run_git):
                with contextlib.redirect_stdout(buffer):
                    self.assertTrue(
                        git_sync.backfill_after_commit(root, quiet=False)
                    )

            self.assertIn("占位符", buffer.getvalue())
            self.assertFalse(any(c[:1] == ["commit"] for c in calls))

    def test_recall_new_record_is_backfilled_end_to_end(self):
        """端到端：recall new 生成记录 → 带 Ref 提交 → 占位符被真实回填。"""
        import create_ver

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = ROOT / "references" / "logic-version-git-template.md"
            records_dir = root / "logic_version" / "records"

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                rc = create_ver.create_ver_record(
                    "端到端回填",
                    "e2e-backfill",
                    template_path=template,
                    output_dir=records_dir,
                )
            self.assertEqual(rc, 0)
            record = next(records_dir.glob("logic_version-*-e2e-backfill.md"))
            self.assertIn(
                git_sync.AFTER_COMMIT_PLACEHOLDER,
                record.read_text(encoding="utf-8"),
            )

            for args in (
                ["init"],
                ["config", "user.email", "test@example.invalid"],
                ["config", "user.name", "Recall Test"],
                ["config", "commit.gpgsign", "false"],
                ["add", "-A"],
            ):
                ok, _, stderr = git_sync.run_git(args, cwd=root)
                self.assertTrue(ok, f"git {args} failed: {stderr}")
            record_rel = record.relative_to(root).as_posix()
            ok, _, stderr = git_sync.run_git(
                ["commit", "-m", f"feat: e2e 回填\n\nRef: {record_rel}"], cwd=root
            )
            self.assertTrue(ok, stderr)

            self.assertTrue(git_sync.backfill_after_commit(root, quiet=True))
            content = record.read_text(encoding="utf-8")
            self.assertNotIn("_待填写_", content)
            self.assertRegex(content, r"- after_commit: [0-9a-f]{7,40}")

    def test_drift_sentinel_warns_on_code_only_commit(self):
        """漂移哨兵：提交含代码但未触及 logic 文档时提醒；触及则沉默。"""
        root = Path("D:/recall-test")

        def make_fake(files):
            def fake_run_git(args, cwd=None, timeout=60):
                if args[:3] == ["log", "-1", "--format="]:
                    return True, "\n".join(files), ""
                return True, "", ""

            return fake_run_git

        buffer = io.StringIO()
        with patch.object(
            git_sync, "run_git", side_effect=make_fake(["src/app.py", "README.md"])
        ):
            with contextlib.redirect_stdout(buffer):
                git_sync.warn_missing_logic_docs(root)
        self.assertIn("logic 文档", buffer.getvalue())

        buffer = io.StringIO()
        with patch.object(
            git_sync,
            "run_git",
            side_effect=make_fake(["src/app.py", "logic_readme.md"]),
        ):
            with contextlib.redirect_stdout(buffer):
                git_sync.warn_missing_logic_docs(root)
        self.assertEqual(buffer.getvalue(), "")

    def test_post_commit_mode_treats_soft_skip_as_success(self):
        """hook 场景下无远端/无分支（返回 2）不算失败；真实失败仍传播。"""
        with patch.object(git_sync, "find_project_root", return_value=Path("D:/recall-test")):
            with patch.object(git_sync, "sync_repository", return_value=2):
                self.assertEqual(git_sync.main(["--post-commit"]), 0)
                self.assertEqual(git_sync.main([]), 2)
            with patch.object(git_sync, "sync_repository", return_value=1):
                self.assertEqual(git_sync.main(["--post-commit"]), 1)

    def test_sync_rebases_then_pushes_current_branch(self):
        root = Path("D:/recall-test")
        calls = []

        def fake_run_git(args, cwd=None, timeout=60):
            calls.append(list(args))
            if args[0] == "ls-remote":
                return True, "abc\trefs/heads/main", ""
            return True, "", ""

        with patch.object(git_sync, "_git_root", return_value=root), patch.object(
            git_sync, "_remote_config", return_value="origin"
        ), patch.object(
            git_sync, "_remote_url", return_value="https://example.invalid/recall.git"
        ), patch.object(git_sync, "_is_dirty", return_value=False), patch.object(
            git_sync, "_current_branch", return_value="main"
        ), patch.object(git_sync, "run_git", side_effect=fake_run_git):
            self.assertEqual(git_sync.sync_repository(root, quiet=True), 0)

        self.assertIn(["pull", "--rebase", "--autostash", "origin", "main"], calls)
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)

    def test_explicit_commit_message_uses_argv_and_syncs(self):
        root = Path("D:/recall-test")
        calls = []

        def fake_run_git(args, cwd=None, timeout=60):
            calls.append(list(args))
            if args[0] == "status":
                return True, " M notes.md", ""
            if args[0] == "ls-remote":
                return True, "", ""
            return True, "", ""

        with patch.object(git_sync, "_git_root", return_value=root), patch.object(
            git_sync, "_remote_config", return_value="origin"
        ), patch.object(
            git_sync, "_remote_url", return_value="https://example.invalid/recall.git"
        ), patch.object(git_sync, "_current_branch", return_value="main"), patch.object(
            git_sync, "run_git", side_effect=fake_run_git
        ):
            self.assertEqual(
                git_sync.sync_repository(root, commit_message='docs: "sync"', quiet=True),
                0,
            )

        self.assertIn(["add", "-A"], calls)
        self.assertIn(["commit", "-m", 'docs: "sync"'], calls)
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)


if __name__ == "__main__":
    unittest.main()
