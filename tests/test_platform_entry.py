"""Run the actual platform wrapper with Chinese paths and redirected output."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PlatformEntryTests(unittest.TestCase):
    def test_native_wrapper_in_chinese_directory_with_utf8_redirection(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / '中文 项目'
            project.mkdir()
            (project / 'logic_readme.md').write_text('# 中文项目\n', encoding='utf-8')
            output = project / '中文 输出.txt'
            environment = dict(os.environ)
            if os.name == 'nt':
                command = f'call "{ROOT / "recall.bat"}" status > "{output}"'
                command_line = f'"{os.environ.get("COMSPEC", "cmd.exe")}" /d /s /c "{command}"'
                result = subprocess.run(command_line, cwd=project,
                                        input=b'', capture_output=True, env=environment, timeout=20)
            else:
                with output.open('wb') as destination:
                    result = subprocess.run(['bash', str(ROOT / 'recall.sh'), 'status'], cwd=project,
                                            input=b'', stdout=destination, stderr=subprocess.PIPE,
                                            env=environment, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
            content = output.read_text(encoding='utf-8')
            self.assertIn('Recall 系统状态', content)
            self.assertNotIn('Traceback', content)
            self.assertNotIn('UnicodeEncodeError', content)


if __name__ == '__main__':
    unittest.main()
