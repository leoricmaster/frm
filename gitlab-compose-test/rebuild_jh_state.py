#!/usr/bin/env python3
"""极狐GitLab 原型状态重建驱动（2026-09-09，配合 intel_excavator 组名迁移）。

从 gitlab-compose-test/*-repo/ 留档镜像复刻组树/用户/仓库/MR/tag/Release/单据，
复现旧实例（GitLab CE 19.3.1）终态。用法:

    python3 rebuild_jh_state.py A|B|C|D|E|F|G|H|I|J|Z

  A 用户+组树+platform成员+ci-templates(含宪法MR !1/!2)
  B firmware 项目+成员+保护分支+CI v1
  C firmware MR !1/!2 + tag v0.2.0-field + Release
  D firmware MR !3/!4
  E HARBOR_* 组变量 + CI 演进到终版 + MR 模板
  F firmware MR !5(液压抖动) + tag v0.9.0-rc1 + Release
  G perception 仓库 + MINIO_* 变量 + 流水线
  H intake + 11标签 + 里程碑 + 四单分诊
  I 组看板六状态列（需先浏览器访问过看板页）
  J 全员中文 + 吊销模拟 PAT + 终态核对
  Z 吊销模拟 PAT（收尾单独跑）

状态落盘 /tmp/jh-rebuild-state.json；API 按留档进度.md 记录的坑位规避：
/repository/files 恒 404 → 一律走 Commits API；merge 必带 sha；标签不做 ?name= 过滤。
"""
import base64, json, pathlib, sys, time, urllib.error, urllib.parse, urllib.request

BASE = "http://127.0.0.1:8081/api/v4"
WEB = "http://10.66.35.35:8081"
ROOT_TOK = "glpat-RebuildJH2026TokenProto000001"
STATE_F = pathlib.Path("/tmp/jh-rebuild-state.json")
MIRROR = pathlib.Path(__file__).resolve().parent
HARBOR_SEC = pathlib.Path("/tmp/harbor-robot-secret.txt").read_text().strip()

USERS = {  # 极狐密码策略禁常用词，改强随机（仅本脚本与截图脚本引用）
    "dev1":   {"name": "dev1",   "pwd": "Kq9$vE2m!Rz7"},
    "maint1": {"name": "maint1", "pwd": "Wn4$kJ8p!Ue3"},
    "guest1": {"name": "guest1", "pwd": "Xc7$wB3n!Tq8"},
    "plat1":  {"name": "plat1",  "pwd": "Bt6$rA5c!Yo9"},
}

# ── ci-templates 内容（宪法仓库无留档镜像，内容自 transcript 恢复）──
TPL = {}
TPL["autonomy.yml"] = """\
.algo-template:
  stage: build
  image: ${CI_REGISTRY}/algo/cuda:latest
  tags: [gpu]
  script:
    - echo "[algo-template] 模型训练与评测 ${CI_PROJECT_NAME}"
    - python train.py --data ${DATASET_PATH}
    - python eval.py --model outputs/model.pt --threshold 0.85
  artifacts:
    paths:
      - outputs/model.pt
      - eval_report.json
"""
TPL["vehicle.yml"] = """\
.vehicle-template:
  stage: build
  image: ${CI_REGISTRY}/vehicle/qt:latest
  script:
    - echo "[vehicle-template] 车载C++/Qt构建 ${CI_PROJECT_NAME}"
    - cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j
    - cpack -G DEB -B build
  artifacts:
    paths:
      - build/*.deb
"""
TPL["cloud.yml"] = """\
.cloud-template:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - echo "[cloud-template] 云端构建部署 ${CI_PROJECT_NAME}"
    - docker build -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA::8} .
    - docker push ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA::0:8}
  tags: [deploy]
"""
# phase-1 终版（去掉 image 适配 shell executor）；宪法 MR !1/!2 再演进出终版
FW_TPL_V1 = """\
.firmware-template:
  stage: build
  variables:
    CROSS_COMPILE: arm-noneeabi-
    BUILD_TYPE: release
  script:
    - echo "[firmware-template] 交叉编译 ${CI_PROJECT_NAME}"
    - make ${BUILD_TYPE}
    - ./scripts/sign_firmware.sh build/*.bin || echo "sign skipped (proto)"
  artifacts:
    paths:
      - build/*.bin
      - manifest.json
"""
def fw_tpl_v2():  # 宪法 MR !1 后：+ 产物非空校验
    return FW_TPL_V1.replace(
        '    - ./scripts/sign_firmware.sh build/*.bin || echo "sign skipped (proto)"\n',
        '    - ./scripts/sign_firmware.sh build/*.bin || echo "sign skipped (proto)"\n'
        '    - test -s build/*.bin || (echo "产物为空，禁止发布" && exit 1)\n')
def fw_tpl_final():  # 宪法 MR !2 后：无 Makefile 伪构建（= 旧实例终态）
    return fw_tpl_v2().replace(
        '    - make ${BUILD_TYPE}\n',
        '    - if [ -f Makefile ]; then make ${BUILD_TYPE}; else echo "[firmware-template] 无Makefile，伪构建(原型)"; fi\n')

