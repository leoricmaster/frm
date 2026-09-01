# 教程同步二阶段（Harbor/MinIO）方案

- 日期：2026-09-01
- 目标：教程从"仅 GitLab 一阶段"同步到"Harbor/MinIO 已验证的二阶段"，消除文档与原型的能力脱节
- 约束来源：`docs/superpowers/specs/2026-08-31-role-tutorials-design.md`（教程 spec）、`check.py`（静态自检）、`2026-08-31-excavator-code-management-design.md` §6.4（产物归宿权威定义）、test-plan §8（二阶段验证证据）

## 0. 前提变更：解除 spec 的排除条款

教程 spec §8「不做什么」第 4 条原写：

> 不覆盖 Harbor/MinIO/LDAP（原型未验证的组件不写进操作教程，仅在延伸阅读提及设计方向）

此条订立于 phase 1（2026-08-31），当时 Harbor/MinIO 尚未验证。Phase 2（2026-09-01）已验证 Harbor 直推+代理、MinIO 三桶三场景、CI 凭据受保护打码（test-plan §8.2 九项全 ✅）。**前提不再成立**，须先改 spec 再改教程。

- Harbor/MinIO：解除排除，纳入相应角色教程（有截图证据）
- LDAP：**仍未验证**（test-plan §0 注明 LDAP 是正式实施项，原型不接），排除条款对 LDAP 保留

产物归宿权威定义（设计 §6.4）：

| 内容 | 存储 | 阶段 |
|---|---|---|
| 容器镜像（CI 基础镜像、CUDA 训练环境） | Harbor | 二阶段新增 |
| 二进制通用包（Conan/npm/Maven） | GitLab package registry | 一阶段已覆盖 |
| 固件 .bin、部署包 | GitLab Release 附件 | 一阶段已覆盖 |
| 大文件（数据集、模型权重） | MinIO，git 只存清单与指针 | 二阶段新增 |

## 1. 改 spec（1 文件）

`docs/superpowers/specs/2026-08-31-role-tutorials-design.md`：

- 顶部素材行：`20 张` → `20 张一阶段 + 11 张二阶段截图（21–31，复用验证证据，不补拍）`
- §5 各角色大纲：补二阶段相关条目（见下方各教程）
- §6 截图分配总表：追加 21–31 的分配行
- §6 末尾"19 张已用"统计更新
- §8 第 4 条改写为：
  > 不覆盖 LDAP（原型未验证，仅在延伸阅读提及设计方向）；Harbor/MinIO 已于二阶段验证（test-plan §8），纳入 platform / field-engineer / developer / owner 相应教程并复用 21–31 截图

## 2. 复制截图（gitlab-compose-test/screenshots/ → docs/tutorials/assets/）

复用集（7 张，均为 1440×900 PNG，已确认为真实图片）：

| 截图 | 用于 | 说明 |
|---|---|---|
| 26-harbor-projects.png | platform | Harbor 两项目（frm-ci + docker-hub-proxy） |
| 28-harbor-proxy.png | platform | 代理缓存项目（上游 docker.1ms.run） |
| 29-minio-buckets.png | platform、index、field | MinIO 三桶 |
| 23-fetch-dataset-job.png | platform、developer | 取数 job trace（[MASKED] 打码 + sha256 校验） |
| 21-perception-pipelines.png | developer | autonomy 多阶段流水线（scan/data/build/publish） |
| 27-harbor-frmci.png | owner | Harbor frm-ci 项目内已推镜像 |
| 30-minio-dataset.png | field | dataset-model 桶内 field-archive 归档目录 |

（22/24/25/31 暂不复用——内容与已选片重叠或对该角色非必要，避免教程图过多失焦。）

## 3. 更新 6 个 HTML

### 3.1 index.html（轻）

- **术语速查**追加三行：Harbor（容器镜像仓库，CI 构建的镜像归宿）、MinIO（对象存储，数据集/模型权重归宿）、投放区（现场数据 write-only 投放桶，只能投不能删/列）
- **通用入门**末尾加一个"产物去哪了"小框（why 框）：三去向一句话——.bin→Release、镜像→Harbor、大文件→MinIO；引设计 §6.4
- **footer**：`2026-08-31` → `2026-08-31 / 09-01 两阶段原型`，覆盖说明补 Harbor/MinIO

### 3.2 platform.html（改动最大——平台新增 Harbor/MinIO 纳管职责）

