# GlobalCloud GPC 运维说明

## 1. 日常健康检查

服务运行后执行：

```bash
.venv311/bin/python tools/gpc_health_check.py --json
```

重点关注：

- `local_health_score`
- `production_readiness_score`
- `database_runtime`
- `odoo_state`
- `python_dependencies`
- `zh_cn_po_syntax`

生产环境健康检查不通过时，不得继续发布。

## 2. 日志检查

建议收集以下日志：

- Odoo 主进程日志。
- 反向代理访问日志和错误日志。
- PostgreSQL 日志。
- systemd、supervisor 或容器运行日志。

重点排查：

- 持续 traceback。
- 数据库连接失败。
- 长事务和锁等待。
- 资源加载失败。
- 频繁 401、403、500。

## 3. 备份策略

每次发布前必须备份数据库和 filestore。

数据库备份示例：

```bash
pg_dump -Fc -d GCGPC -f backup-GCGPC-$(date +%Y%m%d%H%M%S).dump
```

filestore 备份示例：

```bash
tar -czf filestore-GCGPC-$(date +%Y%m%d%H%M%S).tar.gz /var/lib/globalcloud-gpc/odoo-data
```

备份必须记录：

- 备份时间。
- 代码版本或 commit。
- 数据库名。
- 备份文件路径。
- 操作人。

## 4. 恢复演练

上线前至少完成一次恢复演练。

数据库恢复示例：

```bash
createdb -O odoo GCGPC_restore
pg_restore -d GCGPC_restore backup-GCGPC-YYYYMMDDHHMMSS.dump
```

恢复后必须验证：

- 登录页。
- 后台首页。
- 应用入口。
- 至少一条核心业务数据读取。
- 中文界面显示。

## 5. 配置管理

- 真实配置只允许放在 `.runtime/`、`/etc/globalcloud-gpc/` 或密钥管理系统。
- 配置样例只允许使用占位值。
- 配置变更必须记录原因、时间、影响和回滚方式。

## 6. 监控建议

第一阶段至少监控：

- HTTP 200/500 状态。
- PostgreSQL 可用性。
- Odoo 进程存活。
- 磁盘使用率。
- 数据库连接数。
- 长事务和锁等待。
- 日志中 traceback 数量。

## 7. 常见故障定位

### 登录页打不开

检查 Odoo 进程、反向代理端口和日志。

### `/odoo/apps` 打不开

检查登录状态、数据库连接、模块注册表和反向代理路径转发。

### websocket 异常

检查 `gevent_port`、反向代理 `/websocket` 转发和 `proxy_mode`。

### 健康检查提示 dirty worktree

说明当前代码树存在未提交或未跟踪文件。交付前必须确认这些变更是否应提交、忽略或移除。
