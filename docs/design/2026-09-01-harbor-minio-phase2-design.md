# Harbor / MinIO 二阶段验证设计

- 日期：2026-09-01
- 状态：已与发起人逐节确认
- 依据：[统一代码管理体系设计](./2026-08-31-excavator-code-management-design.md) §5.3/§6.4/§6.5/§7.2、[原型验证结论](./2026-09-07-prototype-verification.md)（原验证计划 §0 曾标"Harbor/MinIO 二阶段为 ⏸"，原稿见 git 历史）
- 定位：补齐原型第一阶段未验证的两类产物归宿（容器镜像→Harbor、大文件→MinIO），使设计 §6.4 四类产物存放分工全部有本地证据；同时为正式实施阶段 1（基础设施：Nexus/Harbor 代理 + MinIO）提供原地复用的验证。

## 1. 背景与目标

第一阶段（2026-08-31 完成）验证了 GitLab 托管/权限/MR/CI/Release 附件/package registry，Harbor 与 MinIO 缺位。后果：设计承诺的"算法组 GPU 训练"与"现场数据回流"两条业务线在原型里没有落点，体系闭环缺一角。

二阶段在现有 compose（gitlab + runner）中加入 Harbor 与 MinIO，验证三个场景：

1. **镜像出口收敛**（§5.3）：CI 拉基础镜像不直连外网，一律走内网 Harbor 代理缓存；训练镜像构建后推回 Harbor，runner 从 Harbor 拉。
2. **大文件与现场数据通道**（§6.4 + §7.2）：数据集/模型权重不进 git、git 只存指针清单；驻场采集数据经投放区回传；训练产物入库并在 manifest 留指针。
3. **CI 凭据集成**（§6.5）：Harbor/MinIO 凭据走 GitLab 受保护变量，job 日志打码验证。

## 2. 已确认的关键决策

| 决策点 | 结论 |
|---|---|
| Harbor 镜像来源 | 7897 代理后台慢拉（约 1.5–2h），期间并行做 MinIO |
| 验证深度 | 跑通 + 截图入档 + 验证结论页更新（延续第一阶段证据链风格） |
| Harbor 接入形态 | 组件容器直接写进主 `docker-compose.yml`（与 GitLab/runner 同网络同生命周期） |
| Harbor 项目规划 | 双项目：`frm-ci`（直推）+ `docker-hub-proxy`（proxy cache，上游指向可达镜像加速源） |
| MinIO 场景 | 三场景全做：大文件指针+CI 取用 / 现场投放区回传 / 训练产物入库 |
| 端口 | Harbor 8084(http)；MinIO 9002(API)/9003(Console)——避开 pih 占用的 9000/9001 与 GitLab 的 8081/8082 |
| TLS | http + insecure-registries（原型简化，TLS 留正式实施，与第一阶段"LDAP 简化"同风格） |
| sudo 协作 | 宿主 daemon.json 修改与 docker 重启由用户亲自执行，执行到该步时给出确切命令 |
| 教程 | 本轮不动，验证完成后再按实际路径补（教程不先于验证） |

## 3. 架构与端口

```
宿主机 (10.66.35.35) — frm-net (docker bridge)
├── frm-gitlab    :8081(web)/8082(ssh)      [现有]
├── frm-runner    shell executor, 挂宿主 docker.sock [现有]
├── frm-harbor    :8084(http) → core/nginx/registry/jobservice/db/redis 等 ~10 组件 [新增]
│     ├── 项目 frm-ci            —— CI 构建镜像直推（GPU 训练镜像等）
│     └── 项目 docker-hub-proxy  —— proxy cache，上游指向可达镜像源
└── frm-minio     :9002(API)/9003(Console)   [新增]
      ├── dataset-model    桶 —— 数据集/模型权重，git 存指针清单
      ├── field-dropzone   桶 —— 现场采集数据投放区（write-only）
      └── training-output  桶 —— 训练产物入库
```

- Harbor 组件来自官方 offline installer 解包，逐个翻译为 compose services；容器名加 `frm-` 前缀，内部走 frm-net 主机名（harbor-core、harbor-registry 等），对外仅暴露 8084。
- MinIO 复用本机已有 `minio/minio:latest` 镜像，一个 server 容器 + 一个 mc 初始化任务（建桶/建策略）；与 pih 项目的 MinIO 完全隔离（容器名/端口/卷均不同）。
- runner 为 shell executor 且挂宿主 docker.sock（第一阶段实测确认），CI 的 docker build/push/pull 即宿主 docker 操作——Harbor 信任只需配宿主 daemon 一处。