# firmware 仓库 .gitlab-ci.yml 演进（v1 = phase-1 自写 script；终版 = 留档镜像）
FW_CI_V1 = """\
# 仓库层：include 通用层（§6.2 三层模型）
include:
  - project: intel_excavator/platform/ci-templates
    ref: main
    file: firmware.yml

stages:
  - scan
  - build

gitleaks-check:
  stage: scan
  script:
    - echo "gitleaks密钥扫描占位(§6.5)"
  only:
    - merge_requests

build-firmware:
  stage: build
  variables:
    CROSS_COMPILE: arm-noneeabi-
  before_script:
    - mkdir -p build scripts
    - echo "firmware-binary" > build/hydraulic-controller.bin
    - echo '#!/bin/sh' > scripts/sign_firmware.sh
    - echo 'echo "proto-sign $1"' >> scripts/sign_firmware.sh
    - chmod +x scripts/sign_firmware.sh
    - printf '{"name":"hydraulic-controller","commit":"%s","branch":"%s","build_time":"%s","runner":"%s"}\\n' "$CI_COMMIT_SHA" "$CI_COMMIT_BRANCH" "$CI_JOB_STARTED_AT" "$CI_RUNNER_DESCRIPTION" > manifest.json
  script:
    - echo "[build] 伪构建 ${CI_PROJECT_NAME}（原型）"
    - ./scripts/sign_firmware.sh build/*.bin || echo "sign skipped (proto)"
  artifacts:
    paths:
      - build/*.bin
      - manifest.json
"""
def fw_ci_extends():  # D 段：build-firmware 改 extends（v1 其余不动，build-firmware 块 = 终版镜像同款）
    final = (MIRROR / "firmware-repo/.gitlab-ci.yml").read_text()
    bf = final[final.index("build-firmware:"):final.index("# 二阶段")].rstrip() + "\n"
    return FW_CI_V1[:FW_CI_V1.index("build-firmware:")] + bf

def fw_ci_v2():  # phase-2：+ image-build（尚无 only —— 留给 E 段演进）
    return fw_ci_extends().replace(
        "stages:\n  - scan\n  - build\n",
        "stages:\n  - scan\n  - build\n  - image\n") + """
# 二阶段：镜像出口收敛（§5.3）——CI 构建镜像推内网 Harbor，不直连外网
image-build:
  stage: image
  script:
    - echo "[image] 构建并推送 CI 基础镜像到 Harbor frm-ci 项目"
    - export DOCKER_HOST=unix:///var/run/docker.sock
    - printf 'FROM docker.m.daocloud.io/library/alpine:latest\\nLABEL org.opencontainers.image.revision=%s\\n' "$CI_COMMIT_SHA" > Dockerfile.ci
    - docker build -t "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" -f Dockerfile.ci .
    - echo "$HARBOR_PASS" | docker login "$HARBOR_REGISTRY" -u "$HARBOR_USER" --password-stdin
    - docker push "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"
    - docker rmi "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" || true
    # 从 Harbor 拉回验证（runner 一律走 Harbor §5.3）
    - docker pull "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"
"""

LABELS = [  # (名称, 颜色, 描述) —— 与旧实例逐字一致
    ("状态::待受理", "#808080", "新单进受理台，等分诊"),
    ("状态::已排期", "#1F75CB", "进版本里程碑，域 Owner 已排期"),
    ("状态::开发中", "#FC9403", "特性分支/MR 在途"),
    ("状态::待验证", "#6E49CB", "已合入，等外部验收（台架/现场/提出方）"),
    ("状态::暂缓",   "#8F8F00", "本版本不做，恢复时回已排期"),
    ("状态::已拒绝", "#C0392B", "分诊婉拒（重复/超范围），关闭留痕"),
    ("来源::集团", "#0033CC", "集团下达/集团平台要求"),
    ("来源::市场", "#00867D", "市场/销售代客户提出"),
    ("来源::客户", "#8E24AA", "客户直接提出"),
    ("来源::现场", "#D14438", "驻场/售后反馈（缺陷单为主）"),
    ("来源::内部", "#4C7E00", "团队自提技术需求"),
]

# ── 基础设施 ─────────────────────────────────────────────
def load():
    return json.loads(STATE_F.read_text()) if STATE_F.exists() else {}

def save(st):
    STATE_F.write_text(json.dumps(st, ensure_ascii=False, indent=1))

def api(method, path, token=None, data=None, form=None, raw=False):
    """form: dict → application/x-www-form-urlencoded（中文自动转义）。"""
    body, headers = None, {"PRIVATE-TOKEN": token or ROOT_TOK}
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

def tok(user):
    return ROOT_TOK if user == "root" else load()["pats"][user]

def commit_files(pid, user, branch, msg, files, start_branch=None):
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
    s, d = api("POST", f"/projects/{pid}/repository/commits", tok(user), body)
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

def mr_create_merge(pid, user, src, title, desc=None, merger=None):
    form = {"source_branch": src, "target_branch": "main", "title": title,
            "remove_source_branch": "true"}
    if desc:
        form["description"] = desc
    s, d = api("POST", f"/projects/{pid}/merge_requests", tok(user), form=form)
    if s != 201:
        raise SystemExit(f"[MR 建失败] {src}: {s} {d}")
    iid = d["iid"]
    for i in range(24):  # 等 head 流水线出结果再合（保持截图证据全绿）
        s, ps = api("GET", f"/projects/{pid}/merge_requests/{iid}/pipelines?per_page=1")
        st = ps[0]["status"] if ps else "none"
        if st == "failed":
            raise SystemExit(f"[MR !{iid} 流水线红] {ps}")
        if st in ("success", "skipped", "manual"):
            break
        time.sleep(5)
    for i in range(24):
        s, m = api("GET", f"/projects/{pid}/merge_requests/{iid}", tok(user))
        if m.get("merge_status") == "can_be_merged":
            break
        time.sleep(4)
    sha = m["diff_refs"]["head_sha"]
    # 合入人独立于建单人（保护分支 main 仅 Maintainer 可合——旧实例 dev1 建 / maint1 合）
    for i in range(8):
        s, r = api("PUT", f"/projects/{pid}/merge_requests/{iid}/merge?sha={sha}", tok(merger or user))
        if s == 200 and r.get("state") == "merged":
            print(f"  [MR] !{iid} {title} → merged ({r['merge_commit_sha'][:8]})")
            return iid, r["merge_commit_sha"]
        time.sleep(4)
    raise SystemExit(f"[MR 合失败] !{iid}: {s} {r}")

