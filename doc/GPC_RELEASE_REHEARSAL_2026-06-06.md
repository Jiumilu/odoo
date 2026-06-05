# GlobalCloud GPC 上线演练记录

日期：2026-06-06

## 演练范围

本轮演练目标是证明当前仓库具备继续交付的基础条件：服务可运行、数据库健康、核心模块安装、认证后台入口可达、核心业务流程闭环、真实浏览器表单路径可用。

## 演练步骤与结果

| 步骤 | 命令/证据 | 结果 |
|---|---|---|
| 工作树健康 | `git status --short --branch` | 提交后复跑应为干净工作树 |
| 系统健康 | `.venv311/bin/python tools/gpc_health_check.py --json` | `local_health_score=100`，`production_readiness_score=100` |
| 单元测试 | `.venv311/bin/python -m unittest discover -s tests -p 'test_*.py' -v` | `11/11 OK` |
| 认证后台 smoke | `.venv311/bin/python tools/gpc_authenticated_backend_smoke.py --base-url http://127.0.0.1:8069` | 登录成功，9 个后台入口通过 |
| 核心流程 smoke | `tools/gpc_core_flow_smoke.py --report-json ... --report-md ...` | 联系人、CRM、销售、采购、库存、制造、项目、权限边界均通过 |
| 覆盖率 | `coverage report -m tools/gpc_core_flow_smoke.py` | 核心 smoke coverage `99%` |
| 浏览器表单 E2E | `node tools/gpc_browser_form_e2e.cjs --base-url http://127.0.0.1:8069 ...` | 登录、联系人新建、保存、搜索通过 |

## 回滚方案

- 代码回滚：回退最近 GPC 质量工具提交，不回退上游 Odoo 源码。
- 运行态回滚：停止 8069 反向代理和 Odoo worker，恢复到直接 8070 访问或重新执行 `.runtime/gpc-odoo.conf` 启动命令。
- 数据回滚：核心 ORM smoke 使用事务 rollback；浏览器表单 E2E 会创建测试联系人，可通过名称前缀 `GPC Browser Form E2E` 定位并删除。

## 演练结论

当前项目具备继续开发和交付准备基础。正式上线前仍需把浏览器 E2E 的 Playwright 来源标准化到目标 CI/部署环境，并执行远端 CI 或目标环境等价门禁。
