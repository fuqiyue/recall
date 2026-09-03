# -*- coding: utf-8 -*-
"""recall_common 单测（RULE-021）：根查找、Git 调用与未推送计数只此一份实现。"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import recall_common  # noqa: E402


class FindProjectRootTests(unittest.TestCase):
    def test_finds_marker_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "logic_readme.md").write_text("# x\n", encoding="utf-8")
            deep = root / "a" / "b"
            deep.mkdir(parents=True)
            self.assertEqual(recall_common.find_project_root(deep), root)

    def test_without_marker_returns_origin_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            origin = Path(tmp).resolve()
            found = recall_common.find_project_root(origin)
            # 临时目录父链上可能意外存在标记文件；只断言"无标记时回退到起点"
            if not any((p / "logic_readme.md").exists() for p in [origin, *origin.parents]):
                self.assertEqual(found, origin)

    def test_fallback_is_honored(self):
        with tempfile.TemporaryDirectory() as tmp:
            origin = Path(tmp).resolve()
            if any((p / "logic_readme.md").exists() for p in [origin, *origin.parents]):
                self.skipTest("temp dir sits under a Recall project")
            found = recall_common.find_project_root(origin, fallback=recall_common.SELF_ROOT)
            self.assertEqual(found, recall_common.SELF_ROOT)


class RunGitTests(unittest.TestCase):
    def test_run_git_never_raises_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, out, err = recall_common.run_git(["status", "--porcelain"], cwd=Path(tmp), timeout=10)
            # 非仓库：ok=False 且不抛异常；Git 缺失时同样 ok=False
            self.assertFalse(ok)
            self.assertEqual(out, "")
            self.assertIsInstance(err, str)

    def test_git_output_returns_none_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(recall_common.git_output(["rev-parse", "HEAD"], cwd=Path(tmp), timeout=10))

    def test_unpushed_count_is_none_without_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(recall_common.unpushed_commit_count(Path(tmp)))

    def test_run_git_keeps_porcelain_leading_space(self):
        """首行 `` M path`` 的前导空格不能被 strip 掉，否则状态码和路径各错一位。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
                self.assertTrue(recall_common.run_git(args, cwd=root, timeout=10)[0])
            (root / ".marker").write_text("a", encoding="utf-8")
            recall_common.run_git(["add", ".marker"], cwd=root, timeout=10)
            recall_common.run_git(["commit", "-q", "-m", "init"], cwd=root, timeout=10)
            (root / ".marker").write_text("b", encoding="utf-8")
            ok, out, _ = recall_common.run_git(["status", "--porcelain"], cwd=root, timeout=10)
            self.assertTrue(ok)
            self.assertEqual(out.splitlines()[0], " M .marker")

    def test_parse_porcelain_handles_rename_quotes_and_short_lines(self):
        entries = recall_common.parse_porcelain(
            ' M scripts/recall.py\n'
            'R  old_name.md -> new_name.md\n'
            '?? "有 空格/文件.md"\n'
            '\n'
            'A  logic_version/records/new.md\n'
        )
        self.assertEqual(
            entries,
            [
                (" M", "scripts/recall.py"),
                ("R ", "new_name.md"),
                ("??", "有 空格/文件.md"),
                ("A ", "logic_version/records/new.md"),
            ],
        )
        tracked, untracked = recall_common.classify_porcelain(
            ' M a.py\n?? b.py\nR  c.md -> d.md\n'
        )
        self.assertEqual((tracked, untracked), (["a.py", "d.md"], ["b.py"]))
        self.assertEqual(recall_common.classify_porcelain(None), ([], []))

    def test_run_git_decodes_non_ascii_as_utf8(self):
        """中文提交信息在 GBK 默认编码下曾让 status 崩溃；这里直接在本仓库读一次。"""
        ok, out, _ = recall_common.run_git(["log", "-1", "--format=%s"], cwd=ROOT, timeout=10)
        if not ok:
            self.skipTest("not a git checkout")
        self.assertIsInstance(out, str)
        self.assertNotIn("�" * 3, out)  # 不应整段变成替换字符


