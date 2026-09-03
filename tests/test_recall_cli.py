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
import route_docs
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


class StatusRuleCountTests(unittest.TestCase):
    """RULE-021 ③：status 的规则数按定义行统计宪法 + 全部领域，与 validate 同口径。

    旧实现在根文档正则数 RULE 引用：指针行"见 RULE-010/011/013"也被算进去，
    报出的数既不是宪法的也不是全项目的（2026-09-04：status 21 vs validate 23）。
    """

    def test_counts_definition_rows_across_constitution_and_domains(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "logic_readme.md").write_text(
                "## 当前制度\n\n| rule_id | 规则等级 | 规则 |\n|---|---|---|\n"
                "| RULE-001 | key | 逻辑回档 |\n| RULE-002 | key | 只留最新 |\n\n"
                "领域规则：RULE-010/011 见领域文档；正文提到 RULE-099 不算定义\n",
                encoding="utf-8",
            )
            domain = root / "logic_domains" / "sync"
            domain.mkdir(parents=True)
            (domain / "logic_readme.md").write_text(
                "| RULE-010 | key | 自动同步 |\n| RULE-011 | key | 自动保存 |\n"
                "| RULE-001 | key | 与宪法撞号也只算一次 |\n",
                encoding="utf-8",
            )
            found = recall.count_rule_definitions(
                root / "logic_readme.md", [domain / "logic_readme.md", root / "missing.md"]
            )
        self.assertEqual(found, {"RULE-001", "RULE-002", "RULE-010", "RULE-011"})

    def test_matches_validate_count_in_this_repo(self):
        readme = ROOT / "logic_readme.md"
        domains = [d.readme for d in recall.registered_domains(ROOT)]
        cli_count = len(recall.count_rule_definitions(readme, domains))
        validate_ids = {rid for rid, _ in validate.extract_rule_definitions(readme)}
        for domain_readme in domains:
            validate_ids |= {rid for rid, _ in validate.extract_rule_definitions(domain_readme)}
        self.assertEqual(cli_count, len(validate_ids))


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

    # 一法多议案 / 旧议案 vs 新法（VER-20260904-001）

    MULTI_PROPOSAL_LEDGER = (
        "## CHG-20260901-001: 收紧输出契约\n"
        "- created: 2026-01-01\n"
        "- authority_surfaces: RULE-001\n"
        "- conflicts_with: none\n"
        "\n"
        "## CHG-20260901-002: 放宽输出契约\n"
        "- created: 2026-01-05\n"
        "- last_status_change: 2026-01-20\n"
        "- authority_surfaces: RULE-001, RULE-002\n"
        "- conflicts_with: none\n"
    )

    def test_extract_rule_dates_reads_last_reviewed_column(self):
        content = (
            "| rule_id | 规则等级 | 当前有效规则/行为 | why | 决策记录 | 决策依据 | 验证证据 | validity | last_reviewed | review_owner |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| RULE-001 | key | 规则一 | 原因 | none | user | 证据 | valid | 2026-02-01 | self |\n"
            "| RULE-002 | ordinary | 规则二 | 原因 | none | user | 证据 | valid | 2026-03-15 | self |\n"
            "| RULE-003 | ordinary | 规则三 | 原因 | none | user | 证据 | valid | 待定 | self |\n"
            "| RULE-004 | ordinary | 短行没有日期列 |\n"
        )
        self.assertEqual(
            detect_conflicts.extract_rule_dates(content),
            {"RULE-001": "2026-02-01", "RULE-002": "2026-03-15"},
        )

    def test_multi_proposal_conflict_without_reciprocal_conflicts_with(self):
        changes = detect_conflicts.extract_changes(self.MULTI_PROPOSAL_LEDGER)
        self.assertEqual([c["id"] for c in changes], ["CHG-20260901-001", "CHG-20260901-002"])
        findings = detect_conflicts.check_multi_proposal_conflicts(changes)
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0][:2], ("CHG-20260901-001", "CHG-20260901-002"))
        self.assertIn("RULE-001", findings[0][2])
        self.assertNotIn("RULE-002", findings[0][2])

    def test_multi_proposal_one_way_declaration_still_reported(self):
        ledger = self.MULTI_PROPOSAL_LEDGER.replace(
            "- conflicts_with: none\n\n", "- conflicts_with: CHG-20260901-002\n\n", 1
        )
        findings = detect_conflicts.check_multi_proposal_conflicts(
            detect_conflicts.extract_changes(ledger)
        )
        self.assertEqual(len(findings), 1, findings)

    def test_multi_proposal_reciprocal_declaration_is_clean(self):
        ledger = self.MULTI_PROPOSAL_LEDGER.replace(
            "- conflicts_with: none\n\n", "- conflicts_with: CHG-20260901-002\n\n", 1
        ).replace(
            "- authority_surfaces: RULE-001, RULE-002\n- conflicts_with: none\n",
            "- authority_surfaces: RULE-001, RULE-002\n- conflicts_with: chg-20260901-001\n",
        )
        changes = detect_conflicts.extract_changes(ledger)
        self.assertEqual(detect_conflicts.check_multi_proposal_conflicts(changes), [])

    def test_multi_proposal_disjoint_targets_are_clean(self):
        ledger = self.MULTI_PROPOSAL_LEDGER.replace(
            "- authority_surfaces: RULE-001, RULE-002", "- authority_surfaces: RULE-002"
        )
        self.assertEqual(
            detect_conflicts.check_multi_proposal_conflicts(
                detect_conflicts.extract_changes(ledger)
            ),
            [],
        )

    def test_stale_baseline_when_rule_reviewed_after_proposal(self):
        changes = detect_conflicts.extract_changes(self.MULTI_PROPOSAL_LEDGER)
        findings = detect_conflicts.check_stale_baselines(changes, {"RULE-001": "2026-02-01"})
        # 001 created 2026-01-01 < 2026-02-01 → 失效；002 最近变动 2026-01-20 < 2026-02-01 → 也失效
        self.assertEqual(
            [f[:2] for f in findings],
            [("CHG-20260901-001", "RULE-001"), ("CHG-20260901-002", "RULE-001")],
        )
        self.assertIn("2026-02-01", findings[0][2])
        self.assertIn("2026-01-01", findings[0][2])
        self.assertIn("2026-01-20", findings[1][2])

    def test_stale_baseline_uses_last_status_change_and_ignores_old_rules(self):
        changes = detect_conflicts.extract_changes(self.MULTI_PROPOSAL_LEDGER)
        # 规则在 002 最近变动之前、001 立案之后修订 → 只有 001 失效
        findings = detect_conflicts.check_stale_baselines(changes, {"RULE-001": "2026-01-10"})
        self.assertEqual([f[:2] for f in findings], [("CHG-20260901-001", "RULE-001")])
        # 规则早于所有议案、或不在任何议案的 authority_surfaces 里 → 无发现
        self.assertEqual(
            detect_conflicts.check_stale_baselines(
                changes, {"RULE-001": "2025-12-31", "RULE-999": "2026-09-01"}
            ),
            [],
        )

    def test_stale_baseline_skips_changes_without_dates(self):
        ledger = "## CHG-20260901-003: 无日期\n- created: event-driven\n- authority_surfaces: RULE-001\n"
        changes = detect_conflicts.extract_changes(ledger)
        self.assertEqual(
            detect_conflicts.check_stale_baselines(changes, {"RULE-001": "2026-02-01"}), []
        )


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


