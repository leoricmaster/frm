#!/usr/bin/env python3
"""角色流程验证截图 — dev1 MR 视角、Release 页、模板传播证据页。"""
import time
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
P = "excavator/firmware/hydraulic-controller"
PT = "excavator/platform/ci-templates"

PAGES = [
    ("14-mr2-merged",   f"{URL}/{P}/-/merge_requests/2",                    "MR !2 PID调参（已合入+批准记录）"),
    ("15-mr2-changes",  f"{URL}/{P}/-/merge_requests/2/diffs",              "MR !2 代码diff评审页"),
    ("16-release",      f"{URL}/{P}/-/releases/v0.2.0-field",               "Release v0.2.0-field 发布页"),
    ("17-pipeline19",   f"{URL}/{P}/-/pipelines/19",                        "流水线#19 模板传播验证"),
    ("18-job18-trace",  f"{URL}/{P}/-/jobs/18",                             "build job：模板script生效trace"),
    ("19-ci-mr",        f"{URL}/{PT}/-/merge_requests/2",                   "ci-templates 宪法变更MR"),
    ("20-mr4-field",    f"{URL}/{P}/-/merge_requests/4",                    "应急补单MR !4（§7.3闭环）"),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        page.goto(f"{URL}/users/sign_in", wait_until="networkidle")
        page.fill("input[name='user[login]']", "root")
        page.fill("input[name='user[password]']", "Excavator#2026Proto")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        for fname, url, label in PAGES:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(1.5)
                page.screenshot(path=f"{OUT}/{fname}.png", full_page=False)
                print(f"[OK] {fname} — {label}")
            except Exception as e:
                print(f"[FAIL] {fname} — {label}: {str(e)[:80]}")
        browser.close()

if __name__ == "__main__":
    main()
