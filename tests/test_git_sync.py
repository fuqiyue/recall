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