def find_group(st, path):
    s, d = api("GET", "/groups/" + urllib.parse.quote(path, safe=""))
    return d["id"] if s == 200 else None

def find_project(st, path):
    s, d = api("GET", "/projects/" + urllib.parse.quote(path, safe=""))
    return d["id"] if s == 200 else None

def transfer_issue(src_pid, iid, to_pid):
    """极狐 /transfer 恒 404 → 回退 CE 旧端点 /move?to_project_id=。"""
    s, d = api("POST", f"/projects/{src_pid}/issues/{iid}/transfer", form={"to_project_id": to_pid})
    if s not in (200, 201):
        s, d = api("POST", f"/projects/{src_pid}/issues/{iid}/move?to_project_id={to_pid}")
    if s not in (200, 201):
        raise SystemExit(f"[移交失败] issue {iid}: {s} {d}")
    return d["iid"]

def artifact(pid, ref, job, path):
    s, t = api("GET", f"/projects/{pid}/jobs/artifacts/{urllib.parse.quote(ref, safe='')}"
              f"/raw/{urllib.parse.quote(path, safe='/')}?job={job}", raw=True)
    return t if s == 200 else None

# ── A 用户/组树/ci-templates ─────────────────────────────
def sec_a():
    st = load()
    st.setdefault("pats", {})
    uids = {}
    for u, meta in USERS.items():
        s, d = api("GET", f"/users?username={u}")
        if d:
            uids[u] = d[0]["id"]
        else:
            s, d = api("POST", "/users", form={"username": u, "name": meta["name"],
                        "email": f"{u}@excavator.local", "password": meta["pwd"],
                        "skip_confirmation": "true", "force_random_password": "false"})
            if s != 201:
                raise SystemExit(f"[建用户失败] {u}: {s} {d}")
            uids[u] = d["id"]
        # 管理员代建用户 PAT（root PAT 无 sudo scope，坑位见进度记录）
        s, d = api("POST", "/personal_access_tokens", form={"user_id": uids[u],
                    "name": "rebuild-sim", "scopes[]": "api", "expires_at": "2026-10-01"})
        if s == 201:
            st["pats"][u] = d["token"]
        elif u not in st["pats"]:
            # 本构建无代建PAT端点（404）→ rails 预置，见 mkusers.rb；先跳过
            print(f"  [PAT跳过] {u}（待 rails 预置）")
    st["uids"] = uids

    # 组树：intel_excavator + firmware/autonomy/vehicle/cloud/app/platform
    s, d = api("POST", "/groups", form={"name": "intel_excavator", "path": "intel_excavator"})
    gid = d["id"] if s == 201 else find_group(st, "intel_excavator")
    if not gid:
        raise SystemExit(f"[建组失败] {s} {d}")
    st["gid"] = gid
    for sub in ("firmware", "autonomy", "vehicle", "cloud", "app", "platform"):
        s, d = api("POST", "/groups", form={"name": sub, "path": sub, "parent_id": gid})
        if s == 201:
            print(f"  [group] {sub} id={d['id']}")
    for k, p in (("g_fw", "firmware"), ("g_au", "autonomy"), ("g_pl", "platform")):
        st[k] = find_group(st, f"intel_excavator/{p}")

    # platform 组成员：plat1=Maintainer；全员 Reporter（§7.3-1 硬规则：模板全员可读）
    for u, lvl in (("plat1", 40), ("maint1", 30), ("dev1", 20), ("guest1", 20)):
        api("POST", f"/groups/{st['g_pl']}/members", form={"user_id": uids[u], "access_level": lvl})

    # ci-templates（宪法仓库）
    pid = find_project(st, "intel_excavator/platform/ci-templates")
    if not pid:
        s, d = api("POST", "/projects", form={"name": "ci-templates", "path": "ci-templates",
                    "namespace_id": st["g_pl"], "default_branch": "main",
                    "initialize_with_readme": "true", "description": "CI模板宪法-规则集中管理"})
        if s != 201:
            raise SystemExit(f"[建 ci-templates 失败] {s} {d}")
        pid = d["id"]
    st["pid_tpl"] = pid
    for f, msg in (("autonomy.yml", "feat: 算法CI模板"), ("vehicle.yml", "feat: 车载CI模板"),
                   ("cloud.yml", "feat: 云端CI模板"),
                   ("firmware.yml", "fix: 模板去掉image适配shell executor")):
        content = FW_TPL_V1 if f == "firmware.yml" else TPL[f]
        s, d = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote(f, safe='')}/raw?ref=main", raw=True)
        if s != 200:
            commit_files(pid, "root", "main", msg, {f: content}, start_branch="main")
            print(f"  [tpl] {f} 提交")
    # 宪法 MR !1：maint1 提交校验，plat1 建 MR 并合入
    s, d = api("GET", f"/projects/{pid}/merge_requests?per_page=5")
    if not d:
        commit_files(pid, "maint1", "update-fw-template",
                     "feat(模板): 固件产物非空校验——空产物禁止进入发布流\n\n宪法变更：影响所有 include firmware.yml 的固件仓库。\n评审重点：校验逻辑是否误伤多产物场景。",
                     {"firmware.yml": fw_tpl_v2()}, start_branch="main")
        mr_create_merge(pid, "plat1", "update-fw-template", "feat(模板): 固件产物非空校验")
        # 宪法 MR !2：plat1 伪构建兼容
        commit_files(pid, "plat1", "fix-proto-build",
                     "fix(模板): 无Makefile时伪构建——兼容原型runner（真机构建时此分支不会走到）",
                     {"firmware.yml": fw_tpl_final()}, start_branch="main")
        mr_create_merge(pid, "plat1", "fix-proto-build", "fix(模板): 原型环境伪构建兼容")
    save(st)
    print(f"A 完成: gid={gid} tpl={pid} users={uids}")

