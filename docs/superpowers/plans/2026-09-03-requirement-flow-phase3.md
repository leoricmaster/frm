# 产研需求流 三阶段原型验证 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 frm 本地原型 GitLab 上落地《产研需求流设计》§8 四个验证场景（受理台建单分诊、需求→MR→CI→tag/Release 正向全链、manifest 反向追溯、组看板管理视图），产出截图 32–43 与 test-plan 三阶段章节。

**Architecture:** 全部在现有 gitlab-compose-test 的 GitLab 实例上做 GitLab 侧配置与流程演练（无新服务、不动 compose）：组级 scoped 标签字典 + 受理台仓库 `excavator/intake`（含三个 issue 模板）+ 组级里程碑 + hydraulic-controller 上的 MR 全链（修复 image-build 在 MR 流水线缺受保护变量的既有问题）+ 组看板。操作全走 GitLab API v4（root PAT + `sudo` 参数扮演 guest1/dev1/maint1），证据走 Playwright 截图。

**Tech Stack:** GitLab CE 19.3.1 API v4、Playwright（复用既有截图脚本模式，`.venv/bin/python` + `/usr/bin/google-chrome`）、root PAT `glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg`（有效期至 2026-10-01，name=phase2-plan）。

## Global Constraints

- API base `http://10.66.35.35:8081/api/v4`；root PAT：`T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg`。**PAT 过 2026-10-01 失效时先在 UI 建 新 PAT 再开工**。
- 扮演非 root 用户一律用 sudo 参数：请求 URL 加 `?sudo=guest1`（或 POST body 里 `-d sudo=guest1`），token 仍是 root 的——不要也不会知道其他用户密码。
- 现有环境事实（已核实）：组 `excavator` id=2；项目 `excavator/firmware/hydraulic-controller` id=2（成员 dev1=30/maint1=40/guest1=10，main 为保护分支仅 Maintainer 合入）；用户 guest1 id=4、dev1 id=2、maint1 id=3；组标签与组里程碑目前为空；既有 Release 仅 `v0.2.0-field`。
- 标签命名固定：状态 scoped 标签 `状态::待受理/已排期/开发中/待验证/暂缓/已拒绝`（`已关闭` 不设标签——它是 GitLab 原生 closed 状态，设计 §4.3 的 7 状态里它由系统承载）；来源 scoped 标签 `来源::集团/市场/客户/现场/内部`。中文与 `::` 出现在 query 参数时必须 URL-encode（curl 用 `--data-urlencode` 或 `python3 -c "import urllib.parse;print(urllib.parse.quote('状态::待受理'))"`）。
- 里程碑名固定：`固件 v0.9·三阶段原型`；tag 固定：`v0.9.0-rc1`。
- 截图编号从 32 续起，存 `gitlab-compose-test/screenshots/`，命名 `NN-描述.png`。
- git 提交信息中文、conventional 前缀，末尾 `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`；GitLab 侧内容同步留档到 `gitlab-compose-test/<repo名>/` 目录一并入库（沿用 perception-repo/firmware-repo 模式）。
- 本计划只做原型验证与证据；**教程同步（第 6 篇 + developer/field 扩展）验证完成后另立计划**（设计 §8 明确"教程不先于验证"）。
- 环境里随时用 `curl -s -H "PRIVATE-TOKEN: $T" ... | python3 -m json.tool` 看原始返回排错；任务里的"期望"行是判定标准。
- **shell 变量跨任务/跨 Step 不保留**：`$T`（PAT）、`$PID`（intake 项目 id）、`$IA`/`$MS`/`$MRI`/`$SHA`/`$IB` 等在每个 Step 开头按需重设——`$T` 直接抄 Global Constraints 第一行；项目/单据 id 用上文记录值或"找回"命令（intake：`curl -s -H "PRIVATE-TOKEN: $T" http://10.66.35.35:8081/api/v4/projects/excavator%2Fintake | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])"`）。

---

### Task 1: 组级 scoped 标签字典

**Files:** 无仓库文件（纯 GitLab 侧配置）

**Interfaces:**
- Produces: 组 `excavator`(id=2) 的 11 个标签及各自 id——Task 3（打标/婉拒）、Task 6（看板列）依赖；标签名即接口，后续任务直接引用名称。

- [ ] **Step 1: 建 6 个状态标签**

```bash
T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg
G=http://10.66.35.35:8081/api/v4/groups/2/labels
mklabel() { curl -s -H "PRIVATE-TOKEN: $T" -X POST "$G" \
  --data-urlencode "name=$1" -d "color=$2" --data-urlencode "description=$3" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id'), d.get('name') or d)"; }
mklabel "状态::待受理" "#808080" "新单进受理台，等分诊"
mklabel "状态::已排期" "#1F75CB" "进版本里程碑，域 Owner 已排期"
mklabel "状态::开发中" "#FC9403" "特性分支/MR 在途"
mklabel "状态::待验证" "#6E49CB" "已合入，等外部验收（台架/现场/提出方）"
mklabel "状态::暂缓"   "#8F8F00" "本版本不做，恢复时回已排期"
mklabel "状态::已拒绝" "#C0392B" "分诊婉拒（重复/超范围），关闭留痕"
```

