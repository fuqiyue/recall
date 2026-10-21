# VER-20261012-001: Recall技能入口与文档一致性优化

## 记录控制
- version_id: VER-20261012-001
- version_slug: logic_version-20261012-001-skill-document-clarity
- status: effective
- immutable: true
- date: 2026-10-12
- change_id: CHG-20261012-001
- proposal_revision: 1
- changed_by: Codex
- recall_route: medium
- governance_mode: personal
- governance_ref: git:https://github.com/fuqiyue/recall@main
- governance_evidence: git:f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3；原文档SHA及本次检查记录
- governance_verification: recorded
- governance_verified_at: 2026-10-12
- before_commit: f2b1e09d7082eaebd11a57415ee7aa7ceeec0ca3
- after_commit: none
- decision_confirmed_by: user
- decision_confirmed_at: 2026-10-12
- decision_ref: user:2026-10-12 明确优化Recall技能自身D:/vscode3/recall
- proposal_commit_or_blob: ../backups/skill-document-clarity-20261012/proposal.txt

## 为什么做这个决策？
技能规则已经完备，但入口仍有跨项目RULE归属歧义；CHG模板复制大段制度，根文档存在重复标题、真源混写及“先实施后留记录”的流程描述。用户明确优化技能自身文档，需要使入口、宪法、参考和CLI实际职责一致。
- raw_request: 请优化目前的recall文档，根据recall skill；目标为Recall技能自身的文档（D:/vscode3/recall）。
- decomposition: 明确项目定位/技能维护边界；统一读取、授权、通道与关案入口；压缩重复模板制度；修正文档真源、实施顺序、标题与日期字段；保留字段schema、接口及历史。
- fit_analysis: 复用INT-20260816-003与FLOW-002，沿RULE-019/022渐进披露；不新增领域、字段、CLI行为或业务授权。

## 决策过程
采用现有文件内部精简和一致性修正：技能入口给定位/读取、需求授权、三通道与交付顺序；细节继续由references按需提供。模板的制度段改为规则指针和操作步骤，保留所有正式字段/schema及personal最小块。保持现状仍会复制规章；新建指南或领域会增加第二入口，故不采用。

## 影响范围
SKILL.md、logic_readme.md、logic_change.md、README.md、references/logic-change-template.md、references/document-model.md，以及历史索引/本记录。明确维护源与消费项目，修正FLOW-002先记录再实施；last_reviewed属于规则行、last_verified属于文档控制。模板裁掉重复规章约29%，正式字段不删。CLI代码、安装入口、模型、权限与项目业务规则保持。

## 验证方式
技能quick_validate检查frontmatter与脚手架；实际项目recall audit/validate/index/next/route核结构、引用、最近索引与无残留议案。AI语义审查核用户来源不扩权、目标明确、需求先记录、按影响选深度、规则唯一、原字段与历史保全及交付闭环。命令输出/结果和处置见[检查记录](../backups/skill-document-clarity-20261012/checks.json)。文档改动不以测试文件存在或静态门冒充代码/部署验证。

## 回滚方式
按[原字节清单](../backups/skill-document-clarity-20261012/manifest.json)和当前diff撤本次增量；存在后续修改时只撤对应段落。旧VER不改写，保留本记录与纠正来源。Git工作树状态在受限执行环境不可读取，未把工具警告伪装成干净工作树；未提交/推送。

## 临时产物
只删除本次编辑、验证及回撤暂存文件，保留原文快照、议案、检查和本记录；实际处置写入checks.json。教材误选的整理已回撤，其后续业务字段保全并记录单独撤销收据，不带入本技能规则。

## 关联
- current_logic: logic_readme.md#当前制度
- proposal_id: CHG-20261012-001
- former_proposal_path: logic_change.md
- code/tests: 文档解析、引用与技能元数据核验；无CLI实现变化
