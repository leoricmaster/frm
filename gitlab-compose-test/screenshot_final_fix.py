#!/usr/bin/env python3
"""终审修复补拍 — 17-pipeline14（root: tag 流水线）+ 05-project-guest（guest1: Guest 视角项目主页）。
输出截图 + DOM 证据（stdout）。"""
import time
from playwright.sync_api import sync_playwright
from shot_utils import hide_duo_banner

URL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
P = "intel_excavator/firmware/hydraulic-controller"

def login(page, user, pw):
    page.goto(f"{URL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", user)
    page.fill("input[name='user[password]']", pw)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

def evidence(page, checks):
    body = page.inner_text("body")
    print(f"    URL: {page.url}")
    print(f"    title: {page.title()}")
    for label, needle in checks:
        hit = needle in body
        print(f"    DOM 含 {label!r} ({needle!r}): {hit}")
    return body

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome')

        # --- C1: root 截 tag 流水线 #14 ---
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        login(page, "root", "Excavator#2026Proto")
        page.goto(f"{URL}/{P}/-/pipelines/14", wait_until="domcontentloaded", timeout=15000)
        time.sleep(2)
        print("[C1] pipeline #14 DOM 证据:")
        evidence(page, [
            ("tag 名 v0.2.0-field", "v0.2.0-field"),
            ("手动 job promote-release", "promote-release"),
        ])
        hide_duo_banner(page)
        page.screenshot(path=f"{OUT}/17-pipeline14.png", full_page=False)
        print(f"[OK] 17-pipeline14.png saved")
        ctx.close()

        # --- C2: guest1 截项目主页 ---
        ctx2 = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page2 = ctx2.new_page()
        login(page2, "guest1", "Xc7$wB3n!Tq8")
        print("[C2] guest1 登录后:", page2.url)
        page2.goto(f"{URL}/{P}", wait_until="domcontentloaded", timeout=15000)
        time.sleep(2)
        print("[C2] guest1 项目主页 DOM 证据:")
        body = evidence(page2, [
            ("项目名 hydraulic-controller", "hydraulic-controller"),
            ("readme 文件树链接", "README.md"),
            ("Code 按钮", "Code"),
        ])
        hide_duo_banner(page2)
        page2.screenshot(path=f"{OUT}/05-project-guest.png", full_page=False)
        print("[OK] 05-project-guest.png saved")
        ctx2.close()
        browser.close()

if __name__ == "__main__":
    main()
