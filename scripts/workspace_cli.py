"""CLI for project paths, file maps and artifact reconciliation."""

import argparse
import json
from pathlib import Path

from recall_common import find_project_root
from workspace_check import check_workspace
from workspace_inventory import inventory, markdown, write_maps
from workspace_paths import contract, project_path


def print_workspace(result):
    views = []
    if result["round_result"]:
        views.append(("本轮 " + result["round_result"]["round"], result["round_result"]))
    if result["task_result"]:
        views.append(("本任务 " + result["task_result"]["task"], result["task_result"]))
    views.append(("全项目", result))
    for title, view in views:
        findings = view["findings"]
        counts = {level: sum(f["severity"] == level for f in findings) for level in ("error", "warning", "info")}
        print(f"{title}：{'通过' if view['ok'] else '未通过'}；错误 {counts['error']}，提示 {counts['warning']}，进行中 {counts['info']}")
    shown = result["round_result"] or result["task_result"] or result
    for finding in shown["findings"][:20]:
        print(f"  [{finding['severity']}] {finding['code']} {finding['path']}：{finding['message']}")
    if len(shown["findings"]) > 20 or result["other_findings"]:
        print("其余问题和全局归属见 --json；本次退出码只对应所选任务/轮次。" if result["task_result"] else "其余问题见 --json。")


def main(args=None, command="inventory"):
    parser = argparse.ArgumentParser(description="项目工作路径与任务产物")
    parser.add_argument("--project", help="明确项目根（须含logic_readme.md）")
    parser.add_argument("--json", action="store_true")
    if command == "inventory":
        parser.add_argument("paths", nargs="*")
        parser.add_argument("--data-root", action="append", default=[])
        parser.add_argument("--max-depth", type=int, default=3)
        parser.add_argument("--max-entries", type=int, default=1000)
        parser.add_argument("--write", action="store_true", help="写可重建logic_domains/**/file_map.md")
    elif command == "workspace":
        parser.add_argument("--closing", help="按CHG-ID核对关案条件")
        parser.add_argument("--task", help="单独报告任务结果；全局问题仍保留")
        parser.add_argument("--round", dest="round_id", help="核对本轮台账处置（须搭配--task）")
        parser.add_argument("--max-entries", type=int, default=2000)
    else:
        parser.add_argument("path", help="输出前核对项目相对路径；不创建文件")
    options = parser.parse_args(args)
    root = Path(options.project).resolve() if options.project else find_project_root()
    if not (root / "logic_readme.md").is_file():
        raise ValueError(f"未找到明确项目根：{root}")
    if getattr(options, "max_entries", 1) < 1 or getattr(options, "max_depth", 0) < 0:
        raise ValueError("扫描预算必须为正数，深度不能为负")
    if command == "path":
        cfg = contract(root)
        result = dict(cfg, resolved=project_path(root, options.path).as_posix())
    elif command == "workspace":
        result = check_workspace(root, closing=options.closing, task=options.task,
                                 round_id=options.round_id, max_entries=options.max_entries)
    else:
        result = inventory(root, options.paths, data_roots=options.data_root,
                           max_depth=options.max_depth, max_entries=options.max_entries)
        if options.write:
            result["written"] = write_maps(root, result)
        if not options.json:
            print(markdown(result))
            if result.get("written"):
                print("已更新：" + ", ".join(result["written"]))
            return 0
    if command == "workspace" and not options.json:
        print_workspace(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2) if options.json else result["resolved"])
    return 0 if result.get("selection_ok", result.get("ok", True)) else 1
