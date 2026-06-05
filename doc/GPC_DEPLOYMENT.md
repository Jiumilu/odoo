# GlobalCloud GPC 部署说明

适用范围：GlobalCloud GPC（绿色供应链公共服务平台）当前 19.0 分支。

本文只描述部署和交付操作，不改变业务架构。

## 1. 部署前置条件

- Python 3.11。
- PostgreSQL 14 或更高版本。
- `gettext`，用于校验中文 PO 文件。
- 可写的数据目录，例如 `/var/lib/globalcloud-gpc/odoo-data`。
- 私有配置文件，例如 `/etc/globalcloud-gpc/odoo.conf`。
- 反向代理，例如 Nginx、Caddy 或本仓库的 `tools/gpc_reverse_proxy.py`。

## 2. 推荐目录

```text
/opt/globalcloud-gpc/current        当前代码
/opt/globalcloud-gpc/releases       历史发布版本
/var/lib/globalcloud-gpc/odoo-data  Odoo filestore
/var/log/globalcloud-gpc            日志目录
/etc/globalcloud-gpc/odoo.conf      私有配置
```

## 3. 配置文件

从样例复制配置：

```bash
cp config/gpc-odoo.production.conf.example /etc/globalcloud-gpc/odoo.conf
chmod 600 /etc/globalcloud-gpc/odoo.conf
```

必须修改：

- `addons_path`
- `data_dir`
- `db_host`
- `db_port`
- `db_user`
- `db_password`
- `db_name`
- `admin_passwd`

生产环境要求：

- `list_db = False`
- `proxy_mode = True`
- `workers >= 2`
- 配置文件权限不得对组或其他用户开放。

## 4. 数据库准备

创建数据库用户和数据库：

```bash
createuser --pwprompt odoo
createdb -O odoo GCGPC
```

如使用已有数据库，部署前必须完成备份，备份要求见 [GPC_OPERATIONS.md](/doc/GPC_OPERATIONS.md)。

## 5. 安装依赖

```bash
python3.11 -m venv .venv311
.venv311/bin/python -m pip install --upgrade pip setuptools wheel
.venv311/bin/python -m pip install -r requirements.txt
```

## 6. 启动服务

启动 Odoo：

```bash
.venv311/bin/python odoo-bin -c /etc/globalcloud-gpc/odoo.conf -d GCGPC
```

如果使用本仓库反向代理：

```bash
.venv311/bin/python tools/gpc_reverse_proxy.py \
  --listen-host 127.0.0.1 \
  --listen-port 8069 \
  --http-target http://127.0.0.1:8070 \
  --websocket-target http://127.0.0.1:8072
```

生产环境建议使用 systemd、supervisor 或容器编排托管进程。

## 7. 部署后验证

必须执行：

```bash
.venv311/bin/python -m pip check
.venv311/bin/python tools/gpc_health_check.py --config /etc/globalcloud-gpc/odoo.conf --base-url http://127.0.0.1:8069 --json
```

必须人工验证：

- 登录页可打开。
- `/odoo/apps` 可打开。
- 中文菜单和标题显示正常。
- 数据库无待安装、待升级、待卸载模块。
- 日志无持续异常堆栈。

## 8. 禁止事项

- 禁止提交真实 `.runtime/gpc-odoo.conf`。
- 禁止使用默认 `admin_passwd` 或默认数据库密码。
- 禁止生产环境暴露数据库端口到公网。
- 禁止未备份数据库和 filestore 就执行升级。
