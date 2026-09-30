# Unified installer candidate

The tested Windows-link prototype now forwards to one Bash entry that supports
Linux, WSL Linux-filesystem projects, and shared Windows/WSL Windows-drive
projects. The source worktree includes the maintained skills and both hooks;
no explicit `--source` workaround is required.

From the target project's Git root:

```bash
bash /mnt/c/Users/vardana/Documents/Proj/workflow-hub/.worktrees/trackline-winlinks/install-workflow.sh --replace-links .
```

Add `--dry-run` for a preview. See [README quick start](README.md#quick-start)
for dependencies and options. Keep this source worktree available until code
is integrated and the project is reinstalled from the permanent checkout.

Run regression tests with `python3 -m unittest discover -s tests -v`.
For real native Windows link and hook checks from WSL, set
`TRACKLINE_WINDOWS_TESTS=1` before that command.
