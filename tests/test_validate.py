import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("validate", SCRIPT_PATH)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATE
SPEC.loader.exec_module(VALIDATE)


REGISTRY_HEADER = (
    "| module_id | scope_path | membership | scope_type/layer | doc_policy "
    "| logic_readme | logic_change | owner | status |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)
README_ONLY_ROW = (
    "| MOD-APP | src | in-system | module/runtime-code | readme-only "
    "| [app](src/logic_readme.md) | none | self | active |\n"
)
PAIRED_DOMAIN_ROW = (
    "| MOD-BILLING | logic_domains/billing | in-system | domain/runtime-code | paired "
    "| [billing](logic_domains/billing/logic_readme.md) "
    "| [changes](logic_domains/billing/logic_change.md) | self | active |\n"
)
OUT_OF_SYSTEM_PAIRED_ROW = (
    "| MOD-VENDOR | vendor | out-of-system | foreign/runtime-code | paired "
    "| none | none | self | active |\n"
)


def write_record(records_dir: Path, name: str, status: str) -> Path:
    path = records_dir / name
    path.write_text(
        f"# VER demo\n\n- status: {status}\n- after_commit: abc1234\n",
        encoding="utf-8",
    )
    return path


class RejectedRecordRegistrationTests(unittest.TestCase):
    """RULE-015：rejected/cancelled/rolled-back 记录豁免有效决策索引登记。"""

    def _run(self, readme_content: str):
        result = VALIDATE.ValidationResult()
        with tempfile.TemporaryDirectory() as temporary:
            records_dir = Path(temporary)
            records = [
                write_record(
                    records_dir, "logic_version-20260816-101-win.md", "effective"
                ),
                write_record(
                    records_dir, "logic_version-20260816-102-lost.md", "rejected"
                ),
            ]
            index_path = records_dir / "index.md"
            index_path.write_text(
                "| VER-20260816-101 | win |\n| VER-20260816-102 | lost |\n",
                encoding="utf-8",
            )
            VALIDATE.check_ver_registrations(
                records, index_path, readme_content, result
            )
        return result

    def test_rejected_record_not_required_in_effective_index(self) -> None:
        result = self._run("| VER-20260816-101 | win | rules | link |\n")
        self.assertFalse(
            [msg for msg in result.warnings if "VER-20260816-102" in msg],
            result.warnings,
        )
        self.assertFalse(result.errors, result.errors)

    def test_rejected_record_in_effective_index_is_flagged(self) -> None:
        result = self._run(
            "| VER-20260816-101 | win | rules | link |\n"
            "| VER-20260816-102 | lost | rules | link |\n"
        )
        self.assertTrue(
            [
                msg
                for msg in result.warnings
                if "VER-20260816-102" in msg and "不应登记" in msg
            ],
            result.warnings,
        )

    def test_effective_record_still_requires_registration(self) -> None:
        result = self._run("")
        self.assertTrue(
            [
                msg
                for msg in result.warnings
                if "VER-20260816-101" in msg and "有效决策索引" in msg
            ],
            result.warnings,
        )


class ChildReadmeCoverageTests(unittest.TestCase):
    """RULE-018：已登记子文档纳入编号空间与一致性检查。"""

    def test_missing_registered_child_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = "# Root\n\n### 范围登记表\n\n" + REGISTRY_HEADER + README_ONLY_ROW
            paths, missing = VALIDATE.find_registered_child_readmes(content, root)
        self.assertEqual(paths, [])
        self.assertEqual(missing, ["src"])

    def test_existing_registered_child_is_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text("# child\n", encoding="utf-8")
            content = "# Root\n\n### 范围登记表\n\n" + REGISTRY_HEADER + README_ONLY_ROW
            paths, missing = VALIDATE.find_registered_child_readmes(content, root)
        self.assertEqual(missing, [])
        self.assertEqual([p.name for p in paths], ["logic_readme.md"])

    def test_duplicate_rule_across_root_and_child_is_an_error(self) -> None:
        old_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "logic_readme.md").write_text(
                "# Root\n\n## 当前制度\n\n"
                "| RULE-001 | key | 根规则 |\n\n"
                "### 范围登记表\n\n" + REGISTRY_HEADER + README_ONLY_ROW,
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "logic_readme.md").write_text(
                "# Child\n\n| RULE-001 | key | 子文档撞号 |\n", encoding="utf-8"
            )
            os.chdir(root)
            try:
                result = VALIDATE.validate_recall()
            finally:
                os.chdir(old_cwd)
        self.assertTrue(
            [
                msg
                for msg in result.errors
                if "RULE-001" in msg and "src/logic_readme.md" in msg
            ],
            result.errors,
        )


