# GlobalCloud GPC 远端 CI 能力检查

日期：2026-06-06

## 检查命令

```bash
gh repo view odoo/odoo --json nameWithOwner,isFork,defaultBranchRef,url,viewerPermission
gh repo view Jiumilu/odoo --json nameWithOwner,isFork,defaultBranchRef,url
git remote get-url --push origin
```

## 当前结果

| 项目 | 结果 |
|---|---|
| `origin` push URL | `https://github.com/odoo/odoo.git` |
| `odoo/odoo` 权限 | `viewerPermission=READ` |
| `odoo/odoo` 默认分支 | `19.0` |
| `Jiumilu/odoo` fork | 已创建 |
| CI 分支 | `gpc-quality-100` |
| 首次 CI run | `27045220938` |

## 首次远端 CI 结果

首次 run 已实际触发 GitHub Actions，前置门禁已通过：

- checkout
- Python setup
- Node setup
- system packages
- Python dependencies
- Playwright dependencies
- runtime config
- pip check
- py_compile
- browser E2E syntax
- unit tests
- zh_CN PO syntax
- core module installation

失败步骤：`Apply runtime localization defaults`。

失败原因：CI 最小模块集未安装 `website`，而 `tools/gpc_apply_runtime_localization.py` 无条件访问 `env["website"]`。

修复动作：运行态本地化脚本已改为检测可选模型是否存在；缺失 `website`、`mail.template`、`discuss.channel`、`mail.message` 时记录到 `skipped_models`，不再使最小 CI 模块集失败。

## 结论

当前已具备可写 fork 并已触发远端 CI。第一次 run 已发现并修复一个 CI-only 缺陷；需要重新推送后确认第二轮 run 结果。
