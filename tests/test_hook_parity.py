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
            for override in ({}, {'CONTEXT_WARN_TOKENS': 'invalid', 'CONTEXT_REFERENCE_WINDOW': '0'}):
                env = dict(os.environ, **override)
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
            # Both intentionally require a transcript, even with a payload count.
            no_transcript = json.dumps({'total_tokens': 180000})
            for command in (['bash', str(ROOT / 'hooks/context-zone.sh')],
                            [ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                             installer.winpath(ROOT / 'hooks/context-zone.ps1')]):
                self.assertEqual(subprocess.check_output(command, input=no_transcript, text=True).strip(), '')


if __name__ == '__main__':
    unittest.main()
