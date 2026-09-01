# Harbor / MinIO 二阶段验证 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 frm 本地原型中接入 Harbor（直推+代理缓存）与 MinIO（三桶三场景），补齐设计 §6.4 四类产物存放分工的最后两类证据，产出截图与 test-plan 更新。

**Architecture:** 现有 `gitlab-compose-test/docker-compose.yml`（gitlab + runner，frm-net）扩展两组服务：MinIO（server + mc 初始化，端口 9002/9003）与 Harbor v2.12.3（~10 组件容器翻译进主 compose，端口 8084，http+insecure）。CI 侧新建 `excavator/autonomy/perception` 示例仓库走 MinIO 三场景，`firmware/hydraulic-controller` 加镜像构建 job 走 Harbor。凭据全部走 GitLab 受保护变量。

**Tech Stack:** Docker Compose v2.40、Harbor v2.12.3（goharbor 镜像，hub.rat.dev 源已实测可达）、MinIO（本地已有 minio/minio:latest）、mc、GitLab CE 19.3.1 API v4、Playwright（复用第一阶段截图脚本模式）、root PAT `glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg`（有效期至 2026-10-01，name=phase2-plan）。

## Global Constraints

- 所有 GitLab API 调用用 root PAT：`T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg`，API base `http://10.66.35.35:8081/api/v4`。
- Harbor 版本锁定 `v2.12.3`（已实测 hub.rat.dev 可拉该 tag）；镜像源格式 `hub.rat.dev/goharbor/<组件>:v2.12.3`，拉完 `docker tag` 回 `goharbor/<组件>:v2.12.3`。
- 端口铁律：Harbor 对外 8084；MinIO API 9002 / Console 9003。不得占用 8080/9000/9001（pih 项目）与 8081/8082（GitLab）。
- 宿主机 IP `10.66.35.35`；runner 为 **shell executor**（容器内**无 docker CLI**，CI 里的 docker 命令需先安装 docker CLI 或改用挂载方式，见 Task 6 处理）。
- 原型凭据（沿用第一阶段风格，不入正式环境）：Harbor admin `Harbor#2026Proto`；MinIO root `Excavator#2026Proto`；MinIO 各桶凭据见 Task 3。
- GitLab 项目路径写 API 时 URL-encode：`excavator%2Fautonomy%2Fperception`。
- 截图编号从 21 续起，存 `gitlab-compose-test/screenshots/`，命名 `NN-描述.png`。
- git 提交信息用中文、conventional commit 前缀，末尾加 `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`。
- 每个任务完成即 commit（screenshots、compose、脚本入库；`config/ logs/ data/ runner-config/ minio-data/ harbor-data/` 不入库，加 .gitignore）。

---

### Task 1: MinIO 服务进 compose 并建桶

**Files:**
- Modify: `gitlab-compose-test/docker-compose.yml`（追加 minio + minio-init 两服务、minio-data 卷说明）
- Modify: `gitlab-compose-test/.gitignore`（加 `minio-data/`）

**Interfaces:**
- Produces: MinIO API `http://frm-minio:9002`（容器内）/ `http://10.66.35.35:9002`（宿主）；Console `http://10.66.35.35:9003`；root 凭据 `Excavator#2026Proto`；桶 `dataset-model`、`field-dropzone`、`training-output`（Task 3/4/5/7 依赖）。

- [ ] **Step 1: 停止并追加 compose 服务**

```bash
cd /home/lancer/projects/frm/gitlab-compose-test
```

在 `docker-compose.yml` 的 `gitlab-runner` 服务之后、`networks:` 之前追加（保持既有缩进 2 空格）：

```yaml
  # ── 二阶段：MinIO 对象存储（§6.4 大文件归宿 / §7.2 现场数据通道）──
  # 端口避开 pih 项目已占用的 9000/9001：9002 API、9003 Console
  minio:
    image: minio/minio:latest          # 本地已有镜像，无需拉取
    container_name: frm-minio
    restart: unless-stopped
    command: server /data --console-address ":9003"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: "Excavator#2026Proto"
    ports:
      - "9002:9002"   # S3 API（CI / mc 用）
      - "9003:9003"   # Web Console（截图用）
    volumes:
      - ./minio-data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - frm-net

  # 一次性初始化：建三桶（幂等，重跑无害）
  minio-init:
    image: minio/mc:latest
    container_name: frm-minio-init
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      sh -c "
      mc alias set local http://frm-minio:9002 minioadmin 'Excavator#2026Proto' &&
      mc mb -p local/dataset-model local/field-dropzone local/training-output &&
      echo 'buckets ready'"
    networks:
      - frm-net
    restart: "no"
```

注意：`minio/mc:latest` 已就位（实测 `docker pull docker.m.daocloud.io/minio/mc:latest` 成功后 retag；hub.rat.dev 拉它 404，勿用）。

`.gitignore` 追加一行：

