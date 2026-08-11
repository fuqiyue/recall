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
        self.assertIn(["config", "--local", "pull.rebase", "true"], calls)
        self.assertIn(["config", "--local", "fetch.prune", "true"], calls)
        self.assertIn(["config", "--local", "push.autoSetupRemote", "true"], calls)

    def test_dirty_worktree_is_not_committed_without_explicit_message(self):
        """脏工作区不被自动提交，但不阻断已提交历史的同步（RULE-011）。"""
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
        ), patch.object(git_sync, "_is_dirty", return_value=True), patch.object(
            git_sync, "_current_branch", return_value="main"
        ), patch.object(git_sync, "run_git", side_effect=fake_run_git):
            self.assertEqual(git_sync.sync_repository(root, quiet=True), 0)

        self.assertNotIn(["add", "-A"], calls)
        self.assertFalse(any(call[:1] == ["commit"] for call in calls))
        self.assertIn(["pull", "--rebase", "--autostash", "origin", "main"], calls)
        self.assertIn(["push", "--set-upstream", "origin", "main"], calls)

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
