"""Recall 审计器分层包（VER-20260903-002）。

层次自下而上：constants → textutil → fsclassify → changes → semantic → integrity
→ formal → archive → report → cli；只允许向下依赖。入口见 scripts/audit_logic_map.py。

包内的 Git 调用与输出编码防护经 scripts/recall_common.py（RULE-021），因此把 scripts/
加入 sys.path，整目录部署即满足。
"""
import sys as _sys
from pathlib import Path as _Path

_SCRIPTS_DIR = str(_Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in _sys.path:
    _sys.path.insert(0, _SCRIPTS_DIR)
