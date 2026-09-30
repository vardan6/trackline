"""Shared installation, settings preservation, and transaction recovery."""
import argparse
import base64
import copy
from decimal import Decimal
import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

SKILLS = ('cross-review', 'doc-update', 'handoff', 'next-slice', 'plan-review',
          'planning-capture', 'review-triage', 'roadmap-split', 'session-close', 'session-open')
EXTERNAL = ('grill-me', 'grill-with-docs')
DOCS = ('requirements', 'design', 'adr', 'reviews', 'research', 'archive')
BASH_COMMAND = 'bash "$(git rev-parse --show-toplevel)/.agents/hooks/context-zone.sh"'
WINDOWS_COMMAND = ('powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass '
                   '-Command "[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); '
                   '$root = git rev-parse --show-toplevel; '
                   'if ($LASTEXITCODE -ne 0) { exit 1 }; '
                   "$hook = Join-Path $root '.agents/hooks/context-zone.ps1'; "
                   '& ([scriptblock]::Create([IO.File]::ReadAllText($hook, [Text.Encoding]::UTF8)))"')


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def winpath(path):
    # wslpath follows existing links. Translate a directory with no linked
    # ancestors, then append the lexical suffix so inspection sees the link
    # itself, not its target (including directory links and cloud placeholders).
    path = Path(os.path.abspath(path))
    anchor = path.parent
    while not anchor.is_dir() or any(p.is_symlink() for p in (anchor, *anchor.parents)):
        anchor = anchor.parent
    translated = run('wslpath', '-w', str(anchor))
    return ntpath.join(translated, *path.relative_to(anchor).parts)


def discover_powershell():
    found = shutil.which('powershell.exe')
    if found:
        return found
    cmd = shutil.which('cmd.exe')
    if cmd:
        windir = run(cmd, '/d', '/c', 'echo %SystemRoot%')
        return run('wslpath', '-u', windir + r'\System32\WindowsPowerShell\v1.0\powershell.exe')
    # Windows PATH import may be disabled. Read actual DrvFs mount locations,
    # rather than assuming /mnt/c, then look for the system executable.
    for line in Path('/proc/mounts').read_text().splitlines():
        fields = line.split()
        if len(fields) >= 4 and (fields[2] == 'drvfs' or 'aname=drvfs' in fields[3]):
            mount = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), fields[1])
            candidate = Path(mount) / 'Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
            if candidate.is_file():
                return str(candidate)
    return None


def windows_inventory(powershell, paths):
    names = [(str(path), winpath(path)) for path in paths if os.path.lexists(path)]
    if not names:
        return {}
    script = """
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TracklineLinkInfo {
    [StructLayout(LayoutKind.Sequential)]
    public struct TagInfo { public uint attributes; public uint tag; }
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, ExactSpelling=true, SetLastError=true)]
    static extern IntPtr CreateFileW(string path, uint access, uint share, IntPtr security, uint disposition, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool GetFileInformationByHandleEx(IntPtr handle, int infoClass, out TagInfo info, uint size);
    [DllImport("kernel32.dll")]
    static extern bool CloseHandle(IntPtr handle);
    public static uint[] Inspect(string path) {
        IntPtr handle = CreateFileW(path, 0, 7, IntPtr.Zero, 3, 0x02200000, IntPtr.Zero);
        if (handle == new IntPtr(-1)) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
        try {
            TagInfo info;
            if (!GetFileInformationByHandleEx(handle, 9, out info, 8))
                throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
            return new uint[] { info.attributes, info.tag };
        } finally { CloseHandle(handle); }
    }
}
'@
$names = [Console]::In.ReadToEnd() | ConvertFrom-Json
$result = @()
foreach ($pair in $names) {
    $info = [TracklineLinkInfo]::Inspect($pair[1])
    $result += [pscustomobject]@{
        path=$pair[0]; reparse=(($info[0] -band 1024) -ne 0);
        native=($info[1] -eq 2684354572); lx=($info[1] -eq 2684354589);
        junction=($info[1] -eq 2684354563)
    }
}
ConvertTo-Json -InputObject @($result) -Compress
"""
    output = subprocess.check_output(
        [powershell, '-NoProfile', '-NonInteractive', '-EncodedCommand',
         base64.b64encode(script.encode('utf-16le')).decode()], input=json.dumps(names), text=True)
    return {item['path']: item for item in json.loads(output)}


