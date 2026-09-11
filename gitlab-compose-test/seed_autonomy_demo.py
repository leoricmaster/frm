#!/usr/bin/env python3
"""autonomy/perception 示例状态（2026-09-11，developer.html 教程换自动装车示例）。

在既有组树上补算法域演示态（G 段只建了仓库+main 流水线，MR/单据侧是空的）：
  1. dev1/maint1 进 perception 项目（Developer/Maintainer，镜像 B 段 firmware 项目成员）
  2. perception 加 .gitlab/merge_request_templates/默认.md（四项自查，同 firmware 终版）
  3. 组里程碑「算法 v0.1·三阶段原型」
  4. intake 提【需求】自动装车对位单 → transfer 进 perception（需求流 §4 分诊转入）
  5. 分支 feat/load-align：train.py 装车对位置信度阈值 0.85→0.80
  6. MR 开着不合（教程停在"等 Owner 合入"），Closes #单号 + 里程碑，流水线等绿

用法: python3 seed_autonomy_demo.py（root token；幂等：已存在即跳过）

辅助函数照抄 rebuild_jh_state.py（那边 import 有副作用：读 /tmp harbor secret）。
"""
import base64, json, sys, time, urllib.error, urllib.parse, urllib.request

BASE = "http://127.0.0.1:8081/api/v4"
ROOT_TOK = "glpat-RebuildJH2026TokenProto000001"


def api(method, path, data=None, form=None, raw=False):
    """form: dict → application/x-www-form-urlencoded（中文自动转义）。"""
    body, headers = None, {"PRIVATE-TOKEN": ROOT_TOK}
    if form is not None:
        body = urllib.parse.urlencode(form, doseq=True).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode()
            return r.status, (t if raw else (json.loads(t) if t.strip() else None))
    except urllib.error.HTTPError as e:
        t = e.read().decode()
        try:
            return e.code, json.loads(t)
        except Exception:
            return e.code, t


def commit_files(pid, branch, msg, files, start_branch=None):
    """files: {path: content}；中文路径/内容走 base64 动作，规避 files API 404。"""
    if start_branch and branch != start_branch:  # MR 特性分支幂等：已存在则跳过
        s, _ = api("GET", f"/projects/{pid}/repository/branches/{urllib.parse.quote(branch, safe='')}")
        if s == 200:
            print(f"  [commit跳过] {branch} 已存在")
            return None
    base = start_branch or branch
    actions = []
    for p, c in files.items():
        s, _ = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote(p, safe='')}"
                  f"/raw?ref={urllib.parse.quote(base, safe='')}", raw=True)
        actions.append({"action": "update" if s == 200 else "create", "file_path": p,
                        "encoding": "base64",
                        "content": base64.b64encode(c.encode()).decode()})
    body = {"branch": branch, "commit_message": msg, "actions": actions}
    if start_branch:
        body["start_branch"] = start_branch
    s, d = api("POST", f"/projects/{pid}/repository/commits", data=body)
    if s not in (200, 201):
        raise SystemExit(f"[commit_files 失败] {pid} {branch}: {s} {d}")
    return d["short_id"]


def wait_pipeline(pid, ref, note=""):
    for i in range(120):
        s, d = api("GET", f"/projects/{pid}/pipelines?ref={urllib.parse.quote(ref, safe='')}&per_page=1")
        st = d[0]["status"] if d else "none"
        if st in ("success", "manual", "skipped"):
            print(f"  [pipeline] {ref} → {st} ({d[0]['id'] if d else '-'}) {note}")
            return d[0]["id"] if d else None
        if st in ("failed", "canceled"):
            pl = d[0]["id"]
            _, jobs = api("GET", f"/projects/{pid}/pipelines/{pl}/jobs")
            bad = [j for j in jobs if j["status"] == "failed"]
            log = ""
            if bad:
                _, log = api("GET", f"/projects/{pid}/jobs/{bad[0]['id']}/trace", raw=True)
                log = (log or "")[-600:]
            raise SystemExit(f"[pipeline 红] {ref} #{pl} job={bad[0]['name'] if bad else '?'}\n{log}")
        time.sleep(5)
    raise SystemExit(f"[pipeline 超时] {ref}")