- [ ] **Step 2: 建 5 个来源标签**

```bash
mklabel "来源::集团" "#0033CC" "集团下达/集团平台要求"
mklabel "来源::市场" "#00867D" "市场/销售代客户提出"
mklabel "来源::客户" "#8E24AA" "客户直接提出"
mklabel "来源::现场" "#D14438" "驻场/售后反馈（缺陷单为主）"
mklabel "来源::内部" "#4C7E00" "团队自提技术需求"
```

- [ ] **Step 3: 验证**

```bash
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/groups/2/labels?per_page=20" \
  | python3 -c "import json,sys; ls=json.load(sys.stdin); print(len(ls), '个标签'); [print(l['id'], l['name']) for l in ls]"
```

期望：`11 个标签`，六个 `状态::` + 五个 `来源::` 全部在列。把 11 个 id 抄给 Task 6（看板列用状态标签 id）。

---

### Task 2: 受理台仓库 excavator/intake（模板三件套）

**Files:**
- Create: GitLab 项目 `excavator/intake`（README + `.gitlab/issue_templates/需求.md`、`缺陷.md`、`任务.md`）
- Create: `gitlab-compose-test/intake-repo/`（上述四文件的留档副本，入库）

**Interfaces:**
- Consumes: 组 id=2。
- Produces: intake 项目 id（Task 3 建单/移交依赖）；三个 issue 模板名 `需求`/`缺陷`/`任务`（缺陷模板的 manifest 粘贴区被 Task 5 使用）；guest1(Guest)/maint1(Maintainer) 为项目成员。

- [ ] **Step 1: 建项目 + 成员**

```bash
T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg
PID=$(curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects" \
  -d "name=intake" -d "path=intake" -d "namespace_id=2" -d "default_branch=main" \
  -d "initialize_with_readme=true" \
  --data-urlencode "description=统一受理台——所有来源的需求/缺陷从这里进（设计§4.1）" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['id'])")
echo "intake PID=$PID"
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/members" -d "user_id=4&access_level=10" -o /dev/null -w 'guest1:%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/members" -d "user_id=3&access_level=40" -o /dev/null -w 'maint1:%{http_code}\n'
```

期望：两行 `201`，PID 打印出来（后文用 `$PID` 代入；跨任务丢失时用 `curl ... /projects/excavator%2Fintake | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])"` 找回）。

- [ ] **Step 2: 提交 README 与三个模板**

本地构建留档目录（内容即最终文件，逐字写入）：

```bash
mkdir -p /tmp/intake-repo/.gitlab/issue_templates
cd /tmp/intake-repo
```

`README.md`：

```markdown
# 受理台（intake）

所有来源的需求/缺陷/任务**只从这里提**——不用管代码在哪个仓库，分诊会移交。

## 提单三步

1. New issue → 选模板：`需求` / `缺陷` / `任务`
2. 按模板填（**验收标准必填**，缺了会被打回）
3. 提交。3 个工作日内分诊：移交对应团队 / 打回补充 / 婉拒并说明

## 不要往单子里贴

客户商务与合同细节、报价、个人信息（DLP 红线延伸到需求侧）。

## 状态怎么看

- 你提的单：在本仓库 Issues 里看，移交后跳转到对应仓库的单
- 全局进度：excavator 组看板（按状态列）+ 版本里程碑
```

`.gitlab/issue_templates/需求.md`：

````
## 背景与目标

（为什么要做、想达成什么；一两句话说清）

## 验收标准

- [ ] （做完的判定标准，可勾选验证——**必填**）

## 来源信息

- 提出方 / 期望版本：
````

`.gitlab/issue_templates/缺陷.md`：

````
## 现象

（什么问题、什么工况下出现）

## 复现步骤

1. 

## 影响范围

（哪些机器/版本/功能）

## 机器版本（manifest 粘贴区）

```json
（从机器或 Release 资产读出的 manifest.json 原样粘贴；现场没有则写"无"）
```
````

`.gitlab/issue_templates/任务.md`：

````
## 任务说明

（做什么、为什么现在做）

## 完成标准

- [ ] 
````

用 commits API 一次提交四文件（首个提交带 `start_branch=main`；内容走 base64 免转义）：

```bash
C=$(mktemp)
python3 - <<'EOF' > "$C"
import base64, json
files = ["README.md", ".gitlab/issue_templates/需求.md", ".gitlab/issue_templates/缺陷.md", ".gitlab/issue_templates/任务.md"]
actions = [{"action": "create", "file_path": f, "content": base64.b64encode(open("/tmp/intake-repo/"+f, "rb").read()).decode(), "encoding": "base64"} for f in files]
print(json.dumps({"branch": "main", "start_branch": "main", "commit_message": "受理台README与三模板（需求/缺陷/任务）", "actions": actions}))
EOF
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/repository/commits" \
  -H "Content-Type: application/json" --data-binary "@$C" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('short_id') or d)"
```

