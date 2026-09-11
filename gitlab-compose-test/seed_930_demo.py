#!/usr/bin/env python3
"""种子：里程碑 930 典型数据 + 看板/积压丰富化（root API，幂等）。

为 submitter.html 重拍做准备——42 号里程碑页要有真实完成度（43%，3/7），
41 号组看板、43 号受理台积压要有足够卡片。设计口径：

  里程碑 930（组级，9·30 版本节点）共 7 单：
    关闭 3：N1 台架回归用例(fw) / N2 遥控器指令丢失(fw) / N3 标注小工具(perception)
    开放 4：fw#2 余抖(待验证，存量挂靠) / perception#1 对位误拒(存量挂靠)
            / N4 热加载压测(fw，开发中) / N6 载荷谱可配(fw，已排期)
  3/7 = 43%，与 submitter.html 图注一致。

另两处存量对齐：
  fw#1 液压抖动：线上 opened，但资产 37 拍的是"合入自动关单"——按故事线补关
                （标签同步推进到 开发中，即合入那一刻的状态）。
  受理台 3 张 guest 单由 screenshot_submitter_fix.py 经 UI 提交（root 无 sudo scope，
  无法代提），本脚本不负责；它们由该脚本 Phase B 补 状态::待受理 标签。
"""
import json
import sys
import urllib.parse
import urllib.request

GL = "http://127.0.0.1:8081"
T = "glpat-RebuildJH2026TokenProto000001"
GRP = "intel_excavator"
FW = 5        # intel_excavator/firmware/hydraulic-controller
PERC = 6      # intel_excavator/autonomy/perception
DEV1 = 2      # dev1 用户 id

MS_TITLE = "930"
MS_DESC = "9·30 版本节点——固件 / 算法跨域收口"


def api(path, method="GET", data=None):
    req = urllib.request.Request(f"{GL}/api/v4{path}",
                                 headers={"PRIVATE-TOKEN": T}, method=method)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        r = urllib.request.urlopen(req, body)
        return json.load(r) if r.status != 204 else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()[:200]}") from e


def q(s):
    return urllib.parse.quote(s, safe="")


def find_issue(pid, kw):
    for i in api(f"/projects/{pid}/issues?per_page=100"):
        if kw in i["title"]:
            return i
    return None


def ensure_issue(pid, title, labels, desc, state="opened", assignee=DEV1,
                 created_at=None, ms_id=None):
    """按标题幂等建单；已存在则只对齐 关闭态/里程碑/标签。"""
    ex = find_issue(pid, title)
    if ex:
        print(f"[skip] #{ex['iid']} 已存在: {title}")
        if ms_id:
            attach_ms(ex, ms_id)
        return ex
    params = {"title": title, "description": desc, "labels": ",".join(labels)}
    if assignee:
        params["assignee_ids"] = [assignee]
    if created_at:  # 仅 admin 生效，失败不致命
        try:
            return _create(pid, params, created_at, state, ms_id)
        except RuntimeError as e:
            print(f"[warn] 带时间戳创建失败，退回普通创建: {str(e)[:90]}")
    return _create(pid, params, None, state, ms_id)


def _create(pid, params, created_at, state, ms_id):
    p = dict(params)
    if created_at:
        p["created_at"] = created_at
    if ms_id:
        p["milestone_id"] = ms_id
    it = api(f"/projects/{pid}/issues", "POST", p)
    print(f"[new ] #{it['iid']} ({pid}) {it['title']}  created_at={created_at or 'now'}")
    if state == "closed":
        api(f"/projects/{pid}/issues/{it['iid']}", "PUT", {"state_event": "close"})
        print(f"[close] #{it['iid']}")
    return it


def ensure_milestone():
    for m in api(f"/groups/{GRP}/milestones?per_page=50"):
        if m["title"] == MS_TITLE:
            print(f"[skip] 里程碑已存在 id={m['id']}")
            return m
    m = api(f"/groups/{GRP}/milestones", "POST",
            {"title": MS_TITLE, "description": MS_DESC})
    print(f"[new ] 里程碑 {MS_TITLE} id={m['id']}")
    return m


def attach_ms(issue, ms_id):
    """挂里程碑（issue 仅容一个里程碑，直接覆盖）。"""
    if (issue.get("milestone") or {}).get("id") == ms_id:
        return
    api(f"/projects/{issue['project_id']}/issues/{issue['iid']}", "PUT",
        {"milestone_id": ms_id})
    print(f"[ms  ] #{issue['iid']} -> {MS_TITLE}")