# ── B firmware 项目与 CI v1 ─────────────────────────────
def sec_b():
    st = load()
    pid = find_project(st, "intel_excavator/firmware/hydraulic-controller")
    if not pid:
        s, d = api("POST", "/projects", form={"name": "hydraulic-controller", "path": "hydraulic-controller",
                    "namespace_id": st["g_fw"], "default_branch": "main",
                    "initialize_with_readme": "true",
                    "description": "液压控制器固件（firmware 域示例仓库）"})
        if s != 201:
            raise SystemExit(f"[建 firmware 失败] {s} {d}")
        pid = d["id"]
    st["pid_fw"] = pid
    for u, lvl in (("dev1", 30), ("maint1", 40), ("guest1", 10)):
        api("POST", f"/projects/{pid}/members", form={"user_id": st["uids"][u], "access_level": lvl})
    # 保护分支：仅 Maintainer push/merge，禁 force push
    api("DELETE", f"/projects/{pid}/protected_branches/main")
    s, d = api("POST", f"/projects/{pid}/protected_branches",
               form={"name": "main", "push_access_levels[]": 40, "merge_access_levels[]": 40,
                     "allow_force_push": "false"})
    print(f"  [保护分支] {s}")
    s, _ = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote('.gitlab-ci.yml', safe='')}/raw?ref=main", raw=True)
    if s != 200:
        commit_files(pid, "root", "main", "feat: 仓库层CI——include通用层模板（§6.2）",
                     {".gitlab-ci.yml": FW_CI_V1}, start_branch="main")
    save(st)
    wait_pipeline(pid, "main", "CI v1")
    print(f"B 完成: firmware pid={pid}")

# ── C MR !1/!2 + v0.2.0-field ───────────────────────────
def sec_c():
    st = load()
    pid = st["pid_fw"]
    s, mrs = api("GET", f"/projects/{pid}/merge_requests?per_page=20")
    if len(mrs) < 2:
        # MR !1：评审流程冒烟（dev1 建 / maint1 合）
        commit_files(pid, "dev1", "feature/smoke-mr", "docs: 评审流程冒烟说明",
                     {"docs/smoke.md": "# 冒烟验证\n\n特性分支 → MR → CI 绿 → Owner 合入（§4.2）。\n"},
                     start_branch="main")
        mr_create_merge(pid, "dev1", "feature/smoke-mr", "feat: 评审流程冒烟验证",
                        "## 验证MR评审流程\n对应设计文档§4.2 trunk-based + MR合入。\n\n### 验证项\n- [x] 特性分支创建\n- [x] MR 创建（禁止直接 push main）\n- [x] CI 通过\n- [x] Owner 合入", merger="maint1")
        wait_pipeline(pid, "main", "MR !1 合入后")
        # MR !2：CHANGELOG（截图 14/15 的对象）
        commit_files(pid, "dev1", "feature/test-branch", "docs: 添加更新日志",
                     {"CHANGELOG.md": "# 更新日志\n\n## v0.2.0-field（现场验证版）\n\n- 首个现场验证版固件\n"},
                     start_branch="main")
        mr_create_merge(pid, "dev1", "feature/test-branch", "feat: 添加更新日志",
                        "## 验证MR评审流程\n对应设计文档§4.2 trunk-based + MR合入。\n\n### 改动\n- 添加 CHANGELOG.md\n\n### 验证项\n- [x] 特性分支创建\n- [x] MR 创建（禁止直接 push main）\n- [x] CI 全绿\n- [x] Owner 评审合入", merger="maint1")
        wait_pipeline(pid, "main", "MR !2 合入后")
    # tag v0.2.0-field + Release（资产=流水线制品）——tag 与 Release 分别幂等
    s, tags = api("GET", f"/projects/{pid}/repository/tags")
    if not any(t["name"] == "v0.2.0-field" for t in tags):
        api("POST", f"/projects/{pid}/protected_tags",
            form={"name": "v0.2.0-field", "create_access_level": 40})
        s, d = api("POST", f"/projects/{pid}/repository/tags",
                   form={"tag_name": "v0.2.0-field", "ref": "main", "message": "现场验证版"})
        if s != 201:
            raise SystemExit(f"[tag 失败] {s} {d}")
        wait_pipeline(pid, "v0.2.0-field", "tag 流水线")
    s, rel = api("GET", f"/projects/{pid}/releases")
    if not any(r["tag_name"] == "v0.2.0-field" for r in rel):
        release_with_artifacts(pid, "v0.2.0-field", "固件 v0.2.0-field", None)
    save(st)
    print("C 完成: MR !1/!2 + v0.2.0-field")