REGISTRY_README = """# Constitution

## 范围登记与归属

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [root](logic_readme.md) | [changes](logic_change.md) | self | active |
| MOD-BILLING | logic_domains/billing | in-system | domain/runtime-code | paired | [billing](logic_domains/billing/logic_readme.md) | [changes](logic_domains/billing/logic_change.md) | self | active |
| MOD-LEGACY | src/legacy | in-system | module/runtime-code | readme-only | [legacy](src/legacy/logic_readme.md) | none | self | active |
| MOD-INHERIT | src/app | in-system | module/runtime-code | inherited | [app](logic_readme.md#scope-app) | [changes](logic_change.md) | self | active |
| MOD-VENDOR | vendor | out-of-system | foreign/runtime-code | paired | none | none | self | active |

## 当前制度
"""


class RegisteredDomainsTests(unittest.TestCase):
    """RULE-018 一二级拆分法：宪法登记表 -> 部门法（readme + change）与旧式 readme-only。"""

    def _write_project(self, root: Path) -> None:
        (root / "logic_readme.md").write_text(REGISTRY_README, encoding="utf-8")
        (root / "logic_change.md").write_text("# root ledger\n", encoding="utf-8")
        billing = root / "logic_domains" / "billing"
        billing.mkdir(parents=True)
        (billing / "logic_readme.md").write_text(
            "# Billing\n\n## 范围登记与归属\n\n"
            "- owned_paths: src/billing, scripts/bill_*.py; docs/billing/\n",
            encoding="utf-8",
        )
        (billing / "logic_change.md").write_text("# billing ledger\n", encoding="utf-8")
        legacy = root / "src" / "legacy"
        legacy.mkdir(parents=True)
        (legacy / "logic_readme.md").write_text(
            "# Legacy\n\n- owned_paths: none\n", encoding="utf-8"
        )

    def test_registered_domains_returns_paired_and_readme_only_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            domains = recall_common.registered_domains(root)
            by_id = {d.module_id: d for d in domains}

            self.assertEqual(sorted(by_id), ["MOD-BILLING", "MOD-LEGACY"])
            billing = by_id["MOD-BILLING"]
            self.assertEqual(billing.scope_path, "logic_domains/billing")
            self.assertEqual(billing.doc_policy, "paired")
            self.assertEqual(billing.readme, root / "logic_domains" / "billing" / "logic_readme.md")
            self.assertEqual(billing.change, root / "logic_domains" / "billing" / "logic_change.md")
            self.assertEqual(
                billing.owned_paths(), ["src/billing", "scripts/bill_*.py", "docs/billing"]
            )
            legacy = by_id["MOD-LEGACY"]
            self.assertEqual(legacy.doc_policy, "readme-only")
            self.assertIsNone(legacy.change)
            self.assertEqual(legacy.owned_paths(), [])

    def test_registered_domains_without_constitution_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(recall_common.registered_domains(Path(tmp)), [])

    def test_owned_paths_of_missing_readme_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            domain = recall_common.LogicDomain("MOD-X", "logic_domains/x", Path(tmp), "paired")
            self.assertEqual(domain.owned_paths(), [])

    def test_change_ledgers_lists_root_first_then_existing_domain_ledgers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            ledgers = recall_common.change_ledgers(root)
            self.assertEqual(
                ledgers,
                [
                    ("logic_change.md", root / "logic_change.md"),
                    (
                        "logic_domains/billing/logic_change.md",
                        root / "logic_domains" / "billing" / "logic_change.md",
                    ),
                ],
            )
            # 领域账本文件缺失时不列出，根账本缺失时也不列出
            (root / "logic_domains" / "billing" / "logic_change.md").unlink()
            (root / "logic_change.md").unlink()
            self.assertEqual(recall_common.change_ledgers(root), [])


class SingleGitInfrastructureGateTests(unittest.TestCase):
    """RULE-021 的机器门：scripts/ 下只有 recall_common 可以直接用 subprocess 调 git。

    今天 run_git 的 strip 差异证明两套 Git 调用一定会漂移；文字规则拦不住新
    脚本再抄一份，所以用静态扫描把"只此一份"变成测试失败。
    """

    def test_no_direct_subprocess_git_outside_recall_common(self):
        offenders = []
        for path in sorted((ROOT / "scripts").rglob("*.py")):
            if path.name == "recall_common.py" or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "subprocess." in stripped and "recall_common" not in stripped:
                    offenders.append(f"{path.relative_to(ROOT)}:{lineno}: {stripped}")
        self.assertEqual(
            offenders,
            [],
            "scripts/ 下禁止绕过 recall_common.run_git 直接调 subprocess（RULE-021）",
        )


if __name__ == "__main__":
    unittest.main()
