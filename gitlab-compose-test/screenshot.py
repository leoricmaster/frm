#!/usr/bin/env python3
"""GitLab 界面截图脚本 — 登录后逐页截图，供评估界面可用性。
对应设计文档：验证 MR/保护分支/组结构/流水线/制品的界面是否可接受。"""
import sys, time
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
LOGIN, PASS = "root", "Excavator#2026Proto"

PAGES = [
    ("02-dashboard",   f"{URL}/",                                                    "主面板"),
    ("03-groups",      f"{URL}/groups/excavator",                                    "excavator 组结构"),
    ("04-group-tree",  f"{URL}/groups/excavator/-/subgroups",                       "子组列表"),
    ("05-project",     f"{URL}/excavator/firmware/hydraulic-controller",            "示例项目"),
    ("06-pipelines",   f"{URL}/excavator/firmware/hydraulic-controller/-/pipelines", "流水线列表"),
    ("07-ci-success",  f"{URL}/excavator/firmware/hydraulic-controller/-/pipelines/3","流水线#3(全绿)"),
    ("08-mr-list",     f"{URL}/excavator/firmware/hydraulic-controller/-/merge_requests","MR列表"),
    ("09-mr-closed",   f"{URL}/excavator/firmware/hydraulic-controller/-/merge_requests/1","MR!1(已合入)"),
    ("10-protect",     f"{URL}/excavator/firmware/hydraulic-controller/-/settings/repository","保护分支设置"),
    ("11-ci-templates",f"{URL}/excavator/platform/ci-templates",                    "CI模板仓库(平台宪法)"),
    ("12-members",     f"{URL}/excavator/firmware/hydraulic-controller/-/project_members","成员权限(三级)"),
    ("13-packages",    f"{URL}/excavator/firmware/hydraulic-controller/-/packages", "制品/package registry"),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        # 登录
        page.goto(f"{URL}/users/sign_in", wait_until="networkidle")
        page.fill("input[name='user[login]']", LOGIN)
        page.fill("input[name='user[password]']", PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        # 逐页截图
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