# ── D MR !3(extends) / !4(应急) ─────────────────────────
def sec_d():
    st = load()
    pid = st["pid_fw"]
    s, mrs = api("GET", f"/projects/{pid}/merge_requests?per_page=20")
    if len(mrs) < 4:
        # MR !3：build-firmware 改 extends（§7.3-2 发现的修正）
        commit_files(pid, "dev1", "fix/extends-template", "ci: build-firmware 改为 extends 平台模板（§6.2）",
                     {".gitlab-ci.yml": fw_ci_extends()}, start_branch="main")
        mr_create_merge(pid, "dev1", "fix/extends-template", "ci: build-firmware 改为 extends 平台模板（§6.2）",
                        "自写 script 不吃模板更新（§7.3-2 实测），改为 extends 继承宪法模板。", merger="maint1")
        wait_pipeline(pid, "main", "MR !3 合入后")
        # MR !4：现场应急补单（截图 20 的对象）
        commit_files(pid, "dev1", "field/hotfix-pressure-sensor",
                     "fix: 现场应急PID补偿（断网期间本地构建临时包，回网24h内补MR）",
                     {"src/pid_params.h": "#ifndef PID_PARAMS_H\n#define PID_PARAMS_H\n\n// 现场应急：压力传感器 PID 前馈补偿（§7.3 24h 补单）\n#define PID_KP 2.10\n#define PID_KI 0.35\n#define PID_FEEDFWD 0.12\n\n#endif\n"},
                     start_branch="main")
        mr_create_merge(pid, "dev1", "field/hotfix-pressure-sensor", "fix: 现场应急PID补偿（§7.3 24h内补MR）",
                        "## 现场应急补单\n\n断网期间机器急等，本地构建临时包已刷；回网补 MR 走正式构建（§7.3 应急兜底闭环）。\n", merger="maint1")
        wait_pipeline(pid, "main", "MR !4 合入后")
    save(st)
    print("D 完成: MR !3/!4")

# ── E HARBOR 变量 + CI 终版 + MR 模板 ───────────────────
def sec_e():
    st = load()
    pid = st["pid_fw"]
    setvar("groups", st["g_fw"], "HARBOR_REGISTRY", "10.66.35.35:8084", mask=False, protected=True)
    # 极狐坑位：变量值里的 $ 会被引用展开（CE 不展开）→ 必须 $$ 转义，job 内才拿到字面 $
    setvar("groups", st["g_fw"], "HARBOR_USER", "robot$$frm-ci+gitlab-ci", mask=False, protected=True)
    setvar("groups", st["g_fw"], "HARBOR_PASS", HARBOR_SEC, mask=True, protected=True)
    s, t = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote('.gitlab-ci.yml', safe='')}/raw?ref=main", raw=True)
    final = (MIRROR / "firmware-repo/.gitlab-ci.yml").read_text()
    if t != final:
        if "image-build" not in t:  # 先演进到 phase-2 形态（+image-build 无 only），再一步到终版
            commit_files(pid, "root", "main", "feat(ci): image-build 镜像构建推送 Harbor（§5.3 出口收敛）",
                         {".gitlab-ci.yml": fw_ci_v2()})
            wait_pipeline(pid, "main", "image-build 首跑")
        commit_files(pid, "root", "main",
                     "image-build 仅 main/tag 触发（受保护变量在 MR 流水线不可见）+ promote-release 手动晋升",
                     {".gitlab-ci.yml": final})
        wait_pipeline(pid, "main", "CI 终版")
    s, t = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote('.gitlab/merge_request_templates/%E9%BB%98%E8%AE%A4.md', safe='')}/raw?ref=main", raw=True)
    if s != 200:
        commit_files(pid, "root", "main", "MR 模板：关联单号+里程碑+合码自查 checklist（设计§5.1）",
                     {".gitlab/merge_request_templates/默认.md":
                      (MIRROR / "firmware-repo/.gitlab/merge_request_templates/默认.md").read_text()})
        wait_pipeline(pid, "main", "MR 模板")
    save(st)
    print("E 完成: HARBOR_* + CI 终版 + MR 模板")