GRP = "intel_excavator"
PCP = f"{GRP}/autonomy/perception"
IAP = f"{GRP}/intake"

MR_TEMPLATE = """## 关联

- 需求/缺陷单：Closes #单号（**需外部验收的单只写 `#单号` 引用**，合入后进 待验证 由验收人关单）

## 变更说明

（做了什么、怎么验证的）

## 合码前自查

- [ ] 关联单号已写（Closes 或引用）
- [ ] 已选定里程碑
- [ ] CI 全绿
- [ ] 自测通过
"""

ISSUE_DESC = """## 背景与目标

自动装车工况下，对位识别置信度阈值 0.85 偏保守：低速贴近卡车阶段误拒率约 12%，
操作员频繁手动接管，自动装车节拍拉长。目标：阈值整定后误拒率降到 5% 以内，
且不引入错装（对位错误直接装车）。

## 验收标准

- [ ] 对位判定阈值可配置，随训练产物输出，manifest 可追溯
- [ ] 回放数据集上误拒率 ≤5%，错装率不劣化
- [ ] 阈值变更走 MR + CI，不在现场改代码

## 来源信息

- 提出方 / 期望版本：整机产品组 / 算法 v0.1"""

TRAIN_V2 = """#!/usr/bin/env python3
\"\"\"原型假训练：读数据集→产"模型权重"。真实 GPU 训练是正式实施项。\"\"\"
import hashlib, json, os, sys

ALIGN_CONF = 0.80  # 装车对位判定阈值 0.85→0.80：低速贴近工况误拒率 -12%（#1）

data_path = sys.argv[1]
with open(data_path, "rb") as f:
    blob = f.read()
print(f"dataset {len(blob)} bytes loaded")

os.makedirs("outputs", exist_ok=True)
weights = hashlib.sha256(blob).digest() + blob[:1024]   # 内容派生的假权重
with open("outputs/model.pt", "wb") as f:
    f.write(weights)
print(json.dumps({"model": "outputs/model.pt", "params": len(weights),
                  "align_conf": ALIGN_CONF}))
"""

MR_DESC = """Closes #1

## 关联

- 需求单：Closes #1（默认路径：合入即自动关单；单由受理台分诊转入本仓）

## 变更说明

- 对位判定阈值 ALIGN_CONF 0.85→0.80，并随训练产物输出 align_conf，manifest 可追溯
- 回放验证：误拒率 12.4%→4.1%，错装率未劣化（本地复跑 train.py，权重 sha256 与 CI 一致）

## 合码前自查

- [x] 关联单号已写（Closes）
- [x] 已选定里程碑（算法 v0.1·三阶段原型）
- [x] CI 全绿
- [x] 自测通过
"""


def pid_of(path):
    s, d = api("GET", "/projects/" + urllib.parse.quote(path, safe=""))
    assert s == 200, f"项目不存在: {path} {d}"
    return d["id"]


