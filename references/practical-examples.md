# 三个最小操作示例

以下是教学设定，不是实际项目的授权或现行规则。字段名来自[个人最小块](logic-change-template.md#personal-最小块)，操作顺序来自[生命周期](change-lifecycle.md)；完整可运行项目在 [mini-project](examples/mini-project/logic_readme.md)。先复制它到自己的临时目录，命令在副本根运行，`recall` 使用维护源CLI。

## 1. 首次接入：建立可以读、路由和验证的最小项目

示例项目保留旧paired领域以验证兼容，另含根readme/change、问候函数和一个单元测试。新项目按[接入流程](project-onboarding.md)使用readme-only领域及独立任务文件；已有Git管道才按实际需要运行init。

```bash
recall route src/app.py --json
recall audit --json
recall validate
recall index --json
recall next --json
python -m unittest discover -s tests
```

预期：路由命中core；静态门通过；validate无错误（未接入Git时仍提示真实仓库限制）；根公报一致；next无任务；1个单元测试通过。文件结构可作为起点，示例的来源/日期/角色必须替换为真实事实。

## 2. 中等修改：先记录需求，再验证和收尾

教学需求：整理问候实现与相关测试，保持 `greet(name)` 返回值不变。将个人最小块写入 `logic_changes/问候整理/logic_change.md`，填需求三字段、已有授权、影响和回滚，设置medium/implementing、scope为logic_domains/core；产物台账内联，临时代码放`.work/临时-问候整理`，根公报由index生成。

```bash
recall index --write
recall next --json
recall route src/app.py
python -m unittest discover -s tests
recall audit --json
```

预期：next显示进行中及下一步；改前/改后问候断言一致。修改与验证节点记入同一修订表；自审通过后按需更新readme、清理临时产物，workspace按CHG核对实物；将需求、修订表与清理事实归入精简VER/index。关闭时移除任务文件和空目录，再运行index/next。

## 3. 中断接手：继续promoting清单

教学现场：实现与测试已通过，readme已更新，但台账尚未处置、VER尚未定稿。CHG保持promoting，`next_action` 写“核本次临时台账，执行清理，定稿VER/index，再关案”。

```bash
recall next --json
recall route src/app.py
recall audit --json
```

预期：next显示收尾；读取关联CHG、真实文件和证据后完成剩余清单。已交付实现不用重复执行；已定稿历史不能覆盖，纠正另建记录。最终核index一致、next归零、本次working已清理。工具负责发现和校验，清理、文档晋升和关案由代理依已获授权逐项执行。

示例回归：`python -m unittest discover -s tests -p test_recall_cli.py`，在临时副本中真跑CLI、个人模板状态转换及收尾检查，不修改这里的fixture。