```
# MinIO 运行时数据（二阶段）
minio-data/
```

- [ ] **Step 2: 起服务并验证**

```bash
docker compose up -d minio minio-init
docker compose ps minio            # 期望 healthy（约 30s）
docker logs frm-minio-init 2>&1 | tail -4   # 期望出现 buckets ready
curl -s -o /dev/null -w '%{http_code}\n' http://10.66.35.35:9002/minio/health/live   # 期望 200
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml .gitignore
git commit -m "feat(compose): MinIO 进原型（9002/9003，三桶初始化）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: mc 侧写工具 + 现场回传模拟（§7.2 投放区）

**Files:**
- Create: `gitlab-compose-test/minio-ops.sh`（平台侧/现场侧 mc 操作合集，自包含脚本）

**Interfaces:**
- Consumes: Task 1 的 MinIO 与 `dataset-model`/`field-dropzone` 桶。
- Produces: 脚本内函数式的子命令 `field-upload`（现场凭据上传）、`dropzone-ls`（write-only 验证）、`archive-dropzone`（平台归档）——Task 7 截图直接调用本脚本复现；受_limit 只读凭据 `fieldagent`（Task 7 截图用）。

- [ ] **Step 1: 创建受限现场凭据与 write-only 策略**

写 `gitlab-compose-test/minio-ops.sh`（完整内容）：

```bash
#!/usr/bin/env bash
# MinIO 三场景操作脚本（§6.4/§7.2）—— 二阶段验证的可复现入口
# 用法: ./minio-ops.sh <setup|field-upload|dropzone-ls|archive-dropzone|seed-dataset>
set -euo pipefail
MC="docker run --rm --network frm-gitlab_frm-net minio/mc:latest"
ALIAS="mc alias set L http://frm-minio:9002 minioadmin Excavator#2026Proto >/dev/null"

