# GlobalCloud GPC 回滚预案

## 1. 回滚触发条件

满足任一条件时必须考虑回滚：

- 发布后登录页或后台入口不可用。
- 数据库迁移失败或模块状态异常。
- 核心业务流程中断。
- 大量 500 错误或持续 traceback。
- 数据写入异常、权限异常或数据丢失风险。
- 健康检查无法恢复到发布前水平。

## 2. 回滚前检查

记录：

- 当前 commit。
- 发布前 commit。
- 数据库备份文件。
- filestore 备份文件。
- 当前错误日志。
- 已执行的升级或迁移命令。

## 3. 代码回滚

如果使用 release 目录：

```bash
ln -sfn /opt/globalcloud-gpc/releases/<previous-release> /opt/globalcloud-gpc/current
systemctl restart globalcloud-gpc
```

如果使用 git checkout：

```bash
git fetch origin
git switch <stable-branch>
git reset --hard <previous-commit>
systemctl restart globalcloud-gpc
```

注意：只有在运维回滚窗口内才能使用破坏性 git 命令，并且必须确认没有未保存的人工变更。

## 4. 数据库回滚

当数据库结构或业务数据已经被错误发布影响时，必须恢复数据库备份。

```bash
dropdb GCGPC
createdb -O odoo GCGPC
pg_restore -d GCGPC backup-GCGPC-YYYYMMDDHHMMSS.dump
```

## 5. filestore 回滚

```bash
rm -rf /var/lib/globalcloud-gpc/odoo-data
tar -xzf filestore-GCGPC-YYYYMMDDHHMMSS.tar.gz -C /
```

恢复路径必须与配置中的 `data_dir` 一致。

## 6. 回滚后验证

必须执行：

```bash
.venv311/bin/python tools/gpc_health_check.py --json
```

必须人工验证：

- 登录页。
- 后台首页。
- 应用入口。
- 关键业务数据读取。
- 中文界面显示。
- 日志无持续新错误。

## 7. 回滚后记录

回滚结束后必须补充：

- 触发原因。
- 影响范围。
- 回滚时间。
- 回滚责任人。
- 验证结果。
- 后续修复任务。
