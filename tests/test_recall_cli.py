# -*- coding: utf-8 -*-
"""CLI 胶水层冒烟测试。

审查发现（VER-20260811-002）：recall.py 与子模块之间的函数签名、
记录文件名和项目根查找各自漂移，而坏掉的恰好都是没有测试的部分。
本文件只做接口级断言，不追求覆盖业务分支。
"""

import contextlib
import io
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
import create_ver
import detect_conflicts
import link_ver_git
import recall
import validate


class TempProject:
    """带 logic_readme.md 和模板的临时项目，chdir 进入后自动还原。"""

    def __enter__(self):
        self._old_cwd = Path.cwd()
        self.root = Path(tempfile.mkdtemp(prefix="recall-cli-test-"))
        (self.root / "logic_readme.md").write_text("# test\n", encoding="utf-8")
        refs = self.root / "references"
        refs.mkdir()
        shutil.copy(
            ROOT / "references" / "logic-version-template.md",
            refs / "logic-version-template.md",
        )
        os.chdir(self.root)
        return self.root

    def __exit__(self, *exc):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.root, ignore_errors=True)
        return False


class CreateVerTests(unittest.TestCase):
    def test_generated_record_uses_canonical_name_and_schema(self):
        """recall new 生成的记录必须能被 validate/status/list 发现并通过字段校验。"""
        with TempProject() as root:
            self.assertEqual(create_ver.create_ver_record("测试标题", "smoke-test"), 0)

            records = list((root / "logic_version" / "records").glob("*.md"))
            self.assertEqual(len(records), 1)
            record = records[0]

            # 三个消费者共用的规范文件名
            self.assertRegex(record.name, r"^logic_version-\d{8}-\d{3}-smoke-test\.md$")
            self.assertTrue(recall.RECORD_NAME_RE.match(record.name))
            self.assertTrue(validate.RECORD_NAME_RE.match(record.name))
            self.assertTrue(link_ver_git.RECORD_NAME_RE.match(record.name))

            # 生成内容满足 validate 的必填字段（RULE-009）
            self.assertEqual(validate.check_required_fields(record), [])

            content = record.read_text(encoding="utf-8")
            self.assertIn("测试标题", content)
            self.assertIn(f"VER-{date.today().strftime('%Y%m%d')}-001", content)

    def test_next_number_counts_legacy_names(self):
        """旧命名 ver-*.md 占用的序号不能被重复分配。"""
        with TempProject() as root:
            records_dir = root / "logic_version" / "records"
            records_dir.mkdir(parents=True)
            today = date.today().strftime("%Y%m%d")
            (records_dir / f"ver-{today}-002-old.md").write_text("x", encoding="utf-8")
            self.assertEqual(create_ver.get_next_ver_number(records_dir, today), 3)

    def test_cmd_new_signature_matches(self):
        """recall.py cmd_new 与 create_ver 的接口保持一致（曾经断裂）。"""
        with TempProject():
            self.assertEqual(recall.cmd_new(["标题", "cmd-new-smoke"]), 0)
        self.assertEqual(recall.cmd_new(["只有一个参数"]), 1)


class StatusRecordDiscoveryTests(unittest.TestCase):
    def test_find_version_records_matches_canonical_names_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            (records_dir / "logic_version-20260811-001-a.md").write_text("x", encoding="utf-8")
            (records_dir / "ver-20260811-001-legacy.md").write_text("x", encoding="utf-8")
            (records_dir / "README.md").write_text("x", encoding="utf-8")
            names = [p.name for p in recall.find_version_records(records_dir)]
            self.assertEqual(names, ["logic_version-20260811-001-a.md"])


class DetectConflictsTests(unittest.TestCase):
    def test_extract_changes_accepts_heading_format(self):
        """标准 `## CHG-...:` 标题必须被提取（旧正则只认行首裸写法）。"""
        content = (
            "## CHG-20260811-001: 废弃暗色模式规则\n"
            "\n"
            "- 提议修改 RULE-001，废弃现行行为\n"
        )
        changes = detect_conflicts.extract_changes(content)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["id"], "CHG-20260811-001")
        self.assertEqual(changes[0]["title"], "废弃暗色模式规则")

        rules = [{"id": "RULE-001", "level": "key", "description": "x", "reason": "y"}]
        conflicts = detect_conflicts.check_change_rule_conflicts(changes, rules)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0][:2], ("CHG-20260811-001", "RULE-001"))

    def test_extract_changes_still_accepts_bare_format(self):
        content = "CHG-20260811-002: 裸格式标题\n正文\n"
        changes = detect_conflicts.extract_changes(content)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["id"], "CHG-20260811-002")


README_WITH_INTENT_LAYER = """# test

## 当前制度

| rule_id | 规则等级 | 当前有效规则/行为 | why | 决策记录 |
|---|---|---|---|---|
| RULE-001 | key | 示例规则正文 | 示例原因 | [VER-20260816-001](logic_version/records/logic_version-20260816-001-demo.md) |

## 功能意图与用户流程

### 功能意图登记

| intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 | last_verified |
|---|---|---|---|---|---|---|
| INT-20260816-001 | demo 命令 | 示例用户目标 | FLOW-001#1 | RULE-001 | src/app.py | 2026-08-16 |

### 用户流程

- FLOW-001 示例：1. 运行 demo → INT-20260816-001
"""