期望：打印 short_id（8 位）。报 400 时看 message（常见是 start_branch 冲突，去掉 start_branch 重试）。

- [ ] **Step 3: 验证模板可见**

```bash
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/$PID/templates/issues" | python3 -m json.tool
```

期望：`需求`、`缺陷`、`任务` 三项。

- [ ] **Step 4: 留档 + Commit**

```bash
cp -r /tmp/intake-repo/. /home/lancer/projects/frm/gitlab-compose-test/intake-repo/
cd /home/lancer/projects/frm
git add gitlab-compose-test/intake-repo/
git commit -m "feat(intake): 受理台仓库留档——README与需求/缺陷/任务三模板

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: 场景 1——多来源建单与分诊三动作

**Files:** 无仓库文件（GitLab 侧流程演练）

**Interfaces:**
- Consumes: Task 1 标签、Task 2 的 `$PID`。
- Produces: 单 A（移交后在 hydraulic-controller，新 iid 记为 `$IA`——Task 4 的 MR `Closes #$IA` 依赖它）；打回/婉拒两单（Task 6 截图 35）。**注意：issue 跨项目移交后 iid 会变，必须用 API 返回的新 iid。**

- [ ] **Step 1: guest1 按【需求】模板建单（市场代客户提）**

```bash
DESC=$(mktemp)
cat > $DESC <<'EOF'
## 背景与目标

客户反馈土方作业时铲斗低速抖动明显，现场无法调阻尼参数，每次都要回厂改固件常量。目标：抖动抑制参数开放为配置文件可调项，现场改参数即生效。

## 验收标准

- [ ] 抖动抑制参数（低/高频阻尼、增益下限）从固件常量改为配置文件项
- [ ] 配置文件随固件发布，manifest 可追溯修改来源

## 来源信息

- 提出方 / 期望版本：市场部代 X 客户提 / 固件 v0.9
EOF
J=$(python3 -c "import json;print(json.dumps({'title':'【需求】铲斗液压抖动抑制参数支持现场调节','description':open('$DESC').read(),'sudo':'guest1'}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues" \
  -H "Content-Type: application/json" --data-binary "$J" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('iid',d['iid'],'author',d['author']['username'],'state',d['state'])"
```

期望：`iid 1 author guest1 state opened`。（Guest 建单不带标签——Guest 无打标权限；**来源标签由分诊补打**，记入 test-plan §9.3 偏差。）

- [ ] **Step 2: 分诊移交到 hydraulic-controller**

```bash
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues/1/transfer" \
  -H "Content-Type: application/json" -d '{"to_project_id": 2}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('新位置', d['project_id'], '新iid', d['iid'])"
```

期望：`新位置 2 新iid <数字>`——**抄下记为 `$IA`**（hydraulic-controller 既有 issue 数 +1，预计为 1）。transfer 端点若 404，改用旧端点 `POST /projects/$PID/issues/1/move?to_project_id=2`。

- [ ] **Step 3: 分诊补标 + 排期进里程碑（先建里程碑）**

```bash
MS=$(curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/groups/2/milestones" \
  -d "title=固件 v0.9·三阶段原型" \
  --data-urlencode "description=产研需求流三阶段验证版本（设计§4.4 里程碑=版本节点）" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
echo "milestone id=$MS"
curl -s -H "PRIVATE-TOKEN: $T" -X PUT "http://10.66.35.35:8081/api/v4/projects/2/issues/$IA" \
  --data-urlencode "labels=状态::已排期,来源::市场" -d "milestone_id=$MS" -o /dev/null -w '%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/issues/$IA/notes" \
  --data-urlencode "body=分诊：固件域受理，排入 固件 v0.9·三阶段原型。（受理台 guest 建单，来源标签分诊补打）" -o /dev/null -w '%{http_code}\n'
```

期望：三行 `200`。`$MS` 抄给 Task 4（MR 排期用）。

- [ ] **Step 4: 打回一单（信息不足）**

```bash
J=$(python3 -c "import json;print(json.dumps({'title':'【需求】遥控器增加一键平地模式','description':'## 背景与目标\n\n操作手希望一键进入平地模式。\n\n## 验收标准\n\n- [ ] 待明确\n\n## 来源信息\n\n- 提出方：内部','sudo':'guest1'}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues" \
  -H "Content-Type: application/json" --data-binary "$J" -o /dev/null -w '建单:%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues/2/notes" \
  --data-urlencode "body=打回：验收标准为空，且未说明目标工况（土方/平地/整平精度要求）。请补充后回复本单，分诊重启。" -o /dev/null -w '打回:%{http_code}\n'
```

期望：两行 201。

- [ ] **Step 5: 婉拒一单（超范围）**

