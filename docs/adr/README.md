# 架构决策记录（ADR）索引

本项目关键决策的正式记录。目的：**每个决策连同意图、否决的备选与重开条件固化为一页**，避免同一问题被反复重议——想重开某个决策，先看它的"重新打开的条件"是否满足。

## 约定

- **状态**：`已接受` / `已取代（由 ADR-XXXX 取代）` / `讨论中`；
- **不改旧文**：决策变更时新写一条 ADR 并在旧 ADR 状态行标注取代关系，原文保留（决策史本身是资产）；
- **重开流程**：重议某决策 = 提一条新 ADR（或修订 MR），须引用旧 ADR 编号并说明重开条件已满足；
- 编号一经分配不复用；每条 ADR 必含六节：背景 / 决策 / 考量 / 否决的备选方案 / 后果 / 重新打开的条件；
- 决策事实来源为三份设计文档（逐节评审确认过），ADR 不引入新决策，只固化既有决策——新决策先走设计评审，再补 ADR。

## 索引

### 平台与授权

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0001](0001-platform-gitlab-ce.md) | 平台选型：自建 GitLab CE 一体化 | 一体化平台承载全部体系；集团设施是演进路径不是独立方案 |
| [ADR-0002](0002-edition-and-upgrade-path.md) | 版本策略：gitlab-ee 免费运行 | 缺失的 Premium 功能用制度/CI 替代，痛点成真再升级 |

### 代码组织与权限

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0003](0003-repo-structure-by-product-domain.md) | 仓库结构：单顶层组、按产品域 | 团队会重组，产品域相对稳定；platform 与 intake 例外直挂顶层 |
| [ADR-0004](0004-permission-model-three-tiers.md) | 权限模型：三级权限 | 只用 Guest/Developer/Maintainer；禁止个人持顶层 Owner |
| [ADR-0005](0005-ldap-account-lifecycle.md) | 账号体系：LDAP 域账号生命周期 | 禁本地建号；CE 边界靠"手动加组 + 脚本封禁"补齐 |
| [ADR-0006](0006-trunk-based-branching.md) | 分支模型：trunk-based 简化版 | main 常绿 + 短命分支 + MR；禁直推是系统强制 |
| [ADR-0007](0007-legacy-code-intake-bar.md) | 存量代码收编门槛 | 说不清用途的不入库；迁移期只立规则不追旧账 |

### DLP 共存

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0008](0008-dlp-two-zone-model.md) | DLP 两区模型与构建区豁免 | 谈判是交换不是对抗；加密边界在终端；产物必须构建区构建 |

### CI/CD 与制品

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0009](0009-ci-three-layer-templates.md) | CI 三层模板模型与配置分工 | "怎么跑"集中（ci-templates 宪法），"跑什么才算对"下沉 |
| [ADR-0010](0010-runner-pools-and-trigger-tiers.md) | Runner 池标签化与触发分级 | 五池隔离；push 快验 / nightly 全量 / HIL 手动 |
| [ADR-0011](0011-artifact-storage-split.md) | 制品归宿：三类系统 + manifest | 按形态分流；commit hash 缝合三家；Release 是发布门面 |
| [ADR-0012](0012-secrets-management.md) | 密钥管理 | 受保护变量 + 打码；明文密钥走受控主机；gitleaks 补拦截缺口 |
| [ADR-0013](0013-egress-convergence-harbor-minio.md) | 构建区出口收敛 | Harbor 双项目 + MinIO 三桶（write-only 投放区）；数据向内、代码只走 git |

### 驻场

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0014](0014-offline-field-baseline.md) | 驻场离线基线 | 离线为基线、有网为加速；现场永远不编译；临时包 24h 补账 |

### 需求流

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0015](0015-requirement-flow-on-gitlab.md) | 需求流选型：GitLab 原生轻量 | 流程摩擦足够小是胜负手；专业工具留作集团强制时的预留 |
| [ADR-0016](0016-intake-and-triage.md) | 受理台与分诊机制 | 唯一进料口 + 三模板 + 分诊三动作 + 3 日 SLA |
| [ADR-0017](0017-status-board-milestones.md) | 状态机、看板与里程碑纪律 | 7 状态一个不多；看板列即例会议程；标签字典走 MR |
| [ADR-0018](0018-three-nos-and-traceability.md) | 三无制度与双向追溯 | 无单不开发 / 无 MR 不合码 / 无里程碑不发布；追溯链系统自动生成 |

### 方法论与底线

| 编号 | 标题 | 一句话决策 |
|---|---|---|
| [ADR-0019](0019-prototype-first-methodology.md) | 原型先行方法论 | 决策先在本地原型实测；简化项显式列举；教程不先于验证 |
| [ADR-0020](0020-backup-and-dr.md) | 备份容灾与恢复演练 | MinIO 按资产备份（现场数据不可再生）；未演练的备份等于没有 |

## 决策来源

- [统一代码管理体系设计（2026-08-31）](../superpowers/specs/2026-08-31-excavator-code-management-design.md)
- [Harbor/MinIO 二阶段验证设计（2026-09-01）](../superpowers/specs/2026-09-01-harbor-minio-phase2-design.md)
- [产研需求流设计（2026-09-03）](../superpowers/specs/2026-09-03-requirement-flow-design.md)
- 归档日期：2026-09-07；后续补充决策（如 2026-09-07 确认的 CI 配置分工与触发分级细化）在对应 ADR 的"决策日期"行标注。