case "${1:-}" in
  setup)     # 一次性：建现场受限用户（只能写投放区，不能列目录）
    $MC $ALIAS
    $MC admin user add L fieldagent FieldAgent#2026
    $MC admin policy create L dropzone-write /dev/stdin <<'POL'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:PutObject"],"Resource":["arn:aws:s3:::field-dropzone/*"]}]}
POL
    $MC admin policy attach L dropzone-write --user fieldagent
    echo "[setup] fieldagent 用户就绪（仅 s3:PutObject 到 field-dropzone/*）"
    ;;
  field-upload)   # 现场：传感器数据回传（§7.2 数据向内流）
    shift; F="${1:-/tmp/sensor-$(date +%s).bag}"
    head -c 2097152 /dev/urandom > "$F"   # 2MB 模拟传感器数据
    $MC $ALIAS
    $MC cp "$F" L/field-dropzone/$(basename "$F")
    echo "[field-upload] $(basename "$F") 已进投放区"
    ;;
  dropzone-ls)    # 验证 write-only：fieldagent 列目录应被拒
    $MC alias set F http://frm-minio:9002 fieldagent FieldAgent#2026 >/dev/null
    echo "--- fieldagent 尝试列目录（期望 AccessDenied）:"
    $MC ls F/field-dropzone && echo "!!! 未被拒绝" || echo "[OK] 列目录被拒（write-only 生效）"
    ;;
  archive-dropzone)   # 平台侧：取走投放区数据归档到 dataset-model
    $MC $ALIAS
    $MC mirror --overwrite L/field-dropzone L/dataset-model/field-archive/
    $MC rm --force --recursive L/field-dropzone/
    echo "[archive-dropzone] 投放区已归档并清空"
    ;;
  seed-dataset)  # 平台侧：放示例数据集 + 打印 sha256（CI 校验用）
    $MC $ALIAS
    head -c 5242880 /dev/urandom > /tmp/demo-dataset.bin   # 5MB 假数据集
    SHA=$(sha256sum /tmp/demo-dataset.bin | cut -d' ' -f1)
    $MC cp /tmp/demo-dataset.bin L/dataset-model/datasets/demo-dataset-v1.bin
    echo "{\"path\":\"s3://dataset-model/datasets/demo-dataset-v1.bin\",\"size\":5242880,\"sha256\":\"$SHA\"}"
    ;;
  *) echo "用法: $0 setup|field-upload|dropzone-ls|archive-dropzone|seed-dataset"; exit 2;;
esac
```

注意：`$MC` 每次都是独立 `docker run`，`$ALIAS` 变量在 `$MC` 后展开为它的参数；`field-upload` 里的本地文件路径要挂载进容器——把 `$MC` 对 `field-upload`/`seed-dataset` 两个子命令改为带 `-v /tmp:/tmp` 的形式（`docker run --rm -v /tmp:/tmp --network ...`）。

- [ ] **Step 2: 执行 setup + 三步验证**

```bash
chmod +x gitlab-compose-test/minio-ops.sh
gitlab-compose-test/minio-ops.sh setup
gitlab-compose-test/minio-ops.sh field-upload          # 模拟现场回传一个文件
gitlab-compose-test/minio-ops.sh dropzone-ls           # 期望: AccessDenied + [OK] write-only 生效
```

- [ ] **Step 3: Commit**

```bash
git add gitlab-compose-test/minio-ops.sh
git commit -m "feat(minio): 投放区 write-only 策略与现场回传模拟脚本

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: autonomy/perception 仓库 + 数据集指针 + MinIO 取数流水线（§6.4）

**Files:**
- Create: GitLab 项目 `excavator/autonomy/perception`（含 `.gitlab-ci.yml`、`datasets.manifest.json`、`train.py`）——本地临时目录构建后 API 推送

**Interfaces:**
- Consumes: Task 1 的 `dataset-model` 桶；Task 2 `seed-dataset` 输出的 sha256；GitLab CI 变量 `MINIO_ENDPOINT`/`MINIO_KEY`/`MINIO_SECRET`（Task 5 定义）。
- Produces: 流水线 job `fetch-dataset`（拉取+校验）与 `train-model`（产出权重→推 `training-output`→manifest 记指针），Task 7 截图对象。

- [ ] **Step 1: 建仓库（API）**

```bash
T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects" \
  -d "name=perception" -d "path=perception" -d "namespace_id=6" \
  -d "default_branch=main" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('path_with_namespace') or d)"
```

（`namespace_id=6` 是 `excavator/autonomy` 组 id——若返回错误，先查：`curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/groups/excavator%2Fautonomy" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])"`，用查到的值替换。）

- [ ] **Step 2: 播种数据集并记录指针**

```bash
gitlab-compose-test/minio-ops.sh seed-dataset
# 输出形如 {"path":"s3://dataset-model/datasets/demo-dataset-v1.bin","size":5242880,"sha256":"<64位>"}——抄下 sha256
```

- [ ] **Step 3: 仓库三文件（本地构建树 + API 提交）**

本地目录 `/tmp/perception-repo/`：

`datasets.manifest.json`（sha256 用 Step 2 实际输出替换 `<SHA256>`）：

```json
{
  "datasets": [
    {
      "name": "demo-dataset-v1",
      "path": "s3://dataset-model/datasets/demo-dataset-v1.bin",
      "endpoint": "http://frm-minio:9002",
      "size": 5242880,
      "sha256": "<SHA256>"
    }
  ]
}
```

`train.py`（假训练，原型只验证数据流）：

```python
#!/usr/bin/env python3
"""原型假训练：读数据集→产"模型权重"。真实 GPU 训练是正式实施项。"""
import hashlib, json, os, sys

data_path = sys.argv[1]
with open(data_path, "rb") as f:
    blob = f.read()
print(f"dataset {len(blob)} bytes loaded")

os.makedirs("outputs", exist_ok=True)
weights = hashlib.sha256(blob).digest() + blob[:1024]   # 内容派生的假权重
with open("outputs/model.pt", "wb") as f:
    f.write(weights)
print(json.dumps({"model": "outputs/model.pt", "params": len(weights)}))
```

`.gitlab-ci.yml`：

```yaml
# 算法仓库层：include 通用层（§6.2）+ MinIO 数据/产物通道（§6.4 二阶段验证）
include:
  - project: excavator/platform/ci-templates
    ref: main
    file: autonomy.yml

stages:
  - scan
  - data
  - build
  - publish

gitleaks-check:
  stage: scan
  script:
    - echo "gitleaks密钥扫描占位(§6.5)"
  only:
    - merge_requests

fetch-dataset:
  stage: data
  script:
    - echo "[fetch] 从 MinIO 拉数据集（git 只存指针 §6.4）"
    - KEY=${MINIO_KEY} SECRET=${MINIO_SECRET} EP=${MINIO_ENDPOINT}
    - sha_expect=$(python3 -c "import json; print(json.load(open('datasets.manifest.json'))['datasets'][0]['sha256'])")
    - curl -s -u "$MINIO_KEY:$MINIO_SECRET" -o demo-dataset.bin "$MINIO_ENDPOINT/dataset-model/datasets/demo-dataset-v1.bin"
    - sha_got=$(sha256sum demo-dataset.bin | cut -d' ' -f1)
    - echo "expect=$sha_expect got=$sha_got"
    - test "$sha_expect" = "$sha_got" || (echo "sha256 校验失败" && exit 1)
    - echo "[fetch] 校验通过，数据集可用"
  artifacts:
    paths: [demo-dataset.bin]
    expire_in: 1 hour

train-model:
  stage: build
  script:
    - python3 train.py demo-dataset.bin
    - SHA=$(sha256sum outputs/model.pt | cut -d' ' -f1)
    - SIZE=$(stat -c%s outputs/model.pt)
    - curl -s -u "$MINIO_KEY:$MINIO_SECRET" -X PUT --data-binary @outputs/model.pt "$MINIO_ENDPOINT/training-output/perception/model-$CI_COMMIT_SHORT_SHA.pt"
    - printf '{"name":"perception","commit":"%s","model_uri":"s3://training-output/perception/model-%s.pt","size":%s,"sha256":"%s","build_time":"%s","runner":"%s"}\n' "$CI_COMMIT_SHA" "$CI_COMMIT_SHORT_SHA" "$SIZE" "$SHA" "$CI_JOB_STARTED_AT" "$CI_RUNNER_DESCRIPTION" > manifest.json
    - cat manifest.json
  artifacts:
    paths: [manifest.json]

promote-model:
  stage: publish
  script:
    - echo "模型晋升（§6.3 手动批准）——原型占位"
  when: manual
```

注意：`fetch-dataset` 里那行 `KEY=${MINIO_KEY} ...` 是冗余行，写入时删掉，只保留实际用到的变量引用。

用 API 逐个提交三文件（每个文件一次 commit，`/repository/files/<urlencoded-path>` PUT，`branch=main`、`commit_message` 自述）。命令模板：

```bash
B64=$(base64 -w0 /tmp/perception-repo/datasets.manifest.json)
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/excavator%2Fautonomy%2Fperception/repository/files" \
  -d "branch=main" -d "encoding=base64" -d "content=$B64" \
  -d "commit_message=数据集指针清单（大文件不进git §6.4）" -d "file_path=datasets.manifest.json" | head -c 200
```

（train.py、.gitlab-ci.yml 同法；首个文件提交需带 `-d "start_branch=main"`。）

- [ ] **Step 4: 检查流水线预期失败方式**

push 后自动触发流水线；此时 CI 变量（Task 5）尚未配置，`fetch-dataset` 会因 `$MINIO_KEY` 为空 curl 失败——**这是预期的中间态**，记录 pipeline id，Task 5 配好变量后 retry 即绿。不 commit 仓库文件到 frm git（它是 GitLab 侧产物），只把三文件留档到 `gitlab-compose-test/perception-repo/` 目录一并入库供复现。

```bash
mkdir -p gitlab-compose-test/perception-repo
cp /tmp/perception-repo/{datasets.manifest.json,train.py,.gitlab-ci.yml} gitlab-compose-test/perception-repo/
```

---

### Task 4: Harbor 镜像就位（后台任务，与 Task 1-3 并行已启动）

**Files:** 无仓库文件（纯环境操作）

**Interfaces:**
- Produces: 本地 `goharbor/*:v2.12.3` 十个镜像（Task 6 compose 依赖）。组件清单：harbor-core、harbor-jobservice、harbor-registry、harbor-registryctl、harbor-db、harbor-redis、harbor-portal、harbor-trivy-adapter、harbor-nginx、harbor-log。

- [ ] **Step 1: 确认后台拉取完成**

后台任务已在跑（registryctl/core 已就位）。检查：

```bash
docker images --format '{{.Repository}}:{{.Tag}}' | grep '^goharbor' | sort
```

期望 10 行（v2.12.3 全套）。若个别缺：

```bash
timeout 550 docker pull hub.rat.dev/goharbor/<组件>:v2.12.3
docker tag hub.rat.dev/goharbor/<组件>:v2.12.3 goharbor/<组件>:v2.12.3
```

- [ ] **Step 2: 补拉 prepare 依赖（若走离线包方案则不需要）**

选定实现路径后此步可能被 Task 6 的替代方案覆盖，见 Task 6 开头说明。

---

### Task 5: GitLab 受保护 CI 变量（§6.5）

**Files:** 无仓库文件（GitLab 组级变量 + 触发重跑）

**Interfaces:**
- Consumes: MinIO 凭据（Task 1 root `minioadmin`/`Excavator#2026Proto`——CI 专用只读/读写凭据在 Step 1 建）；Harbor robot 凭据（Task 6 产出后回填）。
- Produces: 组 `excavator/autonomy` 变量 `MINIO_ENDPOINT=http://frm-minio:9002`、`MINIO_KEY`、`MINIO_SECRET`（masked+protected）；组 `excavator/firmware` 变量 `HARBOR_REGISTRY=10.66.35.35:8084`、`HARBOR_USER`、`HARBOR_PASS`（Task 6/7 依赖）。Task 3 的流水线 retry 即绿。

- [ ] **Step 1: 建 CI 专用 MinIO 凭据（最小权限）**

```bash
gitlab-compose-test/minio-ops.sh 之外的补充（直接 mc）:
docker run --rm --network frm-gitlab_frm-net minio/mc:latest sh -c "
mc alias set L http://frm-minio:9002 minioadmin Excavator#2026Proto &&
mc admin user add L ci-bot CiBot#2026 &&
mc admin policy create L ci-full /dev/stdin <<'POL'
{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\"],\"Resource\":[\"arn:aws:s3:::dataset-model/*\",\"arn:aws:s3:::training-output/*\"]}]}
POL
mc admin policy attach L ci-full --user ci-bot"
```

- [ ] **Step 2: 写入 GitLab 组变量（API）**

```bash
T=glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg
setvar() { curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/groups/$1/variables" -d key=$2 -d value=$3 -d masked=true -d protected=true -o /dev/null -w "$2:%{http_code}\n"; }
# autonomy 组（id 用实际值，查询: /api/v4/groups/excavator%2Fautonomy -> id）
setvar <autonomy_gid> MINIO_ENDPOINT http://frm-minio:9002
setvar <autonomy_gid> MINIO_KEY ci-bot
setvar <autonomy_gid> MINIO_SECRET 'CiBot#2026'
```

注意：`MINIO_ENDPOINT` 值含 `://` 与端口，不能 masked（GitLab 掩码要求 ≥8 字符且格式受限），对它单独用 `-d masked=false`。`CiBot#2026` 长 10 字符可 masked。

- [ ] **Step 3: retry Task 3 的流水线**

```bash
curl -s -H "PRIVATE-TOKEN: $T" -X POST "http://10.66.35.35:8081/api/v4/projects/excavator%2Fautonomy%2Fperception/pipelines/<pid>/retry" -o /dev/null -w '%{http_code}\n'
# 轮询至 success：
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/projects/excavator%2Fautonomy%2Fperception/pipelines?per_page=1" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['status'])"
```

期望 `success`；job 日志里 `MINIO_SECRET` 显示为 `[masked]`（截图素材，Task 7）。

---

### Task 6: Harbor 服务进 compose + 项目创建 + 镜像流水线（§5.3）

**Files:**
- Modify: `gitlab-compose-test/docker-compose.yml`（追加 Harbor ~10 服务）
- Modify: `gitlab-compose-test/.gitignore`（加 `harbor-data/`）
- Modify: `gitlab-compose-test/perception-repo/` 无关；firmware 流水线走 GitLab API 改 `excavator/firmware/hydraulic-controller` 的 `.gitlab-ci.yml`

**Interfaces:**
- Consumes: Task 4 的十个 goharbor 镜像；宿主 `/etc/docker/daemon.json`（需用户 sudo）。
- Produces: Harbor `http://10.66.35.35:8084`（admin/`Harbor#2026Proto`），项目 `frm-ci` + `docker-hub-proxy`（proxy 上游 `https://hub.rat.dev`，验证代理拓扑）；robot 账号凭据（回填 Task 5 组变量 HARBOR_*）；firmware 流水线新增 `image-build` job。

**实现路径决策（执行时二选一，先试 A）**：
- **路径 A（compose 直译）**：从官方 offline installer 的 `harbor/docker-compose.yml.jinja` 模板逐服务翻译。为拿到模板，需下载 730MB 离线包——太重，改为：从 GitHub `goharbor/harbor` 仓库 `make/` 目录直连拉模板文件（代理可达 raw.githubusercontent.com）。若模板拼装顺利走 A。
- **路径 B（离线包安装后收编）**：`wget` 离线包（730MB，代理 ~2h 或 hub.rat.dev 方式无直链）→ `./install.sh --with-trivy` 起原生 Harbor → `docker compose -f /data/harbor/docker-compose.yml` 导出服务定义 → 翻译进主 compose。**若 A 的模板拼装卡壳超过 30 分钟即转 B（用已拉好的本地镜像，install.sh 不再拉取）**。
- 无论 A/B：容器名加 `frm-harbor-` 前缀、挂 `./harbor-data/`、接 `frm-net`、对外仅暴露 8084。

- [ ] **Step 1: sudo 配 insecure-registries（用户执行）**

提示用户在提示符执行（`!` 前缀）：

```
! sudo bash -c 'cat /etc/docker/daemon.json 2>/dev/null; echo ---'
```

先看现有内容，然后给出合并后的完整文件让用户写入并重启：

```
! sudo bash -c 'test -f /etc/docker/daemon.json || echo "{}" > /etc/docker/daemon.json; python3 -c "
import json
d = json.load(open(\"/etc/docker/daemon.json\"))
d.setdefault(\"insecure-registries\", [])
if \"10.66.35.35:8084\" not in d[\"insecure-registries\"]: d[\"insecure-registries\"].append(\"10.66.35.35:8084\")
json.dump(d, open(\"/etc/docker/daemon.json\",\"w\"), indent=2)
" && systemctl restart docker'
```

重启后验证 pih 容器自动回来：`docker ps | grep pih`（期望 pih-web/app/postgres/minio 均 Up）。

- [ ] **Step 2: Harbor compose 服务起起来（按路径 A/B 的产出）**

```bash
docker compose up -d
docker compose ps | grep frm-harbor   # 期望 nginx(8084)/core/jobservice/registry 等 Up
curl -s -o /dev/null -w '%{http_code}\n' http://10.66.35.35:8084/api/v2.0/health   # 期望 200
curl -s -u "admin:Harbor#2026Proto" http://10.66.35.35:8084/api/v2.0/users/current | python3 -c "import json,sys; print(json.load(sys.stdin)['username'])"   # admin
```

- [ ] **Step 3: 建双项目 + robot 凭据（API）**

```bash
H="curl -s -u admin:Harbor#2026Proto -H Content-Type:application/json http://10.66.35.35:8084/api/v2.0"
$H/projects -d '{"project_name":"frm-ci","metadata":{"public":"false"}}' -o /dev/null -w 'frm-ci:%{http_code}\n' -X POST
$H/projects -d '{"project_name":"docker-hub-proxy","metadata":{"public":"true"},"registry_id":<rid>}' -o /dev/null -w 'proxy:%{http_code}\n' -X POST
```

先建 registry endpoint（proxy 的上游）再建 proxy 项目：

```bash
$H/registries -X POST -d '{"name":"rat-dev","url":"https://hub.rat.dev","type":"docker-hub","credential":{"type":"basic","access_key":"","access_secret":""}}' | python3 -c "import json,sys; print(json.load(sys.stdin).get('id'))"
```

（上游填 hub.rat.dev——它是实测可达的镜像源；本机 Docker Hub 直连不通，故代理拓扑指向可达上游，正式实施时改指内网 Nexus/上级 Harbor。）

robot 账号（CI 推送用）：

```bash
$H/projects/frm-ci/robots -X POST -d '{"name":"gitlab-ci","duration":-1,"access":[{"action":"push","resource":"repository"}]}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['name'], d.get('secret'))"
```

- [ ] **Step 4: firmware 仓库加 image-build job（API 改 .gitlab-ci.yml）**

在 `excavator/firmware/hydraulic-controller` 的 `.gitlab-ci.yml` 追加（保持既有内容，stages 加 `image`）：

```yaml
  # 二阶段：镜像出口收敛（§5.3）——CI 构建镜像推内网 Harbor，不直连外网
image-build:
  stage: image
  script:
    - echo "[image] 构建并推送 CI 基础镜像到 Harbor frm-ci 项目"
    - docker version || (apt-get update -qq && apt-get install -qqy docker.io >/dev/null)   # runner 容器内无 docker CLI，首次自装
    - export DOCKER_HOST=unix:///var/run/docker.sock
    - printf 'FROM docker.m.daocloud.io/library/alpine:latest\nLABEL org.opencontainers.image.revision=%s\n' "$CI_COMMIT_SHA" > Dockerfile.ci
    - docker build -t "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" -f Dockerfile.ci .
    - echo "$HARBOR_PASS" | docker login "$HARBOR_REGISTRY" -u "$HARBOR_USER" --password-stdin
    - docker push "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"
    - docker rmi "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA" || true
    # 从 Harbor 拉回验证（runner 一律走 Harbor §5.3）
    - docker pull "$HARBOR_REGISTRY/frm-ci/ci-base:$CI_COMMIT_SHORT_SHA"
```

注意：基础镜像用 `docker.m.daocloud.io/library/alpine:latest`（本地已有，Docker Hub 直连不通）；若 runner 容器内装 docker.io 因 apt 源受阻，降级为 `docker save`/`docker load` 方案或直接在流水线里用 `curl` 调 Harbor API 的 blob 上传（记录于 test-plan 的偏差说明）。stages 列表相应改为 `[scan, build, image, release]`。

- [ ] **Step 5: 回填 HARBOR_* 组变量并跑绿**

用 Task 5 Step 2 同法给 `excavator/firmware` 组写 `HARBOR_REGISTRY=10.66.35.35:8084`、`HARBOR_USER=robot$frm-ci+gitlab-ci`、`HARBOR_PASS=<robot secret>`。push 触发或 retry 流水线至 success。

- [ ] **Step 6: proxy 拉取验证 + Commit**

```bash
docker pull 10.66.35.35:8084/docker-hub-proxy/library/busybox:latest
curl -s -u admin:Harbor#2026Proto "http://10.66.35.35:8084/api/v2.0/projects/docker-hub-proxy/repositories" | python3 -m json.tool | head -20   # 期望 busybox 缓存记录
```

```bash
git add docker-compose.yml .gitignore
git commit -m "feat(compose): Harbor v2.12.3 进原型（8084，直推+代理缓存双项目）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: 截图第二批（编号续 21）

**Files:**
- Create: `gitlab-compose-test/screenshot_phase2.py`（仿 screenshot.py 的 Playwright 脚本）
- Create: `gitlab-compose-test/screenshots/21-*.png` 至 `~27-*.png`

**Interfaces:**
- Consumes: Task 1-6 全部运行态（GitLab root 登录、Harbor admin 登录、MinIO Console 登录、两条绿流水线、Harbor 缓存记录）。
- Produces: 验证证据图（Task 8 test-plan 引用）。

- [ ] **Step 1: 写截图脚本**

完整脚本（复用第一阶段模式：chromium at `/usr/bin/google-chrome`，viewport 1440×900，登录→逐页截）：

```python
#!/usr/bin/env python3
"""二阶段截图：Harbor 双项目与推拉记录、MinIO 三桶与投放区、两条流水线证据。"""
import sys, time
from playwright.sync_api import sync_playwright

OUT = "/home/lancer/projects/frm/gitlab-compose-test/screenshots"
GL, HB, MN = "http://127.0.0.1:8081", "http://10.66.35.35:8084", "http://10.66.35.35:9003"

def gl_shot(page):
    page.goto(f"{GL}/users/sign_in", wait_until="networkidle")
    page.fill("input[name='user[login]']", "root"); page.fill("input[name='user[password]']", "Excavator#2026Proto")
    page.click("button[type='submit']"); page.wait_for_load_state("networkidle"); time.sleep(2)
    PAGES = [
        ("21-perception-pipelines", f"{GL}/excavator/autonomy/perception/-/pipelines", "perception 流水线列表"),
        ("22-perception-green",     None, "perception 最新流水线全绿详情（URL 动态取）"),
        ("23-fetch-dataset-job",    None, "fetch-dataset job 日志（MinIO 拉取+sha256 校验+masked 变量）"),
        ("24-train-model-job",      None, "train-model job 日志（推 training-output+manifest 指针）"),
        ("25-fw-image-build-job",   None, "firmware image-build job 日志（docker push/pull Harbor）"),
    ]
    # 22-25 的 URL 由 API 查最新 pipeline/jobs 后填入（脚本内 requests 查询）
    import json, urllib.request
    hdr = {"PRIVATE-TOKEN": "glpat-dsd8nyjb7efZJJ-g4_uRrW86MQp1OjEH.01.0w1o12cfg"}
    def api(path):
        return json.load(urllib.request.urlopen(urllib.request.Request(f"{GL}/api/v4{path}", headers=hdr)))
    pl = api("/projects/excavator%2Fautonomy%2Fperception/pipelines?per_page=1")[0]
    jobs = api(f"/projects/excavator%2Fautonomy%2Fperception/pipelines/{pl['id']}/jobs")
    for fname, url, label in PAGES:
        if fname == "22-perception-green": url = f"{GL}/excavator/autonomy/perception/-/pipelines/{pl['id']}"
        if fname == "23-fetch-dataset-job": url = f"{GL}/excavator/autonomy/perception/-/jobs/{[j for j in jobs if j['name']=='fetch-dataset'][0]['id']}"
        if fname == "24-train-model-job":   url = f"{GL}/excavator/autonomy/perception/-/jobs/{[j for j in jobs if j['name']=='train-model'][0]['id']}"
        if fname == "25-fw-image-build-job":
            fw = api("/projects/excavator%2Ffirmware%2Fhydraulic-controller/pipelines?per_page=1")[0]
            fjobs = api(f"/projects/excavator%2Ffirmware%2Fhydraulic-controller/pipelines/{fw['id']}/jobs")
            url = f"{GL}/excavator/firmware/hydraulic-controller/-/jobs/{[j for j in fjobs if j['name']=='image-build'][0]['id']}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000); time.sleep(1.5)
            page.screenshot(path=f"{OUT}/{fname}.png"); print(f"[OK] {fname} — {label}")
        except Exception as e: print(f"[FAIL] {fname}: {str(e)[:80]}")

def hb_shot(page):
    page.goto(f"{HB}/harbor/sign-in", wait_until="networkidle")
    page.fill("input[name='login_name']", "admin"); page.fill("input[id='login_password'] ", "Harbor#2026Proto")
    page.click("button[id='log_on']"); page.wait_for_load_state("networkidle"); time.sleep(2)
    for fname, url, label in [
        ("26-harbor-projects",  f"{HB}/harbor/projects", "Harbor 项目列表（frm-ci + docker-hub-proxy）"),
        ("27-harbor-frmci",     f"{HB}/harbor/projects/frm-ci/repositories", "frm-ci 镜像仓（CI 推送的 ci-base）"),
        ("28-harbor-proxy",     f"{HB}/harbor/projects/docker-hub-proxy/repositories", "代理缓存项目（busybox 缓存记录）"),
    ]:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000); time.sleep(1.5)
            page.screenshot(path=f"{OUT}/{fname}.png"); print(f"[OK] {fname} — {label}")
        except Exception as e: print(f"[FAIL] {fname}: {str(e)[:80]}")

def mn_shot(page):
    page.goto(f"{MN}/login", wait_until="networkidle")
    page.fill("input[id='login-username']", "minioadmin"); page.fill("input[id='login-password']", "Excavator#2026Proto")
    page.click("button[type='submit']"); page.wait_for_load_state("networkidle"); time.sleep(2)
    for fname, url, label in [
        ("29-minio-buckets",     f"{MN}/buckets", "MinIO 三桶总览"),
        ("30-minio-dataset",     f"{MN}/buckets/dataset-model/browse", "dataset-model（数据集+现场归档）"),
        ("31-minio-training",    f"{MN}/buckets/training-output/browse", "training-output（模型权重）"),
    ]:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000); time.sleep(1.5)
            page.screenshot(path=f"{OUT}/{fname}.png"); print(f"[OK] {fname} — {label}")
        except Exception as e: print(f"[FAIL] {fname}: {str(e)[:80]}")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    ctx = browser.new_context(viewport={"width":1440,"height":900}, ignore_https_errors=True)
    page = ctx.new_page()
    gl_shot(page); hb_shot(page); mn_shot(page)
    browser.close()
```

注意：Harbor/MinIO 登录选择器以实际 DOM 为准（执行时先 `page.content()` 探一次再定），上例选择器是 Harbor 2.x/MinIO 常见值，失败即现场调整。截图失败不阻塞——逐张重试或手补。

- [ ] **Step 2: 执行并核对**

```bash
cd /home/lancer/projects/frm/gitlab-compose-test && .venv/bin/python screenshot_phase2.py 2>/dev/null || python3 screenshot_phase2.py
ls screenshots/2*-3*.png | wc -l    # 期望 ~11 张（21-31）
```

- [ ] **Step 3: Commit**

```bash
git add screenshot_phase2.py screenshots/
git commit -m "feat(evidence): 二阶段截图 21-31（Harbor/MinIO/流水线证据）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: test-plan 更新 + 收尾 commit

**Files:**
- Modify: `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`（§0 表 Harbor/MinIO 行改 ✅；新增"第二阶段验证结果"章节）

**Interfaces:**
- Consumes: Task 1-7 的全部结果与截图文件名。

- [ ] **Step 1: 更新 §0 表格行**

```markdown
| Harbor / MinIO | §6.4 / §11 | ✅ 第二阶段完成（Harbor 直推+代理、MinIO 三桶三场景） |
```

- [ ] **Step 2: 追加第二阶段验证结果章节（文档末尾）**

内容模板（结果列以实际执行为准逐格填）：

```markdown
## 8. 第二阶段验证结果（2026-09-01）

### 8.1 环境变更记录

| 变更 | 内容 | 原因 |
|---|---|---|
| docker-compose.yml | +minio/minio-init 两服务（9002/9003）；+Harbor v2.12.3 十服务（8084） | §6.4 两类产物归宿落地 |
| /etc/docker/daemon.json | insecure-registries 追加 10.66.35.35:8084 | Harbor http 原型简化（TLS 留正式实施） |
| 镜像源 | goharbor/* 经 hub.rat.dev 拉取后 retag | Docker Hub 直连不通的替代路径 |

### 8.2 验证结果

| 验证项 | 设计章节 | 结果 | 证据 |
|---|---|---|---|
| MinIO 三桶初始化 | §6.4 | ✅ | 29-minio-buckets.png |
| 大文件指针+CI 取数校验 | §6.4 | ✅ | 22-perception-green.png / 23-fetch-dataset-job.png |
| 现场投放区 write-only 回传 | §7.2 | ✅ | minio-ops.sh dropzone-ls 输出（AccessDenied） |
| 投放区归档 | §7.2 | ✅ | 30-minio-dataset.png（field-archive/ 目录） |
| 训练产物入库+manifest 指针 | §6.3/§6.4 | ✅ | 24-train-model-job.png / 31-minio-training.png |
| CI 凭据受保护+打码 | §6.5 | ✅ | 23-fetch-dataset-job.png（[masked]） |
| Harbor 直推（build→push→pull） | §5.3/§6.4 | ✅ | 25-fw-image-build-job.png / 27-harbor-frmci.png |
| Harbor 代理缓存拓扑 | §5.3 | ✅ | 28-harbor-proxy.png |
| compose 全家 healthy | — | ✅ | docker compose ps 输出 |

### 8.3 偏差与发现

（执行中记录：runner 无 docker CLI 的处理方式、proxy 上游选择、任何与设计的偏差及理由）

### 8.4 仍未验证（留正式实施）

Harbor TLS/漏洞扫描/多租户、MinIO 分布式与备份策略（§11 按资产备份）、Nexus、GPU 真实训练。
```

- [ ] **Step 3: 最终 commit**

```bash
git add docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md gitlab-compose-test/perception-repo/
git commit -m "docs(test-plan): 二阶段验证结果入档（Harbor/MinIO 证据链）

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