def set_labels(issue, labels):
    if sorted(issue["labels"]) == sorted(labels):
        return
    api(f"/projects/{issue['project_id']}/issues/{issue['iid']}", "PUT",
        {"labels": ",".join(labels)})
    print(f"[lab ] #{issue['iid']} {issue['labels']} -> {labels}")


def main():
    ms = ensure_milestone()

    # ---- 新建 5 单（3 关 2 开）----
    ensure_issue(
        FW, "【任务】抖动参数边界纳入台架回归用例",
        ["来源::内部", "状态::开发中"],
        "液压抖动参数现场可调上线后，把参数边界用例补进台架回归，防现场调参越界。\n\n"
        "## 完成标准\n\n- [x] 边界值表进回归用例集\n- [x] 连跑 3 晚无越界报警",
        state="closed", created_at="2026-08-27T09:30:00Z", ms_id=ms["id"])
    ensure_issue(
        FW, "【缺陷】遥控器配对后偶发指令丢失",
        ["来源::现场", "状态::开发中"],
        "配对完成后前 5 分钟偶发指令丢失 1–2 条，重配对可复现；影响 EXC-2026-013。"
        "定位为配对握手期信道扫描窗口冲突，已修复合入。",
        state="closed", created_at="2026-08-21T14:00:00Z", ms_id=ms["id"])
    ensure_issue(
        PERC, "【任务】对位误拒样本回流标注小工具",
        ["来源::内部", "状态::开发中"],
        "现场误拒样本手工归档太散，做一个小工具把误拒帧按 manifest 批量打标回流训练集。\n\n"
        "## 完成标准\n\n- [x] 支持 manifest 批次导入\n- [x] 标注结果直连训练集目录结构",
        state="closed", created_at="2026-08-15T10:00:00Z", ms_id=ms["id"])
    ensure_issue(
        FW, "【任务】配置文件热加载 72h 压测",
        ["来源::内部", "状态::开发中"],
        "热加载合入后补一轮 72h 长稳压测，覆盖现场改参频率上限场景。",
        state="opened", created_at="2026-09-03T11:00:00Z", ms_id=ms["id"])
    ensure_issue(
        FW, "【需求】铲斗载荷谱采集频率开放可配",
        ["来源::客户", "状态::已排期"],
        "载荷谱采集频率当前写死 50Hz，大客户工况采集要 100Hz。\n\n"
        "## 验收标准\n\n- [ ] 采集频率 10–200Hz 现场可配\n- [ ] 配置项进 manifest",
        state="opened", created_at="2026-09-08T15:00:00Z", ms_id=ms["id"])

    # ---- 存量挂靠 / 对齐 ----
    fw2 = find_issue(FW, "余抖")
    if fw2:
        attach_ms(fw2, ms["id"])
        set_labels(fw2, ["来源::现场", "状态::待验证"])
        api(f"/projects/{FW}/issues/{fw2['iid']}", "PUT",
            {"assignee_ids": [DEV1]}) if not fw2["assignees"] else None

    perc1 = find_issue(PERC, "对位误拒率偏高")
    if perc1:
        attach_ms(perc1, ms["id"])
        set_labels(perc1, ["来源::现场", "状态::开发中"])
        if not perc1["assignees"]:
            api(f"/projects/{PERC}/issues/{perc1['iid']}", "PUT",
                {"assignee_ids": [DEV1]})
            print(f"[asg ] perception#{perc1['iid']} -> dev1")

    fw1 = find_issue(FW, "液压抖动")
    if fw1 and fw1["state"] == "opened":
        set_labels(fw1, ["来源::市场", "状态::开发中"])
        api(f"/projects/{FW}/issues/{fw1['iid']}", "PUT",
            {"state_event": "close"})
        print(f"[close] fw#{fw1['iid']} 液压抖动——对齐资产 37 合入自动关单故事线")

    # ---- 核对 ----
    print("\n== 930 里程碑核对 ==")
    ms_issues = [i for pid in (FW, PERC) for i in api(
        f"/projects/{pid}/issues?per_page=100")
        if (i.get("milestone") or {}).get("title") == MS_TITLE]
    op = sum(1 for i in ms_issues if i["state"] == "opened")
    cl = len(ms_issues) - op
    print(f"  {MS_TITLE}: {op} 开放 / {cl} 关闭 = {round(100*cl/len(ms_issues))}%（目标 3/7=43%）")
    backlog = [i for i in api("/projects/7/issues?per_page=100")
               if i["state"] == "opened" and "状态::待受理" in i["labels"]]
    print(f"  受理台待受理积压: {len(backlog)} 单（guest 3 单入队后应为 4）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
