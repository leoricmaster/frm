#!/usr/bin/env python3
"""三阶段截图：需求流四场景证据（受理台/分诊/正向全链/反向追溯/看板）。

复用一二阶段模式：chromium at /usr/bin/google-chrome，viewport 1440×900（41 号看板例外，见下）。
单张重试：`.venv/bin/python screenshot_phase3.py 33 41` 只重拍编号前缀匹配的页。

2026-09-03 现场探测适配（GitLab 19.3.1）：
  1. URL 形态：Web UI 不认 /projects/<path%2Fname>/… 与 /projects/<id>/… 形态（404），
     全部改用 canonical web 路径（/intel_excavator/intake/-/…、/intel_excavator/firmware/hydraulic-controller/-/…）。
     /issues/new 与 /issues 列表会 302 到 work_items 路由（19.x 正常行为），目标页面正常渲染。
  2. 组看板懒创建 + 超宽全景：GET /groups/2/boards 首查为空，浏览器访问 /groups/intel_excavator/-/boards
     后才生成默认板（id=1，"Development"）；Step 1 已在该板加 6 个状态列。列宽固定 400px，
     Open+6 状态列+Closed 全景约 3500px——41 号按实测宽度临时放大视口后截图，其余保持 1440×900。
  3. 32 号模板表单：?issuable_template=需求 正常预填；编辑器是 tiptap 富文本（DOM 无 textarea，
     模板内容在 [contenteditable] 内，模板下拉显示"需求"）。
  4. 滚动定位：33/34/35/36/38/39 用 scroll_to_text 把分诊/打回/婉拒评论、自查 checklist、
     manifest 资产、manifest 粘贴区滚入视口（block=center，取含标记文本的最内层元素）。
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright
from shot_utils import hide_duo_banner

OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GL = "http://127.0.0.1:8081"
T = "glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg"

INTAKE_WEB = f"{GL}/intel_excavator/intake/-"
FW_WEB = f"{GL}/intel_excavator/firmware/hydraulic-controller/-"
GRP_WEB = f"{GL}/groups/intel_excavator/-"


def api(path):
    req = urllib.request.Request(f"{GL}/api/v4{path}", headers={"PRIVATE-TOKEN": T})
    return json.load(urllib.request.urlopen(req))


def q(s):  # URL-encode 中文/:: 标签名
    return urllib.parse.quote(s, safe="")


# ---- 动态 id（API 实查，不硬编码）----
IA = next(i["iid"] for i in api("/projects/2/issues?per_page=100") if "液压抖动" in i["title"])
MR = next(m for m in api("/projects/2/merge_requests?per_page=20")
          if m["state"] == "merged" and "液压抖动" in m["title"])
MRI, SHA = MR["iid"], MR["merge_commit_sha"]
MS = api("/groups/2/milestones")[0]["id"]
IB = next(i["iid"] for i in api("/projects/2/issues?per_page=100") if "余抖" in i["title"])
BOARD = api("/groups/2/boards")[0]
print(f"[info] IA(需求单)=#{IA}  MR=!{MRI} sha={SHA[:8]}…  MS(里程碑)={MS}  IB(缺陷单)=#{IB}")
print(f"[info] board id={BOARD['id']} name={BOARD['name']!r} labels={[l['label']['name'] for l in BOARD['lists']]}")

# (文件名, URL, 标签说明, 滚动标记或 None)
PAGES = [
    ("32-intake-template-form", f"{INTAKE_WEB}/issues/new?issuable_template=" + q("需求"),
     "受理台需求模板表单", "背景与目标"),
    ("33-intake-issue-filed", f"{INTAKE_WEB}/issues/2",
     "打回单（分诊评论+待受理）", "打回："),
    ("34-issue-transferred", f"{FW_WEB}/issues/{IA}",
     "移交后的需求单（已排期+里程碑+分诊评论）", "分诊：固件域受理"),
    ("35-issue-rejected", f"{INTAKE_WEB}/issues/3",
     "婉拒单（已拒绝+理由）", "婉拒"),
    ("36-mr-closes-issue", f"{FW_WEB}/merge_requests/{MRI}",
     "MR：Closes #+里程碑+自查checklist", "合码前自查"),
    # 37 与 34 同单：34 滚到分诊评论（展示已排期+里程碑+Closed 徽章），37 滚到底部
    # 系统注记（mentioned in commit a20d1a80 / closed with merge request !5）——
    # 页面高度放不下标题区+全部注记，按简报"merged 引用"要求取底部注记区。
    ("37-issue-auto-closed", f"{FW_WEB}/issues/{IA}",
     "合入后自动关单（Closed+merged引用）", "a20d1a80"),
    ("38-release-milestone", f"{FW_WEB}/releases/v0.9.0-rc1",
     "Release（v0.9.0-rc1+manifest 资产）", "manifest.json"),
    ("39-defect-manifest", f"{FW_WEB}/issues/{IB}",
     "缺陷单：manifest粘贴区", "机器版本"),
    ("40-reverse-commit", f"{FW_WEB}/commit/{SHA}",
     "commit页：MR关联（反向第②跳）", None),
    ("41-group-board", f"{GRP_WEB}/boards",
     "组看板：状态列全景", None),
    ("42-milestone-progress", f"{GRP_WEB}/milestones/{MS}",
     "里程碑完成度+版本内清单", None),
    ("43-intake-backlog", f"{INTAKE_WEB}/issues?label_name=" + q("状态::待受理"),
     "受理台积压视图（待受理过滤）", None),
]


def scroll_to_text(page, marker):
    """把含标记文本的最内层元素滚到视口中部（长元素按最内层小元素命中）。"""
    try:
        page.evaluate(
            """([m]) => {
                const els = Array.from(document.querySelectorAll('div,p,li,td,pre,code,h1,h2,h3,h4'));
                const hits = els.filter(e => (e.innerText || '').includes(m)
                                            && (e.innerText || '').length < 2000);
                if (hits.length) hits[hits.length - 1].scrollIntoView({block: 'center'});
            }""", [marker])
        time.sleep(0.8)
    except Exception as e:
        print(f"  [warn] scroll_to_text({marker!r}): {str(e)[:70]}")


def board_width(page):
    """实测看板全景宽度（Open+6状态列+Closed 各 400px + 左导航）。"""
    try:
        return page.evaluate(
            """() => {
                const bs = Array.from(document.querySelectorAll('.board'));
                if (!bs.length) return 3550;
                const right = Math.max(...bs.map(b => b.getBoundingClientRect().right));
                return Math.min(Math.ceil(right) + 60, 4000);
            }""")
    except Exception:
        return 3550


def shot(page, fname, url, label, marker=None, sleep=2.0):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(sleep)
        if marker:
            scroll_to_text(page, marker)
        hide_duo_banner(page)
        page.screenshot(path=f"{OUT}/{fname}.png")
        print(f"[OK] {fname} — {label}")
        return True
    except Exception as e:
        print(f"[FAIL] {fname} — {label}: {str(e)[:110]}")
        return False


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    pages = [p for p in PAGES if not only or any(p[0].startswith(o) for o in only)]
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
        page.fill("input[name='user[login]']", "root")
        page.fill("input[name='user[password]']", "Excavator#2026Proto")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        print(f"[info] login ok, landed on {page.url}")

        for fname, url, label, marker in pages:
            if fname.startswith("41-"):  # 看板全景：先量宽再放大视口
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(4)
                w = board_width(page)
                print(f"[info] board panorama width -> {w}px viewport")
                page.set_viewport_size({"width": w, "height": 900})
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(4)
                try:
                    hide_duo_banner(page)
                    page.screenshot(path=f"{OUT}/{fname}.png")
                    print(f"[OK] {fname} — {label}（视口 {w}×900）")
                except Exception as e:
                    print(f"[FAIL] {fname} — {label}: {str(e)[:110]}")
                page.set_viewport_size({"width": 1440, "height": 900})
            else:
                shot(page, fname, url, label, marker)

        ctx.close()
        browser.close()
    print("[done] phase3 截图结束")


if __name__ == "__main__":
    main()
