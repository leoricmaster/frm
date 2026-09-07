# ADR-0011：制品归宿——三类系统分工 + manifest 追溯

- 状态：已接受
- 决策日期：2026-08-31
- 来源：[统一代码管理体系设计 §6.3、§6.4](../superpowers/specs/2026-08-31-excavator-code-management-design.md)
- 关联：ADR-0013（Harbor/MinIO 具体形态）、ADR-0008（产物不加密）、ADR-0018（发布挂里程碑）

## 背景

产物形态与体量差异极大：KB 级固件、GB 级模型权重、容器镜像、通用包。单一存储放不下全部诉求。

## 决策

1. **按形态分流**（判据：是否容器 / 是否与版本强绑定 / 体量是否超出 git 该装的范围）：

| 内容 | 存储 |
|---|---|
| 容器镜像（CI 基础镜像、CUDA 训练环境） | Harbor |
| 二进制制品（Conan/npm/Maven/PyPI 通用包） | GitLab 内置 package registry |
| 固件 .bin、部署包 | GitLab Release 附件 |
| 大文件（数据集、模型权重） | **不进 git**，放 MinIO，git 里只存清单与指针 |

2. **同一 commit hash 的制品从构建到烧进挖机全程可追溯**：发布用 tag + Release，每个发布固件能回答"源码 commit、构建环境（镜像 digest）、签名者、时间"；
3. 发布物内嵌 `manifest.json`（版本号、commit、构建时间、依赖清单）——现场维护一查即知机器上跑的是什么；
4. 三家的关系：**GitLab Release 是发布门面/账本，Harbor 是双向口岸（出口仓库+入口代理），MinIO 是数据侧仓库；commit hash + manifest 把三家缝成一次可追溯的发布**。

## 考量

- git 装大文件的后果：仓库撑爆、clone 变慢、历史污染——不可逆；
- Release 是唯一对外发布门面：驻场工程师只面对 Release 页，不需要知道后面几家。

## 否决的备选方案

- 全进 git——大文件致命；
- 全放一个制品库——版本语义（tag/Release）、容器语义（registry）、对象语义（桶）强行混用。

## 后果

- 正面：每类产物落在最合适的系统，发布可追溯闭环；
- 代价：三个系统的备份/权限/运维各一套（ADR-0020）；追溯链依赖 manifest 纪律（CI 模板强制内嵌）。

## 重新打开的条件

- 某类产物体量/频次剧变（如模型权重成为主要交付物）→ 重议其归宿；
- GitLab package registry 能力不足（如需 apt 仓）→ 引入 Nexus 承接。