# ── F MR !5 + v0.9.0-rc1 ────────────────────────────────
def sec_f():
    st = load()
    pid = st["pid_fw"]
    s, mrs = api("GET", f"/projects/{pid}/merge_requests?per_page=20")
    if len(mrs) < 5:
        s, iss = api("GET", f"/projects/{pid}/issues?per_page=20")
        ia = next((i["iid"] for i in iss if "液压抖动" in i["title"]), None)
        desc = (f"Closes #{ia}\n\n## 关联\n\n- 需求单：Closes #{ia}（默认路径：合入即自动关单）\n\n"
                "## 变更说明\n\n- 新增 tuning_params.yaml，阻尼/增益参数从固件常量改为配置文件项\n\n"
                "## 合码前自查\n\n- [x] 关联单号已写（Closes）\n- [x] 已选定里程碑（固件 v0.9·三阶段原型）\n"
                "- [x] CI 全绿\n- [x] 自测通过（build-firmware 产物非空校验通过）")
        commit_files(pid, "dev1", "feat/hydro-tuning",
                     f"#{ia} 抖动抑制参数改为配置文件项",
                     {"tuning_params.yaml": (MIRROR / "firmware-repo/tuning_params.yaml").read_text()},
                     start_branch="main")
        iid, sha = mr_create_merge(pid, "dev1", "feat/hydro-tuning", "液压抖动抑制参数支持现场调节", desc, merger="maint1")
        st["mr5_sha"] = sha
        wait_pipeline(pid, "main", "MR !5 合入后")
    s, tags = api("GET", f"/projects/{pid}/repository/tags")
    if not any(t["name"] == "v0.9.0-rc1" for t in tags):
        api("POST", f"/projects/{pid}/protected_tags", form={"name": "v0.9.0-rc1", "create_access_level": 40})
        s, d = api("POST", f"/projects/{pid}/repository/tags",
                   form={"tag_name": "v0.9.0-rc1", "ref": "main", "message": "三阶段验证版本"})
        if s != 201:
            raise SystemExit(f"[tag 失败] {s} {d}")
        wait_pipeline(pid, "v0.9.0-rc1", "tag 流水线（promote-release 手动=终态）")
    s, rel = api("GET", f"/projects/{pid}/releases")
    if not any(r["tag_name"] == "v0.9.0-rc1" for r in rel):
        s, iss = api("GET", f"/projects/{pid}/issues?per_page=20")
        ia = next((i["iid"] for i in iss if "液压抖动" in i["title"]), None)
        release_with_artifacts(pid, "v0.9.0-rc1", "固件 v0.9.0-rc1",
                               f"三阶段验证版本：抖动参数可配置（需求单 #{ia}）。发布说明=里程碑清单（设计§2.4 手工复制起步）。")
    save(st)
    print("F 完成: MR !5 + v0.9.0-rc1")

# ── G perception ────────────────────────────────────────
def sec_g():
    st = load()
    pid = find_project(st, "intel_excavator/autonomy/perception")
    if not pid:
        s, d = api("POST", "/projects", form={"name": "perception", "path": "perception",
                    "namespace_id": st["g_au"], "default_branch": "main",
                    "description": "感知算法示例仓库（数据集指针+MinIO通道 §6.4）"})
        if s != 201:
            raise SystemExit(f"[建 perception 失败] {s} {d}")
        pid = d["id"]
    st["pid_pc"] = pid
    setvar("groups", st["g_au"], "MINIO_ENDPOINT", "http://frm-minio:9002", mask=False, protected=True)
    setvar("groups", st["g_au"], "MINIO_KEY", "ci-bot", mask=False, protected=True)  # 6字符不可masked
    setvar("groups", st["g_au"], "MINIO_SECRET", "CiBot#2026", mask=True, protected=True)
    s, t = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote('train.py', safe='')}/raw?ref=main", raw=True)
    if s != 200:
        files = {}
        for f in ("datasets.manifest.json", "train.py", ".gitlab-ci.yml"):
            files[f] = (MIRROR / "perception-repo" / f).read_text()
        commit_files(pid, "root", "main", "perception 三件套：数据集指针/假训练/CI（§6.4）",
                     files, start_branch="main")
    save(st)
    wait_pipeline(pid, "main", "perception 取数→训练→入库")
    print(f"G 完成: perception pid={pid}")

