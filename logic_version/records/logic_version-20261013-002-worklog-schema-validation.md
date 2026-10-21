# VER-20261013-002: 活跃工作台账与历史格式追加校验
## 记录控制
- version_id: VER-20261013-002
- version_slug: logic_version-20261013-002-worklog-schema-validation
- status: effective
- immutable: true
- date: 2026-10-13
- change_id: CHG-20261013-002
- proposal_revision: 1
- before_commit: none
- after_commit: none
## 为什么做这个决策？
- raw_request: 用户本聊天认可修复历史格式及3个活跃台账被误报缺失的问题并要求解决。
- decomposition: 区分经过来源核验的活跃working行与归档索引；验证SHA绑定的格式追加记录；补正例和错配/缺失/漂移反例。
- fit_analysis: 沿所属项目当前规则和用户意图，历史保全，文档校验不代教材业务验收。
## 影响范围
validate.py、task_context.py、反例测试、工具领域规则及模板；通用技能不保存教材业务授权。
## 验证方式
现行源码完整回归312项：312通过、0跳过，0失败/0错误；真实working回链、格式补充SHA及空标题锚点反例通过。33份旧Recall VER字节不变。 文档自审核唯一正文、授权/原需求保全、来源绑定及旧链接；必要阅读量/旧Git追溯提示保留，不编造原实现提交。检查边界为本地文档和工具，不代课程业务验收。
## 回滚方式
按来源SHA和本次diff逐段撤增量；有后续写入时不整份覆盖。历史记录保留，教材业务库/原件/正确成果及其他任务不回退。

## 临时产物处置
本聊天候选/基线副本、测试夹具、临时脚本及本案working目录已精确清理；保留受控原字节、SHA对账、写入清单和测试/检查输出作为交付依据。其他业务working、原件和真实课件保持。
