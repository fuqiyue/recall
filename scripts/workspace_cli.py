"""CLI for project paths, file maps and artifact reconciliation."""

import argparse
import json
from pathlib import Path

from recall_common import find_project_root
from workspace_check import check_workspace
from workspace_inventory import inventory, markdown, write_maps
from workspace_paths import contract, project_path


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
        result = check_workspace(root, closing=options.closing, max_entries=options.max_entries)
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
    print(json.dumps(result, ensure_ascii=False, indent=2) if options.json or command != "path" else result["resolved"])
    return 0 if result.get("ok", True) else 1
