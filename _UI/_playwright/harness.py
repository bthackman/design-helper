"""
Playwright test harness for the Design Process Tool's browser-dependent UI (Project Window,
Massing Studio, Test-Fit Studio) — NOT part of the shipped tool. Lets Claude Code drive real
click-through flows headlessly, backed by the actual filesystem, instead of needing a human
at the keyboard for every round of verification. See fs-mock.js for why this exists and what
it does and doesn't cover (notably: the IndexedDB-persisted-handle "reconnect" path isn't
exercised, only the first-connect picker path).

Usage sketch:

    from playwright.sync_api import sync_playwright
    from harness import install_fs_mock, set_dir_pick, set_open_pick, set_save_pick

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        install_fs_mock(page)
        page.goto("file:///C:/.../_UI/Project-Window.html")
        set_dir_pick(page, r"C:\...\Design Process Tool")
        page.click("#openRepo")
        page.wait_for_timeout(500)
        ...
        browser.close()
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
FS_MOCK_SCRIPT = HERE / "fs-mock.js"


def _list_dir(path):
    p = Path(path)
    out = []
    for entry in sorted(p.iterdir(), key=lambda e: e.name.lower()):
        if entry.name == ".git" or entry.name.startswith("."):
            continue
        out.append({"name": entry.name, "isDir": entry.is_dir()})
    return json.dumps(out)


def _read_file(path):
    return Path(path).read_text(encoding="utf-8")


def _write_file(path, content):
    Path(path).write_text(content, encoding="utf-8")
    return True


def _is_dir(path):
    return Path(path).is_dir()


def _is_file(path):
    return Path(path).is_file()


def _mkdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return True


def _mtime(path):
    return int(Path(path).stat().st_mtime * 1000)


def install_fs_mock(page):
    """Call once per page, BEFORE page.goto(). Registers the real-filesystem bridge
    functions and injects fs-mock.js so it runs before the target page's own scripts."""
    page.expose_function("__fsListDir", _list_dir)
    page.expose_function("__fsReadFile", _read_file)
    page.expose_function("__fsWriteFile", _write_file)
    page.expose_function("__fsIsDir", _is_dir)
    page.expose_function("__fsIsFile", _is_file)
    page.expose_function("__fsMkdir", _mkdir)
    page.expose_function("__fsMtime", _mtime)
    page.add_init_script(path=str(FS_MOCK_SCRIPT))


def set_dir_pick(page, path):
    """The next window.showDirectoryPicker() call will resolve to this real folder."""
    page.evaluate("(p) => { window.__NEXT_DIR_PATH = p; }", str(path))


def set_open_pick(page, path):
    """The next window.showOpenFilePicker() call will resolve to this real file."""
    page.evaluate("(p) => { window.__NEXT_OPEN_PATH = p; }", str(path))


def set_save_pick(page, path):
    """The next window.showSaveFilePicker() call will resolve to this real file path
    (created if it doesn't exist yet, once something is actually written to it)."""
    page.evaluate("(p) => { window.__NEXT_SAVE_PATH = p; }", str(path))


def collect_console_and_errors(page):
    """Attach listeners and return (console_msgs, page_errors) lists that fill live."""
    console_msgs = []
    page_errors = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    return console_msgs, page_errors
