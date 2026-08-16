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


class DocDriftTests(unittest.TestCase):
    def test_non_git_directory_is_silent(self) -> None:
        result = VALIDATE.ValidationResult()
        with tempfile.TemporaryDirectory() as temporary:
            VALIDATE.check_doc_drift(Path(temporary), result)
        self.assertFalse(result.errors)
        self.assertFalse(result.warnings)
        self.assertFalse(result.info)


if __name__ == "__main__":
    unittest.main()
