# Unified installer

The Windows-link prototype is integrated in this Trackline checkout. One Bash
entry supports Linux, WSL Linux-filesystem projects, and shared Windows/WSL
Windows-drive projects. This checkout contains the maintained skills and both
hooks; no explicit `--source` workaround is required.

From the target project's Git root:

```bash
bash /path/to/trackline/install-workflow.sh --replace-links .
```

Add `--dry-run` for a preview. See [README quick start](README.md#quick-start)
for dependencies and options. Installed artifacts link into the permanent
Trackline checkout, so keep it available. The isolated prototype worktree is no
longer needed for installation.

Run regression tests with `python3 -m unittest discover -s tests -v`.
For real native Windows link and hook checks from WSL, set
`TRACKLINE_WINDOWS_TESTS=1` before that command.
