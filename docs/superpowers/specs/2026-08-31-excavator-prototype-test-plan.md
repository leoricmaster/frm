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

## 7. 角色工作流梳理与模拟验收（2026-08-31 第二轮）

按设计 §4.3/§6/§7 梳理五类角色在日常系统中的典型工作流，并逐一在原型实例上以该角色真实身份（impersonation token）走完全程。

### 7.1 角色与典型工作流

| 角色 | 权限层 | 典型工作流 | 涉及设计章节 |
|---|---|---|---|
| **开发工程师**（dev1） | Developer(30)，限本组 | clone → 特性分支 → push → MR → 等 CI → 修到绿 | §4.2/§4.3 |
| **仓库 Owner**（maint1） | Maintainer(40)，1–2 人/仓库 | 评审 MR → approve → 合入 main → 打 tag → 手动批准晋升 → 建 Release | §4.3/§6.3 |
| **只读协作者**（guest1） | Guest(10) | 浏览项目页 → 从 Release 下载制品与 manifest（无代码权） | §4.3/§7.2 |
| **平台工程**（plat1） | platform 组 Maintainer | 改 ci-templates 通用层 → MR 评审 → 合入 → 全下游仓库自动继承 | §6.2 |
| **驻场工程师**（离线，模拟为 dev1+guest1 组合） | 出场前 Developer/现场 Guest | 出场前打包 → 现场只刷不编 → 应急改动回公司 24h 内补 MR | §7 全节 |

### 7.2 逐角色模拟验收结果

**A. 开发工程师（dev1）**

| 步骤 | 结果 |
|---|---|
| clone 仓库 | ✅ 正常 |
| 直推 main | ✅ 被拒：`not allowed to push code to protected branches`（系统强制，§4.2） |
| 特性分支 push + 建 MR | ✅ MR !2 创建成功，push 时 GitLab 自动返回建 MR 链接 |
| MR 触发流水线 | ✅ 首次失败→**暴露真实设计问题**（见 7.3-1），修复后 #11/#12 全绿 |

**B. 仓库 Owner（maint1）**

| 步骤 | 结果 |
|---|---|
| 查看/评审 MR !2 | ✅ 1 file changed 可见 |
| approve | ✅ 批准记录落档 |
| 合入（带 SHA 防错合） | ✅ merged by maint1 |
| 合入后 main 流水线 | ✅ #13 全绿 |
| 打 tag v0.2.0-field | ✅ 触发 #14，含 manual 的 promote-release |
| 手动批准晋升（play manual job） | ✅ job success |
| 建 Release + 挂制品链接 | ✅ manifest.json 与 .bin 均可下载 |
| **制品追溯链** | ✅ **manifest.commit = main HEAD = tag commit = MR 合入 commit = 9a77da6f，四方一致（§6.3）** |

**C. 只读协作者（guest1）**

| 步骤 | 结果 |
|---|---|
| 浏览项目页/元数据 | ✅ 200 |
| 从 Release 下载制品+manifest | ✅ 驻场取制品通道成立 |
| clone 代码 | ✅ 被拒（403 not allowed to download code） |
| 读文件树/MR 列表 | ✅ 被拒（403） |
| ⚠️ 读 CI job 日志 | ⚠️ **允许（200）**——见 7.3-3 风险 |

**D. 平台工程（plat1）**

| 步骤 | 结果 |
|---|---|
| maint1（firmware Owner）推 platform 仓库 | ✅ 被拒（403）——权限隔离正确，宪法变更需平台组自己走 MR |
| plat1 建分支改 firmware.yml + MR | ✅ ci-templates MR !1/!2 合入 |
| **模板变更传播验证** | ✅ 下游仓库**零改动**，新流水线 #19 的 build job trace 出现模板新增的 `test -s build/*.bin || echo "产物为空，禁止发布"` 校验——§6.2 "规则集中管理"成立 |

**E. 驻场工程师（离线流）**

| §7 场景 | 结果 |
|---|---|
| 出场前打包（Release 制品+manifest） | ✅ guest 即可完成下载 |
| 现场核对（manifest 一查即知） | ✅ manifest 含 name/commit/build_time/runner |
| 应急改动 24h 补 MR（§7.3） | ✅ MR !4 建立→CI 绿→maint1 批准合入，闭环成立；commit message 留痕"现场应急" |

### 7.3 模拟中发现的设计/实施问题

1. **通用层模板必须对全体开发者可读（重要发现）**：dev1 push 后流水线创建失败，根因是 `.gitlab-ci.yml` include 了 `platform/ci-templates`，但 dev1 在 platform 组无任何角色→"Project not found or access denied"，流水线 0 job 直接 failed。修复：全员加 platform 组 Reporter(20) 只读。**正式实施时应在建组脚本里固化此规则**。
2. **include ≠ 继承（结构缺陷自纠）**：原型初版下游 `build-firmware` 自写 script，include 只是形式引入，模板改了也不传播。改为 `extends: .firmware-template` 后传播才真正成立。**正式迁移时的仓库模板必须用 extends 结构**，且"不 include/不 extends 通用层的流水线不予合入"需写进 MR 检查单。
3. **Guest 可读 CI job 日志（风险）**：构建日志可能带出代码片段/环境信息。CE 默认如此。缓解：敏感变量全部设 Protected（仅受保护分支流水线可见）；若风险不可接受，正式版可讨论将外部协作者改为 Deploy Token/独立 Release 门户。
4. **GitLab 行为备忘**：include 在 pipeline 创建时解析并快照，retry 不重新解析——模板热修后需触发新流水线验证，旧流水线 retry 无效。
5. **平台组权限分离验证**：firmware 的 Maintainer 推 platform 仓库被拒（403）——按设计意图，宪法变更权收在平台组，不随业务仓库 Owner 扩散。

### 7.4 角色流程截图（第二批）

- `14-mr2-merged.png` MR !2 评审页（批准记录/流水线/合入信息）
- `15-mr2-changes.png` MR diff 评审页
- `16-release.png` Release v0.2.0-field（含制品附件与 Evidence 溯源）
- `17-pipeline19.png` 模板传播验证流水线
- `18-job18-trace.png` build job trace（模板 script 生效证据）
- `19-ci-mr.png` ci-templates 宪法变更 MR
- `20-mr4-field.png` 应急补单 MR !4（§7.3 闭环）

## 4. 备选与降级

若 GitLab EE 始终拉不动：改用 `gitlab/gitlab-ce:latest`（功能等价、设计文档 §3.2 已说明 CE 先行），镜像更小、国内源命中率更高。再不行用 Gitea 起一个轻量占位验证组结构/权限逻辑（但会偏离设计选型，仅作流程演练）。
