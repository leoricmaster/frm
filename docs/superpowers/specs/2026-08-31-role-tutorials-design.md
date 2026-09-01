# 角色入门教程设计（HTML 版）

- 日期：2026-08-31
- 状态：已与发起人逐节确认
- 读者：刚毕业的初级工程师、未接触过 GitLab 实践的老工程师
- 素材：一阶段 20 张 + 二阶段 11 张（21–31）原型截图，均复用验证证据、不补拍；二阶段截图于 2026-09-01 验证（test-plan §8）后纳入

## 1. 目标与形态

为五类角色各写一份自包含 HTML 入门教程，外加一个角色导航索引页。教程与目标角色的日常工作强相关：每一步都对应他们在原型实例上真实会做的操作，图文并茂（截图 + 网页操作路径 + git 命令并行），5–10 分钟读完即可上手。

```
docs/tutorials/
├── index.html              # 角色导航：5 张角色卡片 + 通用入门（登录/导航/看流水线）
├── developer.html          # 开发工程师（Developer 30）
├── owner.html              # 仓库 Owner（Maintainer 40）
├── viewer.html             # 只读协作者（Guest 10）
├── platform.html           # 平台工程（ci-templates 守护者）
├── field-engineer.html     # 驻场工程师（离线工作流）
└── assets/                 # 20 张截图的副本（复制，非软链）
```

- 全中文，内联 CSS，无 JS、无外部依赖，双击即开，打印友好（可作培训讲义）。
- 图片相对路径 `assets/xx.png` 引用，与 HTML 同仓提交。

## 2. 已确认的关键决策

| 决策点 | 结论 |
|---|---|
| 交付形态 | 5 个独立 HTML + 1 个索引页 |
| 操作讲法 | 网页操作路径 + git 命令并行展示 |
| 图片策略 | 复用现有 20 张截图，不补拍 |
| 行文风格 | 操作与原理穿插：先"做什么"，再"为什么"（白话解释设计规则）；术语首现给白话释义 |
| 内容架构 | 每份教程完全自包含，互不依赖（仅 index 互链） |

## 3. 每份教程的统一骨架

1. **你是谁** — 角色定位、典型一天/一次任务概述
2. **你能/不能做什么** — 权限表（能做 ✅ / 不能做 ❌）
3. **典型任务流** — 4–7 个步骤卡片，每卡片含：编号、做什么、截图、对应命令块
4. **常见报错自救** — 真实报错信息 + 处置方法
5. **红线清单** — 绝对禁止的事（关联设计章节）
6. **延伸阅读** — 链到设计文档对应章节

## 4. 视觉体系（全站统一）

- 顶栏：角色名 + 一句话定位 + 权限徽章（如 `Developer 30`）
- 步骤卡片：编号 + "做什么" + 截图 + 命令块（网页操作 ⟷ 命令行并列）
- 三种提示框，颜色语义统一：
  - 🔍 **为什么**（蓝）— 背后规则的白话解释
  - ⚠️ **红线**（红）— 绝对禁止的事
  - 💡 **自救**（黄）— 报错时怎么办
- 截图统一标注：图下一行灰字说明"这是哪个页面、看哪里"
- 字体 `system-ui, "PingFang SC", "Microsoft YaHei"`，正文 15px/1.7

## 5. 五份教程内容大纲

### 5.1 developer.html — 开发工程师

- 任务流：clone → 建特性分支 → 改码 push → 建 MR → 等 CI 绿 →（可选）修到绿
- 用图：03-groups、08-mr-list、10-protect、15-mr2-changes、21-perception-pipelines（二阶段）
- 命令：`git clone / checkout -b / push -u origin`
- 🔍 为什么不能直推 main（§4.2 保护分支）
- 🔍 CI 现在还做什么（二阶段旁注）：固件流水线构建镜像推 Harbor、算法流水线从 MinIO 取数+训练产物推回 MinIO——但开发操作不变，push 完等绿（§5.3/§6.4）
- 自救：流水线红了怎么办（点 job 看日志 → 本地复跑 → push 空提交重触发）
- 红线：不上明文密钥、不 `-f` 强推、main 不直推

### 5.2 owner.html — 仓库 Owner

- 任务流：评审 MR（diff → approve）→ 合入 → 打 tag → 手动批准晋升 → 建 Release → 核对 manifest 追溯链
- 用图：14-mr2-merged、16-release、17-pipeline14、27-harbor-frmci（二阶段）
- 🔍 四方一致：manifest.commit = main HEAD = tag commit = MR 合入 commit（§6.3）
- 🔍 为什么 promote-release 是手动（§6.3 制品晋升）
- 🔍 产物三去向（二阶段旁注，§6.4）：.bin+manifest 进 GitLab Release（不变）；容器镜像进 Harbor、模型权重进 MinIO，各自有 tag/指针可追到同一 commit
- 红线：不跳过评审合自己的 MR、不在本机编发布产物（§5.4 铁律）

### 5.3 viewer.html — 只读协作者

- 任务流：登录找项目 → 浏览项目信息 → 从 Release 下载制品 + manifest → 核对 manifest
- 用图：05-project-guest、13-packages、16-release
- 🔍 你看到 403 不是故障，是权限边界（§4.3）
- 自救：clone 被拒 → 找 Owner 开权限或走 Release 通道
- 🔍 产物三去向（二阶段旁注，§6.4）：容器镜像存 Harbor、模型存 MinIO，需单独授权找平台组；Guest 的 Release 下载通道不变
- 红线：不把制品发给未授权的人

