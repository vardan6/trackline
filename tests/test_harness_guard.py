"""harness-guard denies nested agent harness launches and nothing else."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from test_installer import ROOT, installer


def bash(command):
    return {'tool_name': 'Bash', 'tool_input': {'command': command}}


DENY = [
    # The 2026-10-14 incident, as Codex issued it.
    bash("rtk proxy bash -c 'timeout 30s claude -p --model opus --effort max \"Reply with OK only.\" > out.json'"),
    {'tool_name': 'exec', 'tool_input': 'text(await tools.exec_command({cmd:"rtk proxy bash -c \'timeout 30s '
                                        'claude -p --tools \\"\\" x\'",yield_time_ms:1000}));'},
    bash('claude --print --no-session-persistence --model opus -- < prompt.txt'),
    bash('codex exec "review this"'),
    bash('npx -y @anthropic-ai/claude-code -p hi'),
    bash('npm exec @openai/codex@latest -- exec hi'),
    bash('env -i FOO=1 /usr/local/bin/claude -p x'),
    bash('cd /tmp && gemini -p x'),
    bash('echo hi | claude'),
    bash('x=$(codex exec y)'),
    bash('powershell.exe -NoProfile -Command "claude.exe -p hi"'),
    bash('sudo cursor-agent -p hi'),
    {'tool_name': 'exec_command', 'tool_input': {'cmd': 'claude -p hi'}},
    {'tool_name': 'shell', 'tool_input': {'command': ['bash', '-lc', 'codex exec hi']}},
    # 2026-10-16 review #1: a double-quoted cmd must not hide other literal forms.
    {'tool_name': 'exec', 'tool_input': 'await tools.exec_command({cmd: "echo ok"});\n'
                                        "await tools.exec_command({cmd: 'claude -p hi'});"},
    {'tool_name': 'exec', 'tool_input': 'await tools.exec_command({cmd: "echo ok"});\n'
                                        'await tools.exec_command({cmd: `codex exec hi`});'},
    {'tool_name': 'exec', 'tool_input': 'await tools.exec_command({cmd: "echo ok"});\n'
                                        'await tools.exec_command({"cmd": "claude -p hi"});'},
    # Review #2: Windows absolute paths, including the PowerShell call operator.
    bash(r'C:\Tools\claude.exe -p hi'),
    {'tool_name': 'PowerShell', 'tool_input': {'command': r"& 'C:\Tools\claude.exe' -p hi"}},
    # Review #3: wrapper options with a separate value.
    bash('timeout --signal TERM 30s claude -p hi'),
    bash('timeout -k 5 30s codex exec hi'),
    bash('sudo -u bob claude -p hi'),
    bash('env -u FOO claude -p hi'),
    bash('env -S "claude -p hi"'),
    bash('nice -n 10 gemini -p hi'),
    bash('xargs -n 1 codex exec'),
    bash('wsl -d Ubuntu claude -p hi'),
    bash('powershell.exe -ExecutionPolicy Bypass -Command "claude -p hi"'),
]
# Review #4: without jq, the raw-payload fallback must still deny a plain launch.
NO_JQ_DENY = [bash('claude -p hi'), bash('timeout 30s codex exec hi'), bash(r'C:\Tools\claude.exe -p hi')]
NO_JQ_ALLOW = [bash('command -v claude'), bash('ls ~/.claude'),
               {'tool_name': 'Edit', 'tool_input': {'file_path': 'a.md', 'new_string': 'run `claude -p`'}}]
ALLOW = [
    bash('command -v claude'),
    bash('which codex; rg -n claude skills/'),
    bash('git commit -m "Block nested claude launches"'),
    bash('rtk proxy rg -n "codex exec" .'),
    bash('ollama run qwen2.5-coder'),
    bash('ls ~/.claude ~/.codex'),
    bash('python3 -m unittest discover -s tests'),
    bash('sudo -u bob rg -n claude .'),
    bash('timeout --signal TERM 30s rg codex'),
    {'tool_name': 'Edit', 'tool_input': {'file_path': 'a.md', 'new_string': 'run `claude -p`'}},
    {'tool_name': 'exec', 'tool_input': 'text(await tools.apply_patch("*** Begin Patch\\n+- `claude -p` x"))'},
    {'tool_name': 'Agent', 'tool_input': {'prompt': 'do not run claude -p'}},
]


def decision(command, payload, env=None):
    output = subprocess.check_output(command, input=json.dumps(payload), text=True, env=env).strip()
    return json.loads(output)['hookSpecificOutput'] if output else None


class HarnessGuardTests(unittest.TestCase):
    def check(self, command):
        for payload in DENY:
            with self.subTest(deny=payload):
                result = decision(command, payload)
                self.assertEqual(result and result['permissionDecision'], 'deny')
                self.assertIn('other provider', result['permissionDecisionReason'])
        for payload in ALLOW:
            with self.subTest(allow=payload):
                self.assertIsNone(decision(command, payload))

    def test_bash(self):
        self.check(['bash', str(ROOT / 'hooks/harness-guard.sh')])

    def test_bash_without_jq(self):
        with tempfile.TemporaryDirectory() as bin_dir:
            for tool in 'cat', 'sed':
                os.symlink(shutil.which(tool), os.path.join(bin_dir, tool))
            command = [shutil.which('bash'), str(ROOT / 'hooks/harness-guard.sh')]
            env = {'PATH': bin_dir}
            for payload in NO_JQ_DENY:
                with self.subTest(deny=payload):
                    result = decision(command, payload, env)
                    self.assertEqual(result and result['permissionDecision'], 'deny')
            for payload in NO_JQ_ALLOW:
                with self.subTest(allow=payload):
                    self.assertIsNone(decision(command, payload, env))

    @unittest.skipUnless(os.environ.get('TRACKLINE_WINDOWS_TESTS') == '1', 'requires Windows PowerShell')
    def test_powershell_parity(self):
        self.check([installer.discover_powershell(), '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                    '-File', installer.winpath(ROOT / 'hooks/harness-guard.ps1')])


if __name__ == '__main__':
    unittest.main()
