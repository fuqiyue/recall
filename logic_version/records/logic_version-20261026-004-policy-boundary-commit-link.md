# VER-20261026-004: 现行规则与历史留档边界更新提交关联

## 记录控制
- version_id: VER-20261026-004
- version_slug: logic_version-20261026-004-policy-boundary-commit-link
- status: correction
- immutable: true
- corrects: VER-20261026-001
- date: 2026-10-26
- change_id: none
- before_commit: 0e38394bf6ce3abafbff2d54175b222630e5b90d
- after_commit: 752b2ce53871de40b648a6f9172975a1e58fbfd8
- changed_by: Codex

## 为什么做这个决策？
用户要求更新 GitHub。原记录定稿时尚未提交，现已核验实际实施提交；按 Git管道 RULE-013 追加提交证据，原不可变文件不改写。
- raw_request: none
- decomposition: none
- fit_analysis: none

## 影响范围
仅补充 VER-20261026-001 的提交关联；实施文件包含 SKILL.md、AGENTS.md、CLAUDE.md、根与领域readme、references及历史索引。本记录没有新增规则或业务行为。

## 验证方式
git show 752b2ce53871de40b648a6f9172975a1e58fbfd8 --stat 已核对原留档和对应实现文件同批提交；发布前全量353项测试通过（1项本机符号链接环境跳过）。原记录SHA256保持 034af21c27b32e1cf639621dd93a75c120509634163165c7ef295ce15df5d235。

## 回滚方式
提交关联如需纠正，再追加勘误记录；不修改原记录。实际实现可按Git历史回滚。

## 关联
- original_record: [VER-20261026-001](logic_version-20261026-001-current-policy-archive-boundary.md)
- current_logic: [Git管道 RULE-013](../../logic_domains/git-pipeline/logic_readme.md)
