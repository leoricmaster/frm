#!/usr/bin/env python3
"""管理区「新建用户」页截图 — 用示范值填字段、不提交。
对应 ops.html §6.1 开账号说明；示范账号 gw_zhangyunfeng@irootech.com。"""
import time
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8081"
LOGIN, PASS = "root", "Excavator#2026Proto"
OUT = "/home/lancer/projects/frm/docs/tutorials/assets/02-admin-new-user.png"

FIELDS = [
    ("input[name='user[name]']",     "张云锋"),
    ("input[name='user[username]']", "gw_zhangyunfeng"),
    ("input[name='user[email]']",    "gw_zhangyunfeng@irootech.com"),
    ("input[name='user[password]']", "TempPass#2026"),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        # 登录 root
        page.goto(f"{URL}/users/sign_in", wait_until="networkidle")
        page.fill("input[name='user[login]']", LOGIN)
        page.fill("input[name='user[password]']", PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        # 进管理区新建用户页
        page.goto(f"{URL}/admin/users/new", wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)
        # 填示范值（不提交）
        for sel, val in FIELDS:
            try:
                page.fill(sel, val)
                print(f"[fill] {sel} = {val}")
            except Exception as e:
                print(f"[skip] {sel}: {str(e)[:80]}")
        page.screenshot(path=OUT, full_page=False)
        print(f"[OK] saved {OUT}")
        browser.close()

if __name__ == "__main__":
    main()