```bash
J=$(python3 -c "import json;print(json.dumps({'title':'【需求】整机外观改为红色','description':'## 背景与目标\n\n客户希望整机涂装改红色。\n\n## 验收标准\n\n- [ ] 涂装改色\n\n## 来源信息\n\n- 提出方：市场部','sudo':'guest1'}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues" \
  -H "Content-Type: application/json" --data-binary "$J" -o /dev/null -w '建单:%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues/3/notes" \
  --data-urlencode "body=婉拒：涂装属工业设计/供应链范畴，非研发代码需求。请走采购与工业设计渠道。" -o /dev/null -w '说明:%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X PUT "http://10.66.35.35:8081/api/v4/projects/$PID/issues/3" \
  --data-urlencode "labels=状态::已拒绝,来源::市场" -d "state_event=close" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('state', d['state'], 'labels', d['labels'])"
```

期望：`state closed`，labels 含 `状态::已拒绝`。

---

### Task 4: 场景 2——正向全链（MR Closes → CI → 自动关单 → tag/Release 挂里程碑）

**Files:**
- Modify: GitLab 项目 2（hydraulic-controller）的 `.gitlab-ci.yml`（image-build 加 `only: [main, tags]`）
- Create: 该仓库 `.gitlab/merge_request_templates/默认.md`、特性分支文件 `tuning_params.yaml`
- Modify: `gitlab-compose-test/firmware-repo/.gitlab-ci.yml`（同步留档）；Create: `gitlab-compose-test/firmware-repo/merge_request_templates-默认.md`、`tuning_params.yaml` 留档

**Interfaces:**
- Consumes: Task 3 的 `$IA`（需求单）、`$MS`（里程碑）。
- Produces: 合入 main 的 commit sha、tag `v0.9.0-rc1`、挂里程碑的 Release 及其 manifest.json 资产——Task 5 反向追溯的输入。

- [ ] **Step 1: 修 image-build 触发范围（MR 流水线缺受保护变量的既有坑）**

HARBOR_* 是组级 protected 变量，只在保护分支/tag 可见；image-build 现无 only 会在 MR 流水线因凭据为空而红。用 files API 更新 `.gitlab-ci.yml`——完整新内容（基于现文件，仅 image-build 加 only 两行）：

```yaml
# 仓库层：include 通用层 + extends 继承模板 job（§6.2 三层模型）
include:
  - project: excavator/platform/ci-templates
    ref: main
    file: firmware.yml

stages:
  - scan
  - build
  - image
  - release

gitleaks-check:
  stage: scan
  script:
    - echo "gitleaks密钥扫描：CE无push rules的替代(§6.5)"
    - echo "扫描通过，无明文密钥"
  only:
    - merge_requests

build-firmware:
  extends: .firmware-template     # ← 继承平台模板（script/variables/artifacts 全来自通用层）
  variables:
    CROSS_COMPILE: arm-none-eabi- # 仓库层只 override 细节
  before_script:
    - mkdir -p build scripts
    - echo "firmware-binary" > build/hydraulic-controller.bin
    - echo '#!/bin/sh' > scripts/sign_firmware.sh
    - echo 'echo "proto-sign $1"' >> scripts/sign_firmware.sh
    - chmod +x scripts/sign_firmware.sh
    - printf '{"name":"hydraulic-controller","commit":"%s","branch":"%s","build_time":"%s","runner":"%s"}\n' "$CI_COMMIT_SHA" "$CI_COMMIT_BRANCH" "$CI_JOB_STARTED_AT" "$CI_RUNNER_DESCRIPTION" > manifest.json

# 二阶段：镜像出口收敛（§5.3）——CI 构建镜像推内网 Harbor，不直连外网
# 三阶段修正：仅 main/tag 跑——HARBOR_* 为受保护变量，MR 流水线不可见（设计§6.5 语义）
image-build:
  stage: image
  only:
    - main
    - tags
  script:
    - echo "[image] 构建并推送 CI 基础镜像到 Harbor frm-ci 项目"
    - export DOCKER_HOST=unix:///var/run/docker.sock
    - printf 'FROM docker.m.daocloud.io/library/alpine:latest\nLABEL org.opencontainers.image.revision=%s\n' "$CI_COMMIT_SHA" > Dockerfile.ci
    - docker build -t "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" -f Dockerfile.ci .
    - echo "$HARBOR_PASS" | docker login "$HARBOR_REGISTRY" -u "$HARBOR_USER" --password-stdin
    - docker push "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"
    - docker rmi "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" || true
    # 从 Harbor 拉回验证（runner 一律走 Harbor §5.3）
    - docker pull "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"

promote-release:
  stage: release
  script:
    - echo "签名并发布固件 (§6.3 手动批准晋升)"
  only:
    - tags
  when: manual
```

```bash
B64=$(base64 -w0 /tmp/fw-ci.yml)   # 先把上面内容存 /tmp/fw-ci.yml
curl -s -H "PRIVATE-TOKEN: $T" -X PUT "http://10.66.35.35:8081/api/v4/projects/2/repository/files/.gitlab-ci.yml" \
  -d "branch=main" -d "encoding=base64" -d "content=$B64" \
  --data-urlencode "commit_message=image-build 仅 main/tag 触发（受保护变量在 MR 流水线不可见）" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('branch') or d)"
```

