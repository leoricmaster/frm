#!/usr/bin/env python3
"""补拍 04-group-tree.png：intel_excavator 组的子组树（Group overview → Subgroups）。"""
import time
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots/04-group-tree.png"

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
    # intel_excavator 组主页（子组以卡片形式列在页面里）
    page.goto(f"{URL}/intel_excavator", wait_until="networkidle", timeout=20000)
    time.sleep(2)
    page.screenshot(path=OUT, full_page=False)
    print(f"[OK] {OUT} — intel_excavator 组主页（含 6 子组卡片）")
    browser.close()