# ── H intake + 标签 + 里程碑 + 四单 ─────────────────────
def sec_h():
    st = load()
    gid = st["gid"]
    # 11 组标签（?name= 过滤有坑：全量拉回再比对）
    s, have = api("GET", f"/groups/{gid}/labels?per_page=50")
    have_names = {l["name"] for l in have}
    for name, color, desc in LABELS:
        if name not in have_names:
            s, d = api("POST", f"/groups/{gid}/labels", form={"name": name, "color": color, "description": desc})
            if s != 201:
                raise SystemExit(f"[标签失败] {name}: {s} {d}")
    # 里程碑
    s, ms = api("GET", f"/groups/{gid}/milestones?per_page=10")
    if not ms:
        s, d = api("POST", f"/groups/{gid}/milestones", form={"title": "固件 v0.9·三阶段原型",
                   "description": "产研需求流三阶段验证版本（设计§4.4 里程碑=版本节点）"})
        st["ms_id"] = d["id"]
    else:
        st["ms_id"] = ms[0]["id"]
    # intake 项目
    pid = find_project(st, "intel_excavator/intake")
    if not pid:
        s, d = api("POST", "/projects", form={"name": "intake", "path": "intake",
                    "namespace_id": gid, "default_branch": "main", "initialize_with_readme": "true",
                    "description": "统一受理台——所有来源的需求/缺陷从这里进（设计§4.1）"})
        if s != 201:
            raise SystemExit(f"[建 intake 失败] {s} {d}")
        pid = d["id"]
    st["pid_ia"] = pid
    for u, lvl in (("guest1", 10), ("maint1", 40)):
        api("POST", f"/projects/{pid}/members", form={"user_id": st["uids"][u], "access_level": lvl})
    s, t = api("GET", f"/projects/{pid}/repository/files/{urllib.parse.quote('.gitlab/issue_templates/%E9%9C%80%E6%B1%82.md', safe='')}/raw?ref=main", raw=True)
    if s != 200:
        files = {"README.md": (MIRROR / "intake-repo/README.md").read_text(),
                 ".gitlab/issue_templates/需求.md": (MIRROR / "intake-repo/.gitlab/issue_templates/需求.md").read_text(),
                 ".gitlab/issue_templates/缺陷.md": (MIRROR / "intake-repo/.gitlab/issue_templates/缺陷.md").read_text(),
                 ".gitlab/issue_templates/任务.md": (MIRROR / "intake-repo/.gitlab/issue_templates/任务.md").read_text()}
        commit_files(pid, "root", "main", "受理台README与三模板（需求/缺陷/任务）", files, start_branch="main")

    fw = st["pid_fw"]
    s, iss = api("GET", f"/projects/{pid}/issues?per_page=20")
    if not iss:
        # 单1：需求（guest1 建）→ 移交 firmware → 排期+里程碑+分诊评论
        desc1 = ("## 背景与目标\n\n客户反馈土方作业时铲斗低速抖动明显，现场无法调阻尼参数，每次都要回厂改固件常量。"
                 "目标：抖动抑制参数开放为配置文件可调项，现场改参数即生效。\n\n"
                 "## 验收标准\n\n- [ ] 抖动抑制参数（低/高频阻尼、增益下限）从固件常量改为配置文件项\n"
                 "- [ ] 配置文件随固件发布，manifest 可追溯修改来源\n\n"
                 "## 来源信息\n\n- 提出方 / 期望版本：市场部代 X 客户提 / 固件 v0.9")
        s, d = api("POST", f"/projects/{pid}/issues", tok("guest1"),
                   form={"title": "【需求】铲斗液压抖动抑制参数支持现场调节", "description": desc1})
        ia = transfer_issue(pid, 1, fw)
        st["ia"] = ia
        api("PUT", f"/projects/{fw}/issues/{ia}", tok("maint1"),
            form={"labels": "状态::已排期,来源::市场", "milestone_id": st["ms_id"]})
        api("POST", f"/projects/{fw}/issues/{ia}/notes", tok("maint1"),
            form={"body": "分诊：固件域受理，排入 固件 v0.9·三阶段原型。（受理台 guest 建单，来源标签分诊补打）"})
        # 单2：打回（信息不足）
        desc2 = ("## 背景与目标\n\n操作手希望一键进入平地模式。\n\n## 验收标准\n\n- [ ] 待明确\n\n"
                 "## 来源信息\n\n- 提出方：内部")
        api("POST", f"/projects/{pid}/issues", tok("guest1"),
            form={"title": "【需求】遥控器增加一键平地模式", "description": desc2})
        api("POST", f"/projects/{pid}/issues/2/notes", tok("maint1"),
            form={"body": "打回：验收标准为空，且未说明目标工况（土方/平地/整平精度要求）。请补充后回复本单，分诊重启。"})
        api("PUT", f"/projects/{pid}/issues/2", tok("maint1"), form={"labels": "状态::待受理"})
        # 单3：婉拒（超范围）+ 关闭
        desc3 = "## 背景与目标\n\n客户希望整机涂装改红色。\n\n## 验收标准\n\n- [ ] 涂装改色\n\n## 来源信息\n\n- 提出方：市场部"
        api("POST", f"/projects/{pid}/issues", tok("guest1"),
            form={"title": "【需求】整机外观改为红色", "description": desc3})
        api("POST", f"/projects/{pid}/issues/3/notes", tok("maint1"),
            form={"body": "婉拒：涂装属工业设计/供应链范畴，非研发代码需求。请走采购与工业设计渠道。"})
        api("PUT", f"/projects/{pid}/issues/3", tok("maint1"),
            form={"labels": "状态::已拒绝,来源::市场", "state_event": "close"})
        # 单4：缺陷（manifest 粘贴）→ 定位评论 → 移交 firmware → 待验证
        mf = (MIRROR / "firmware-repo/manifest-v0.9.0-rc1.json").read_text().strip()
        # 用新实例实际 manifest 替换（commit 字段与旧实例不同）
        new_mf = artifact(fw, "v0.9.0-rc1", "build-firmware", "manifest.json")
        if new_mf:
            mf = new_mf.strip()
        desc4 = ("## 现象\n\nv0.9.0-rc1 整机低速工况铲斗仍有余抖，参数调到上限无改善。\n\n"
                 "## 复现步骤\n\n1. 刷 v0.9.0-rc1\n2. 低速土方作业 10 分钟\n\n"
                 "## 影响范围\n\n已刷 rc1 的 2 台试验机\n\n## 机器版本（manifest 粘贴区）\n\n```json\n" + mf + "\n```")
        api("POST", f"/projects/{pid}/issues", tok("guest1"),
            form={"title": "【缺陷】v0.9.0-rc1 低速工况铲斗余抖", "description": desc4})
        s, mr5 = api("GET", f"/projects/{fw}/merge_requests?per_page=5")
        sha5 = mr5[0]["merge_commit_sha"]
        api("POST", f"/projects/{pid}/issues/4/notes", tok("maint1"),
            form={"body": f"定位：manifest→commit {sha5[:8]}→MR !{mr5[0]['iid']}→需求单 #{ia}（该行为为抖动参数可配置需求引入）。转固件域分析参数边界，分诊移交。"})
        ib = transfer_issue(pid, 4, fw)
        st["ib"] = ib
        api("PUT", f"/projects/{fw}/issues/{ib}", tok("maint1"),
            form={"labels": "状态::待验证,来源::现场"})
    save(st)
    print(f"H 完成: intake={pid} ia={st.get('ia')} ib={st.get('ib')} ms={st['ms_id']}")

