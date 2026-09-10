# gitlab-repro.md 重构为正式实施与运维手册 — 设计

- 日期：2026-09-10
- 状态：设计已确认（三节分批过审），待实施
- 决策人：lancer

## 1. 背景与问题

现行 `docs/ops/gitlab-repro.md` 受众错位——写成了"复现手册"，把读者当成要复刻原型测试的人；实际读者是**阶段 1 正式实施这套系统的平台运维**，需要的是理解设计并建立自己的实例。三点表现：

1. **以 yml 为权威**："各组件作用与资源上限见 docker-compose.yml 注释"——方向反了，文档应承载架构设计供人评审 yml，而非让 yml 当准绳。
2. **一键复刻当主路径**：rebuild 脚本复刻的是测试数据（intel_excavator 组树、液压抖动 MR），读者要建的是自己的组树，大概率会改。
3. **测试机特化参数无标注**：IP `10.66.35.35`、端口 8081–8083/9002–9003（测试机冲突所致）、原型密码内嵌，读者分不清方案固有与测试将就。

梳理中发现四处测试遗留须纠正：

| # | 问题 | 事实 |
|---|---|---|
| 1 | compose 无容器资源上限 | 仅 `shm_size: 256m` 与 puma/sidekiq 应用调优；文档却称"资源上限见 compose 注释"，名不副实 |
| 2 | compose 注释指向不存在的 README | runner 注释"注册…（见 README）"，目录无此文件；现文档也**全篇缺失 Runner 注册**这个起栈后必做步骤 |
| 3 | 镜像钉版纪律不一致 | GitLab 钉 `19.3.1-jh.0`（ADR-0021），runner/minio/mc 全 `:latest`，离线机房不可复现 |
| 4 | rebuild 脚本硬依赖 `/tmp/harbor-robot-secret.txt` | 脚本自身问题，本次不改，只在文档中钉准定位 |

## 2. 已确认决策

| 决策点 | 结论 |
|---|---|
| 文档定位 | **正式实施指南**：面向阶段 1 正式实施运维；原型特化内容降级附录并标"示例值，按实际改" |
| 架构图范围 | **落地形态 + 演进注记**：实线画本次部署（与 compose 对照），虚线标设计终态扩展位（Runner 池/Harbor/LDAP/备份） |
| 纠正范围 | **文档 + compose 硬伤**：钉版、悬空引用、补资源上限；IP/密码参数化（.env）不做，以正文标注替代 |
| 重构方案 | **方案 A**：运维生命周期为轴 + 架构表立权威（否决 B 映射表骨架——重复设计文档；否决 C 最小改动——受众错位未解） |

## 3. 文档骨架与内容去留

改名：`docs/ops/gitlab-repro.md` → `docs/ops/gitlab-ops.md`（`git mv` 重写，`--follow` 保留历史；全仓无引用需更新）。标题「极狐 GitLab 实施与运维手册」。

| 新章节 | 来源 | 处理 |
|---|---|---|
| 0 定位与边界 | 现「范围」行 | 改写：受众=阶段 1 正式实施平台运维；why→`docs/design/`+`docs/adr/`，how→本文 |
| 1 系统架构 | 新写 | mermaid 图 + 组件表（§4） |
| 2 部署准备 | 现 §0 前置条件表 | 主机规格指向设计 §7；镜像预拉清单含钉版；端口标"示例值，因测试机冲突"；凭据口径分原型/正式 |
| 3 起栈与就绪 | 现 §1 | 就绪信号判定 + **补 Runner 注册**（admin 区取 token → `docker exec frm-runner gitlab-runner register` → docker executor、docker.sock GID 说明 → 验证在线+跑通流水线）。实际注册参数实施时从容器内 config.toml 核对 |
| 4 首启初始化 | 现 §2 | 保留三动作（root 改密 / 核对注册关 / 关 Web IDE 单一源回退）；seed-once 口径集中为一条原则：omnibus 键首启生效，已运行实例须 DB 直改（`gitlab-rails runner`） |
| 5 按设计建立组织结构 | 新写（核心章） | 5.1 组树(ADR-0003) / 5.2 用户与权限(ADR-0004/0005) / 5.3 仓库与保护分支(ADR-0006) / 5.4 CI 三层模板(ADR-0009) / 5.5 需求流(ADR-0015–0017)。每小节：通用做法(UI/API) → 指向 ADR →「原型示例值见附录A」 |
| 6 日常运维 | 现 §5 | 基本保留（开账号 / 封禁回收 / 备份恢复） |
| 附录A 原型复现 | 现 §3 整节 + 现 §6 证据 | 挪入；开头钉死定位："测试 fixture，复刻原型验证终态（演示/回归用），非正式实施路径"；A–Z 段表、进度文件、证据位置（repo 镜像 + screenshots 01–43）并入 |
| 附录B 已知坑位 | 现 §4 | 保留，指向验证结论 §3–13 差异表 |