CONSTITUTION_WITH_DOMAINS = """# Constitution

### 范围登记表

| module_id | scope_path | membership | scope_type/layer | doc_policy | logic_readme | logic_change | owner | status |
|---|---|---|---|---|---|---|---|---|
| MOD-ROOT | . | in-system | root/runtime-code | paired | [root](logic_readme.md) | [changes](logic_change.md) | self | active |
| MOD-BILLING | logic_domains/billing | in-system | domain/runtime-code | paired | [billing](logic_domains/billing/logic_readme.md) | [changes](logic_domains/billing/logic_change.md) | self | active |
| MOD-SYNC | logic_domains/sync | in-system | domain/runtime-code | paired | [sync](logic_domains/sync/logic_readme.md) | [changes](logic_domains/sync/logic_change.md) | self | active |
"""


CONSTITUTION_WITH_INTENTS = CONSTITUTION_WITH_DOMAINS + """
## 功能意图与用户流程

### 功能意图登记

| intent_id | 功能入口 | intent | 流程位置 | 关联规则 | 代码锚点 | 来源 | last_verified |
|---|---|---|---|---|---|---|---|
| INT-20260904-001 | 开票命令 | 月末批量生成发票编号 | FLOW-001#1 | none | src/billing/invoice.py | user:2026-09-04 | 2026-09-04 |
| INT-20260904-002 | 提交后推送 | 提交后自动推送远端 | FLOW-001#2 | RULE-SYNC-001 | none | inferred | 2026-09-04 |

### 用户流程

- FLOW-001 示例：1. 开票 → INT-20260904-001；2. 推送 → INT-20260904-002
"""


