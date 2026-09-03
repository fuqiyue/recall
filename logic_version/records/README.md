# 历史决策记录目录

本目录保存已关闭变更的不可变决策记录（逻辑回档，RULE-003）。记什么、不记什么见 [../index.md](../index.md)"关于逻辑回档"节；字段与写法见 `references/logic-version-template.md`。

## 记录命名规则

```
logic_version-YYYYMMDD-NNN-<scope>.md
```

创建方与全部发现方共用同一正则（RULE-012）；用 `recall new "<描述>" <短标签>` 生成骨架即符合命名。

## 索引

全部记录的索引见 [../index.md](../index.md)，本目录不维护第二份清单。已发布的记录不可修改（INV-003），只能追加新记录取代其中的事实陈述；唯一合法的既有文件变更是 hook 对 `after_commit` 占位符的一次性回填（RULE-013）。
