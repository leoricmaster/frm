#!/usr/bin/env python3
"""submitter.html 证据重拍（2026-09-11）：

Phase A（guest1 会话）：受理台按三模板真实提单，提交前截"填好待提交"表单
         32 需求 / 32b 缺陷 / 32c 任务——root PAT 无 sudo scope，代提不可行，
         经 UI 提交同时保证作者=guest1（与 33 号图口径一致）。
Phase B（root API）：给 3 张新单补 状态::待受理（分诊代打）。
Phase C（root 会话）：41 组看板全景（重拍，卡片更丰富）/
         42 里程碑 930 页（43%，3/7）/ 43 受理台积压（4 单在队）。

表单自动化要点（2026-09-11 探测，GitLab 19.3.1-jh）：
  - 表单 302 到 work_items 路由；标题框 input[id^="work-item-title"]（动态后缀）
  - 编辑器 tiptap 无 textarea——经 [data-testid="editing-mode-switcher"] 切纯文本
    填 markdown 再切回富文本渲染；textarea 选择器排除 Duo 聊天框（有 placeholder）
  - Duo 右侧聊天面板 [data-testid="chat-component"] 截图前隐藏
  - 提交按钮文案「创建 Issue」
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright
from shot_utils import hide_duo_banner

OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GL = "http://127.0.0.1:8081"
T = "glpat-RebuildJH2026TokenProto000001"
INTAKE_WEB = f"{GL}/intel_excavator/intake/-"
GRP_WEB = f"{GL}/groups/intel_excavator/-"

# ---- Phase A 三张单（模板结构一一对应，guest1 口吻）----
FILINGS = [
    ("32-intake-template-form", "需求", "【需求】铲斗称重数据支持按工况导出报表", """## 背景与目标

客服部代 X 客户提：车队运营周报需要按工况（挖掘 / 回转 / 怠速）汇总铲斗称重数据，人工抄录太费人。

## 验收标准

- [ ] 中控屏可按「日期 + 工况」导出称重数据 CSV
- [ ] 导出时间范围现场可配（最长 90 天）

## 来源信息

- 提出方 / 期望版本：客服部 · 代 X 客户 / 930""", "背景与目标"),
    ("32b-intake-template-form-defect", "缺陷", "【缺陷】雨刮器低速间歇档偶发停顿", """## 现象

低速间歇档连续运行约 10 分钟后，雨刮偶发停顿 2–3 秒再恢复；高速档未见。

## 复现步骤

1. 雨刮拨至低速间歇档
2. 连续喷水刮拭约 10 分钟
3. 观察刮片中途停顿（样机 EXC-2026-013 三天里复现 4 次）

## 影响范围

EXC-2026-013 / 017 两台样机，固件 v0.8.2。

## 机器版本（manifest 粘贴区）

```json
无（现场未导出 manifest，机器号 EXC-2026-013，可安排下次保养时导）
```""", "现象"),
    ("32c-intake-template-form-task", "任务", "【任务】操作手册补充遥控器平地模式章节", """## 任务说明

现场反馈操作手册缺「遥控器平地模式」使用说明，客服在反复解答同一问题；手册在本组仓库，补一章一劳永逸。

## 完成标准

