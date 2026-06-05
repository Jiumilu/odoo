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
- 本地工具单元测试已加入 `tests/test_gpc_tools.py`，并纳入 `.github/workflows/gpc-quality.yml`。
- 外部集成范围已写入 `doc/GPC_SCOPE_AND_EXTERNAL_INTEGRATIONS.md`。

## 2. 100 分完成判定

| 维度 | 是否可声称 100 | 当前证据 | 阻止 100 的原因 |
|---|---|---|---|
| 健康度 | 接近 | `tools/gpc_health_check.py --json` 可恢复到 local/prod 100；8069/8070/8072 均可运行 | 当前本轮仍有待提交文件，提交后才可重新确认 clean worktree |
| 功能完整性 | 接近 | 核心模块和 9 条 ORM smoke 通过；登录后 9 个后台入口浏览器通过 | 仍缺真实用户级表单点击 E2E 自动化，当前由 ORM smoke 证明业务闭环 |
| 软件测试 | 未完成 | 单元测试 6/6 通过；核心 smoke 通过；核心 smoke coverage 88% | 未达到 95% 覆盖率目标；浏览器 E2E 尚未脚本化进入 CI |
| 中文化 | 接近 | 公开页面、登录页、404、登录后后台入口无可见旧品牌残留 | 导出文件、邮件预览、报表字段仍需抽查 |
| 治理成熟度 | 接近 | README、CI、部署、运维、回滚、范围说明、测试报告、证据文件齐备 | 远端 GitHub Actions 未实际运行，ADR/上线演练记录仍不足 |

## 3. 下一步

要真实达到 100，下一轮必须完成：

1. 提交本轮代码与证据后复跑健康检查，确认 clean worktree 下 local/prod health 均为 100。
2. 将浏览器登录态 E2E 脚本化，至少覆盖登录、进入后台模块、创建/搜索/查看一条业务记录。
3. 将核心流程 coverage 从 88% 提升到 95% 以上，或建立明确的风险接受说明。
4. 补 ADR、上线演练记录、远端 CI 或本地等价 CI 完整日志。
5. 抽查导出、邮件预览、报表字段的中文化。

## 4. 当前结论

当前目标尚未完成，不能把平均分 93 或局部补强说成 100。继续推进。
