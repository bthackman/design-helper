# Playwright harness — setup and use

Dev tooling for verifying the browser-dependent parts of this tool (Project Window, Massing Studio,
Test-Fit Studio, and the generated `Design-Studio.html`). **Not part of the shipped tool** — nothing here
is packaged into `design-process.skill`, and no shipped file depends on it.

Written 2026-09-09 after a session discovered that `harness.py` had been in the repo for a day with no
install notes and no working interpreter on the machine — despite `HANDOFF.md` recording harness runs.
If you are picking this up on a new machine, start here.

## Install

Playwright needs both a Python package and a browser binary. The browser is a separate ~150 MB download
and is **not** installed by `pip` alone:

```
python -m pip install playwright
python -m playwright install chromium
```

**Check which interpreter you actually got.** This is the part that bites: a machine can easily have
several Pythons, and the one on `PATH` is often not the one with Playwright. Verify before assuming:

```
python -c "import playwright, sys; print(sys.executable)"
```

On the original author's Windows machine as of 2026-09-09 the working interpreter was
`C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe` — while `python`/`py` on `PATH`
resolved to Python 3.14, which did **not** have it. Expect this to differ per machine; don't hardcode
that path into anything you commit.

## Running against the Studios

The Studios are plain `file://` pages, so no server is needed:

```python
from playwright.sync_api import sync_playwright

URL = "file:///C:/AI/Claude/design-helper/Projects/Nonimuss-Residence/Design-Studio.html"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1600, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(2500)          # Massing pulls three.js/chart.js from a CDN — give it time
    print(pg.evaluate("() => state.length"))
    b.close()
```

Two things worth knowing before you write a test:

- **Massing Studio needs network.** It loads Three.js and Chart.js from `cdnjs.cloudflare.com`. Test-Fit
  and the Project Window are genuinely offline.
- **`file://` frames cannot script each other.** Chrome treats them as opaque origins, so cross-frame
  access throws `SecurityError` unless Chrome is launched with `--allow-file-access-from-files`. This is
  why the two Studios were merged into one document rather than composed with iframes.

## `fs-mock.js` / `harness.py`

Only needed for flows that open a **native file picker** (the Studios' Save/Load, the Project Window's
folder connect). Headless Chromium implements the File System Access API but its real pickers hang forever
waiting for an OS dialog that can never appear. `install_fs_mock(page)` replaces them with mocks backed by
the real filesystem via Python bridge functions, so reads and writes still hit real files.

Known gap, unchanged: the IndexedDB persisted-handle "reconnect" path is **not** exercised — only the
first-connect picker path. Structured-clone strips the mock objects' methods.

## Conventions this project follows

- **Scratch scripts are throwaway** — write them to a temp directory, not into the repo.
- **Screenshots go in `qa-scratch/`**, prefixed by what produced them (`step4_`, `step5_`, `review_`…), and
  reports cite their exact paths so a claim can be checked later.
- **Never point a test at a project's canonical interchange files.** Use `qa-scratch/` copies; a test that
  overwrites real project data is worse than no test.
- **The bar for "verified" is a real click-through**, not a brace-count and not a screenshot glance. Two
  bugs on 2026-09-09 were invisible to code review: `layoutPanels()` looking its panels up from an array of
  string literals a rename could not see, and a Chart.js star painted *underneath* another dataset — that
  one needed a pixel-level `getImageData` check to catch.
- **After any refactor, diff `buildInterchange()` and `buildExportData()` before and after** (dropping
  `buildInterchange()`'s `generated` timestamp) and require byte-identical output.
