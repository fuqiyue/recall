# VER-20261027-002: 追加公开文档整理的真实提交关联

## 记录控制

- version_id: VER-20261027-002
- version_slug: logic_version-20261027-002-public-docs-commit-link
- status: correction
- immutable: true
- date: 2026-10-27
- governance_mode: personal
- change_id: none
- corrects: VER-20261027-001
- before_commit: 2fc51924c3d3d87b818abeedebe400eaa0d58471
- after_commit: 2fc51924c3d3d87b818abeedebe400eaa0d58471

## 为什么做这个决策？

原 VER-20261027-001 在本地文档交付时已定稿，after_commit 为 none。用户随后明确要求“帮我把这次整理好的文档提交并推送到 GitHub”。按 Git 管道 RULE-013 追加真实提交证据，原记录保持不可变。

- raw_request: none
- decomposition: none
- fit_analysis: none

## 决策过程

采用追加 correction：指向已包含三份公开文档、归档和对应索引的实际提交，保留原交付时点的事实。未采用覆盖原记录的方式，以保持归档完整。

## 修订记录

不适用；本次为无 CHG 的简单提交补链。

## 影响范围

- 原变更提交 2fc51924c3d3d87b818abeedebe400eaa0d58471 包含 README.md、CONTRIBUTING.md、SECURITY.md、logic_readme.md、logic_version/index.md 和原 VER 记录。
- 本次新增本记录并在历史索引追加一行，不改变现行规则或原记录。
- 已有其他本地修改与备份文件保留，不纳入本次推送。

## 验证方式

- 已用 git show --stat 和暂存清单核对原提交的六个文件。
- 从暂存树导出的独立快照通过 current-state 文档审计，坏链为 0；临时快照已自动删除。
- git diff --cached --check 通过；原记录 after_commit 保持 none，补链使用真实实施 SHA。
- 此记录登记后运行 recall validate 与 recall query commit，核对追加追溯。

## 回滚方式

如需撤销本次补链，另记纠正并撤销其索引增量；原文档提交按 Git 正常撤销流程处理，保留已归档记录。

## 清理与交付

本次仅新增正式记录和索引，未遗留临时输出。远端推送完成状态以本轮 Git 核对结果为准。

## 经验与教训

先交付后提交的记录用追加证据连接真实提交，保留各时点事实。

## 关联

- current_logic: ../../logic_readme.md；../../logic_domains/git-pipeline/logic_readme.md（RULE-013）
- proposal_id: none
- code/tests: README.md、CONTRIBUTING.md、SECURITY.md、logic_readme.md、logic_version/index.md
