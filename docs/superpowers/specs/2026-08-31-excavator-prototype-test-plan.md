# 智能挖机代码管理体系 — 本地原型验证计划

- 日期：2026-08-31
- 状态：进行中
- 依据：[统一代码管理体系设计](./2026-08-31-excavator-code-management-design.md)
- 目标：在本地（无 DLP、无 VPN 的裸环境）把设计中的核心组件跑通，验证"能跑通"且"界面/功能可接受"，对应设计文档第 8 节阶段 1 完成标准。

## 0. 验证范围与边界

| 验证项 | 对应设计章节 | 原型覆盖 |
|---|---|---|
| GitLab 部署与登录 | §8 阶段1 | ✅ root 本地账号（LDAP 是正式实施项，原型不接） |
| excavator 组结构 | §4.1 | ✅ 顶层 group + 6 个子 group |
| 三级权限模型 | §4.3 | ✅ Guest/Developer/Maintainer 验证 |
| 保护分支（禁直推 main） | §4.2 | ✅ 系统强制 |
| MR 创建与评审界面 | §4.2 / §3.2 | ✅ 截图评估界面可用性 |
| 示例 CI 流水线全绿 | §6.2 / §8 | ✅ Runner + 一条 .gitlab-ci.yml |
| 制品追溯 manifest | §6.3 | ✅ 流水线产出 manifest.json |
| Harbor / MinIO | §6.4 / §11 | ⏸ 第二阶段（GitLab 内置 registry/MinIO 先替代） |

不覆盖：DLP 两区模型（§5，需集团产品名）、VPN 场景（§7.4）、HIL 台架（§6.1）——这些是正式实施谈判项，不在原型范围。

## 1. 环境实测结论（关键约束）

| 项 | 实测 | 影响 |
|---|---|---|
| 本机资源 | 62G RAM / 32 核 / 565G 磁盘 | 充裕，GitLab 最低 4G |
| Docker | 29.1.3 + compose 2.40 | 可用 |
| Docker Hub 直连 | **不通**（timeout） | 必须走代理或镜像源 |
| 镜像源（daocloud 等） | gitlab 命名空间被限流/拒绝（401/DENIED） | 仅小镜像可用，GitLab 拉不动 |
| 代理 `127.0.0.1:7897` | **通**，但吞吐 ~108 KB/s | 30MB≈4.5min，GitLab EE(~3GB)≈8h，不可接受 |
| sudo | **需密码**，无法自助重启 docker daemon 配代理 | docker pull 走代理受阻 |

**当前瓶颈**：无高速拉取通道。镜像拉取是唯一阻塞项，其余步骤均已就绪。

## 2. 分阶段执行计划

### 阶段 A：解决镜像拉取（阻塞项）

按优先级尝试，成功一项即停：

1. **daemon 走代理**（需用户协助）：用户执行 `sudo` 配置 docker 的 systemd drop-in 走 7897 代理后重启 docker。一次性解决，后续所有 pull 走代理。需手动给一次 sudo 密码。
2. **代理后台慢拉**：用 7897 代理把 GitLab EE 挂后台拉（约 8h，中长期任务可接受），期间推进其他非阻塞准备。
3. **用户离线导入**：用户自行在有网机器 `docker save` 后拷入本机 `docker load`，最快。

> 已写好的 compose 见 `gitlab-compose-test/docker-compose.yml`，镜像就位即可起。

### 阶段 B：部署与初始化（镜像就位后，约 30 分钟）

1. `docker compose up -d` 启动 GitLab + Runner
2. 轮询 `http://10.66.35.35:8081/-/readiness` 直到就绪（首次 reconfigure 3–5 分钟）
3. root 登录（密码已写入 compose：`Excavator#2026Proto`）

### 阶段 C：复刻设计结构（约 30 分钟）

1. 建顶层 group `excavator` + 子 group：firmware / autonomy / vehicle / cloud / app / platform
2. `platform/ci-templates` 仓库放四套 CI 模板（固件/算法/车载/云端，对应 §6.2 通用层）
3. 建示例仓库 `firmware/hydraulic-controller` 含 `.gitlab-ci.yml`（include 通用层）

### 阶段 D：CI 流水线验证（约 20 分钟）

1. 注册 gitlab-runner（docker executor，复用本机 docker socket）
2. push 触发流水线，验证：lint → build → 产出 `manifest.json`（§6.3）→ 全绿
3. 验证保护分支：直推 main 被拒，MR 合入正常

### 阶段 E：界面与功能评估（约 20 分钟）

用 Playwright 截图，逐项核对界面可用性：

- 登录页 / 主界面
- group 与仓库结构树
- MR 创建 + 评审界面（对应 §3.2 CE 下审批替代方案的体感）
- 保护分支配置页
- 流水线 / 制品页（package registry）

截图汇总交付用户判定"界面/功能是否可接受"。

## 3. 进度

- [x] 环境与网络实测（§1）
- [x] compose 文件编写（`gitlab-compose-test/docker-compose.yml`）
- [x] 阶段 A：镜像拉取（改用 gitlab-ce，阻塞解除）
- [x] 阶段 B：部署与初始化（GitLab healthy，root 登录成功）
- [x] 阶段 C：复刻设计结构（excavator + 6 子组，2 示例仓库，4 套 CI 模板）
- [x] 阶段 D：CI 流水线验证（pipeline#3 全绿，manifest 产出）
- [x] 阶段 E：界面与功能评估（12 张截图）

## 5. 验证结果（2026-08-31 完成）

| 验证项 | 设计章节 | 结果 | 证据 |
|---|---|---|---|
| GitLab 部署与登录 | §8 阶段1 | ✅ | 容器 healthy，root 登录 200 |
| excavator 组结构 | §4.1 | ✅ | 顶层 + firmware/autonomy/vehicle/cloud/app/platform 六子组 |
| 三级权限模型 | §4.3 | ✅ | dev1=Developer / maint1=Maintainer / guest1=Guest |
| 保护分支禁直推 main | §4.2 | ✅ | main 的 push/merge 限 Maintainer(40)，Developer(30) 无法 push |
| MR 创建与评审 | §4.2/§3.2 | ✅ | MR !1：特性分支→审批→合入，state=merged |
| 示例流水线全绿 | §6.2/§8 | ✅ | pipeline#3 success，含 include 通用层 |
| 制品追溯 manifest | §6.3 | ✅ | manifest.json 含 commit/branch/build_time/runner |
| 界面可用性 | §3.2 | ✅ | 12 张截图，见 `gitlab-compose-test/screenshots/` |

## 6. 界面截图清单

截图位于 `gitlab-compose-test/screenshots/`，可逐张打开评估：

- `01-login.png` 登录页
- `02-dashboard.png` 主面板
- `03-groups.png` / `04-group-tree.png` excavator 组结构树
- `05-project.png` 示例项目主页
- `06-pipelines.png` / `07-ci-success.png` 流水线列表与全绿详情
- `08-mr-list.png` / `09-mr-closed.png` MR 列表与已合入详情
- `10-protect.png` 保护分支设置
- `11-ci-templates.png` CI 模板仓库（平台宪法）
- `12-members.png` 成员权限页
- `13-packages.png` package registry

## 4. 备选与降级

若 GitLab EE 始终拉不动：改用 `gitlab/gitlab-ce:latest`（功能等价、设计文档 §3.2 已说明 CE 先行），镜像更小、国内源命中率更高。再不行用 Gitea 起一个轻量占位验证组结构/权限逻辑（但会偏离设计选型，仅作流程演练）。
