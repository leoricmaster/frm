# 运维与复现手册：极狐 GitLab 原型环境

- 状态：草稿
- 范围：把一个空白极狐 GitLab 实例从零搭起来、复刻原型终态、日常运维账号与备份——交付平台运维与复现环境的人员照着走。
- 与其他文档的边界：决策（为什么这么做、为什么不用别的）见 `docs/design/` 与 `docs/adr/`；本文只写「怎么照着做」。坑位差异不抄，指向验证结论。

## 0. 前置条件

| 项 | 要求 | 出处 |
|---|---|---|
| GitLab 主机 | 8C / 16G / 200G SSD（原型按本机富余可放宽） | 设计 §7 资源清单 |
| Docker + compose | 已装 | — |
| 占用端口 | 8081 web / 8082 ssh / 8083 registry(预留) / 9002 MinIO API / 9003 MinIO Console | compose.yml 注释 |
| 镜像 | `registry.gitlab.cn/omnibus/gitlab-jh:19.3.1-jh.0` 预拉（离线机房） | ADR-0021 |

原型凭据 `Excavator#2026Proto` 内嵌于 compose，仅限本测试栈；正式实施凭据另行管理。

> 端口选择的来由：测试机 8080 / 9000 / 9001 已被占用，故改用 8081–8083 与 9002 / 9003。若你的机器这些端口空闲，可自行改回默认。

## 1. 起栈

```bash
cd gitlab-compose-test
docker compose up -d
```

栈含 GitLab / Runner / MinIO / minio-init（幂等建三桶）。各组件作用与资源上限见 `gitlab-compose-test/docker-compose.yml` 注释，不在此重复。

待 GitLab 就绪（首次约 3–5 分钟）后浏览器开 http://10.66.35.35:8081。

## 2. 初始化（首次 root 登录后做一次）

1. **root 首登改密**：用 compose 内嵌口令登录，立即改密。
2. **核对注册已关**：compose 已默认 `gitlab_signup_enabled=false` 与 `can_create_group=false`，正常无需动作；登录页应无「注册」入口即为生效。

> 为什么关注册？账号一律管理员开通（见 §5.1），契合设计 §4.3「平台组统一开通」口径，也为阶段 1 接 LDAP 时账号名对齐留好干净底子。`can_create_group` 同关，防止用户乱建顶层组。
>
> LDAP 域账号对接是**阶段 1 正式实施项**，现阶段用本地账号。上线前管理员按 AD 用户名建号，LDAP 接通后同名域账号首次登录即复用，切换干净（ADR-0005）。

## 3. 复刻实例终态

实例的完整状态（组树 / 用户 / 仓库 / MR / CI / tag / Release / 单据 / 看板）由重建脚本一键复刻：

```bash
python3 rebuild_jh_state.py A|B|...|Z
```

逐段一句话说明（按依赖顺序）：

| 段 | 做什么 |
|---|---|
| A | 用户 + 组树（顶层 intel_excavator + 六子组）+ platform 成员 + ci-templates 含宪法 MR !1/!2 |
| B | firmware 项目 + 成员 + 保护分支 + CI v1 |
| C | firmware MR !1/!2 + tag v0.2.0-field + Release |
| D | firmware MR !3/!4 |
| E | HARBOR_* 组变量 + CI 演进到终版 + MR 模板 |
| F | firmware MR !5（液压抖动）+ tag v0.9.0-rc1 + Release |
| G | perception 仓库 + MINIO_* 变量 + 流水线 |
| H | intake + 11 标签 + 里程碑 + 四单分诊 |
| I | 组看板六状态列（需先浏览器访问过看板页——见已知坑位） |
| J | 全员中文 + 吊销模拟 PAT + 终态核对 |
| Z | 吊销模拟 PAT（收尾单独跑） |

脚本落盘进度 `/tmp/jh-rebuild-state.json`，可断点续跑。

## 4. 已知坑位（不抄，指向验证结论）

极狐与 CE 的七处 API/路由差异、组看板懒创建、`/repository/files` 恒 404 等规避方式，见原型验证结论 §3-13 差异表：
`docs/design/2026-09-07-prototype-verification.md`

## 5. 日常运维

### 5.1 开账号（关注册后的唯一入口）

原型环境无 SMTP（compose 未配邮件），发不了重置链接，账号由管理员显式建：

- **界面**：管理区 → 用户 → 新建用户，填姓名 / 用户名（对齐 AD）/ 邮箱，设初始密码。
- **API**：`POST /api/v4/users`（管理员 token），可脚本批量建号，对上线波峰好用。

初始密码线下交付（口述 / 凭证通道），要求首登改密。权限另算——建号后由仓库 Owner 加组加角色（CE 无分组同步，见 ADR-0005 边界表），账号 ≠ 权限。

### 5.2 封禁与离职回收

GitLab 不自动清离职者存量访问（SSH key / 令牌 / 会话）。阶段 1 实施定时脚本比对 AD 禁用名单 → 调 API 封禁账号（ADR-0005）。原型验证即以此模式操作（验证结论 §3 实测#12）。

### 5.3 备份与恢复

GitLab 原生全量备份每日，含配置 + 仓库 + 数据库，保留异地 / 离线副本；恢复演练每半年一次（ADR-0020）。MinIO 数据按资产备份（数据集 / 权重 / 现场采集不可再生）。**未演练过的备份等于没有备份。**

## 6. 证据与留档

- 实例终态镜像：`gitlab-compose-test/*-repo/`
- 验证证据截图 01–43：`gitlab-compose-test/screenshots/`
- 决策来源：`docs/adr/`（账号 ADR-0005、备份 ADR-0020、版本 ADR-0021）