class DomainLedgerTests(unittest.TestCase):
    """RULE-018 一二级拆分法：paired 领域纳入子文档检查；领域 CHG 必须登记进根公报。"""

    DOMAIN_CHG = "CHG-20260903-101"

    def test_paired_domain_readme_is_registered_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            domain = root / "logic_domains" / "billing"
            domain.mkdir(parents=True)
            (domain / "logic_readme.md").write_text("# billing\n", encoding="utf-8")
            content = (
                "# Root\n\n### 范围登记表\n\n"
                + REGISTRY_HEADER
                + PAIRED_DOMAIN_ROW
                + OUT_OF_SYSTEM_PAIRED_ROW
            )
            paths, missing = VALIDATE.find_registered_child_readmes(content, root)
        self.assertEqual(missing, [])
        self.assertEqual(
            [p.relative_to(root).as_posix() for p in paths],
            ["logic_domains/billing/logic_readme.md"],
        )

    def _write_project(self, root: Path, *, gazette: bool) -> None:
        (root / "logic_readme.md").write_text(
            "# Root\n\n## 当前制度\n\n| RULE-001 | key | 根规则 |\n\n"
            "### 范围登记表\n\n" + REGISTRY_HEADER + PAIRED_DOMAIN_ROW,
            encoding="utf-8",
        )
        gazette_row = (
            f"| {self.DOMAIN_CHG} | draft | logic_domains/billing | self | 发票 | none "
            f"| [{self.DOMAIN_CHG}](logic_domains/billing/logic_change.md#{self.DOMAIN_CHG.lower()}) "
            "| 2026-09-03 |\n"
            if gazette
            else ""
        )
        (root / "logic_change.md").write_text(
            "# Root ledger\n\n## 活跃议案索引\n\n"
            "| change_id | status | scope | owner | target/summary | blocked_by "
            "| proposal_path | last_updated |\n|---|---|---|---|---|---|---|---|\n"
            + gazette_row,
            encoding="utf-8",
        )
        domain = root / "logic_domains" / "billing"
        domain.mkdir(parents=True)
        (domain / "logic_readme.md").write_text(
            "# Billing\n\n| RULE-002 | ordinary | 领域规则 |\n", encoding="utf-8"
        )
        (domain / "logic_change.md").write_text(
            f"# Billing ledger\n\n## {self.DOMAIN_CHG}: 发票编号\n\n- status: draft\n",
            encoding="utf-8",
        )

    def _validate(self, root: Path):
        old_cwd = Path.cwd()
        os.chdir(root)
        try:
            return VALIDATE.validate_recall()
        finally:
            os.chdir(old_cwd)

    def test_domain_chg_missing_from_root_gazette_warns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_project(root, gazette=False)
            result = self._validate(root)
        hits = [
            msg
            for msg in result.warnings
            if self.DOMAIN_CHG in msg and "未登记进根 logic_change.md 活跃议案索引" in msg
        ]
        self.assertEqual(len(hits), 1, result.warnings)
        self.assertIn("logic_domains/billing/logic_change.md", hits[0])
        self.assertTrue(
            [msg for msg in result.info if "1 份领域账本" in msg], result.info
        )

    def test_domain_chg_registered_in_root_gazette_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_project(root, gazette=True)
            result = self._validate(root)
        self.assertFalse(
            [msg for msg in result.warnings if "未登记进根 logic_change.md" in msg],
            result.warnings,
        )
        # 领域 readme 的规则定义与根共用编号空间：RULE-001 / RULE-002 各定义一次
        self.assertFalse(
            [msg for msg in result.errors if "被定义多次" in msg], result.errors
        )
        self.assertTrue(
            [msg for msg in result.info if "找到 2 条规则定义" in msg], result.info
        )