核心翻转：第 5 章教"按设计建你自己的组树"，原型值退为示例；rebuild 脚本从主路径退为附录 fixture。

## 4. 架构图与组件表（新文档第 1 章）

图（mermaid，最终版须为合法可渲染语法）：实线=本次落地四容器 + 宿主 docker.sock + 端口 + 数据流（CI 任务调度、CI 上传数据集/权重、幂等建三桶）；虚线=演进位——AD/LDAP(ADR-0005)、Runner 池独立虚机 fw-build×2/veh-build/cloud-deploy(ADR-0010)、Harbor(ADR-0013)、备份存储(ADR-0020)。设计意图：一眼分清"现在建什么/往哪长"，虚线即设计文档锚点。

组件表（yml 评审准绳）：

| 组件 | 职责 | 镜像（钉版） | 宿主端口 | 数据卷 | 资源上限 |
|---|---|---|---|---|---|
| gitlab | 托管/MR/CI 调度/内置制品库 | `gitlab-jh:19.3.1-jh.0` | 8081 web / 8082 ssh / 8083 registry 预留 | config/logs/data | 4C / 8G |
| gitlab-runner | docker executor 跑 CI | `gitlab-runner:v19.3.1` | — | runner-config | 2C / 2G |
| minio | 大文件对象存储（三桶） | `minio:RELEASE.2025-09-07T16-13-09Z` | 9002 / 9003 | minio-data | 1.5C / 2G |
| minio-init | 幂等建三桶，跑完即退 | `mc:RELEASE.2025-08-13T08-35-41Z` | — | — | 0.5C / 512M |

- 上限口径：设计 §7 主机 8C/16G，四容器合计 8C/12.5G，留 OS 与页缓存余量；`deploy.resources.limits`（compose v2 非 swarm 生效）。
- 版本依据：全部为**实测在跑**版本（`gitlab-runner --version`=19.3.1 与 GitLab 主版本对齐；minio/mc 为容器内 `--version` 读出）。
- 表下钉原则一句：**本表是准绳，改 yml 先对表；表要改先过设计文档。**

## 5. compose 修改（三处）

| # | 现状 | 改为 |
|---|---|---|
| 1 | runner/minio/mc `:latest` | §4 表中钉版 |
| 2 | runner 注释悬空"（见 README）" | 改指 `docs/ops/gitlab-ops.md` 第 3 章 |
| 3 | 无资源上限 | 四服务加 `deploy.resources.limits`，数值同 §4 表；gitlab 服务旧注释"按本机 62G/32C 富余设定"改为生产口径说明 |

生效影响：钉版无实质变化（本地 latest 即实测版本）；资源上限下次 `up -d` recreate 生效，实施时先 `docker stats` 核对现用量在限内、`docker compose config` 校验后再收口。

## 6. 边界（不做）

- IP/端口/密码参数化（.env 外置）——正文以"示例值"标注替代。
- rebuild 脚本代码不改（含 /tmp 依赖），只改文档定位。
- 栈内服务配置（puma/sidekiq 调优值）不动。

## 7. 验收标准

1. `gitlab-ops.md` 按 §3 骨架成文；正文中原型值均带"示例"标注，无"照抄即得"口吻。
2. mermaid 语法合法（GitLab 渲染环境自查），图与 compose 实况一一对应。
3. `docker compose config` 通过；`docker stats` 快照显示现用量 < 新限值。
4. compose 内无悬空文档引用（grep "README" 无孤儿）。
5. `git log --follow docs/ops/gitlab-ops.md` 可回溯至 gitlab-repro.md 历史。
