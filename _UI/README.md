# _UI — Project Window working files

Built 2026-08-27, ahead of any UI. Everything here is tested in Node against a synthetic
project; none of it has met a real one yet.

| File | What it is |
|---|---|
| `probe.html` | **Open this first.** Ten-second browser test: does folder access work from `file://`? Reads, then writes and deletes a scratch file. Prints a verdict. |
| `inspect-project.js` | `node _UI/inspect-project.js Projects/<name>` — inventories a real project, flags column drift, checks `massing.json`, and prints what the Window would show including the conscience panel. `--write-state` generates `0_Spine/state.json`. |
| `spine-parse.js` | Table + card parsers and phase-state inference. Browser-ready (pure functions, no Node APIs beyond the module export). |
| `audit.js` | The conscience panel logic. |
| `runtest.js`, `audittest.js` | The test suites. `node _UI/runtest.js` from the repo root — 33 + 9 checks. |

## Tomorrow, in order

1. Open `probe.html` in Chrome. If the verdict is green, the Window can be a plain file.
   If not, `python -m http.server 8000` from the repo root and everything else still holds.
2. `node _UI/inspect-project.js Projects/<pilot>` — read section 4 (column drift) and
   section 5 (assets, `massing.json`) closely. Those are where the plan's assumptions break.
3. Fix any drift the inspector reports, in `spine-parse.js` or in the template — whichever is wrong.
4. `--write-state` once the inference looks right, then correct the file by hand.
5. Only then start on the Window shell.

The test suites expect `testproj/` and `design-helper/_templates/` as siblings; they were written
against a scratch fixture and will need their paths adjusted if you want to re-run them here.
