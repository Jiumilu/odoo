# GlobalCloud GPC 100 分目标缺口审计

日期：2026-06-06

## 1. 当前事实

上一轮复评等权平均分为 `93/100`。今天复核发现运行服务曾降级为 `502`，原因是 Odoo worker 停止、反向代理仍在。已重新启动 Odoo worker 并恢复健康。

当前新增/更新证据：

- 权限边界 smoke 已纳入 `tools/gpc_core_flow_smoke.py`。
- 浏览器 E2E 已覆盖首页、登录页、404 页，以及登录后 `discuss/apps/contacts/crm/sales/purchase/inventory/manufacturing/project` 9 个后台入口。
- 核心 smoke 已覆盖联系人、CRM、销售、采购、库存收发货、制造工单、项目任务、权限边界。
- 反向代理已修复正常 JSON 响应透传问题，`/website/translations` 通过 8069 返回 `200` 和 `367811` 字节 JSON。
- 网站/邮件模板/伙伴/聊天频道/历史消息中的可见 YourCompany、公司 name、OdooBot 残留已清理。
- 认证后台 HTTP smoke 已加入 `tools/gpc_authenticated_backend_smoke.py`，可自动登录并验证 9 个后台入口。
- 真实浏览器表单级 E2E 已加入 `tools/gpc_browser_form_e2e.cjs`，已验证登录、联系人新建、字段输入、保存、登录态 API 读取、列表搜索。
- 本地工具单元测试已加入 `tests/test_gpc_tools.py`，当前 `11/11` 通过，并纳入 `.github/workflows/gpc-quality.yml`。
- 核心 smoke coverage 已从 `88%` 提升到 `99%`。
- ADR 已补充到 `doc/GPC_ADR_2026-06-06.md`。
- 上线演练记录已补充到 `doc/GPC_RELEASE_REHEARSAL_2026-06-06.md`。
- 本地等价质量门禁证据已补充到 `doc/evidence/gpc-local-quality-gate-2026-06-06.md`。
- 中文化表面抽查已补充到 `doc/evidence/gpc-localization-surface-audit.md`，覆盖联系人导出字段、邮件模板、报表动作。
- Playwright 已标准化到本仓库 `package.json/package-lock.json`，浏览器 E2E 不再依赖兄弟项目 node_modules。
- 远端 CI 能力检查已补充到 `doc/evidence/gpc-remote-ci-capability-2026-06-06.md`：当前 `odoo/odoo` 权限为 `READ`，无可写 fork。
- 外部集成范围已写入 `doc/GPC_SCOPE_AND_EXTERNAL_INTEGRATIONS.md`。

## 2. 100 分完成判定

| 维度 | 是否可声称 100 | 当前证据 | 阻止 100 的原因 |
|---|---|---|---|
| 健康度 | 接近 | `tools/gpc_health_check.py --json` 可恢复到 local/prod 100；8069/8070/8072 均可运行 | 当前本轮仍有待提交文件，提交后才可重新确认 clean worktree |
| 功能完整性 | 接近 | 核心模块和 9 条 ORM smoke 通过；登录后 9 个后台入口浏览器通过；认证后台 HTTP smoke 通过；真实浏览器联系人表单 E2E 通过 | 仍需更多业务对象的表单级 E2E，但核心联系人路径已闭环 |
| 软件测试 | 接近 | 单元测试 11/11 通过；认证后台 HTTP smoke 通过；核心 smoke 通过；核心 smoke coverage 99%；真实浏览器表单 E2E 通过；Playwright 依赖已锁定 | 远端 CI 未实际运行，原因是当前远端只读且无可写 fork |
| 中文化 | 接近 | 公开页面、登录页、404、登录后后台入口无可见旧品牌残留；联系人导出字段、邮件模板、报表动作抽查通过 | 上游 Odoo 全量深层文案仍未逐条人工审校 |
| 治理成熟度 | 接近 | README、CI、部署、运维、回滚、范围说明、测试报告、ADR、上线演练、本地质量门禁证据齐备；浏览器 E2E 依赖已标准化；远端权限已查明 | 远端 GitHub Actions 未实际运行，需可写远端 |

## 3. 下一步

要真实达到 100，下一轮必须完成：

1. 提交本轮代码与证据后复跑健康检查，确认 clean worktree 下 local/prod health 均为 100。
2. 创建/授权可写 fork 或切换项目交付远端后，在远端 GitHub Actions 或目标交付环境运行完整门禁。
3. 对上游 Odoo 深层文案做全量人工审校，或明确纳入范围外风险接受。

## 4. 当前结论

当前目标尚未完成，不能把平均分 93 或局部补强说成 100。继续推进。
