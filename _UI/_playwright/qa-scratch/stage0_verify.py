import sys
sys.path.insert(0, r"C:\Users\BHackman\OneDrive - DIALOG\BHackman Drive\00_AI\Claude\Design Process Tool\_UI\_playwright")
from playwright.sync_api import sync_playwright
from harness import install_fs_mock, set_open_pick, set_save_pick, collect_console_and_errors

TF_URL = "file:///C:/Users/BHackman/OneDrive%20-%20DIALOG/BHackman%20Drive/00_AI/Claude/Design%20Process%20Tool/Projects/Nonimuss-Residence/4_Space-Planning/Test-Fit-Studio.html"
MS_URL = "file:///C:/Users/BHackman/OneDrive%20-%20DIALOG/BHackman%20Drive/00_AI/Claude/Design%20Process%20Tool/Projects/Nonimuss-Residence/3_Massing/Massing-Studio.html"
QA = r"C:\Users\BHackman\OneDrive - DIALOG\BHackman Drive\00_AI\Claude\Design Process Tool\_UI\_playwright\qa-scratch"
MASSING_JSON = QA + r"\massing-stage0.json"
TESTFIT_JSON = QA + r"\testfit-stage0.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ---- Direction 1: Massing -> Test-Fit ghost rectangle ----
    ms = browser.new_page(viewport={"width": 1600, "height": 950})
    install_fs_mock(ms)
    ms_console, ms_errors = collect_console_and_errors(ms)
    ms.goto(MS_URL)
    ms.wait_for_timeout(500)
    # resize House to something distinctive
    ms.evaluate("selIdx = state.findIndex(b=>b.id==='House'); buildSliders();")
    ms.evaluate("(() => { const b = state[selIdx]; b.w = 13; b.d = 10; rebuild(); refresh(); })()")
    set_save_pick(ms, MASSING_JSON)
    ms.evaluate("saveForSync()")
    ms.wait_for_timeout(500)
    print("Massing save status:", ms.evaluate("document.getElementById('syncStatus').textContent"))
    ms.close()

    tf = browser.new_page(viewport={"width": 1600, "height": 950})
    install_fs_mock(tf)
    tf_console, tf_errors = collect_console_and_errors(tf)
    tf.goto(TF_URL)
    tf.wait_for_timeout(500)
    set_open_pick(tf, MASSING_JSON)
    tf.evaluate("syncFromMassing()")
    tf.wait_for_timeout(500)
    print("Test-Fit sync status:", tf.evaluate("document.getElementById('massingSyncStatus').textContent"))
    print("volumesByLevel:", tf.evaluate("JSON.stringify(massingSync && massingSync.volumesByLevel)"))
    ghost_present = tf.evaluate("document.querySelectorAll('#svg rect[stroke=\"#8a6d3b\"]').length")
    print("ghost rect count on Ground:", ghost_present)
    tf.screenshot(path=QA + r"\dir1_testfit_ghost.png")
    print("Test-Fit console/errors:", tf_console[-10:], tf_errors)
    tf.close()

    # ---- Direction 2: Test-Fit -> Massing ghost wireframe ----
    tf2 = browser.new_page(viewport={"width": 1600, "height": 950})
    install_fs_mock(tf2)
    tf2.goto(TF_URL)
    tf2.wait_for_timeout(500)
    # move GU to Upper to make a real, distinctive change
    tf2.evaluate("rooms['GU'].level='Upper'; render();")
    set_save_pick(tf2, TESTFIT_JSON)
    tf2.evaluate("saveOwnState()")
    tf2.wait_for_timeout(500)
    print("Test-Fit save status:", tf2.evaluate("document.getElementById('ownSaveStatus').textContent"))
    tf2.close()

    ms2 = browser.new_page(viewport={"width": 1600, "height": 950})
    install_fs_mock(ms2)
    ms2_console, ms2_errors = collect_console_and_errors(ms2)
    ms2.goto(MS_URL)
    ms2.wait_for_timeout(500)
    set_open_pick(ms2, TESTFIT_JSON)
    ms2.evaluate("syncFromTestFit()")
    ms2.wait_for_timeout(500)
    print("Massing sync status:", ms2.evaluate("document.getElementById('tfSyncStatus').textContent"))
    ghost_children = ms2.evaluate("ghostGroup.children.length")
    print("ghostGroup children count:", ghost_children)
    ms2.screenshot(path=QA + r"\dir2_massing_ghost.png")
    print("Massing console/errors:", ms2_console[-10:], ms2_errors)
    ms2.close()

    browser.close()