def windows_claude_dependencies(powershell):
    script = """
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$bash = $env:CLAUDE_CODE_GIT_BASH_PATH
if (-not $bash) {
    $git = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($git) { $bash = Join-Path (Split-Path (Split-Path $git.Source -Parent) -Parent) 'bin\\bash.exe' }
}
$available = $false
if ($bash -and (Test-Path -LiteralPath $bash)) {
    & $bash --noprofile --norc -c 'command -v jq >/dev/null 2>&1' *> $null
    $available = ($LASTEXITCODE -eq 0)
}
if ($available) { 'ready' } else { 'missing' }
"""
    return run(powershell, '-NoProfile', '-NonInteractive', '-EncodedCommand',
               base64.b64encode(script.encode('utf-16le')).decode()) == 'ready'


def checkout(root):
    return (root / 'AGENTS.md').is_file() and (root / 'skills').is_dir() and (root / 'install-workflow.sh').is_file()


def wsl_runtime():
    return bool(os.environ.get('WSL_DISTRO_NAME')) or 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()


def owned(path, relative):
    """Recognize a symlink to the named artifact in a Trackline checkout."""
    if not path.is_symlink():
        return False
    try:
        target = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return False
    root = target
    for _ in Path(relative).parts:
        root = root.parent
    return checkout(root) and target == root / relative


def read_json(path):
    if not os.path.lexists(path):
        return {}
    with path.open(encoding='utf-8-sig') as stream:
        data = json.load(stream, parse_float=Decimal)
    if not isinstance(data, dict):
        raise ValueError(f'JSON settings must be an object: {path}')
    return data


