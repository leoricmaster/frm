#!/usr/bin/env python3
"""极狐实例全量重拍（中文界面）——GitLab 侧 01-25、32-43，共 37 张。

26-31 为 Harbor/MinIO 控制台截图，与 GitLab 实例无关，沿用原文件不重拍。
所有动态对象（流水线/job/MR iid/单据 iid/里程碑 id）一律 API 解析，不写死。
看板（41）：先以浏览器访问组看板页触发懒创建，再 API 补六状态列（等价
rebuild_jh_state.py I 段），最后用宽视口截全景。

前置：rebuild_jh_state.py B-H 已跑完（5 MR / 2 tag / 2 Release / intake 四单）。
"""
import json, pathlib, sys, time, urllib.parse, urllib.request
from playwright.sync_api import sync_playwright
from shot_utils import hide_duo_banner

GL = "http://127.0.0.1:8081"
API = GL + "/api/v4"
TOK = "glpat-RebuildJH2026TokenProto000001"
OUT = pathlib.Path(__file__).resolve().parent / "screenshots"
ROOT_PW = "Excavator#2026Proto"
GUEST_PW = "Xc7$wB3n!Tq8"
FWP, PCP, IAP, TPLP = ("intel_excavator/firmware/hydraulic-controller",
                       "intel_excavator/autonomy/perception",
                       "intel_excavator/intake",
                       "intel_excavator/platform/ci-templates")
GRP = "intel_excavator"

def api(path):
    req = urllib.request.Request(API + path, headers={"PRIVATE-TOKEN": TOK})
    return json.load(urllib.request.urlopen(req))

def q(s):
    return urllib.parse.quote(s, safe="")

def pidof(path):
    return api("/projects/" + q(path))["id"]

def login(page, user, pw):
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", user)
    page.fill("input[name='user[password]']", pw)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

def shot(page, name, url, label, wait=1.8):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(wait)
        hide_duo_banner(page)
        page.screenshot(path=str(OUT / f"{name}.png"))
        print(f"[OK] {name} — {label}  <{page.title()}>")
    except Exception as e:
        print(f"[FAIL] {name}: {str(e)[:110]}")

def resolve():
    fw, pc, iap = pidof(FWP), pidof(PCP), pidof(IAP)
    mr = {m["source_branch"]: m for m in api(f"/projects/{fw}/merge_requests?per_page=20")}
    need = ("feature/smoke-mr", "feature/test-branch", "fix/extends-template",
            "field/hotfix-pressure-sensor", "feat/hydro-tuning")
    missing = [b for b in need if b not in mr]
    if missing:
        raise SystemExit(f"[前置不足] 缺 MR 分支: {missing}——先跑完 rebuild_jh_state.py B-H")
    pls = api(f"/projects/{fw}/pipelines?per_page=60")
    d = {"fw": fw, "pc": pc, "iap": iap,
         "mr1": mr["feature/smoke-mr"]["iid"], "mr2": mr["feature/test-branch"]["iid"],
         "mr4": mr["field/hotfix-pressure-sensor"]["iid"], "mr5": mr["feat/hydro-tuning"]["iid"],
         "sha5": mr["feat/hydro-tuning"]["merge_commit_sha"],
         "main_green": next(p["id"] for p in pls if p["ref"] == "main" and p["status"] == "success"),
         "latest_main": next(p["id"] for p in pls if p["ref"] == "main"),
         "tag_field": next(p["id"] for p in pls if p["ref"] == "v0.2.0-field"),
         "tag_rc1": next(p["id"] for p in pls if p["ref"] == "v0.9.0-rc1")}
    jobs = api(f"/projects/{fw}/pipelines/{d['latest_main']}/jobs")
    d["job_bf"] = next(j["id"] for j in jobs if j["name"] == "build-firmware")
    d["job_ib"] = next(j["id"] for j in jobs if j["name"] == "image-build")
    pl = api(f"/projects/{pc}/pipelines?per_page=5")[0]["id"]
    pj = {j["name"]: j["id"] for j in api(f"/projects/{pc}/pipelines/{pl}/jobs")}
    d["pcp"] = pl
    d["job_fetch"] = pj.get("fetch-dataset")
    d["job_train"] = pj.get("train-model")
    iss = api(f"/projects/{fw}/issues?per_page=20")
    d["ia"] = next(i["iid"] for i in iss if "液压抖动" in i["title"])
    d["ib"] = next(i["iid"] for i in iss if "余抖" in i["title"])
    d["ms"] = api(f"/groups/{q(GRP)}/milestones")[0]["id"]
    return d

