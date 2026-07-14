# Credits

This workflow uses several skills authored by **Matt Pocock**, vendored into
this repository under the terms of the MIT License. The full license text and
copyright notice are in [`skills/LICENSE-mattpocock`](skills/LICENSE-mattpocock).

## Vendored skills (MIT — © 2026 Matt Pocock)

Source: [`mattpocock/skills`](https://github.com/mattpocock/skills) —
"Skills for Real Engineers."

| Skill in this repo        | Upstream path                          |
|---------------------------|----------------------------------------|
| `skills/grill-me/`        | `skills/productivity/grill-me`         |
| `skills/grill-with-docs/` | `skills/engineering/grill-with-docs`   |
| `skills/handoff/`         | `skills/productivity/handoff`          |

These three are copied (vendored) rather than authored here. They are used in
this workflow's planning phase (`grill-me`, `grill-with-docs`) and for
cross-tool/model session transfer (`handoff`). The remaining skills in
`skills/` — `session-open`, `planning-capture`, `plan-review`, `next-slice`,
`doc-update`, `cross-review`, `review-triage`, `session-close` — are authored
in this repository.

## Notes

- The copies were taken from a local install (`~/.agents/skills/`) where the
  upstream `LICENSE` had been stripped; the MIT notice was restored from the
  source repository so attribution and license travel with the files.
- Vendored copies are pinned and may drift from upstream. To refresh, re-copy
  from [`mattpocock/skills`](https://github.com/mattpocock/skills) and keep this
  file and `skills/LICENSE-mattpocock` in sync.
