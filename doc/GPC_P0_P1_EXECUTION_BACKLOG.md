# GlobalCloud GPC P0/P1 执行 Backlog

基线版本：GPC-BL-2026-06-05-01
状态枚举：待处理 / 进行中 / 阻塞 / 待确认 / 已关闭 / 范围外已登记
负责人默认值：待分配

| 任务ID | 项目 | 问题 | 维度 | 严重级别 | 证据 | 修复目标 | 验收标准 | 负责人 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| GPC-P0-001 | GlobalCloud GPC | 历史问题：无 CI workflow | 软件测试/治理 | 高 | `.github/workflows/gpc-quality.yml` 已建立；远端 run `27046352273` 成功 | 建立最小自动质量门禁 | 远端 CI 自动运行 pip check、py_compile、msgfmt、HTTP smoke、Odoo test runner、认证后台 smoke、Browser E2E、核心流程 smoke | 待分配 | P0 | 已关闭 |
| GPC-P0-002 | GlobalCloud GPC | 核心业务流程未闭环 | 功能完整性 | 高 | 数据库模块状态已升级：核心业务模块 contacts、crm、sale_management、purchase、stock、mrp、project 已安装；`doc/evidence/gpc-core-flow-smoke.json` 通过 | 明确并验证最小核心业务流程 | 联系人、CRM 机会、销售订单、采购订单、项目任务均有入口、数据写入、查看、状态变化和验收记录 | 待分配 | P0 | 已关闭 |
| GPC-P0-003 | GlobalCloud GPC | 历史问题：缺生产部署、运维、回滚说明 | 治理成熟度 | 高 | README、部署说明、运维说明、回滚预案、备份恢复说明已齐备 | 形成可交接部署运维包 | README、部署说明、运维说明、回滚预案、备份恢复说明齐备 | 待分配 | P0 | 已关闭 |
| GPC-P1-001 | GlobalCloud GPC | 登录失败、会话过期等错误提示英文/技术化 | 中文化 | 中高 | 8069 主代理返回中文错误提示，JSON `debug` 为空；404 页面标题为 `页面未找到 \| 绿色供应链公共服务平台` | 用户可理解下一步操作 | 登录失败、会话过期、权限不足、404 页面均为中文用户提示，且不暴露 traceback | 待分配 | P1 | 已关闭 |
| GPC-P1-002 | GlobalCloud GPC | 无覆盖率和测试报告 | 软件测试 | 中高 | `doc/GPC_TEST_REPORT_2026-06-05.md`、`doc/evidence/gpc-coverage.txt`、`doc/evidence/gpc-coverage.json` | 建立测试证明力基线 | 有最小测试报告；定制工具至少有单元或集成测试计划 | 待分配 | P1 | 已关闭 |
| GPC-P1-003 | GlobalCloud GPC | 历史问题：无项目级 changelog/release note | 版本治理 | 中 | `doc/GPC_CHANGELOG.md` 与 `doc/GPC_RELEASE_NOTES.md` 已建立并更新到 100 分闭环 | 建立版本追踪 | 新增 CHANGELOG 与 RELEASE_NOTES，记录本地变更和远端 CI 结果 | 待分配 | P1 | 已关闭 |
| GPC-P1-004 | GlobalCloud GPC | 历史问题：中文 README 和使用/测试说明缺失 | 中文化/治理 | 中 | README 已覆盖安装、启动、端口、数据库、健康检查、测试、交付文档和当前限制 | 中文维护者可独立启动和验证 | README 覆盖安装、启动、端口、数据库、健康检查、测试、常见问题 | 待分配 | P1 | 已关闭 |
| GPC-P1-005 | GlobalCloud GPC | 默认用户时区不符合中国业务环境 | 配置/本地化 | 中 | `res_users` 关联伙伴语言均为 zh_CN，时区均为 Asia/Shanghai | 修正本地化默认配置 | 管理员/内部用户默认时区为 Asia/Shanghai，日期时间显示经抽查正确 | 待分配 | P1 | 已关闭 |

## 非本轮优先项

| 任务ID | 项目 | 问题 | 维度 | 优先级 | 状态 |
|---|---|---|---|---|---|
| GPC-P2-001 | GlobalCloud GPC | 历史问题：OdooBot、My Website、YourCompany、Powered by Odoo 等模板残留 | 中文化 | P2 | 已关闭 |
| GPC-P2-002 | GlobalCloud GPC | 外部集成邮件、短信、Outlook/Gmail、Recaptcha 未做真实连通验证 | 功能/测试 | P2 | 范围外已登记 |
| GPC-P2-003 | GlobalCloud GPC | 历史问题：术语表缺失 | 中文化/治理 | P2 | 已关闭，见 `doc/GPC_TERMINOLOGY.md` |
| GPC-P2-004 | GlobalCloud GPC | 历史问题：ADR/架构决策记录缺失 | 治理 | P2 | 已关闭 |
