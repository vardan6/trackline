"""Compare messages from actual Bash and Windows PowerShell launchers."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_installer import ROOT, installer


@unittest.skipUnless(os.environ.get('TRACKLINE_WINDOWS_TESTS') == '1', 'requires Windows PowerShell')
class HookParityTests(unittest.TestCase):
    def test_messages_and_input_precedence(self):
        ps = installer.discover_powershell()
        with tempfile.TemporaryDirectory(prefix='.hook-test-', dir=ROOT) as directory:
            transcript = Path(directory) / 'transcript café.jsonl'
            event = lambda tokens, window: {'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {
                'last_token_usage': {'input_tokens': tokens}, 'model_context_window': window}}}
            transcript.write_text('\n'.join(json.dumps(e) for e in (event(90000, 200000), event(130000, 258400))) + '\n')
            payloads = [
                {}, {'total_tokens': 79999}, {'total_tokens': 80000},
                {'context_tokens': 100000}, {'transcript_tokens': 120000},
                {'transcript_token_count': 180000}, {'token_count': 110000},
                {'token_usage': {'total_tokens': 99999}},
                {'usage': {'total_tokens': 115000, 'input_tokens': 190000}},
                {'usage': {'input_tokens': 125000}},
                {'workspace_context': {'context_tokens': 150000, 'context_window': 1000000}},
                {'hook_event': {'total_tokens': 180000, 'model_context_window': 1000000}},
                {'total_tokens': 0, 'usage': {'total_tokens': 90000}},
                {'total_tokens': 'invalid'}, {'total_tokens': 110000, 'model_context_window': 0},
            ]
            # WSL forwards variables to Windows processes only when WSLENV
            # lists them; without this PowerShell silently uses its defaults.
            names = ('CONTEXT_WARN_TOKENS', 'CONTEXT_ASK_TOKENS', 'CONTEXT_DUMB_TOKENS',
                     'CONTEXT_FORCE_TOKENS', 'CONTEXT_REFERENCE_WINDOW')
            wslenv = ':'.join(filter(None, [os.environ.get('WSLENV'), *names]))
            overrides = ({}, {'CONTEXT_WARN_TOKENS': 'invalid', 'CONTEXT_REFERENCE_WINDOW': '0'},
                         {'CONTEXT_WARN_TOKENS': '50000', 'CONTEXT_ASK_TOKENS': '60000',
                          'CONTEXT_DUMB_TOKENS': '70000', 'CONTEXT_FORCE_TOKENS': '75000',
                          'CONTEXT_REFERENCE_WINDOW': '150000'})
            payloads += [{'total_tokens': 55000}, {'total_tokens': 65000}, {'total_tokens': 72000}]
            for override in overrides:
                env = dict(os.environ, WSLENV=wslenv, **override)
                for payload in payloads:
                    with self.subTest(payload=payload, override=override):
                        bash_payload = dict(payload, transcript_path=str(transcript))
                        ps_payload = dict(payload, transcript_path=installer.winpath(transcript))
                        bash = subprocess.check_output(['bash', str(ROOT / 'hooks/context-zone.sh')],
                                                       input=json.dumps(bash_payload), text=True, env=env)
                        windows = subprocess.check_output([ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy',
                                                           'Bypass', '-File', installer.winpath(ROOT / 'hooks/context-zone.ps1')],
                                                          input=json.dumps(ps_payload, ensure_ascii=False), text=True, env=env)
                        self.assertEqual(json.loads(bash) if bash.strip() else None,
                                         json.loads(windows) if windows.strip() else None)
            # The valid override must reach PowerShell, not merely match defaults.
            env = dict(os.environ, WSLENV=wslenv, **overrides[2])
            payload = json.dumps({'total_tokens': 55000, 'transcript_path': installer.winpath(transcript)})
            windows = subprocess.check_output([ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                                               installer.winpath(ROOT / 'hooks/context-zone.ps1')],
                                              input=payload, text=True, env=env)
            self.assertIn('consider /session-close', json.loads(windows)['systemMessage'])
            # Both intentionally require a transcript, even with a payload count.
            no_transcript = json.dumps({'total_tokens': 180000})
            for command in (['bash', str(ROOT / 'hooks/context-zone.sh')],
                            [ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                             installer.winpath(ROOT / 'hooks/context-zone.ps1')]):
                self.assertEqual(subprocess.check_output(command, input=no_transcript, text=True).strip(), '')


if __name__ == '__main__':
    unittest.main()
