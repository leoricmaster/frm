#!/usr/bin/env python3
"""定向补拍 4 张：01-login（locale zh-CN）、03-groups（firmware 子组）、
04-group-tree（顶层组概览=六子组+描述）、41-group-board（4000 宽全景）。
每张先打印 DOM 证据（标题/关键字/看板列名），再截图。"""
import time
from playwright.sync_api import sync_playwright

GL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GRP = "intel_excavator"
ROOT_PW = "Excavator#2026Proto"

def login(page, user, pw):
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", user)
    page.fill("input[name='user[password]']", pw)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

def evidence(page, name, checks):
    body = page.inner_text("body")
    print(f"[{name}] title={page.title()!r} url={page.url}")
    for label, needle in checks:
        print(f"    DOM 含 {label!r}: {needle in body}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")

        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  ignore_https_errors=True, locale="zh-CN")
        page = ctx.new_page()
        # 01 登录页（未登录，locale 协商中文）
        page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
        time.sleep(1.5)
        evidence(page, "01-login", [("中文『登录』", "登录"), ("中文『用户名』或『密码』", "密码")])
        page.screenshot(path=f"{OUT}/01-login.png")
        login(page, "root", ROOT_PW)
        # 03 firmware 子组页（组列表 → 项目）
        page.goto(f"{GL}/groups/{GRP}/firmware", wait_until="domcontentloaded")
        time.sleep(2)
        evidence(page, "03-groups", [("组名 firmware", "firmware"),
                                     ("仓库 hydraulic-controller", "hydraulic-controller"),
                                     ("组描述", "控制固件（MCU/PLC/控制器）")])
        page.screenshot(path=f"{OUT}/03-groups.png")
        # 04 顶层组概览（六子组+描述）
        page.goto(f"{GL}/groups/{GRP}", wait_until="domcontentloaded")
        time.sleep(2)
        evidence(page, "04-group-tree", [
            ("顶层描述", "智能挖机项目顶层group"), ("子组 firmware", "firmware"),
            ("子组 autonomy", "autonomy"), ("子组 vehicle", "vehicle"),
            ("子组 cloud", "cloud"), ("子组 app", "app"), ("子组 platform", "platform"),
            ("子组描述·算法", "算法（感知/规划/定位"), ("子组描述·平台工程", "平台工程（CI 模板")])
        page.screenshot(path=f"{OUT}/04-group-tree.png")
        ctx.close()

        # 41 看板全景（4000 宽；DOM 收列名 + 宽度证据）
        wctx = browser.new_context(viewport={"width": 4000, "height": 950},
                                   ignore_https_errors=True, locale="zh-CN")
        wpage = wctx.new_page()
        login(wpage, "root", ROOT_PW)
        wpage.goto(f"{GL}/groups/{GRP}/-/boards", wait_until="domcontentloaded")
        time.sleep(4)
        cols = wpage.evaluate("""() => {
            const els = document.querySelectorAll('[data-testid="board-list"], .board');
            const names = [];
            document.querySelectorAll('h2, h3, [class*="board-title"]').forEach(e => {
                const t = (e.innerText || '').trim();
                if (t && t.length < 40 && /开放|已关闭|状态/.test(t)) names.push(t.split('\\n')[0]);
            });
            const bl = document.querySelector('.boards-list, [class*="boards-list"]');
            return {names: [...new Set(names)],
                    scrollW: bl ? bl.scrollWidth : null, clientW: bl ? bl.clientWidth : null};
        }""")
        print(f"[41-group-board] 列名={cols['names']}")
        print(f"[41-group-board] boards-list scrollW={cols['scrollW']} clientW={cols['clientW']}"
              f"（scrollW<=clientW 即全部可见）")
        wpage.screenshot(path=f"{OUT}/41-group-board.png")
        wctx.close()
        browser.close()
    print("[done] 01/03/04/41 已重拍")

if __name__ == "__main__":
    main()
