#!/usr/bin/env python3
"""developer.html 换自动装车示例的重拍 5 张（2026-09-11，perception 仓）：

  44-autonomy-groups       autonomy 子组页（算法域 → perception 仓库）
  45-perception-protect    perception 保护分支设置（main 限 Maintainer）
  46-perception-mr-list    perception MR 列表（!1 开着）
  47-perception-mr-closes  MR !1 详情：Closes #1 + 里程碑「算法 v0.1」
  48-perception-mr-changes MR !1 Changes：train.py 阈值 diff

前置：seed_autonomy_demo.py 已跑完（单据/MR/流水线绿）。
每张先打印 DOM 证据（标题/关键字），再截图；源图落 screenshots/。
"""
import time
from playwright.sync_api import sync_playwright
from shot_utils import hide_duo_banner

GL = "http://127.0.0.1:8081"
OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
PCP = "intel_excavator/autonomy/perception"
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


def shot(page, url, name, checks, prep=None):
    page.goto(f"{GL}{url}", wait_until="domcontentloaded")
    time.sleep(2.5)
    if prep:
        try:
            prep(page)
        except Exception as e:
            print(f"    [prep 跳过] {str(e)[:100]}")
        time.sleep(1)
    evidence(page, name, checks)
    hide_duo_banner(page)
    page.screenshot(path=f"{OUT}/{name}.png")
    print(f"    已存 {OUT}/{name}.png")


def expand_protected(page):
    """受保护分支卡片若是折叠态则展开；无论折叠与否都滚进视口。"""
    try:
        page.locator("section", has_text="受保护分支").locator("button", has_text="展开").first.click(timeout=3000)
        time.sleep(1)
    except Exception as e:
        print(f"    [展开按钮不存在，视为已展开] {str(e)[:80]}")
    page.get_by_text("受保护分支", exact=False).first.scroll_into_view_if_needed()
    time.sleep(1)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  ignore_https_errors=True, locale="zh-CN")
        page = ctx.new_page()
        login(page, "root", ROOT_PW)

        shot(page, "/groups/intel_excavator/autonomy", "44-autonomy-groups", [
            ("子组名 autonomy", "autonomy"),
            ("仓库 perception", "perception"),
            ("组描述·算法", "算法（感知"),
        ])
        shot(page, f"/{PCP}/-/settings/repository", "45-perception-protect", [
            ("受保护分支", "受保护分支"),
            ("分支 main", "main"),
        ], prep=expand_protected)
        shot(page, f"/{PCP}/-/merge_requests", "46-perception-mr-list", [
            ("MR 标题", "自动装车对位阈值整定"),
            ("源分支 feat/load-align", "feat/load-align"),
        ])
        shot(page, f"/{PCP}/-/merge_requests/1", "47-perception-mr-closes", [
            ("MR 标题", "自动装车对位阈值整定"),
            ("Closes #1", "#1"),
            ("里程碑", "算法 v0.1·三阶段原型"),
            ("自查 checklist", "合码前自查"),
        ])
        shot(page, f"/{PCP}/-/merge_requests/1/diffs", "48-perception-mr-changes", [
            ("文件 train.py", "train.py"),
            ("diff 行 ALIGN_CONF", "ALIGN_CONF"),
            ("阈值 0.80", "0.80"),
        ])
        # 21 顺带重拍：列表里现在有 main + feat/load-align 两条，比 09-09 旧图更完整
        shot(page, f"/{PCP}/-/pipelines", "21-perception-pipelines", [
            ("流水线 ref main", "main"),
            ("流水线 ref feat/load-align", "feat/load-align"),
        ])
        ctx.close()
        browser.close()
    print("[done] 44-48 已拍")


if __name__ == "__main__":
    main()
