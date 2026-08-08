# 集中备份 manifest 模板

只在确需保存 Git 之外的原文件快照时使用。目录固定为项目根 `logic_version/backups/YYYYMMDD-HHMMSS-<CHG-ID>/`，并在其中创建 `manifest.md`；不能在模块代码旁散落 backup/old/v1-copy。

~~~markdown
# Backup Manifest

- backup_id: BAK-YYYYMMDD-HHMMSS
- change_id: <CHG-ID>
- version_id: <VER-ID 或 none>
- created: YYYY-MM-DDTHH:MM:SSZ
- created_by: <角色/工具>
- reason: <为何 Git 或外部备份不足>
- retention_until: YYYY-MM-DD | event-driven
- contains_sensitive_data: yes | no
- storage: repository | <受控外部存储标识>

## 文件清单

| 原仓库相对路径 | 快照相对路径 | SHA-256 | 大小 | 恢复用途 |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 恢复步骤

1. <前置检查>
2. <恢复动作>
3. <恢复后验证>

## 删除条件

<何时以及由谁清理。>
~~~

禁止把密钥、令牌、个人信息、生产数据库或日志直接提交仓库。此类备份放受控外部存储，manifest 只记录不含秘密的标识、责任人和恢复步骤。
