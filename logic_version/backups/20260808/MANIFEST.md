# Backup Manifest: 20260808

## 备份原因

根目录存在平行真源，违反 SKILL.md:180"发布态只有项目根这一对现行文档"。

归档以下文件到 `logic_version/backups/20260808/` 以消除冗余：

## 归档文件

| 文件 | 原因 | 内容去向 |
|---|---|---|
| OPTIMIZATION_ANALYSIS.md | 未登记的活跃议案 | 内容已记录在 CHG-20260808-001 和 VER-20260808-001 |
| PROJECT_STATUS.md | 第三份状态副本，且已过期 | 内容应在 logic_readme.md 前言中维护 |
| VER_TEMPLATE.md | 与 references/logic-version-template.md 冲突的孤儿模板 | 唯一模板是 references/logic-version-template.md |

## 归档日期

2026-08-08

## 关联记录

- CHG-20260808-001: Recall 系统结构重组
- VER-20260808-001: 逻辑完整性修复与反膨胀强制点

## 恢复方式

文件完整保留在本目录，可直接复制回根目录。