def board_lists(page):
    """浏览器访问触发看板懒创建 + API 补六状态列（幂等）。"""
    page.goto(f"{GL}/groups/{GRP}/-/boards", wait_until="domcontentloaded")
    time.sleep(3)
    gid = api(f"/groups/{q(GRP)}")["id"]
    bid = api(f"/groups/{gid}/boards")[0]["id"]
    labels = {l["name"]: l["id"] for l in api(f"/groups/{gid}/labels?per_page=50")}
    have = {x["label"]["name"] for x in api(f"/groups/{gid}/boards/{bid}/lists") if x.get("label")}
    for w in ("状态::待受理", "状态::已排期", "状态::开发中", "状态::待验证", "状态::暂缓", "状态::已拒绝"):
        if w not in have:
            req = urllib.request.Request(
                API + f"/groups/{gid}/boards/{bid}/lists",
                data=urllib.parse.urlencode({"label_id": labels[w]}).encode(),
                headers={"PRIVATE-TOKEN": TOK,
                         "Content-Type": "application/x-www-form-urlencoded"}, method="POST")
            urllib.request.urlopen(req)
            print(f"  [board] +列 {w}")

def main():
    d = resolve()
    print(f"[解析] fw={d['fw']} pc={d['pc']} intake={d['iap']} MR !{d['mr1']}/!{d['mr2']}/!{d['mr4']}/!{d['mr5']} "
          f"IA=#{d['ia']} IB=#{d['ib']} ms={d['ms']} pipelines main#{d['latest_main']} "
          f"tag#{d['tag_field']}/#{d['tag_rc1']}")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")

        # ── root 主上下文（1440×900）──
        # locale=zh-CN：未登录页（登录页）按 Accept-Language 协商，默认 en 会出英文
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True,
                                  locale="zh-CN")
        page = ctx.new_page()
        shot(page, "01-login", f"{GL}/users/sign_in", "登录页", wait=1.2)
        login(page, "root", ROOT_PW)
        P = [
            ("02-dashboard",   f"{GL}/",                                                         "主面板"),
            ("03-groups",      f"{GL}/groups/{GRP}/firmware",                                    "组列表（firmware 域）"),
            # 极狐坑位：/-/subgroups 路由 404 → 顶层组概览页即子组列表（带描述）
            ("04-group-tree",  f"{GL}/groups/{GRP}",                                             "子组列表（六域）"),
            ("05-project",     f"{GL}/{FWP}",                                                    "示例项目"),
            ("06-pipelines",   f"{GL}/{FWP}/-/pipelines",                                        "流水线列表"),
            ("07-ci-success",  f"{GL}/{FWP}/-/pipelines/{d['main_green']}",                      "流水线详情（全绿）"),
            ("08-mr-list",     f"{GL}/{FWP}/-/merge_requests",                                   "MR 列表"),
            ("09-mr-closed",   f"{GL}/{FWP}/-/merge_requests/{d['mr1']}",                        "MR !1（已合入）"),
            ("10-protect",     f"{GL}/{FWP}/-/settings/repository",                              "保护分支设置"),
            ("11-ci-templates", f"{GL}/{TPLP}",                                                  "CI 模板仓库（宪法）"),
            ("12-members",     f"{GL}/{FWP}/-/project_members",                                  "项目成员与权限"),
            ("13-packages",    f"{GL}/{FWP}/-/packages",                                         "包仓库"),
            ("14-mr2-merged",  f"{GL}/{FWP}/-/merge_requests/{d['mr2']}",                        "MR !2（已合入+批准记录）"),
            ("15-mr2-changes", f"{GL}/{FWP}/-/merge_requests/{d['mr2']}/diffs",                  "MR !2 变更页"),
            ("16-release",     f"{GL}/{FWP}/-/releases/v0.2.0-field",                            "Release v0.2.0-field"),
            ("17-pipeline14",  f"{GL}/{FWP}/-/pipelines/{d['tag_rc1']}",                         "tag 流水线（promote-release ⏸ 手动）"),
            ("17-pipeline19",  f"{GL}/{FWP}/-/pipelines/{d['tag_field']}",                       "v0.2.0-field tag 流水线"),
            ("18-job18-trace", f"{GL}/{FWP}/-/jobs/{d['job_bf']}",                               "build job Trace（extends 模板传播）"),
            ("19-ci-mr",       f"{GL}/{TPLP}/-/merge_requests/2",                                "宪法 MR（伪构建兼容）"),
            ("20-mr4-field",   f"{GL}/{FWP}/-/merge_requests/{d['mr4']}",                        "应急补单 MR"),
            ("21-perception-pipelines", f"{GL}/{PCP}/-/pipelines",                               "perception 流水线"),
            ("22-perception-green",     f"{GL}/{PCP}/-/pipelines/{d['pcp']}",                    "perception 流水线全绿"),
            ("23-fetch-dataset-job",    f"{GL}/{PCP}/-/jobs/{d['job_fetch']}",                   "fetch-dataset（MinIO+masked）"),
            ("24-train-model-job",      f"{GL}/{PCP}/-/jobs/{d['job_train']}",                   "train-model（权重入库）"),
            ("25-fw-image-build-job",   f"{GL}/{FWP}/-/jobs/{d['job_ib']}",                       "image-build（Harbor 推拉）"),
            ("32-intake-template-form", f"{GL}/{IAP}/-/issues/new?issuable_template=" + q("需求"), "受理台需求模板表单", 2.4),
            ("33-intake-issue-filed",   f"{GL}/{IAP}/-/issues/2",                                "打回单（待受理+分诊评论）"),
            ("34-issue-transferred",    f"{GL}/{FWP}/-/issues/{d['ia']}",                        "移交后需求单（已排期+里程碑）"),
            ("35-issue-rejected",       f"{GL}/{IAP}/-/issues/3",                                "婉拒单（已拒绝+理由）"),
            ("36-mr-closes-issue",      f"{GL}/{FWP}/-/merge_requests/{d['mr5']}",               "MR !5（Closes+里程碑+自查）"),
            ("37-issue-auto-closed",    f"{GL}/{FWP}/-/issues/{d['ia']}",                        "合入后自动关单"),
            ("38-release-milestone",    f"{GL}/{FWP}/-/releases/v0.9.0-rc1",                     "Release rc1（manifest 资产）"),
            ("39-defect-manifest",      f"{GL}/{FWP}/-/issues/{d['ib']}",                        "缺陷单（manifest 粘贴+定位）"),
            ("40-reverse-commit",       f"{GL}/{FWP}/-/commit/{d['sha5']}",                      "commit 页（反向追溯第②跳）"),
            ("42-milestone-progress",   f"{GL}/groups/{GRP}/-/milestones/{d['ms']}",             "里程碑完成度"),
            ("43-intake-backlog",       f"{GL}/{IAP}/-/issues?label_name=" + q("状态::待受理"),   "受理台积压视图"),
        ]
        # 跳过 job ID 为 None 的截图（perception 流水线可能不含 fetch/train 阶段）
        P = [row for row in P if "/jobs/None" not in str(row[1])]
        for row in P:
            shot(page, *row)
        board_lists(page)  # 看板懒创建 + 六状态列（补齐 I 段）
        ctx.close()

        # ── guest1 视角 ──
        gctx = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=True,
                                   locale="zh-CN")
        gpage = gctx.new_page()
        login(gpage, "guest1", GUEST_PW)
        shot(gpage, "05-project-guest", f"{GL}/{FWP}", "Guest 视角项目主页")
        gctx.close()

        # ── 宽视口看板全景（8 列 ≈ 开放中+六状态+已关闭，实测 4400 才 scrollW==clientW）──
        wctx = browser.new_context(viewport={"width": 4400, "height": 950}, ignore_https_errors=True,
                                   locale="zh-CN")
        wpage = wctx.new_page()
        login(wpage, "root", ROOT_PW)
        shot(wpage, "41-group-board", f"{GL}/groups/{GRP}/-/boards", "组看板（六状态列全景）", wait=3)
        wctx.close()
        browser.close()
    ok = len(list(OUT.glob("*.png")))
    print(f"[done] screenshots 目录现有 {ok} 个 png")

if __name__ == "__main__":
    main()