### 5.4 platform.html — 平台工程

- 任务流一：改 ci-templates → MR 评审 → 合入 → 验证下游传播（看下游 job trace）
- 任务流二（二阶段新增）：纳管镜像仓库与对象存储——Harbor 两项目（frm-ci 直推 + docker-hub-proxy 代理缓存，§5.3 出口收敛）、MinIO 三桶（dataset-model / field-dropzone / training-output，§6.4）、CI 凭据受保护+打码（§6.5）
- 用图：11-ci-templates、19-ci-mr、18-job18-trace、26-harbor-projects、28-harbor-proxy、29-minio-buckets、23-fetch-dataset-job（后四张二阶段）
- 🔍 "宪法"比喻：模板改一行，全部仓库生效（§6.2）
- 🔍 include 快照：retry 不重解析，改模板后看**新**流水线（7.3-4）
- 🔍 为什么构建区拉包走 Harbor 代理（§5.3）：无外网直连、出口收敛、日志可查
- 红线：下游 `.gitlab-ci.yml` 不 include 通用层的不予合入（§6.2 制度）；Harbor/MinIO 凭据不进仓库、不进聊天工具（§6.5）

### 5.5 field-engineer.html — 驻场工程师

- 任务流：出场前打包（代码 + Release 制品 + checklist）→ 现场三个场景（刷固件/改码/取数）→ 应急兜底
- 用图：16-release、20-mr4-field、29-minio-buckets、30-minio-dataset（后两张二阶段）
- 🔍 为什么"现场永远不编译正式版"（§7.2，本地临时验证除外）+ 本地编译/DLP 旁注（工具链随 checklist 带齐、透明加解密不拦本机编译，§7.1/§7.3/§7.4）+ 临时包是救火不是工作方式（§7.3）
- 🔍 场景三取数（二阶段补实物，§7.2）：投放区 write-only——现场只能投、不能删/列别人的；回公司由平台组归档进 dataset-model 的 field-archive 目录
- 🔍 24h 补 MR 的绑定条件：只约束"临时包刷上了机器"的应急——机器跑过非 CI 产物必须回追溯链；纯本地验证后放弃的改动按普通分支废弃即可
- 自救：现场没网改了码（本地 commit → 回网 push → 补 MR）
- 红线：改动不以 commit 回中心仓 = 违规（§7.2 硬规则）；现场数据不走私人网盘/U 盘，只进投放区（§7.4）

### 5.6 index.html — 角色导航 + 通用入门

- 5 张角色卡片（"我是谁 → 看哪份"）
- 通用入门区（所有角色共用的基本动作）：01-login、02-dashboard、04-group-tree、06-pipelines、07-ci-success、12-members
- 产物去向小框（二阶段新增，§6.4）：三去向一句话——固件 .bin→GitLab Release、容器镜像→Harbor、大文件/模型→MinIO
- 术语速查：MR、CI、tag/Release、manifest、保护分支 + Harbor、MinIO、投放区（二阶段新增）的白话释义
- 用图（二阶段新增）：29-minio-buckets（产物去向小框配图）

## 6. 截图分配总表

（16-release 在 owner/viewer/field 三份中复用、29-minio-buckets 在 platform/field/index 三份中复用，符合"自包含"原则；一阶段 19 张已用 + 二阶段 7 张复用（21/23/26/27/28/29/30），09-mr-closed 弃用。）

| 截图 | 用于 |
|---|---|
| 01-login, 02-dashboard, 04-group-tree, 06-pipelines, 07-ci-success, 12-members | index 通用入门 |
| 03-groups, 08-mr-list, 10-protect, 15-mr2-changes | developer |
| 14-mr2-merged, 16-release, 17-pipeline14 | owner |
| 05-project-guest, 13-packages, 16-release | viewer |
| 11-ci-templates, 19-ci-mr, 18-job18-trace | platform |
| 16-release, 20-mr4-field | field-engineer |
| 21-perception-pipelines | developer（CI 多阶段，二阶段） |
| 23-fetch-dataset-job | platform（CI 凭据打码）、developer（二阶段） |
| 26-harbor-projects, 28-harbor-proxy, 29-minio-buckets | platform 纳管节（二阶段） |
| 27-harbor-frmci | owner 镜像归宿（二阶段） |
| 29-minio-buckets, 30-minio-dataset | field-engineer 取数场景、index 产物去向（二阶段） |

## 7. 验收标准

1. 6 个 HTML 双击即开（无外网依赖），图片全部正常显示
2. 每份教程的步骤与 §7 模拟验收中验证过的真实操作一一对应，无臆造步骤
3. 初级工程师视角试读：不查其他资料能独立完成本角色典型任务
4. 打印（或打印预览）不破版

## 8. 不做什么（YAGNI）

- 不做搜索、多语言、暗色模式
- 不补拍新截图
- 不写 Git 本身的教学（如何 add/commit 属于 Git 入门，不是本体系教程范围；教程内命令只覆盖与 GitLab 交互相关的操作）
- 不覆盖 LDAP（原型未验证，仅在延伸阅读提及设计方向）；Harbor/MinIO 已于二阶段验证（test-plan §8 九项全 ✅），纳入 platform / field-engineer / developer / owner 相应教程并复用 21–31 截图
- 不把教程写成 Harbor/MinIO 操作手册——教程是角色上手指南，组件配置细节回溯设计 spec 与 test-plan，教程只讲角色视角会看到什么、怎么对应
