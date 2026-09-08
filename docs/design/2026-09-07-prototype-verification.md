# 原型验证结论（三阶段）

- 日期：2026-09-07（蒸馏自 2026-08-31 / 09-01 / 09-03 三阶段验证记录，原稿见 git 历史 `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`）
- 状态：三阶段全部通过
- 依据：docs/design/ 三份设计文档；证据截图 01–43 存 `gitlab-compose-test/screenshots/`

## 1. 三阶段验证矩阵

### 阶段一 · 平台与权限（2026-08-31）

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| GitLab 部署与登录 | §8 阶段1 | ✅ |
| excavator 组结构（顶层+6子组） | §4.1 | ✅ |
| 三级权限模型 | §4.3 | ✅ |
| 保护分支禁直推 main | §4.2 | ✅ |
| MR 创建与评审 | §4.2/§3.2 | ✅ |
| 示例流水线全绿（include 通用层） | §6.2/§8 | ✅ |
| 制品追溯 manifest | §6.3 | ✅ |
| 界面可用性（截图 01–13） | §3.2 | ✅ |

### 阶段二 · 制品通道（2026-09-01）

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| MinIO 三桶初始化 | §6.4 | ✅ |
| 大文件指针 + CI 取数校验（sha256） | §6.4 | ✅ |
| 现场投放区 write-only 回传 | §7.2 | ✅ |
| 投放区归档 | §7.2 | ✅ |
| 训练产物入库 + manifest 指针 | §6.3/§6.4 | ✅ |
| CI 凭据受保护 + 打码 | §6.5 | ✅ |
| Harbor 直推（build→push→pull） | §5.3/§6.4 | ✅ |
| Harbor 代理缓存拓扑 | §5.3 | ✅ |
| compose 全家 healthy（~15 服务） | — | ✅ |

### 阶段三 · 需求流（2026-09-03）——设计章节列均指《产研需求流设计》

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| Guest 按模板建单 | §4.1 | ✅ |
| 分诊三动作（移交/打回/婉拒） | §4.2 | ✅ |
| 里程碑排期 | §4.4 | ✅ |
| MR Closes 自动关单 | §5.1 | ✅ |
| tag/Release 挂里程碑 + manifest 资产（里程碑关联经里程碑页成立——Release API 的 milestone 参数被静默忽略） | §5.1 | ✅ |
| 反向三跳（manifest→commit→MR→单） | §5.2 | ✅ |
| 外部验收路径（缺陷单 待验证） | §4.3 | ✅ |
| 组看板状态列 | §6 | ✅ |
| 里程碑完成度（CE 按单数） | §6 | ✅ |
| 受理台积压视图 | §6 | ✅ |

## 2. 角色模拟验收（阶段一第二轮）

五类角色以真实身份（impersonation）走完典型工作流，全部通过：

| 角色 | 关键结论 |
|---|---|
| 开发工程师 dev1 | 直推 main 被拒；MR 全流程成立；CI 由红修绿 |
| 仓库 Owner maint1 | 评审/合入/打 tag/手动晋升/建 Release；**manifest.commit = main HEAD = tag commit = MR 合入 commit 四方一致** |
| 只读协作者 guest1 | Release 下载制品 ✅、clone 403 ✅；⚠️ 可读 CI job 日志（见 §3-3） |
| 平台工程 plat1 | 域 Maintainer 推 platform 仓库被 403——宪法变更权不扩散；模板变更下游零改动自动传播 |
| 驻场工程师（离线流） | 出场打包/现场核对/应急 24h 补 MR 全闭环 |

## 3. 关键实测事实（设计规则依赖的边界）

1. **通用层模板须对全体开发者可读**：dev1 在 platform 组无角色 → include 解析失败、流水线 0 job。修复：全员加 platform 组 Reporter(20)。正式实施固化进建组脚本。
2. **include ≠ 继承**：下游须 `extends: .firmware-template` 模板变更才传播；"不 include/不 extends 通用层的流水线不予合入"写进 MR 检查单。
3. **Guest 可读 CI job 日志**（CE 默认）：敏感变量全部设 Protected 缓解（仅受保护分支流水线可见）。
4. **include 在 pipeline 创建时快照解析，retry 不重解析**：模板热修后须触发新流水线验证。
5. **域 Maintainer 推 platform 仓库被 403**：权限分离按设计意图成立。
6. **Harbor 独立 compose**（非并入主 compose）：配置源 `harbor.yml` 入库即可复现，生成 compose 不入库（含随机密钥）。
7. **MinIO 拒 HTTP Basic（400）**：CI 的 curl 须 `--aws-sigv4` 签名（runner 内 curl 8.5.0 支持）。
8. **Harbor proxy 上游实测用 `docker.1ms.run`**（比预估的 hub.rat.dev 稳定）。
9. **Guest 无 label 权限**：来源/状态标签由分诊人代打（已回写需求流设计 §4.1，比"建单时选来源"更稳）。
10. **image-build 须 `only:[main,tags]`**：否则 MR 流水线因缺受保护变量必红；且 tag 须先过 `POST /protected_tags` 保护才可见受保护变量。
11. **组看板懒创建**：首次浏览器访问后 API 才能加列。
12. **root PAT 无 sudo 作用域**：扮演非 root 用户改用"管理员代建用户 PAT、用毕吊销"（作者身份保真）。

## 4. 不覆盖项（留正式实施）

- 谈判依赖项：DLP 两区模型（§5，需集团产品名）、VPN 场景（§7.4）、HIL 台架（§6.1）；
Harbor TLS/多租户/漏洞扫描、MinIO 分布式与备份策略、Nexus、GPU 真实训练（原型只验证拓扑与集成方式）。
- LDAP 真实域账号分诊轮值、`platform/` 标签字典 MR 管控实战、周例会看板纪律、四产品域并行、外部工具（禅道等）导出迁移。

## 5. 证据位置

- `gitlab-compose-test/screenshots/`：01–13 阶段一部署与权限，14–20 阶段一角色流，21–31 阶段二制品通道，32–43 阶段三需求流；
- 教程引用子集在 `docs/tutorials/assets/`；实例侧留档（intake 模板、firmware 示例等）在 `gitlab-compose-test/<repo名>/`。