在现有「典型任务流：模板变更」之后、「常见报错自救」之前，**新增一个 h2 节**：

> `## 典型任务流：纳管镜像仓库与对象存储`

含 3 个步骤卡片：
1. **Harbor 两项目**——frm-ci（业务镜像直推：build→push→pull 回验）+ docker-hub-proxy（代理缓存上游，构建区无外网直连、出口收敛 §5.3）。图 26、28
2. **MinIO 三桶**——dataset-model（数据集指针+sha256）/ field-dropzone（现场投放 write-only）/ training-output（训练产物+manifest s3 指针）。图 29
3. **CI 凭据受保护**——Harbor robot account、MinIO key 走 GitLab 受保护变量（protected+masked），job 日志里凭据显示 `[MASKED]`。图 23

- **红线清单**追加：Harbor/MinIO 凭据不进仓库、不进聊天工具（与现有 runner 密钥红线同列，§6.5）
- **延伸阅读**追加：§6.4 制品与镜像存储分工、§5.3 交换条件（构建区出口收敛）、test-plan §8 二阶段验证结果

### 3.3 field-engineer.html（中——补全通道三的实物证据）

通道三「取数」当前只有文字"日志、传感器数据进 MinIO 投放区"，无截图。补：
- 加图 29 或 30 + 图注：投放区是 write-only——现场只能往里投，不能删、不能列别人的（防数据互覆盖与越权取阅，§7.2）
- 补一句回公司后归档：投放区数据由平台组归档进 dataset-model 桶的 field-archive 目录（图 30）
- **红线**已有"现场数据不走私人网盘/U 盘"，微调使其指向投放区通道

### 3.4 developer.html（轻——CI 现在还做什么，操作不变）

- 「等 CI，读结果」步骤加一个 why 框「CI 现在还做什么」：固件流水线会构建容器镜像并推 Harbor；算法（autonomy）流水线会从 MinIO 取数据集、训练完把模型权重推回 MinIO。**但你的操作不变**——push 完等绿，红了点 job 看日志
- 可选补图 21（多阶段流水线）让开发者认得 scan/data/build/publish 阶段名（若加，图数 4→5）

### 3.5 owner.html（轻——产物三去向，追溯链扩展）

- 「建 Release」步骤前加一个 why 框「产物三去向」：.bin+manifest 仍进 GitLab Release（不变）；容器镜像进 Harbor（图 27），模型权重进 MinIO——后两者各有自己的指针/manifest
- 「核对追溯链」步骤补一句：镜像核对 Harbor 仓库里的 tag→commit；模型核对 MinIO manifest 的 s3 指针→commit；.bin 仍核对 Release manifest 四字段。三方各自可追到同一 commit

### 3.6 viewer.html（最轻——Guest 通道不变，仅点明镜像/模型在他处）

- 权限表或延伸阅读补一句：容器镜像存 Harbor、模型存 MinIO，需单独授权找平台组；**Guest 的 Release 下载通道不变**（仍是 .bin+manifest）
- 不加截图（Guest 视角不触及 Harbor/MinIO 控制台）

## 4. 自检（验收门）

1. `python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html` 全 `[OK]`
   - 骨架 h2 片段齐全（新增 h2 不破坏现有骨架片段匹配）
   - 无外部资源、图片引用全部存在
   - 每页 ≥2 图（platform 增至 6 图，field 增至 3 图，其余不变或 +1）
2. 人工逐图核对：图注与截图实际状态逐字对齐（phase 1 终审 a9781ca 的同款要求）——尤其 26 两项目名、29 三桶名、23 [MASKED] 与 sha256、30 field-archive 目录
3. 内容不臆造：每条新增操作/规则都能回溯到 test-plan §8.2 验证项或设计 §6.4/§5.3/§6.5

## 5. 提交

单条 commit（main 分支，与既有教程提交同款 conventional 前缀）：

```
feat(tutorials): 同步二阶段 Harbor/MinIO——spec 解除排除 + 六篇教程 + 复用 21–31 截图
```

## 6. 不做（YAGNI 边界）

- 不覆盖 LDAP（仍未验证）
- 不补拍新截图（复用 21–31 验证证据）
- 不把教程写成 Harbor/MinIO 操作手册——教程是角色上手指南，组件细节回溯设计 spec 与 test-plan
- 不改一阶段已验证的流程叙事（developer 的 clone→MR、owner 的 tag→Release 主线不动，只追加二阶段旁注）
