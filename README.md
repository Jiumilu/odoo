# GlobalCloud GPC

GlobalCloud GPC（绿色供应链公共服务平台）是基于 Odoo 19.0 的本地化业务平台。本仓库保留 Odoo 核心架构，在当前阶段重点完成品牌中文化、运行健康检查、交付治理和核心流程验证。

## 当前状态

- 当前分支：`19.0`
- 运行入口：`http://127.0.0.1:8069`
- Odoo worker HTTP：`127.0.0.1:8070`
- Odoo websocket/gevent：`127.0.0.1:8072`
- PostgreSQL：本地 Docker 容器 `gpc-postgres`，映射端口 `127.0.0.1:54329`
- 运行配置：`.runtime/gpc-odoo.conf`，该文件包含本地密钥，禁止提交

## 本地启动

1. 准备 Python 3.11 虚拟环境并安装依赖。

   ```bash
   python3.11 -m venv .venv311
   .venv311/bin/python -m pip install --upgrade pip setuptools wheel
   .venv311/bin/python -m pip install -r requirements.txt
   ```

2. 准备运行配置。

   ```bash
   cp config/gpc-odoo.production.conf.example .runtime/gpc-odoo.conf
   chmod 600 .runtime/gpc-odoo.conf
   ```

   修改 `.runtime/gpc-odoo.conf` 中的数据库密码、主密码、`addons_path` 和 `data_dir`。

3. 启动 PostgreSQL。

   当前本地约定使用 Docker 容器 `gpc-postgres`，端口映射到 `127.0.0.1:54329`。如需生产部署，请参考 [GPC_DEPLOYMENT.md](/doc/GPC_DEPLOYMENT.md)。

4. 启动 Odoo worker。

   ```bash
   .venv311/bin/python odoo-bin -c .runtime/gpc-odoo.conf -d GCGPC
   ```

5. 启动本地反向代理。

   ```bash
   .venv311/bin/python tools/gpc_reverse_proxy.py \
     --listen-host 127.0.0.1 \
     --listen-port 8069 \
     --http-target http://127.0.0.1:8070 \
     --websocket-target http://127.0.0.1:8072
   ```

6. 打开系统。

   ```text
   http://127.0.0.1:8069
   ```

## 健康检查

本地服务启动后运行：

```bash
.venv311/bin/python tools/gpc_health_check.py --json
```

健康检查会验证登录页、应用入口、PostgreSQL、数据库锁、模块待处理状态、Python 依赖、中文 PO 语法和本地安全配置。

## 最小测试

当前仓库的最小自动化质量门禁包括：

```bash
.venv311/bin/python -m pip check
.venv311/bin/python -m py_compile tools/gpc_health_check.py tools/gpc_reverse_proxy.py tools/complete_zh_cn_i18n.py
find addons odoo/addons -path '*/i18n/zh_CN.po' -print0 | xargs -0 -n 1 msgfmt --check -o /tmp/gpc_i18n_check.mo
.venv311/bin/python odoo-bin -c .runtime/gpc-odoo.conf -d GCGPC --test-enable --test-tags ':TestSelector.test_selector_parser' --stop-after-init --workers=0 --max-cron-threads=0 --http-port=18091 --log-level=test
```

核心业务 smoke test：

```bash
.venv311/bin/python tools/gpc_core_flow_smoke.py \
  --config .runtime/gpc-odoo.conf \
  --database GCGPC \
  --base-url http://127.0.0.1:8069 \
  --report-json doc/evidence/gpc-core-flow-smoke.json \
  --report-md doc/evidence/gpc-core-flow-smoke.md
```

覆盖率基线：

```bash
.venv311/bin/python -m pip install -r requirements-dev.txt
.venv311/bin/coverage run --include='*/tools/gpc_core_flow_smoke.py' tools/gpc_core_flow_smoke.py \
  --config .runtime/gpc-odoo.conf \
  --database GCGPC \
  --base-url http://127.0.0.1:8069
.venv311/bin/coverage report -m tools/gpc_core_flow_smoke.py
```

GitHub Actions 工作流位于 [.github/workflows/gpc-quality.yml](/.github/workflows/gpc-quality.yml)。

## 交付文档

- [执行基线](/doc/GPC_EXECUTION_BASELINE_2026-06-05.md)
- [P0/P1 执行 Backlog](/doc/GPC_P0_P1_EXECUTION_BACKLOG.md)
- [下一阶段处置决策](/doc/GPC_NEXT_STAGE_DECISION.md)
- [部署说明](/doc/GPC_DEPLOYMENT.md)
- [运维说明](/doc/GPC_OPERATIONS.md)
- [回滚预案](/doc/GPC_ROLLBACK.md)
- [变更记录](/doc/GPC_CHANGELOG.md)
- [发布说明](/doc/GPC_RELEASE_NOTES.md)

## 当前限制

- 当前项目处置等级为 C 类：专项修复后再开发。
- 未清零 P0/P1 前，不建议上线或新增大功能。
- 核心业务流程仍需完成 3-5 条可复现 smoke test。
- 生产部署前必须完成备份、恢复、监控、权限、回滚演练。

## 上游说明

本项目基于 Odoo 19.0。上游 Odoo 文档仍是底层框架和开发参考，地址为 [odoo.com/documentation](https://www.odoo.com/documentation)。