class RouteDocsTests(unittest.TestCase):
    """RULE-018 按需导入：宪法必读，命中职权或关键词的领域才进入读取清单。"""

    def _write_project(self, root: Path) -> None:
        (root / "logic_readme.md").write_text(CONSTITUTION_WITH_DOMAINS, encoding="utf-8")
        (root / "logic_change.md").write_text(
            "# Root ledger\n\n## 活跃议案索引\n\n"
            "| change_id | status | scope | owner | target/summary | blocked_by | proposal_path | last_updated |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| CHG-20260903-101 | draft | logic_domains/billing | self | 发票 | none "
            "| [CHG-20260903-101](logic_domains/billing/logic_change.md#chg-20260903-101) | 2026-09-03 |\n",
            encoding="utf-8",
        )
        for slug, owned, body in (
            ("billing", "src/billing, scripts/bill_*.py", "发票编号规则"),
            ("sync", "scripts/git_sync.py", "自动同步规则"),
        ):
            domain = root / "logic_domains" / slug
            domain.mkdir(parents=True)
            (domain / "logic_readme.md").write_text(
                f"# {slug}\n\n- owned_paths: {owned}\n\n{body}\n", encoding="utf-8"
            )
            (domain / "logic_change.md").write_text(f"# {slug} ledger\n", encoding="utf-8")
        (root / "src" / "billing").mkdir(parents=True)

    def test_constitution_always_first_and_domains_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            plan = route_docs.build_plan(root, [])
        self.assertEqual(
            [item["path"] for item in plan["reading_order"]],
            ["logic_readme.md", "logic_change.md"],
        )
        self.assertEqual(plan["matched_domains"], [])
        self.assertEqual(
            sorted(d["module_id"] for d in plan["domains"]), ["MOD-BILLING", "MOD-SYNC"]
        )
        self.assertGreater(plan["total_tokens_estimate"], 0)
        self.assertTrue(all(item["exists"] for item in plan["reading_order"]))

    def test_path_target_matches_owned_paths_by_prefix_and_glob(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            prefix = route_docs.build_plan(root, ["src/billing/invoice.py"])
            glob_hit = route_docs.build_plan(root, ["scripts/bill_report.py"])
            exact = route_docs.build_plan(root, ["scripts/git_sync.py"])
            miss = route_docs.build_plan(root, ["docs/unrelated.md"])
        self.assertEqual(prefix["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(
            [item["path"] for item in prefix["reading_order"]],
            [
                "logic_readme.md",
                "logic_change.md",
                "logic_domains/billing/logic_readme.md",
                "logic_domains/billing/logic_change.md",
            ],
        )
        self.assertEqual(prefix["in_flight_changes"], ["CHG-20260903-101 (draft) -> logic_domains/billing"])
        self.assertEqual(glob_hit["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(exact["matched_domains"], ["logic_domains/sync"])
        self.assertEqual(miss["matched_domains"], [])
        self.assertEqual(len(miss["reading_order"]), 2)

    def test_keyword_target_searches_domain_readme_and_module_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            by_text = route_docs.build_plan(root, ["发票"])
            by_id = route_docs.build_plan(root, ["mod-sync"])
            both = route_docs.build_plan(root, ["发票", "同步"])
        self.assertEqual(by_text["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(by_id["matched_domains"], ["logic_domains/sync"])
        self.assertEqual(both["matched_domains"], ["logic_domains/billing", "logic_domains/sync"])
        self.assertEqual(len(both["reading_order"]), 6)

    def test_keyword_ignores_boundary_lines_and_table_headers(self):
        """"不负责"行列的是别人的职权，表头是每份文档都一样的列名——都不算命中。

        2026-09-04：`route 审计` 把 git-pipeline 也拉进清单，一次因"不负责：审计/校验"，
        一次因表头"why（仅一句可审计摘要）"；两域全读，按需导入的收益归零。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            sync_readme = root / "logic_domains" / "sync" / "logic_readme.md"
            sync_readme.write_text(
                sync_readme.read_text(encoding="utf-8")
                + "\n## 目标与边界\n\n- 负责：推送\n- 不负责：发票编号（MOD-BILLING）\n\n"
                "## 当前制度\n\n| rule_id | why（仅一句可审计摘要） |\n|---|---|\n"
                "| RULE-SYNC-001 | 提交后自动推送 |\n",
                encoding="utf-8",
            )
            by_boundary = route_docs.build_plan(root, ["发票编号"])
            by_header = route_docs.build_plan(root, ["审计摘要"])
            real_hit = route_docs.build_plan(root, ["自动推送"])
        self.assertEqual(by_boundary["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(by_header["matched_domains"], [])
        self.assertEqual(real_hit["matched_domains"], ["logic_domains/sync"])

    # 按用户意图路由（宪法意图层 → 领域）

    def _write_intent_project(self, root: Path) -> None:
        self._write_project(root)
        (root / "logic_readme.md").write_text(CONSTITUTION_WITH_INTENTS, encoding="utf-8")
        sync_readme = root / "logic_domains" / "sync" / "logic_readme.md"
        sync_readme.write_text(
            sync_readme.read_text(encoding="utf-8")
            + "\n| RULE-SYNC-001 | ordinary | 提交后自动推送 |\n",
            encoding="utf-8",
        )

    def test_constitution_intents_parses_registry_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_intent_project(root)
            intents = route_docs.constitution_intents(root)
            self.assertEqual(route_docs.constitution_intents(root / "nowhere"), [])
        self.assertEqual([i["intent_id"] for i in intents], ["INT-20260904-001", "INT-20260904-002"])
        self.assertEqual(intents[0]["anchors"], ["src/billing/invoice.py"])
        self.assertEqual(intents[0]["rules"], [])
        self.assertEqual(intents[0]["source"], "user:2026-09-04")
        self.assertEqual(intents[1]["anchors"], [])
        self.assertEqual(intents[1]["rules"], ["RULE-SYNC-001"])
        self.assertEqual(intents[1]["source"], "inferred")

    def test_intent_id_target_routes_to_domain_by_code_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_intent_project(root)
            plan = route_docs.build_plan(root, ["int-20260904-001"])
        self.assertEqual(plan["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(len(plan["matched_intents"]), 1)
        self.assertEqual(plan["matched_intents"][0]["intent_id"], "INT-20260904-001")
        self.assertEqual(plan["matched_intents"][0]["source"], "user:2026-09-04")
        self.assertEqual(
            [item["path"] for item in plan["reading_order"]],
            [
                "logic_readme.md",
                "logic_change.md",
                "logic_domains/billing/logic_readme.md",
                "logic_domains/billing/logic_change.md",
            ],
        )
        reason = plan["reading_order"][2]["reason"]
        self.assertIn("INT-20260904-001", reason)
        self.assertIn("src/billing/invoice.py", reason)

    def test_intent_id_target_routes_to_domain_by_rule_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_intent_project(root)
            plan = route_docs.build_plan(root, ["INT-20260904-002"])
        self.assertEqual(plan["matched_domains"], ["logic_domains/sync"])
        self.assertEqual(plan["matched_intents"][0]["source"], "inferred")
        self.assertIn("RULE-SYNC-001", plan["reading_order"][2]["reason"])

    def test_keyword_in_intent_text_matches_intent_and_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_intent_project(root)
            by_intent_text = route_docs.build_plan(root, ["月末批量"])
            by_entry = route_docs.build_plan(root, ["开票命令"])
        self.assertEqual(
            [i["intent_id"] for i in by_intent_text["matched_intents"]], ["INT-20260904-001"]
        )
        self.assertEqual(by_intent_text["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(
            [i["intent_id"] for i in by_entry["matched_intents"]], ["INT-20260904-001"]
        )
        self.assertEqual(by_entry["matched_domains"], ["logic_domains/billing"])

    def test_path_target_does_not_match_intents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_intent_project(root)
            plan = route_docs.build_plan(root, ["src/billing/invoice.py"])
            unknown = route_docs.build_plan(root, ["INT-20260904-999"])
        self.assertEqual(plan["matched_intents"], [])
        self.assertEqual(plan["matched_domains"], ["logic_domains/billing"])
        self.assertEqual(unknown["matched_intents"], [])
        self.assertEqual(unknown["matched_domains"], [])

    def test_plan_without_intent_table_has_empty_matched_intents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(root)
            plan = route_docs.build_plan(root, ["发票"])
        self.assertEqual(plan["matched_intents"], [])
        self.assertEqual(plan["matched_domains"], ["logic_domains/billing"])

    def test_estimate_tokens_counts_cjk_per_char(self):
        self.assertEqual(route_docs.estimate_tokens("abcd" * 10), 10)
        self.assertEqual(route_docs.estimate_tokens("中文"), 2)


class UnpushedHintTests(unittest.TestCase):
    """RULE-010：status 把本地领先上游的提交数变成一行提示；无上游时沉默。"""

    def test_describe_unpushed(self):
        self.assertIsNone(recall.describe_unpushed(None))
        self.assertIsNone(recall.describe_unpushed(0))
        line = recall.describe_unpushed(3)
        self.assertIn("3", line)
        self.assertIn("RULE-010", line)


class CliGlueSmokeTests(unittest.TestCase):
    """RULE-021：每条子命令以子进程方式真跑一遍，只断言退出码与关键输出。

    2026-09-03 两处故障（status 的 GBK 解码、conflicts 把子命令名当项目根）
    都发生在 recall.py 与子模块的装配层，纯函数测试全绿却上不了线。
    """

    RECALL = ROOT / "scripts" / "recall.py"

    def _run(self, *args, cwd=ROOT):
        import subprocess

        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        completed = subprocess.run(
            [sys.executable, str(self.RECALL), *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env=env,
        )
        return completed.returncode, completed.stdout + completed.stderr

    def test_help_exits_zero(self):
        code, out = self._run("help")
        self.assertEqual(code, 0)
        self.assertIn("conflicts", out)

    def test_status_exits_zero_in_this_repo(self):
        code, out = self._run("status")
        self.assertEqual(code, 0, out)
        self.assertIn("Recall 系统状态", out)
        # RULE-018：状态页报告领域（部门法）数量，活跃变更按账本分列 CHG 正文
        self.assertIn("🏛️  领域（部门法）:", out)
        self.assertIn("个 CHG 正文（logic_change.md", out)
        self.assertNotIn("错误", out)
        self.assertNotIn("Traceback", out)

    def test_route_json_exits_zero(self):
        import json

        code, out = self._run("route", "--json")
        self.assertEqual(code, 0, out)
        payload = json.loads(out[out.index("{"):])
        self.assertIn("reading_order", payload)
        self.assertEqual(
            [item["path"] for item in payload["reading_order"][:2]],
            ["logic_readme.md", "logic_change.md"],
        )
        self.assertIn("total_tokens_estimate", payload)

    def test_route_text_mode_from_subdirectory(self):
        code, out = self._run("route", "scripts/git_sync.py", cwd=ROOT / "scripts")
        self.assertEqual(code, 0, out)
        self.assertIn("Recall 读取清单", out)
        self.assertNotIn("Traceback", out)

    def test_audit_forwards_to_static_gate_with_default_profile(self):
        # INT-20260816-008 / UXI-002：一条命令可达审计器；默认 --current-state
        code, out = self._run("audit", cwd=ROOT / "scripts")
        self.assertIn(code, (0, 1), out)
        self.assertIn("Static gate:", out)
        self.assertIn("profile: current-state", out)
        self.assertNotIn("Traceback", out)

    def test_audit_passes_profile_flags_through(self):
        import json

        code, out = self._run("audit", "--json")
        self.assertIn(code, (0, 1), out)
        payload = json.loads(out[out.index("{"):])
        self.assertIn("current_integrity", payload)

    def test_status_rule_count_matches_validate_and_conflicts(self):
        """RULE-021 ③：三条命令对"规则数"只有一个答案。"""
        import re as _re

        _, status_out = self._run("status")
        _, validate_out = self._run("validate")
        _, conflicts_out = self._run("conflicts")
        status_n = int(_re.search(r"现行规则: (\d+) 个", status_out).group(1))
        validate_n = int(_re.search(r"找到 (\d+) 条规则定义", validate_out).group(1))
        conflicts_n = int(_re.search(r"读取到 (\d+) 条规则", conflicts_out).group(1))
        self.assertEqual((status_n, validate_n, conflicts_n), (status_n, status_n, status_n))

    def test_conflicts_resolves_project_root_from_subdirectory(self):
        # 0 = 无冲突，2 = 检出潜在冲突；1 才是胶水层失败（找不到 logic_readme.md）
        code, out = self._run("conflicts", cwd=ROOT / "scripts")
        self.assertIn(code, (0, 2), out)
        self.assertIn("读取到", out)
        self.assertNotIn("未找到 logic_readme.md", out)

    def test_validate_runs_end_to_end(self):
        code, out = self._run("validate")
        self.assertIn(code, (0, 1), out)
        self.assertIn("验证报告", out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
