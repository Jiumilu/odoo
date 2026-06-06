# GlobalCloud GPC 本地质量门禁证据

日期：2026-06-06

## 已执行门禁

| 门禁 | 命令 | 当前结果 |
|---|---|---|
| 工作树 | `git status --short --branch` | 无未提交或未跟踪文件 |
| 健康检查 | `.venv311/bin/python tools/gpc_health_check.py --json` | `local_health_score=100`，`production_readiness_score=100` |
| Python 编译 | `.venv311/bin/python -m py_compile ...` | 通过 |
| 单元测试 | `.venv311/bin/python -m unittest discover -s tests -p 'test_*.py' -v` | `14/14 OK` |
| Node 依赖 | `npm ci` | Playwright 依赖可从本仓库 lockfile 安装，lockfile 使用官方 npm registry |
| 浏览器脚本语法 | `npm test` | 通过 |
| 认证后台 HTTP smoke | `.venv311/bin/python tools/gpc_authenticated_backend_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069` | 通过，9 个后台入口无失败 |
| 核心业务 smoke | `.venv311/bin/python tools/gpc_core_flow_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069 --report-json doc/evidence/gpc-core-flow-smoke.json --report-md doc/evidence/gpc-core-flow-smoke.md` | 通过 |
| 核心 smoke 覆盖率 | `.venv311/bin/python -m coverage report -m tools/gpc_core_flow_smoke.py` | `tools/gpc_core_flow_smoke.py 187 stmts, 0 miss, 100%` |
| 浏览器表单 E2E | `node tools/gpc_browser_form_e2e.cjs --base-url http://127.0.0.1:8069 --report-json doc/evidence/gpc-browser-form-e2e.json --report-md doc/evidence/gpc-browser-form-e2e.md --screenshot doc/evidence/gpc-browser-form-e2e.png` | 通过 |
| 远端 CI | `gh run list --repo Jiumilu/odoo --branch gpc-quality-100` / `gh run view <run>` | 最新成功 run 可复核；已验证成功 run 包括 `27046352273`、`27046712068`、`27046852713` |

## 当前限制

- 当前门禁覆盖 GPC 已启用交付范围。未配置真实凭证的外部邮件、短信、OAuth、Recaptcha、支付通道不计入当前评分范围，进入上线前需要单独联调。

## 结论

本地与远端质量门禁已覆盖安装后运行健康、单元测试、核心业务 ORM 流程、认证后台入口、真实浏览器表单路径和覆盖率证据，当前门禁可支撑五项评分 `100/100`。