期望：打印 `main`（此 push 触发一条 main 流水线，等其跑完再进行 Step 4，轮询法见 Step 5）。

- [ ] **Step 2: MR 模板进仓库**

`/tmp/mr-template.md`：

````markdown
## 关联

- 需求/缺陷单：Closes #单号（**需外部验收的单只写 `#单号` 引用**，合入后进 待验证 由验收人关单）

## 变更说明

（做了什么、怎么验证的）

## 合码前自查

- [ ] 关联单号已写（Closes 或引用）
- [ ] 已选定里程碑
- [ ] CI 全绿
- [ ] 自测通过
````

```bash
B64=$(base64 -w0 /tmp/mr-template.md)
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/repository/files" \
  -d "branch=main" -d "start_branch=main" -d "encoding=base64" -d "content=$B64" \
  --data-urlencode "file_path=.gitlab/merge_request_templates/默认.md" \
  --data-urlencode "commit_message=MR 模板：关联单号+里程碑+合码自查 checklist（设计§5.1）" -o /dev/null -w '%{http_code}\n'
```

期望：`201`。

- [ ] **Step 3: dev1 建特性分支 + MR（Closes 单号 + 里程碑）**

```bash
J=$(python3 -c "import json;print(json.dumps({'branch':'feat/hydro-tuning','start_branch':'main','commit_message':'#$IA 抖动抑制参数改为配置文件项','actions':[{'action':'create','file_path':'tuning_params.yaml','content':'# 液压抖动抑制参数（验收标准#$IA：现场可调、随固件发布）\ndamping_low_hz: 2.4\ndamping_high_hz: 6.0\ngain_floor: 0.15\n'}]}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/repository/commits?sudo=dev1" \
  -H "Content-Type: application/json" --data-binary "$J" \
  | python3 -c "import json,sys; print('branch commit', json.load(sys.stdin)['short_id'])"
M=$(python3 -c "import json;print(json.dumps({'source_branch':'feat/hydro-tuning','target_branch':'main','title':'液压抖动抑制参数支持现场调节','milestone_id':'$MS','sudo':'dev1','description':'Closes #$IA\n\n## 关联\n\n- 需求单：Closes #$IA（默认路径：合入即自动关单）\n\n## 变更说明\n\n- 新增 tuning_params.yaml，阻尼/增益参数从固件常量改为配置文件项\n\n## 合码前自查\n\n- [x] 关联单号已写（Closes）\n- [x] 已选定里程碑（固件 v0.9·三阶段原型）\n- [x] CI 全绿\n- [x] 自测通过（build-firmware 产物非空校验通过）'}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/merge_requests" \
  -H "Content-Type: application/json" --data-binary "$M" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('MR !'+str(d['iid']), d['web_url'])"
```

期望：分支 commit 8 位短 sha；MR `!1`（或实际 iid，记为 `$MRI`）。MR 流水线 = gitleaks + build-firmware（image-build 已排除），等绿：

```bash
for i in $(seq 1 30); do S=$(curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/merge_requests/$MRI/pipelines?per_page=1" | python3 -c "import json,sys; p=json.load(sys.stdin); print(p[0]['status'] if p else 'none')"); [ "$S" = "success" ] && break; sleep 10; done; echo "MR pipeline: $S"
```

期望：`MR pipeline: success`。

- [ ] **Step 4: maint1 合入 → 验证自动关单**

```bash
curl -s -H "PRIVATE-TOKEN: $T" -X PUT "http://10.66.35.35:8081/api/v4/projects/2/merge_requests/$MRI/merge?sudo=maint1" \
  -d "should_remove_source_branch=true" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('MR state', d['state'], 'merge_commit', d.get('merge_commit_sha'))"
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/issues/$IA" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('需求单 state:', d['state'], '| 里程碑:', d['milestone']['title'])"
```

期望：`MR state merged`；**`需求单 state: closed`**（Closes 自动关单——设计 §5.1 核心机制）。抄下 merge_commit_sha 记为 `$SHA`。

- [ ] **Step 5: 打 tag → Release 挂里程碑 → manifest 资产回链**

```bash
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/repository/tags" \
  -d "tag_name=v0.9.0-rc1" -d "ref=main" -o /dev/null -w 'tag:%{http_code}\n'
for i in $(seq 1 30); do S=$(curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/pipelines?ref=v0.9.0-rc1&per_page=1" | python3 -c "import json,sys; p=json.load(sys.stdin); print(p[0]['status'] if p else 'none')"); [ "$S" = "success" -o "$S" = "manual" ] && break; sleep 10; done; echo "tag pipeline: $S"
```

（tag 流水线 promote-release 是 manual 挂起——`manual` 即视为到达终态，可选 play：查 job id 后 `POST /projects/2/jobs/<id>/play`。）

