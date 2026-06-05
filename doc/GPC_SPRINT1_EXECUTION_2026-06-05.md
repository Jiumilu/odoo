# GlobalCloud GPC 第一轮 P0/P1 修复冲刺记录

日期：2026-06-05

## 1. 本轮目标

- 建立最小 CI 质量门禁。
- 补齐交付基础文档。
- 将部分 P0/P1 从评估问题转为已处理或待复评状态。

## 2. 状态变化

| 任务ID | 修复前状态 | 修复后状态 | 证据 |
|---|---|---|---|
| GPC-P0-001 | 待处理 | 待确认 | `.github/workflows/gpc-quality.yml` |
| GPC-P0-003 | 待处理 | 已关闭 | `README.md`、`doc/GPC_DEPLOYMENT.md`、`doc/GPC_OPERATIONS.md`、`doc/GPC_ROLLBACK.md` |
| GPC-P1-003 | 待处理 | 已关闭 | `doc/GPC_CHANGELOG.md`、`doc/GPC_RELEASE_NOTES.md` |
| GPC-P1-004 | 待处理 | 已关闭 | `README.md` |

## 3. 本轮未关闭项

| 任务ID | 状态 | 原因 |
|---|---|---|
| GPC-P0-002 | 待处理 | 需要实际验证 3-5 条核心业务流程 |
| GPC-P1-001 | 待处理 | 需要处理登录失败、会话过期、权限不足和 404 中文提示 |
| GPC-P1-002 | 待处理 | 需要覆盖率或测试报告产物 |
| GPC-P1-005 | 待处理 | 需要确认并修正默认用户时区 |

## 4. 下一步动作

优先处理 `GPC-P0-002`。完成标准是至少 3 条核心流程具备入口、数据写入、查看、状态变化和验收记录。

## 5. 本地验证结果

| 检查项 | 命令 | 结果 |
|---|---|---|
| Python 依赖一致性 | `.venv311/bin/python -m pip check` | 通过，`No broken requirements found.` |
| 工具脚本编译 | `.venv311/bin/python -m py_compile tools/gpc_health_check.py tools/gpc_reverse_proxy.py tools/complete_zh_cn_i18n.py` | 通过 |
| 中文 PO 语法 | `find addons odoo/addons -path '*/i18n/zh_CN.po' -print0 \| xargs -0 -n 1 msgfmt --check -o /tmp/gpc_i18n_check.mo` | 通过 |
| 最小 Odoo test runner | `.venv311/bin/python odoo-bin -c .runtime/gpc-odoo.conf -d GCGPC --test-enable --test-tags ':TestSelector.test_selector_parser' --stop-after-init --workers=0 --max-cron-threads=0 --http-port=18091 --log-level=test` | 通过，`0 failed, 0 error(s) of 1 tests` |
| 本地健康检查 | `.venv311/bin/python tools/gpc_health_check.py --json` | local health `100/100`，production readiness `85/100`，扣分原因仅为本轮未提交文档导致 dirty worktree |
