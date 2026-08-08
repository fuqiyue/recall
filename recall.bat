@echo off
REM Recall CLI launcher (Windows).
REM
REM Keep this file ASCII-only with CRLF line endings (enforced by
REM .gitattributes). cmd.exe locates the next command by byte offset while
REM decoding lines through the console codepage; multi-byte characters plus
REM LF-only endings make it resume mid-line and execute comment fragments.
setlocal

set "RECALL_PY="

where python >nul 2>&1
if not errorlevel 1 goto :use_python

where py >nul 2>&1
if not errorlevel 1 goto :use_py

where python3 >nul 2>&1
if not errorlevel 1 goto :use_python3

echo [ERROR] Python not found on PATH. 1>&2
echo         Install Python 3.8+: https://www.python.org/downloads/ 1>&2
exit /b 127

:use_python
set "RECALL_PY=python"
goto :run

:use_py
set "RECALL_PY=py -3"
goto :run

:use_python3
set "RECALL_PY=python3"
goto :run

:run
%RECALL_PY% "%~dp0scripts\recall.py" %*
exit /b %ERRORLEVEL%