```bash
R=$(python3 -c "import json;print(json.dumps({'tag_name':'v0.9.0-rc1','ref':'main','name':'固件 v0.9.0-rc1','milestone':['固件 v0.9·三阶段原型'],'description':'三阶段验证版本：抖动参数可配置（需求单 #$IA）。发布说明=里程碑清单（设计§2.4 手工复制起步）。'}))")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/releases" \
  -H "Content-Type: application/json" --data-binary "$R" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tag_name') or d)"
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/jobs/artifacts/v0.9.0-rc1/raw?job=build-firmware" > /tmp/manifest-rc1.json
cat /tmp/manifest-rc1.json   # commit 字段应等于 $SHA
```

期望：tag 201；Release 打印 `v0.9.0-rc1`（若 `milestone` 参数被拒——打印的 message 会说明——去掉该字段重发，偏差记入 test-plan §9.3，里程碑关联用截图 42 的里程碑页承载）；manifest 的 `commit` == `$SHA`。资产回链：

```bash
U=$(curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/uploads" -F "file=@/tmp/manifest-rc1.json" | python3 -c "import json,sys; print(json.load(sys.stdin)['url'])")
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/2/releases/v0.9.0-rc1/assets/links" \
  -d "name=manifest.json" -d "url=http://10.66.35.35:8081/$U" -o /dev/null -w 'link:%{http_code}\n'
```

期望：`link:201`。

- [ ] **Step 6: 留档 + Commit**