def main():
    pcp, iap = pid_of(PCP), pid_of(IAP)

    # 1 项目成员（镜像 firmware：dev=30 / maint=40）
    for user, lvl in (("dev1", 30), ("maint1", 40)):
        s, d = api("POST", f"/projects/{pcp}/members", form={"user_id": _uid(user), "access_level": lvl})
        print(f"[成员] {user}→perception: {s} {'' if s in (200, 201) else d}")

    # 2 MR 模板（main 直加——模板属仓库配置，非特性内容）
    s, _ = api("GET", f"/projects/{pcp}/repository/files/"
              f"{urllib.parse.quote('.gitlab/merge_request_templates/默认.md', safe='')}/raw?ref=main", raw=True)
    if s == 200:
        print("[模板] 已存在，跳过")
    else:
        commit_files(pcp, "main", "feat: MR 模板（四项自查，同固件终版）",
                     {".gitlab/merge_request_templates/默认.md": MR_TEMPLATE})
        print("[模板] 已提交")

    # 3 组里程碑
    s, d = api("GET", f"/groups/{_gid(GRP)}/milestones")
    ms = next((m for m in d if m["title"] == "算法 v0.1·三阶段原型"), None)
    if not ms:
        s, ms = api("POST", f"/groups/{_gid(GRP)}/milestones", form={"title": "算法 v0.1·三阶段原型"})
        print(f"[里程碑] 算法 v0.1·三阶段原型: iid={ms['iid']}")
    else:
        print(f"[里程碑] 已存在 iid={ms['iid']}")

    # 4 intake 单 → transfer 进 perception（分诊转入，同 34-issue-transferred 流）
    s, moved = api("GET", f"/projects/{pcp}/issues")
    iss = next((i for i in moved if "自动装车" in i["title"]), None)
    if iss:
        print(f"[单据] perception#{iss['iid']} 已存在，跳过")
    else:
        s, issues = api("GET", f"/projects/{iap}/issues?search={urllib.parse.quote('自动装车')}")
        iss0 = next((i for i in issues if "自动装车" in i["title"]), None)
        if not iss0:
            s, iss0 = api("POST", f"/projects/{iap}/issues", form={
                "title": "【需求】自动装车对位误拒率偏高", "description": ISSUE_DESC})
            assert s == 201, f"[建单失败] {s} {iss0}"
            print(f"[单据] intake#{iss0['iid']} 已建")
        # 极狐 /transfer 恒 404 → 回退 CE 旧端点 /move?to_project_id=（同 rebuild H 段）
        s, iss = api("POST", f"/projects/{iap}/issues/{iss0['iid']}/transfer",
                     form={"to_project_id": pcp})
        if s not in (200, 201):
            s, iss = api("POST", f"/projects/{iap}/issues/{iss0['iid']}/move?to_project_id={pcp}")
        assert s in (200, 201), f"[transfer 失败] {s} {iss}"
        print(f"[单据] intake#{iss0['iid']} → perception#{iss['iid']} {iss['title']}")

    # 5 特性分支（幂等：已存在跳过）
    commit_files(pcp, "feat/load-align",
                 "feat: 装车对位置信度阈值 0.85→0.80（#1）",
                 {"train.py": TRAIN_V2}, start_branch="main")

    # 6 MR：开着不合，等流水线绿
    s, mrs = api("GET", f"/projects/{pcp}/merge_requests?state=opened")
    if mrs:
        mr = mrs[0]
        print(f"[MR] 已存在 !{mr['iid']} {mr['title']}")
    else:
        s, mr = api("POST", f"/projects/{pcp}/merge_requests", form={
            "source_branch": "feat/load-align", "target_branch": "main",
            "title": "feat: 自动装车对位阈值整定", "description": MR_DESC,
            "milestone_id": ms["id"], "remove_source_branch": "false"})
        assert s == 201, f"[MR 建失败] {s} {mr}"
        print(f"[MR] !{mr['iid']} {mr['title']}（里程碑: {ms['title']}）")
    wait_pipeline(pcp, "feat/load-align", "装车对位 MR")
    print(f"[完成] perception !{mr['iid']} open={mr['state']} 单=perception#{iss['iid']}")


_uid_cache = {}
def _uid(name):
    if name not in _uid_cache:
        s, d = api("GET", f"/users?username={name}")
        assert s == 200 and d, f"用户不存在: {name}"
        _uid_cache[name] = d[0]["id"]
    return _uid_cache[name]


_gid_cache = {}
def _gid(path):
    if path not in _gid_cache:
        s, d = api("GET", "/groups/" + urllib.parse.quote(path, safe=""))
        assert s == 200, f"组不存在: {path}"
        _gid_cache[path] = d["id"]
    return _gid_cache[path]


if __name__ == "__main__":
    main()
