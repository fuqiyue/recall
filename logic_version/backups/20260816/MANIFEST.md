# 归档清单 2026-08-16

来源：CHG-20260816-004（审查整改，VER-20260816-005）。这些文件是根目录与
docs/ 下的脱管平行真源候选——内容停留在 2026-08-08~08-11 的旧语义，且既不在
owned_paths 也不在 unmapped_paths，审计的平行真源检测（只认 logic_readme/
logic_change 命名）对它们全盲。同批为审计新增了根目录 Markdown 覆盖对账，
防止同类文件再次脱管。

| 文件 | 归档原因 | 现行真源 |
|---|---|---|
| GIT_INTEGRATION_SUMMARY.md | 重述三层架构/工作流/commit 规范，停留在 5 个 VER 之前 | logic_readme.md（RULE-010..013）、SKILL.md |
| CLI_VALIDATION_SUMMARY.md | CLI 验证总结快照，工具行为已多次演进 | logic_readme.md 测试与验证表 |
| CHANGELOG.md | 停在 2026-08-09 [Unreleased] 的第二份历史真源 | logic_version/index.md + git log |
| GITHUB_PUBLISH_GUIDE.md | 一次性发布指南，任务已完成 | 无（不再需要） |
| .github-config.md | 一次性仓库配置指南，任务已完成 | 无（不再需要） |
| FAQ.md (原 docs/) | "接入现有项目"答案与 RULE-016 模块化渐进接入直接冲突 | SKILL.md、references/project-onboarding.md |
| RECALL_FLOW_GUIDE.md (原 docs/) | 流程教学材料，与 SKILL/生命周期文档重复且滞后 | SKILL.md、references/change-lifecycle.md |
| RECALL_FLOW_DIAGRAMS.md (原 docs/) | 同上 | 同上 |
| git-workflow-integration.md (原 references/) | 515 行孤儿文档：仅 recall help 引用，sync 语义停留在 4 个 VER 之前 | logic_readme.md（RULE-011/013）、SKILL.md |
| logic-version-git-template.md (原 references/) | 双模板权威分裂；实用正文已并入唯一模板 | references/logic-version-template.md |

恢复方式：`git mv` 回原路径即可（Git 历史完整保留）。