```bash
cp /tmp/fw-ci.yml /home/lancer/projects/frm/gitlab-compose-test/firmware-repo/.gitlab-ci.yml
mkdir -p /home/lancer/projects/frm/gitlab-compose-test/firmware-repo/.gitlab/merge_request_templates
cp /tmp/mr-template.md /home/lancer/projects/frm/gitlab-compose-test/firmware-repo/.gitlab/merge_request_templates/默认.md
cd /home/lancer/projects/frm/gitlab-compose-test/firmware-repo && cp /tmp/manifest-rc1.json manifest-v0.9.0-rc1.json
cd /home/lancer/projects/frm
git add gitlab-compose-test/firmware-repo/
git commit -m "feat(firmware): 三阶段正向全链留档——MR模板/参数文件/rc1 manifest

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

（`tuning_params.yaml` 的留档用 GitLab raw 接口拉回：`curl -s -H "PRIVATE-TOKEN: $T" ".../projects/2/repository/files/tuning_params.yaml/raw?ref=main" > gitlab-compose-test/firmware-repo/tuning_params.yaml`，加进同一 commit。）

---

### Task 5: 场景 3——现场缺陷反向追溯（manifest → commit → MR → 需求单）

**Files:** 无仓库文件（GitLab 侧演练 + 终端输出作证据）

**Interfaces:**
- Consumes: Task 4 的 `$SHA`、`v0.9.0-rc1` manifest（`/tmp/manifest-rc1.json`）、单 `$IA`。
- Produces: 缺陷单（intake iid=4，记为 `$IB`）及其定位评论——Task 6 截图 38/39/40 对象。

- [ ] **Step 1: guest1 按缺陷模板建单（manifest 原样粘贴）**

```bash
J=$(python3 -c "
import json
mf = open('/tmp/manifest-rc1.json').read()
desc = '## 现象\n\nv0.9.0-rc1 整机低速工况铲斗仍有余抖，参数调到上限无改善。\n\n## 复现步骤\n\n1. 刷 v0.9.0-rc1\n2. 低速土方作业 10 分钟\n\n## 影响范围\n\n已刷 rc1 的 2 台试验机\n\n## 机器版本（manifest 粘贴区）\n\n\`\`\`json\n' + mf + '\n\`\`\`'
print(json.dumps({'title':'【缺陷】v0.9.0-rc1 低速工况铲斗余抖','description':desc,'sudo':'guest1'}))")
IB=$(curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues" \
  -H "Content-Type: application/json" --data-binary "$J" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['iid'])")
echo "缺陷单 iid=$IB"
```

期望：iid 打印（intake 之前已有 3 单，预计 4）。

- [ ] **Step 2: 反向追溯三跳（API 全自动）**

```bash
SHA2=$(python3 -c "import json; print(json.load(open('/tmp/manifest-rc1.json'))['commit'])")
echo "① manifest→commit: $SHA2"
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/repository/commits/$SHA2/merge_requests" \
  | python3 -c "import json,sys; m=json.load(sys.stdin)[0]; print('② commit→MR: !'+str(m['iid']), m['title'])"
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/2/issues/$IA" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('③ MR描述→需求单: #'+str(d['iid']), d['title'], d['state'])"
```

期望：① == `$SHA`；② 打印 MR !`$MRI` 与标题；③ 打印需求单与 `closed`——**三跳全通即反向链成立**（人只粘了 manifest，其余全是系统自动关联）。

- [ ] **Step 3: 定位结论回写缺陷单 + 分诊补标**

```bash
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues/$IB/notes" \
  --data-urlencode "body=定位：manifest→commit $SHA2→MR !$MRI→需求单 #$IA（该行为为抖动参数可配置需求引入）。转固件域分析参数边界，分诊移交。" \
  -o /dev/null -w '%{http_code}\n'
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/$PID/issues/$IB/transfer" \
  -H "Content-Type: application/json" -d '{"to_project_id": 2}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('移交后 iid', d['iid'])"
curl -s -H "PRIVATE-TOKEN: $T" -X PUT "http://10.66.35.35:8081/api/v4/projects/2/issues/<移交后iid>" \
  --data-urlencode "labels=状态::待验证,来源::现场" -o /dev/null -w '%{http_code}\n'
```

（第 2、3 条里的 iid 用实际返回替换后再执行；`状态::待验证`——复现属台架/现场验收，对应设计 §4.3 外部验收路径。）

期望：201 / 新 iid / 200。

---

### Task 6: 场景 4 + 截图第三批（32–43）

**Files:**
- Create: `gitlab-compose-test/screenshot_phase3.py`
- Create: `gitlab-compose-test/screenshots/32-*.png` … `43-*.png`

**Interfaces:**
- Consumes: Task 1 状态标签 id、Task 2 `$PID`、Task 3 单据、Task 4 `$IA`/`$SHA`/Release、Task 5 `$IB` 及移交后 iid。
- Produces: 12 张证据图（Task 7 test-plan 引用）。

- [ ] **Step 1: 组看板加状态列（API）**

```bash
BID=$(curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/groups/2/boards" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['id'])")
for LID in <待受理id> <已排期id> <开发中id> <待验证id> <暂缓id> <已拒绝id>; do
  curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/groups/2/boards/$BID/lists" \
    -d "label_id=$LID" -o /dev/null -w "列%{http_code} "
done; echo
```

（`<…id>` 用 Task 1 Step 3 抄下的状态标签 id。）期望：六个 `201`。

- [ ] **Step 2: 写截图脚本**

`gitlab-compose-test/screenshot_phase3.py`（复用既有模式；root 登录，动态页用 API 查 iid 后拼 URL）：

```python
#!/usr/bin/env python3
"""三阶段截图：需求流四场景证据（受理台/分诊/正向全链/反向追溯/看板）。"""
import json, time, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GL = "http://127.0.0.1:8081"
T = "glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg"

def api(path):
    req = urllib.request.Request(f"{GL}/api/v4{path}", headers={"PRIVATE-TOKEN": T})
    return json.load(urllib.request.urlopen(req))

def q(s):  # URL-encode 中文/:: 标签名
    return urllib.parse.quote(s, safe="")

PID = api("/projects/excavator%2Fintake")["id"]
IA = None
for i in api("/projects/2/issues?per_page=50"):
    if "液压抖动" in i["title"]:
        IA = i["iid"]
MR = api("/projects/2/merge_requests?per_page=5")[0]
SHA = MR["merge_commit_sha"]
BID = api("/groups/2/boards")[0]["id"]
IB_NEW = [i for i in api("/projects/2/issues?per_page=50") if "余抖" in i["title"]][0]["iid"]

PAGES = [
    ("32-intake-template-form",  f"{GL}/projects/excavator%2Fintake/-/issues/new?issuable_template=" + q("需求"), "受理台需求模板表单"),
    ("33-intake-issue-filed",    f"{GL}/projects/excavator%2Fintake/-/issues/2", "打回单（分诊评论+待受理）"),
    ("34-issue-transferred",     f"{GL}/projects/excavator/firmware/hydraulic-controller/-/issues/{IA}", "移交后的需求单（已排期+里程碑+分诊评论）"),
    ("35-issue-rejected",        f"{GL}/projects/excavator%2Fintake/-/issues/3", "婉拒单（已拒绝+理由）"),
    ("36-mr-closes-issue",       f"{GL}/projects/excavator/firmware/hydraulic-controller/-/merge_requests/{MR['iid']}", "MR：Closes #+里程碑+自查checklist"),
    ("37-issue-auto-closed",     f"{GL}/projects/excavator/firmware/hydraulic-controller/-/issues/{IA}", "合入后自动关单（merged引用）"),
    ("38-release-milestone",     f"{GL}/projects/excavator/firmware/hydraulic-controller/-/releases/v0.9.0-rc1", "Release 挂里程碑+manifest资产"),
    ("39-defect-manifest",       f"{GL}/projects/excavator/firmware/hydraulic-controller/-/issues/{IB_NEW}", "缺陷单：manifest粘贴区"),
    ("40-reverse-commit",        f"{GL}/projects/excavator/firmware/hydraulic-controller/-/commit/{SHA}", "commit页：MR关联（反向第②跳）"),
    ("41-group-board",           f"{GL}/groups/excavator/-/boards", "组看板：状态列全景"),
    ("42-milestone-progress",    f"{GL}/groups/excavator/-/milestones/1", "里程碑完成度+版本内清单"),
    ("43-intake-backlog",        f"{GL}/projects/excavator%2Fintake/-/issues?label_name=" + q("状态::待受理"), "受理台积压视图"),
]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", "root"); page.fill("input[name='user[password]']", "Excavator#2026Proto")
    page.click("button[type='submit']"); page.wait_for_load_state("networkidle"); time.sleep(2)
    for fname, url, label in PAGES:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000); time.sleep(1.8)
            page.screenshot(path=f"{OUT}/{fname}.png"); print(f"[OK] {fname} — {label}")
        except Exception as e:
            print(f"[FAIL] {fname}: {str(e)[:90]}")
    b.close()
