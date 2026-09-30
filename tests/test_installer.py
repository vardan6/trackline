"""Preservation, migration, no-op, and recovery regressions.

Run: python3 -m unittest discover -s tests -v
Add TRACKLINE_WINDOWS_TESTS=1 under WSL to exercise actual native links.
"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'hooks/install-workflow.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def snapshot(root):
    result = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name != '.git']
        for name in dirs + files:
            path = Path(base) / name
            key = str(path.relative_to(root))
            if path.is_symlink():
                result[key] = ('link', os.readlink(path))
            elif path.is_file():
                result[key] = ('file', path.read_bytes(), path.stat().st_mtime_ns)
            else:
                result[key] = ('directory',)
    return result


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='trackline-test-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'project [Unicode café]'
        self.project.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)

    def install(self, *flags, native_linux=True):
        argv = ['install-workflow.py', '--installer-dir', str(ROOT), *flags, str(self.project)]
        with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()) as output:
            if native_linux:
                # Native Linux must never query Windows tools or path translation.
                with mock.patch.object(installer, 'wsl_runtime', return_value=False), \
                     mock.patch.object(installer, 'winpath', side_effect=AssertionError('Windows dependency on Linux')):
                    installer.main()
            else:
                installer.main()
        return output.getvalue()

    def seed_settings(self):
        path = self.project / '.claude/settings.json'
        path.parent.mkdir()
        value = {'label': 'café — 日本語', 'large': 123456789012345678901234567890,
                 'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': 'echo unrelated'}]}]}}
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        return path, value

    def test_linux_install_and_noop_preserve_unicode_and_hooks(self):
        path, value = self.seed_settings()
        self.install()
        data = json.loads(path.read_text())
        self.assertEqual(data['label'], value['label'])
        self.assertEqual(data['large'], value['large'])
        self.assertEqual(data['hooks']['Stop'][0], value['hooks']['Stop'][0])
        self.assertTrue((self.project / '.codex/skills/roadmap-split/DEEP-SPLIT.md').is_file())
        before = snapshot(self.project)
        self.install()
        self.assertEqual(snapshot(self.project), before)

    def test_dry_run_has_zero_writes(self):
        self.seed_settings()
        before = snapshot(self.project)
        self.install('--dry-run')
        self.assertEqual(snapshot(self.project), before)

    def test_bom_settings_permissions_and_optional_skills(self):
        path, value = self.seed_settings()
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8-sig')
        path.chmod(0o600)
        self.install('--with-external')
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(path.read_text())['label'], value['label'])
        self.assertTrue((self.project / '.claude/skills/grill-me/SKILL.md').is_file())

    def test_invalid_json_fails_before_migration(self):
        path, _ = self.seed_settings()
        path.write_text('{broken')
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            self.install('--replace-links')
        self.assertEqual(snapshot(self.project), before)

    def test_merge_preserves_decimal_precision(self):
        path, _ = self.seed_settings()
        path.write_text('{"precision": 0.12345678901234567890123456789}')
        self.install()
        self.assertIn('0.12345678901234567890123456789', path.read_text())

    def test_unrelated_link_and_parent_link_are_conflicts(self):
        elsewhere = self.project.parent / 'unrelated'
        elsewhere.write_text('user data')
        (self.project / 'AGENTS.md').symlink_to(elsewhere)
        before = snapshot(self.project)
        with self.assertRaisesRegex(ValueError, 'CONFLICT'):
            self.install('--replace-links')
        self.assertEqual(snapshot(self.project), before)
        (self.project / 'AGENTS.md').unlink()
        directory = self.project.parent / 'user-skills'
        directory.mkdir()
        (self.project / '.agents').symlink_to(directory)
        with self.assertRaisesRegex(ValueError, 'CONFLICT'):
            self.install('--replace-links')
        self.assertEqual(list(directory.iterdir()), [])

    def test_old_funnel_and_codex_link_migrate_without_modifying_source(self):
        self.install()
        codex = self.project / '.codex/hooks.json'
        codex.unlink()
        source_settings = ROOT / 'hooks/codex.hooks.json'
        original_source = source_settings.read_bytes()
        codex.symlink_to(source_settings)
        skill = self.project / '.claude/skills/session-close'
        skill.unlink()
        skill.symlink_to('../../.agents/skills/session-close')
        legacy = self.project / '.codex/hooks/context-zone.sh'
        legacy.parent.mkdir()
        legacy.symlink_to(ROOT / 'hooks/context-zone.sh')
        self.install('--replace-links')
        self.assertFalse(codex.is_symlink())
        self.assertFalse(os.path.lexists(legacy))
        self.assertFalse(legacy.parent.exists())
        self.assertEqual(source_settings.read_bytes(), original_source)

    def test_dangling_links_from_removed_checkout_are_repaired(self):
        moved = self.project.parent / 'old-trackline'
        shutil.copytree(ROOT, moved, symlinks=True, ignore=shutil.ignore_patterns('.git', 'tests'))
        self.install('--source', str(moved))
        shutil.rmtree(moved)
        with self.assertRaisesRegex(ValueError, 'needs --replace-links'):
            self.install()
        output = self.install('--replace-links')
        self.assertIn('repair  AGENTS.md', output)
        self.assertEqual((self.project / 'AGENTS.md').resolve(), ROOT / 'AGENTS.md')
        self.assertTrue((self.project / '.claude/skills/next-slice/SKILL.md').is_file())

    def test_every_conflict_is_reported_at_once(self):
        (self.project / 'AGENTS.md').write_text('user router')
        (self.project / 'CLAUDE.md').write_text('user notes')
        (self.project / 'docs').mkdir()
        (self.project / 'docs/adr').write_text('not a directory')
        before = snapshot(self.project)
        with self.assertRaises(ValueError) as caught:
            self.install('--replace-links')
        for name in ('AGENTS.md', 'CLAUDE.md', 'docs/adr'):
            self.assertIn(str(self.project / name), str(caught.exception))
        self.assertEqual(snapshot(self.project), before)

    def test_duplicate_hook_removal_drops_only_emptied_groups(self):
        hook = {'type': 'command', 'command': installer.BASH_COMMAND}
        data = {'hooks': {'Stop': [{'hooks': [dict(hook)]}, {'hooks': [dict(hook)]}, {'hooks': []}]}}
        stops = installer.merge(data)['hooks']['Stop']
        self.assertEqual(stops, [{'hooks': [hook]}, {'hooks': []}])

    def test_non_linux_unix_uses_ordinary_links(self):
        with mock.patch.dict(os.environ, {'WSL_DISTRO_NAME': ''}), \
             mock.patch.object(Path, 'read_text', side_effect=FileNotFoundError('/proc')):
            self.assertFalse(installer.wsl_runtime())

    def test_failure_restores_links_settings_and_directories(self):
        self.install()
        before = snapshot(self.project)
        # Fail late, after replacing a setting. Recovery must restore its exact
        # bytes/mtime and remove a newly installed link.
        path = self.project / '.claude/settings.json'
        transaction = installer.Transaction()
        try:
            transaction.replace(path, lambda: path.write_text('changed'))
            new = self.project / 'new/path/link'
            transaction.replace(new, lambda: new.symlink_to(ROOT / 'AGENTS.md'))
            raise OSError('simulated late failure')
        except OSError:
            transaction.rollback()
        self.assertEqual(snapshot(self.project), before)

    def test_main_rollback_on_settings_failure(self):
        self.seed_settings()
        before = snapshot(self.project)
        original = Path.write_text
        def fail_settings(path, *args, **kwargs):
            if path == self.project / '.claude/settings.json':
                raise OSError('settings write denied')
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'write_text', fail_settings), self.assertRaises(OSError):
            self.install()
        self.assertEqual(snapshot(self.project), before)

    def test_git_worktree_root_is_accepted(self):
        gitdir = self.project.parent / 'separate-git-dir'
        (self.project / '.git').rename(gitdir)
        (self.project / '.git').write_text(f'gitdir: {gitdir}\n')
        self.install('--dry-run')


@unittest.skipUnless(os.environ.get('TRACKLINE_WINDOWS_TESTS') == '1', 'requires Windows/WSL interoperability')
class WindowsTests(unittest.TestCase):
    install = InstallerTests.install
    seed_settings = InstallerTests.seed_settings
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.windows-test-', dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'project [Unicode café]'
        self.project.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)

    # Do not repeat the Linux suite on NTFS. These targeted real native-link
    # checks cover migration, native discovery, Unicode, and no-op reruns.
    def test_windows_native_migration_and_noop(self):
        self.seed_settings()
        (self.project / 'AGENTS.md').symlink_to(ROOT / 'AGENTS.md')
        self.install('--replace-links', native_linux=False)
        data = json.loads((self.project / '.codex/hooks.json').read_text())
        command = data['hooks']['Stop'][0]['hooks'][0]['commandWindows']
        self.assertNotIn(str(self.project), command)
        self.assertEqual(json.loads((self.project / '.claude/settings.json').read_text())['label'], 'café — 日本語')
        before = snapshot(self.project)
        self.install(native_linux=False)
        self.assertEqual(snapshot(self.project), before)
        ps = installer.discover_powershell()
        script = "Test-Path -LiteralPath '" + installer.winpath(self.project / '.codex/skills/roadmap-split/DEEP-SPLIT.md').replace("'", "''") + "'"
        self.assertEqual(installer.run(ps, '-NoProfile', '-NonInteractive', '-Command', script), 'True')
        # Runtime root resolution must work after moving the project and from a
        # nested working directory, without reinstalling registration JSON.
        moved = self.project.with_name('moved [project café]')
        self.project.rename(moved)
        self.project = moved
        self.assertTrue((moved / '.agents/hooks/context-zone.ps1').is_file())
        nested = moved / 'nested'
        nested.mkdir()
        transcript = moved / 'transcript.jsonl'
        transcript.write_text('{}\n')
        payload = json.dumps({'transcript_path': installer.winpath(transcript), 'total_tokens': 100001})
        code = command.split('-Command ', 1)[1][1:-1]
        # WSL interop does not reliably set PowerShell's provider location from
        # subprocess cwd. Set the native working directory explicitly, as a
        # native agent process does, then execute the stored command unchanged.
        native_nested = installer.winpath(nested).replace("'", "''")
        code = f"Set-Location -LiteralPath '{native_nested}'; " + code
        result = subprocess.check_output([ps, '-NoProfile', '-NonInteractive', '-Command', code],
                                         input=payload, text=True, cwd=nested)
        self.assertIn('warn zone', json.loads(result)['systemMessage'])
        # Exercise recovery of an actual native file link and JSON, not only
        # Linux symlinks, after a later operation fails.
        before = snapshot(moved)
        transaction = installer.Transaction()
        agents = moved / 'AGENTS.md'
        settings = moved / '.claude/settings.json'
        try:
            transaction.replace(agents, lambda: subprocess.run(
                [ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                 installer.winpath(ROOT / 'hooks/install-winlinks.ps1'), '-Path', installer.winpath(agents),
                 '-Target', installer.winpath(ROOT / 'hooks/context-zone.sh')], check=True))
            transaction.replace(settings, lambda: settings.write_text('{"temporary": true}'))
            raise OSError('late Windows migration failure')
        except OSError:
            transaction.rollback()
        self.assertEqual(snapshot(moved), before)


if __name__ == '__main__':
    unittest.main()