def json_settings(value, level=0):
    """Render JSON without rounding unrelated decimal values during a merge."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (dict, list)):
        opening, closing = ('{', '}') if isinstance(value, dict) else ('[', ']')
        if not value:
            return opening + closing
        if isinstance(value, dict):
            items = [json.dumps(key, ensure_ascii=False) + ': ' + json_settings(item, level + 1)
                     for key, item in value.items()]
        else:
            items = [json_settings(item, level + 1) for item in value]
        prefix = '  ' * (level + 1)
        return opening + '\n' + ',\n'.join(prefix + item for item in items) + '\n' + '  ' * level + closing
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def merge(data, windows=False):
    result = copy.deepcopy(data)
    hooks = result.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('hooks must be an object')
    stops = hooks.setdefault('Stop', [])
    if not isinstance(stops, list):
        raise ValueError('hooks.Stop must be an array')
    found = False
    for group in stops:
        if not isinstance(group, dict) or not isinstance(group.get('hooks', []), list):
            raise ValueError('Stop groups must contain a hooks array')
        kept = []
        for hook in group.get('hooks', []):
            if not isinstance(hook, dict):
                raise ValueError('hook entries must be objects')
            if hook.get('command') == BASH_COMMAND:
                if found:
                    continue
                found = True
                if windows:
                    hook['commandWindows'] = WINDOWS_COMMAND
                else:
                    hook.pop('commandWindows', None)
            kept.append(hook)
        group['hooks'] = kept
    if not found:
        hook = {'type': 'command', 'command': BASH_COMMAND, 'timeout': 30}
        if windows:
            hook['commandWindows'] = WINDOWS_COMMAND
        stops.append({'hooks': [hook]})
    return result


class Transaction:
    def __init__(self):
        self.changes = []
        self.dirs = []

    def mkdir(self, path):
        if path.is_dir():
            return
        self.mkdir(path.parent)
        path.mkdir()
        self.dirs.append(path)

    def replace(self, path, create):
        self.mkdir(path.parent)
        backup = None
        if os.path.lexists(path):
            backup = path.with_name(path.name + '.trackline-old-' + uuid.uuid4().hex)
            path.rename(backup)
        self.changes.append((path, backup))
        create()

    def rollback(self):
        errors = []
        for path, backup in reversed(self.changes):
            try:
                if os.path.lexists(path):
                    path.unlink()
                if backup:
                    backup.rename(path)
            except OSError as error:
                errors.append(f'{path}: {error}; backup: {backup}')
        for path in reversed(self.dirs):
            try:
                path.rmdir()
            except OSError:
                pass
        if errors:
            print('Recovery needs attention:\n' + '\n'.join(errors), file=sys.stderr)

    def commit(self):
        for _, backup in self.changes:
            if backup:
                try:
                    backup.unlink()
                except OSError as error:
                    print(f'Installed; retained backup {backup}: {error}', file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Install from Linux or WSL; select the project filesystem automatically.')
    parser.add_argument('--installer-dir', required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--dry-run', '-n', action='store_true')
    parser.add_argument('--replace-links', '--force', '-f', action='store_true', dest='replace')
    parser.add_argument('--with-external', action='store_true')
    parser.add_argument('project', nargs='?', default='.', type=Path)
    args = parser.parse_args()
    installer = Path(args.installer_dir).resolve()
    source = (args.source or installer).resolve(strict=True)
    project = args.project.resolve(strict=True)
    if not checkout(source):
        raise ValueError('Source must be a Trackline checkout')
    if Path(run('git', '-C', str(project), 'rev-parse', '--show-toplevel')).resolve() != project:
        raise ValueError('Project must be a Git repository root')
    is_wsl = wsl_runtime()
    windows = False
    powershell = None
    if is_wsl:
        if not shutil.which('wslpath'):
            raise ValueError('WSL path translation is unavailable')
        windows = bool(re.match(r'^[A-Za-z]:\\', winpath(project)))
        if windows:
            if not re.match(r'^[A-Za-z]:\\', winpath(source)):
                raise ValueError('Shared Windows/WSL installation requires a Windows-drive source')
            powershell = discover_powershell()
            if not powershell or not Path(powershell).is_file():
                raise ValueError('Windows PowerShell unavailable; enable WSL interoperability and Windows tools in PATH')
            try:
                run(powershell, '-NoProfile', '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.ToString()')
            except (OSError, subprocess.CalledProcessError) as error:
                raise ValueError('Windows PowerShell cannot run; check WSL interoperability') from error
    print('Mode: ' + ('shared Windows/WSL' if windows else 'Linux'))
    attention = []
    if is_wsl and not windows:
        print('WSL Linux-filesystem project: native Windows sharing is not supported by this installation.')
    if windows:
        if windows_claude_dependencies(powershell):
            print('Native Windows Claude hook dependencies: Git Bash and jq found.')
        else:
            attention.append('Native Windows Claude: install jq in Git Bash or set CLAUDE_CODE_GIT_BASH_PATH; verify dependencies before relying on its Stop hook. Windows Codex uses PowerShell.')
            print('ATTENTION: ' + attention[-1])
    if not shutil.which('jq'):
        raise ValueError('jq is required by the Bash Stop hook; install it before installation')
    skills = SKILLS + (EXTERNAL if args.with_external else ())
    links = [(project / 'AGENTS.md', source / 'AGENTS.md', 'AGENTS.md'),
             (project / 'CLAUDE.md', source / 'AGENTS.md', 'AGENTS.md')]
    for skill in skills:
        for scope in ('.agents', '.claude', '.codex'):
            links.append((project / scope / 'skills' / skill, source / 'skills' / skill, f'skills/{skill}'))
    links.append((project / '.agents/hooks/context-zone.sh', source / 'hooks/context-zone.sh', 'hooks/context-zone.sh'))
    if windows:
        links.append((project / '.agents/hooks/context-zone.ps1', source / 'hooks/context-zone.ps1', 'hooks/context-zone.ps1'))
    settings_paths = [project / '.codex/hooks.json', project / '.claude/settings.json']
    legacy = project / '.codex/hooks/context-zone.sh'
    scaffold = [project / 'docs' / name for name in DOCS]
    inspect = {path for path, _, _ in links} | set(settings_paths + scaffold + [legacy])
    for path in tuple(inspect):
        for parent in path.parents:
            if parent == project:
                break
            inspect.add(parent)
    inventory = windows_inventory(powershell, sorted(inspect)) if windows else {}
    for name, item in inventory.items():
        # A cloud placeholder or junction is not an owned symbolic link,
        # even if Windows reports the generic ReparsePoint attribute.
        if item['reparse'] and (not (item['native'] or item['lx']) or not Path(name).is_symlink()):
            raise ValueError(f'CONFLICT non-symbolic reparse point: {name}')
    planned = []
    def check_parents(path):
        for parent in path.parents:
            if parent == project:
                break
            if parent.is_symlink() or (os.path.lexists(parent) and not parent.is_dir()):
                raise ValueError(f'CONFLICT parent is a link or non-directory: {parent}')
    for path, target, relative in links:
        check_parents(path)
        if not target.exists():
            raise ValueError(f'Missing source: {target}')
        if os.path.lexists(path):
            if not owned(path, relative):
                raise ValueError(f'CONFLICT unrelated or real artifact: {path}')
            if path.resolve() == target and (not windows or inventory[str(path)]['native']):
                continue
            if not args.replace:
                raise ValueError(f'Existing managed link needs --replace-links: {path}')
        planned.append((path, target))
    settings = []
    for relative, native in (('.codex/hooks.json', windows), ('.claude/settings.json', False)):
        path = project / relative
        check_parents(path)
        linked = path.is_symlink()
        if linked and (relative != '.codex/hooks.json' or not owned(path, 'hooks/codex.hooks.json')):
            raise ValueError(f'CONFLICT unrelated settings link: {path}')
        if linked and not args.replace:
            raise ValueError(f'Existing managed settings link needs --replace-links: {path}')
        original = read_json(path)
        updated = merge(original, native)
        if updated != original or linked or not path.exists():
            settings.append((path, json_settings(updated) + '\n'))
    check_parents(legacy)
    if os.path.lexists(legacy) and not owned(legacy, 'hooks/context-zone.sh'):
        raise ValueError(f'CONFLICT unrelated legacy hook: {legacy}')
    if os.path.lexists(legacy) and not args.replace:
        raise ValueError('Legacy hook cleanup needs --replace-links')
    for path in scaffold:
        check_parents(path)
        if os.path.lexists(path) and (path.is_symlink() or not path.is_dir()):
            raise ValueError(f'CONFLICT documentation path: {path}')
    for path, target in planned:
        print(f'link    {path.relative_to(project)} -> {target}')
    for path, _ in settings:
        print(f'merge   {path.relative_to(project)}')
    for path in scaffold:
        if not path.exists():
            print(f'mkdir   {path.relative_to(project)}')
    if os.path.lexists(legacy):
        print('prune   .codex/hooks/context-zone.sh')
    if args.dry_run:
        print('Dry run: no changes; Windows link privilege is not probed.')
        return
    def create_link(path, target):
        if windows:
            command = [powershell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                       winpath(installer / 'hooks/install-winlinks.ps1'), '-Path', winpath(path), '-Target', winpath(target)]
            if target.is_dir():
                command.append('-Directory')
            subprocess.run(command, check=True)
        else:
            path.symlink_to(target, target_is_directory=target.is_dir())
    if windows:
        with tempfile.TemporaryDirectory(prefix='.trackline-link-probe-', dir=project) as probe:
            probes = ((Path(probe) / 'directory-link', source / 'skills'),
                      (Path(probe) / 'file-link', source / 'AGENTS.md'))
            try:
                for link, target in probes:
                    create_link(link, target)
                    if not link.exists():
                        raise ValueError('WSL cannot read the Windows-native probe link')
            except (OSError, subprocess.CalledProcessError) as error:
                raise ValueError('Native links unavailable; enable Developer Mode or Windows symlink privilege. No managed artifacts changed.') from error
            finally:
                for link, _ in probes:
                    if os.path.lexists(link):
                        link.unlink()
    transaction = Transaction()
    try:
        for path, target in planned:
            transaction.replace(path, lambda p=path, t=target: create_link(p, t))
        for path, content in settings:
            mode = path.stat().st_mode & 0o777 if path.exists() and not path.is_symlink() else None
            def write_settings(p=path, c=content, permissions=mode):
                p.write_text(c, encoding='utf-8')
                if permissions is not None:
                    p.chmod(permissions)
            transaction.replace(path, write_settings)
        if os.path.lexists(legacy):
            transaction.replace(legacy, lambda: None)
        for path in scaffold:
            transaction.mkdir(path)
    except BaseException:
        transaction.rollback()
        raise
    transaction.commit()
    print(f'Done: {len(planned)} links, {len(settings)} settings updates. Restart agents to reload.')
    if attention:
        print('Needs attention:\n' + '\n'.join('  - ' + message for message in attention))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f'error: {error}', file=sys.stderr)
        sys.exit(1)