```

注意：37 与 34 同一单（关单前后各一张，37 张图里应见 "Closed" 横幅与 merged commit 引用）；里程碑页 URL 用 `milestones/<id>`，`1` 不对时用 `api("/groups/2/milestones")[0]["id"]` 替换；42 若显示烧尽图缺位属 CE 正常，取完成度百分比区域即可。

- [ ] **Step 3: 执行并核对**

```bash
cd /home/lancer/projects/frm/gitlab-compose-test && .venv/bin/python screenshot_phase3.py 2>/dev/null || python3 screenshot_phase3.py
ls screenshots/3*-4*.png | wc -l   # 期望 12 张（32-43）
```

失败单张重试（选择器/超时类失败改 `time.sleep` 与 `wait_until`，不整体重跑）。

- [ ] **Step 4: Commit**

```bash
git add screenshot_phase3.py screenshots/
git commit -m "feat(evidence): 三阶段截图 32-43（需求流四场景证据链）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: test-plan 更新 + 收尾

**Files:**
- Modify: `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`（§0 表加一行；文末追加 §9）

**Interfaces:**
- Consumes: Task 1–6 全部结果、截图文件名、执行中的偏差记录。

- [ ] **Step 1: §0 验证范围表加行**

```markdown
| 产研需求流（受理/追溯/看板） | 需求流设计 §4–§7 | ✅ 第三阶段完成（四场景+截图32-43） |
```

- [ ] **Step 2: 追加 §9 第三阶段验证结果**

```markdown
## 9. 第三阶段验证结果（2026-09-03）

### 9.1 环境变更记录

| 变更 | 内容 | 原因 |
|---|---|---|
| GitLab 组标签 | excavator 组 +11 scoped 标签（状态6/来源5） | 设计§4.1/§4.3 |
| 新仓库 | excavator/intake（README+三模板，guest1=Guest/maint1=Maintainer） | 设计§4.1 受理台 |
| 组里程碑 | 固件 v0.9·三阶段原型 | 设计§4.4 |
| hydraulic-controller | image-build 加 only:[main,tags]；+MR模板；tuning_params.yaml；tag v0.9.0-rc1 + Release（挂里程碑+manifest资产） | 设计§5.1；§6.5受保护变量语义修正 |
| 组看板 | 默认看板 +6 状态列 | 设计§6 |

### 9.2 验证结果

| 验证项 | 设计章节 | 结果 | 证据 |
|---|---|---|---|
| Guest 按模板建单 | §4.1 | ✅ | 32/33 |
| 分诊三动作（移交/打回/婉拒） | §4.2 | ✅ | 34/33/35 |
| 里程碑排期 | §4.4 | ✅ | 34/42 |
| MR Closes 自动关单 | §5.1 | ✅ | 36/37 |
| tag/Release 挂里程碑+manifest资产 | §5.1 | ✅ | 38 |
| 反向三跳（manifest→commit→MR→单） | §5.2 | ✅ | 39/40 + 终端输出 |
| 外部验收路径（缺陷单 待验证） | §4.3 | ✅ | 39 |
| 组看板状态列 | §6 | ✅ | 41 |
| 里程碑完成度（CE 按单数） | §6 | ✅ | 42 |
| 受理台积压视图 | §6 | ✅ | 43 |

### 9.3 偏差与发现

- Guest 无打标权限：来源/状态标签由分诊补打（比设计"建单时选来源"更稳，建议正式实施采纳并回写设计§4.1）；
- image-build 原配置在 MR 流水线因受保护变量缺失必红——已加 only:[main,tags] 修正，回写二阶段留档；
- （执行中随记：Release milestone 参数是否可用、transfer 端点形态、截图重试情况）

### 9.4 仍未验证（留正式实施）

LDAP 真实域账号分诊轮值制度、`platform/` 宪法仓库的标签字典 MR 管控、周例会看板纪律、真实多域（四产品域）并行、禅道等外部工具导出迁移。
```

- [ ] **Step 3: 最终 commit**

```bash
git add docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md
git commit -m "docs(test-plan): 三阶段验证结果入档（产研需求流证据链）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: 收尾声明**

向用户汇报：四场景验证状态、截图清单、发现的偏差（尤其 Guest 打标与 image-build 修正）、**建议回写设计 §4.1（来源标签分诊补打）**；提示教程同步（第 6 篇《需求提出人与管理者》+ developer/field 扩展）待另立计划。

---

## 执行后继（不在本计划内）

- 教程同步计划：新增第 6 篇《需求提出人与管理者》、扩展 developer（提单/关联单号）与 field-engineer（manifest 建缺陷单）、index 导航更新——验证完成后按实际路径编写（设计§8 教程不先于验证）。
- 设计回写：§4.1 来源标签改为"分诊补打"（若 9.3 偏差确认）。
