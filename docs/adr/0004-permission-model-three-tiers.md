# ADR-0004：权限模型——三级权限 + 顶层 Owner 禁忌

- 状态：已接受
- 决策日期：2026-08-31
- 来源：[统一代码管理体系设计 §4.3](../superpowers/specs/2026-08-31-excavator-code-management-design.md)
- 关联：ADR-0003（结构）、ADR-0005（账号）、ADR-0009（平台组对 ci-templates 的唯一变更权）

## 背景

GitLab 有五级项目权限（Guest/Reporter/Developer/Maintainer/Owner）。层级越多，"谁负责"越模糊；体系要防止建立后又出现新的权力单点。

## 决策

1. 全项目只使用三级：

| 角色 | 权限 | 授予对象 |
|---|---|---|
| Guest / Reporter | 只读 | 跨组查阅人员、外部协作者 |
| Developer | push 分支、建 MR | 本组开发成员 |
| Maintainer | 合 MR、管保护分支 | 每仓库 1–2 名 Owner |

2. **禁止任何个人拥有顶层组的 Owner 角色**——Owner 只属于平台维护账号。

## 考量

- 权限层级越少，责任越清楚：Maintainer 即该仓库的守门人与责任人；
- "禁止个人顶层 Owner"与收编存量代码的目标一致：体系建立就是为了消灭代码诸侯，不能再造新的。

## 否决的备选方案

- 用满五级——Reporter 与 Developer、Maintainer 与 Owner 的差异在实践中引发"我到底能不能"的持续争论；
- 给域负责人顶层 Owner——权力随个人扩散，违背平台宪法集中原则（原型实测：firmware Maintainer 推 platform 仓库被 403 拒，即本决策的执行证据）。

## 后果

- 正面：责任地图清晰，Members 页即 Owner 名录；
- 代价：顶层组管理动作（建组、改组设置）集中在平台维护账号，平台维护人是流程瓶颈之一。

## 重新打开的条件

- 出现平台维护人不可用且无交接的场景 → 讨论双账号/交接机制，而非放开个人 Owner。