- [ ] 手册新增平地模式章节（适用场景 + 操作步骤 + 注意事项）
- [ ] 现场技术支持评审通过""", "任务说明"),
]


def api(path, method="GET", data=None):
    req = urllib.request.Request(f"{GL}/api/v4{path}",
                                 headers={"PRIVATE-TOKEN": T}, method=method)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    r = urllib.request.urlopen(req, body)
    return json.load(r) if r.status != 204 else {}


def q(s):
    return urllib.parse.quote(s, safe="")


def hide_duo_panel(page):
    """右侧 Duo 聊天面板（chat-component）占约 1/4 宽，截图前隐藏。"""
    try:
        page.evaluate(
            """() => document.querySelectorAll('[data-testid="chat-component"]')
                   .forEach(el => el.style.display = 'none')""")
    except Exception:
        pass


def scroll_to_text(page, marker):
    page.evaluate(
        """([m]) => {
            const els = Array.from(document.querySelectorAll('div,p,li,td,pre,code,h1,h2,h3,h4'));
            const hits = els.filter(e => (e.innerText || '').includes(m)
                                        && (e.innerText || '').length < 2000);
            if (hits.length) hits[hits.length - 1].scrollIntoView({block: 'center'});
        }""", [marker])
    time.sleep(0.8)


def login(page, user, pw):
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", user)
    page.fill("input[name='user[password]']", pw)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)


def fill_and_file(page, tpl, title, body_md):
    """打开模板表单 → 填标题 → 切纯文本填描述 → 切回富文本 → 返回（未提交）。"""
    page.goto(f"{INTAKE_WEB}/issues/new?issuable_template={q(tpl)}",
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(3)
    page.locator("input[id^='work-item-title']").fill(title)
    page.locator("[data-testid='editing-mode-switcher']").click()
    ta = page.locator("textarea.markdown-area")  # 纯文本框；Duo 聊天框无此类名
    ta.wait_for(state="visible", timeout=5000)
    ta.fill(body_md)
    page.locator("[data-testid='editing-mode-switcher']").click()
    page.wait_for_selector(".rte-text-box", timeout=5000)
    time.sleep(0.5)
    kw = body_md.splitlines()[0].replace("## ", "")
    got = page.locator(".rte-text-box").inner_text()
    assert kw in got, f"富文本回显缺少 {kw!r}，可能内容丢失"


def main():
    filed = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")

        # ---------- Phase A：guest1 提单 + 表单截图 ----------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page, "guest1", "Xc7$wB3n!Tq8")
        print(f"[info] guest1 登录 ok -> {page.url[:60]}")
        for fname, tpl, title, body, marker in FILINGS:
            ex = next((i for i in api("/projects/7/issues?per_page=100")
                       if i["title"] == title), None)
            if ex:  # 幂等：已提过只补标签，不重复提单
                filed.append({"tpl": tpl, "title": title, "iid": ex["iid"]})
                print(f"[skip] intake#{ex['iid']} 已提过: {title}")
                continue
            try:
                fill_and_file(page, tpl, title, body)
                scroll_to_text(page, marker)
                hide_duo_panel(page)
                hide_duo_banner(page)
                page.screenshot(path=f"{OUT}/{fname}.png")
                page.get_by_role("button", name="创建 Issue").click()
                # 19.x 工作项路由是 /work_items/<iid>（表单页 302 同源）
                page.wait_for_url(re.compile(r"/(issues|work_items)/\d+"),
                                  timeout=15000)
                time.sleep(1.5)
                iid = page.url.rstrip("/").split("/")[-1]
                filed.append({"tpl": tpl, "title": title, "iid": int(iid)})
                print(f"[OK] {fname} 已提交 intake#{iid} {title}")
            except Exception as e:
                print(f"[FAIL] {fname} — {title}: {str(e)[:140]}")
                page.screenshot(path=f"{OUT}/{fname}-FAIL.png")
        ctx.close()

        # ---------- Phase B：root 补 待受理 标签 ----------
        for f in filed:
            api(f"/projects/7/issues/{f['iid']}", "PUT",
                {"labels": "状态::待受理", "add_labels": "状态::待受理"})
            print(f"[lab ] intake#{f['iid']} +状态::待受理")

        # ---------- Phase C：root 重拍 41/42/43 ----------
        ms = next(m for m in api("/groups/intel_excavator/milestones?per_page=50")
                  if m["title"] == "930")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page, "root", "Excavator#2026Proto")
        print(f"[info] root 登录 ok -> {page.url[:60]}")

        # 41 组看板全景：先量宽再放大视口
        board_url = f"{GRP_WEB}/boards"
        page.goto(board_url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(4)
        w = page.evaluate(
            """() => {
                const bs = Array.from(document.querySelectorAll('.board'));
                if (!bs.length) return 3550;
                return Math.min(Math.ceil(Math.max(...bs.map(b =>
                    b.getBoundingClientRect().right))) + 60, 4000);
            }""")
        page.set_viewport_size({"width": w, "height": 900})
        page.goto(board_url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(4)
        hide_duo_banner(page)
        page.screenshot(path=f"{OUT}/41-group-board.png")
        print(f"[OK] 41-group-board（视口 {w}×900）")
        page.set_viewport_size({"width": 1440, "height": 900})

        for fname, url, label in [
            ("42-milestone-progress", f"{GRP_WEB}/milestones/{ms['id']}",
             f"里程碑 930 完成度（id={ms['id']}）"),
            ("43-intake-backlog", f"{INTAKE_WEB}/issues?label_name={q('状态::待受理')}",
             "受理台积压（待受理过滤）"),
        ]:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2.5)
                hide_duo_panel(page)
                hide_duo_banner(page)
                page.screenshot(path=f"{OUT}/{fname}.png")
                print(f"[OK] {fname} — {label}")
            except Exception as e:
                print(f"[FAIL] {fname}: {str(e)[:140]}")
        ctx.close()
        browser.close()

    print(f"[done] 提单 {len(filed)}/3，证据落 {OUT}")
    return 0 if len(filed) == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