class QueryIntentTests(unittest.TestCase):
    def _make_project(self, root):
        (root / "logic_readme.md").write_text(
            README_WITH_INTENT_LAYER, encoding="utf-8"
        )
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("pass\n", encoding="utf-8")
        records_dir = root / "logic_version" / "records"
        records_dir.mkdir(parents=True)
        (records_dir / "logic_version-20260816-001-demo.md").write_text(
            "# VER-20260816-001: 示例记录\n\n- version_id: VER-20260816-001\n"
            "- date: 2026-08-16\n- after_commit: abc1234\n\n"
            "- intent_traceability: INT-20260816-001 -> RULE-001 -> "
            "test:src/app.py -> VER-20260816-001\n",
            encoding="utf-8",
        )

    def test_query_intent_resolves_rules_anchors_and_records(self):
        """反向查询：INT → 规则正文 → 代码锚点存在性 → 相关决策记录。"""
        with TempProject() as root:
            self._make_project(root)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exit_code = link_ver_git.query_intent("int-20260816-001")
            output = buffer.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("示例规则正文", output)
            self.assertIn("✅ src/app.py", output)
            self.assertIn("VER-20260816-001", output)

    def test_query_intent_unknown_id_fails_with_listing(self):
        with TempProject() as root:
            self._make_project(root)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exit_code = link_ver_git.query_intent("INT-20260816-999")
            self.assertEqual(exit_code, 1)
            self.assertIn("INT-20260816-001", buffer.getvalue())


class ValidateSemanticChecksTests(unittest.TestCase):
    def test_record_from_chg_without_requirement_fields_warns(self):
        """需求保全（RULE-014）：change_id != none 的新记录缺三字段必须发声。"""
        result = validate.ValidationResult()
        validate.check_record_requirement_fields(
            "- change_id: CHG-20260816-001\n",
            "logic_version-20260816-009-x.md",
            result,
        )
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("raw_request", result.warnings[0])

    def test_record_requirement_check_skips_legacy_and_filled(self):
        result = validate.ValidationResult()
        # 规则生效日之前的历史记录不检查
        validate.check_record_requirement_fields(
            "- change_id: CHG-20260808-001\n",
            "logic_version-20260808-001-x.md",
            result,
        )
        # 三字段齐全的记录通过
        validate.check_record_requirement_fields(
            "- change_id: CHG-20260816-002\n- raw_request: 原话\n"
            "- decomposition: 拆解\n- fit_analysis: 融入\n",
            "logic_version-20260816-009-x.md",
            result,
        )
        self.assertEqual(result.warnings, [])

    def test_intent_anchor_existence_checked_against_root(self):
        """INT 代码锚点悬空必须发声（文件改名后反向查询会静默断链）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme = README_WITH_INTENT_LAYER.replace("src/app.py", "src/gone.py")
            result = validate.ValidationResult()
            validate.check_intent_layer(readme, {"RULE-001"}, result, root)
            self.assertTrue(any("src/gone.py" in w for w in result.warnings))
            # 锚点存在时无警告
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("pass\n", encoding="utf-8")
            result_ok = validate.ValidationResult()
            validate.check_intent_layer(
                README_WITH_INTENT_LAYER, {"RULE-001"}, result_ok, root
            )
            self.assertEqual(result_ok.warnings, [])


class ProjectRootTests(unittest.TestCase):
    def test_link_ver_git_finds_root_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "logic_readme.md").write_text("# test\n", encoding="utf-8")
            subdir = root / "src" / "deep"
            subdir.mkdir(parents=True)
            self.assertEqual(link_ver_git.find_project_root(subdir), root)

    def test_create_ver_falls_back_to_script_project(self):
        """cwd 向上找不到 logic_readme.md 时退回 Recall 自身，而不是写进 cwd。"""
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = Path.cwd()
            os.chdir(tmp)
            try:
                found = create_ver.find_project_root()
            finally:
                os.chdir(old_cwd)
            # 临时目录的父链上可能意外存在 logic_readme.md；
            # 只断言结果不是无标记的临时目录本身
            self.assertNotEqual(found, Path(tmp).resolve())


class StatusLeftoverTests(unittest.TestCase):
    """RULE-020 收尾归零：status 必须把未跟踪文件与已跟踪修改分开列。"""

    def test_classify_porcelain_splits_tracked_and_untracked(self):
        porcelain = (
            " M scripts/recall.py\n"
            "A  logic_version/records/new.md\n"
            "?? scratch_probe.py\n"
            "?? tmp/debug.log\n"
            "R  old.md -> new_name.md\n"
        )
        tracked, untracked = recall.classify_porcelain(porcelain)
        self.assertEqual(
            tracked,
            ["scripts/recall.py", "logic_version/records/new.md", "new_name.md"],
        )
        self.assertEqual(untracked, ["scratch_probe.py", "tmp/debug.log"])

    def test_classify_porcelain_empty_is_clean(self):
        self.assertEqual(recall.classify_porcelain(""), ([], []))
        self.assertEqual(recall.classify_porcelain(None), ([], []))


if __name__ == "__main__":
    unittest.main()