## 4. 验证场景与步骤

### 场景 1：镜像出口收敛（§5.3/§6.4）

1. Harbor UI 建项目 `frm-ci`（普通）与 `docker-hub-proxy`（proxy 类型，上游配可达镜像加速源）；
2. 示例流水线 job：`docker build` 小镜像 → `docker push 10.66.35.35:8084/frm-ci/demo-app:$CI_COMMIT_SHORT_SHA`；
3. runner 侧"从 Harbor 拉"：删本地镜像 → `docker pull` 走 Harbor 地址成功；
4. proxy 验证：`docker pull 10.66.35.35:8084/docker-hub-proxy/<小镜像>` 后，Harbor 仓库页出现缓存记录——"出口收敛"截图证据。

### 场景 2：大文件指针 + 现场回传 + 训练产物（§6.4/§7.2）

1. `dataset-model` 桶放示例数据集（几 MB 假数据 + sha256）；示例仓库 `autonomy/perception` 放 `datasets.manifest.json`（路径/大小/sha256 指针），大文件本体不进 git；
2. CI job：读 manifest → 从 MinIO 拉取 → sha256 校验 → 流水线绿；
3. 现场回传模拟：`mc` 以受限凭据向 `field-dropzone` 上传"传感器数据"，验证 write-only（列目录被拒、上传成功）；平台侧凭据取走归档到 `dataset-model`；
4. 训练产物：流水线产出假"模型权重" → 推 `training-output` → manifest.json 记 MinIO 路径（与 §6.3 manifest 机制衔接）。

### 场景 3：CI 凭据集成（§6.5）

- Harbor/MinIO 凭据配成 GitLab 受保护 CI 变量（HARBOR_USER/HARBOR_PASS、MINIO_KEY/MINIO_SECRET），示例仓库 `.gitlab-ci.yml` 新增 stage 引用；
- 验证变量 masking：job 日志中凭据打码。

## 5. 错误处理与降级

| 风险 | 处理 |
|---|---|
| Harbor 镜像后台慢拉中断/失败 | docker pull 断点续拉（已有层不重下）；彻底失败则 MinIO 三场景独立交付，Harbor 部分留待镜像到位，不阻塞其余证据 |
| proxy 上游全部不可达 | 记录"代理拓扑成立、上游连通性受本机环境限制"入验证结论页——正式实施时机房出口本就收敛到内网代理，拓扑证据已足 |
| sudo 重启 docker 影响 pih 项目 | 重启前核对 pih 容器 restart 策略（unless-stopped 会自动回来），命令由用户亲自执行 |
| MinIO 与 pih 冲突 | 端口/卷/容器名全隔离，无共享路径；兜底恢复命令写入验证结论页 |

## 6. 明确不验证（留正式实施）

Harbor TLS/多租户/漏洞扫描（Trivy）、MinIO 分布式/纠删码、LDAP 对接、Nexus（pip/npm 代理）、GPU 真实训练——原型只验证拓扑与集成方式。

## 7. 交付物与验收

| 交付物 | 验收标准 |
|---|---|
| 更新后的 `docker-compose.yml`（+Harbor ~10 服务 +MinIO 2 服务） | `docker compose up -d` 全部 healthy |
| 示例流水线跑绿（build-push-Harbor / MinIO 拉取校验 / 训练产物入库） | pipeline success，job 日志含凭据打码证据 |
| 截图第二批（编号续 21 起） | Harbor 项目页/推拉记录/代理缓存页、MinIO Console 三桶与投放区、流水线详情，存 `gitlab-compose-test/screenshots/` |
| 验证结论页收录第二阶段结果 | 表格化逐项 ✅ 与设计章节对应，含宿主机 daemon.json 环境变更记录 |

## 8. 实施顺序

1. MinIO 先行（镜像在本地，立即开干）：compose 加服务 → 建桶/策略 → 场景 2 三步 → 截图；
2. Harbor 镜像后台慢拉（与 1 并行）；
3. 镜像到位后：compose 加 Harbor 服务 → sudo 配 insecure-registries → 建项目 → 场景 1 → 截图；
4. 场景 3 凭据集成贯穿 2/3 的流水线；
5. 验证结论页更新、提交。