# ── I 看板列（需先浏览器访问看板页触发懒创建）──────────
def sec_i():
    st = load()
    gid = st["gid"]
    s, boards = api("GET", f"/groups/{gid}/boards")
    if not boards:
        raise SystemExit("[看板不存在] 先用浏览器访问组看板页再跑本段")
    bid = boards[0]["id"]
    s, labels = api("GET", f"/groups/{gid}/labels?per_page=50")
    want = ["状态::待受理", "状态::已排期", "状态::开发中", "状态::待验证", "状态::暂缓", "状态::已拒绝"]
    lmap = {l["name"]: l["id"] for l in labels}
    s, lists = api("GET", f"/groups/{gid}/boards/{bid}/lists")
    have = {x["label"]["name"] for x in lists if x.get("label")}
    for w in want:
        if w not in have:
            s, d = api("POST", f"/groups/{gid}/boards/{bid}/lists", form={"label_id": lmap[w]})
            print(f"  [board] {w}: {s}")
    print("I 完成")

# ── J 语言/吊销/核对 ────────────────────────────────────
def sec_j():
    st = load()
    # 全员中文（含 root）
    users = ["root"] + list(USERS)
    print("  [rails] 设置中文:", users)
    # 终态核对
    checks = []
    for path, key in (("intel_excavator", "组树"), ("intel_excavator/platform/ci-templates", "宪法仓库"),
                      ("intel_excavator/firmware/hydraulic-controller", "固件仓库"),
                      ("intel_excavator/autonomy/perception", "算法仓库"), ("intel_excavator/intake", "受理台")):
        s, _ = api("GET", "/projects/" + urllib.parse.quote(path, safe="") if "/" in path else "/groups/" + urllib.parse.quote(path, safe=""))
        checks.append((key, s == 200))
    s, mrs = api("GET", f"/projects/{st['pid_fw']}/merge_requests?per_page=20")
    checks.append(("MR×5 已合入", sum(1 for m in mrs if m["state"] == "merged") >= 5))
    s, rel = api("GET", f"/projects/{st['pid_fw']}/releases")
    checks.append(("Release×2", len(rel) >= 2))
    s, lab = api("GET", f"/groups/{st['gid']}/labels?per_page=50")
    checks.append(("标签×11", len(lab) == 11))
    s, iss = api("GET", f"/projects/{st['pid_fw']}/issues?per_page=20")
    checks.append(("固件域单×2", len(iss) == 2))
    for k, ok in checks:
        print(f"  [{'OK' if ok else '!!'}] {k}")
    save(st)

def sec_z():
    st = load()
    s, ts = api("GET", "/personal_access_tokens?revoked=false")
    for t in ts:
        if t["name"] == "rebuild-sim":
            api("DELETE", f"/personal_access_tokens/{t['id']}")
            print(f"  [吊销] {t['user_id']} rebuild-sim")
    st.pop("pats", None)
    save(st)
    print("Z 完成")

def setvar(kind, id_, key, value, mask, protected):
    s, d = api("GET", f"/{kind}/{id_}/variables")
    if any(v["key"] == key for v in d):
        return
    form = {"key": key, "value": value, "protected": str(protected).lower()}
    if mask:
        form["masked"] = "true"
    s, d = api("POST", f"/{kind}/{id_}/variables", form=form)
    if s not in (200, 201) and mask:
        form.pop("masked")
        s, d = api("POST", f"/{kind}/{id_}/variables", form=form)
    if s not in (200, 201):
        raise SystemExit(f"[变量失败] {key}: {s} {d}")

def release_with_artifacts(pid, tag, name, desc):
    s, d = api("POST", f"/projects/{pid}/releases",
               form={"tag_name": tag, "ref": "main", "name": name} | ({"description": desc} if desc else {}))
    if s not in (200, 201):
        raise SystemExit(f"[Release 失败] {tag}: {s} {d}")
    for label, path in (("manifest.json", "manifest.json"), ("hydraulic-controller.bin", "build/hydraulic-controller.bin")):
        blob = artifact(pid, tag, "build-firmware", path)
        if not blob:
            print(f"  [资产缺] {tag} {path}")
            continue
        import tempfile, os
        fn = pathlib.Path("/tmp") / f"rel-{tag}-{path.replace('/', '-')}"
        fn.write_bytes(blob.encode() if isinstance(blob, str) else blob)
        ctype = "application/json" if path.endswith(".json") else "application/octet-stream"
        req = urllib.request.Request(f"{BASE}/projects/{pid}/uploads", headers={"PRIVATE-TOKEN": ROOT_TOK}, method="POST")
        body, boundary = None, "----jhrebuild"
        with open(fn, "rb") as f:
            body = ((f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fn.name}\"\r\n"
                     f"Content-Type: {ctype}\r\n\r\n").encode() + f.read()
                    + f"\r\n--{boundary}--\r\n".encode())
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.data = body
        with urllib.request.urlopen(req) as r:
            up = json.loads(r.read().decode())
        api("POST", f"/projects/{pid}/releases/{tag}/assets/links",
            form={"name": label, "url": f"{WEB}{up['url']}"})
        print(f"  [Release] {tag} +{label}")

SECTIONS = {"A": sec_a, "B": sec_b, "C": sec_c, "D": sec_d, "E": sec_e, "F": sec_f,
            "G": sec_g, "H": sec_h, "I": sec_i, "J": sec_j, "Z": sec_z}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in SECTIONS:
        raise SystemExit(__doc__)
    SECTIONS[sys.argv[1]]()