def intent_layer_readme(*, source_header: str | None, source_value: str = "") -> str:
    """带功能意图登记表的最小 readme；``source_header`` 为 None 时不含「来源」列。"""
    has_source = source_header is not None
    header = (
        "| intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 |"
        + (f" {source_header} |" if has_source else "")
        + " last_verified |"
    )
    separator = "|---" * (8 if has_source else 7) + "|"
    row = (
        "| INT-20260816-001 | demo 命令 | 示例用户目标 | FLOW-001#1 | RULE-001 | src/app.py |"
        + (f" {source_value} |" if has_source else "")
        + " 2026-08-16 |"
    )
    return (
        "# test\n\n## 功能意图与用户流程\n\n### 功能意图登记\n\n"
        f"{header}\n{separator}\n{row}\n\n"
        "### 用户流程\n\n- FLOW-001 示例：1. 运行 demo → INT-20260816-001\n"
    )


class IntentSourceColumnTests(unittest.TestCase):
    """RULE-014/016：意图登记表的「来源」列——区分用户表述与 AI 推断。"""

    def _check(self, content: str):
        result = VALIDATE.ValidationResult()
        VALIDATE.check_intent_layer(content, {"RULE-001"}, result)
        return result

    @staticmethod
    def _source_notices(result) -> list:
        # check_intent_layer 末尾总会加一条“校验完成”的 info，只取来源列相关的提示
        return [msg for msg in result.info if "来源" in msg]

    def test_missing_source_column_is_info_only(self) -> None:
        result = self._check(intent_layer_readme(source_header=None))
        notices = self._source_notices(result)
        self.assertEqual(len(notices), 1, result.info)
        self.assertIn("缺少「来源」列", notices[0])
        self.assertIn("logic_readme.md", notices[0])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.errors, [])

    def test_missing_source_column_uses_doc_label(self) -> None:
        result = VALIDATE.ValidationResult()
        VALIDATE.check_intent_layer(
            intent_layer_readme(source_header=None),
            {"RULE-001"},
            result,
            doc_label="src/logic_readme.md",
        )
        self.assertTrue(
            [
                msg
                for msg in result.info
                if "src/logic_readme.md:" in msg and "缺少「来源」列" in msg
            ],
            result.info,
        )

    def test_unconfirmed_sources_warn(self) -> None:
        for value in ("", "inferred", "code-derived", "Inferred", "code-derived:2026-09-04"):
            with self.subTest(source=value):
                result = self._check(intent_layer_readme(source_header="来源", source_value=value))
                self.assertEqual(len(result.warnings), 1, result.warnings)
                self.assertIn("INT-20260816-001", result.warnings[0])
                self.assertIn("尚未经用户确认", result.warnings[0])
                self.assertEqual(self._source_notices(result), [])
                self.assertEqual(result.errors, [])
        empty = self._check(intent_layer_readme(source_header="来源", source_value=""))
        self.assertIn("「空」", empty.warnings[0])

    def test_user_sources_are_silent(self) -> None:
        for value in ("user:2026-09-04", "user-confirmed:2026-09-04", "User-Confirmed:2026-09-04"):
            with self.subTest(source=value):
                result = self._check(intent_layer_readme(source_header="来源", source_value=value))
                self.assertEqual(result.warnings, [])
                self.assertEqual(self._source_notices(result), [])
                self.assertEqual(result.errors, [])

    def test_unrecognized_source_format_warns(self) -> None:
        for value in ("用户口述", "user", "user:昨天", "confirmed:2026-09-04"):
            with self.subTest(source=value):
                result = self._check(intent_layer_readme(source_header="来源", source_value=value))
                self.assertEqual(len(result.warnings), 1, result.warnings)
                self.assertIn("格式无法识别", result.warnings[0])
                self.assertIn(value, result.warnings[0])

    def test_source_header_is_matched_by_prefix_before_last_verified(self) -> None:
        """表头「来源（user/inferred）」这类带说明的写法也算来源列。"""
        result = self._check(
            intent_layer_readme(source_header="来源（user/inferred）", source_value="inferred")
        )
        self.assertEqual(self._source_notices(result), [])
        self.assertEqual(len(result.warnings), 1, result.warnings)
        self.assertIn("尚未经用户确认", result.warnings[0])

    def test_source_column_does_not_break_anchor_check(self) -> None:
        """来源列插在代码锚点之后、last_verified 之前，锚点列位置不变。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = VALIDATE.ValidationResult()
            VALIDATE.check_intent_layer(
                intent_layer_readme(source_header="来源", source_value="user:2026-09-04"),
                {"RULE-001"},
                result,
                root,
            )
            self.assertTrue(any("src/app.py" in msg and "不存在" in msg for msg in result.warnings), result.warnings)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("pass\n", encoding="utf-8")
            ok = VALIDATE.ValidationResult()
            VALIDATE.check_intent_layer(
                intent_layer_readme(source_header="来源", source_value="user:2026-09-04"),
                {"RULE-001"},
                ok,
                root,
            )
        self.assertEqual(ok.warnings, [])


class DocDriftTests(unittest.TestCase):
    def test_non_git_directory_is_silent(self) -> None:
        result = VALIDATE.ValidationResult()
        with tempfile.TemporaryDirectory() as temporary:
            VALIDATE.check_doc_drift(Path(temporary), result)
        self.assertFalse(result.errors)
        self.assertFalse(result.warnings)
        self.assertFalse(result.info)


class UntrackedLeftoverTests(unittest.TestCase):
    """RULE-020 收尾归零：未跟踪且未被忽略的文件只告警、不阻断、不删除。"""

    def test_no_leftovers_is_silent(self) -> None:
        result = VALIDATE.ValidationResult()
        VALIDATE.report_untracked_leftovers([], result)
        VALIDATE.report_untracked_leftovers(["", "   "], result)
        self.assertFalse(result.warnings)
        self.assertFalse(result.errors)

    def test_leftovers_are_listed_as_warning_not_error(self) -> None:
        result = VALIDATE.ValidationResult()
        VALIDATE.report_untracked_leftovers(
            ["scratch_probe.py", "notes/draft.md"], result
        )
        self.assertFalse(result.errors)
        self.assertEqual(len(result.warnings), 1)
        message = result.warnings[0]
        self.assertIn("2 个未跟踪", message)
        self.assertIn("scratch_probe.py", message)
        self.assertIn("notes/draft.md", message)
        self.assertIn("RULE-020", message)

    def test_long_lists_are_truncated(self) -> None:
        result = VALIDATE.ValidationResult()
        paths = [f"junk_{i}.tmp" for i in range(VALIDATE.LEFTOVER_LIST_LIMIT + 3)]
        VALIDATE.report_untracked_leftovers(paths, result)
        message = result.warnings[0]
        self.assertIn("另 3 个", message)
        self.assertNotIn(paths[-1], message)


class UnpushedCommitTests(unittest.TestCase):
    """RULE-010：本地领先上游的提交数 → 非阻断告警；无上游/非仓库沉默。"""

    def test_none_and_zero_are_silent(self) -> None:
        result = VALIDATE.ValidationResult()
        VALIDATE.report_unpushed_commits(None, result)
        VALIDATE.report_unpushed_commits(0, result)
        self.assertFalse(result.warnings)
        self.assertFalse(result.errors)

    def test_positive_count_is_warning_not_error(self) -> None:
        result = VALIDATE.ValidationResult()
        VALIDATE.report_unpushed_commits(4, result)
        self.assertFalse(result.errors)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("4", result.warnings[0])
        self.assertIn("RULE-010", result.warnings[0])


if __name__ == "__main__":
    unittest.main()
