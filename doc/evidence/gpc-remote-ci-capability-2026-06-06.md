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
| 第二次 CI run | `27045410278` |
| 第三次 CI run | `27045705371` |

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

## 第二次远端 CI 结果

第二次 run 已验证第一次修复有效，以下步骤新增通过：

- Apply runtime localization defaults
- minimal Odoo test runner smoke
- HTTP smoke check

失败步骤：`Run core business flow smoke test`。

失败原因：CI 数据库只校验了 `zh_CN.po` 语法，但未在数据库初始化时安装并激活 `zh_CN`；登录态后台 smoke 创建测试账号时设置 `lang=zh_CN`，触发 `UserError: Invalid language code: zh_CN`。

修复动作：

- CI 安装核心业务模块时增加 `--load-language=zh_CN`，确保数据库层面加载简体中文语言。
- 登录态后台 smoke 增加已安装语言选择逻辑：优先使用 `zh_CN`，未安装时回退到 `en_US` 或当前任一已安装语言。
- 本地证据 `doc/evidence/gpc-authenticated-backend-smoke.json` 已记录测试账号实际语言为 `zh_CN`。

## 第三次远端 CI 结果

第三次 run 已验证第二次修复有效，以下步骤新增通过：

- 安装核心业务模块时加载 `zh_CN`
- 登录态后台 smoke 创建测试账号并使用 `lang=zh_CN`
- Browser 表单 E2E
- 核心业务 smoke 中联系人、CRM、销售、采购、库存、制造、项目流程

失败步骤：`Run core business flow smoke test` 中的 `permission_boundary` 子项。

失败原因：CI 最小数据库未加载 demo portal 用户；脚本按 `login=portal` 查询得到空记录集后继续调用 `env(user=portal)`，触发 `ValueError('Expected singleton: res.users()')`。同时脚本对自定义管理员 `gcgpc@csydsc.com` 的存在也有本地环境假设。

修复动作：

- 权限边界 smoke 在自定义管理员不存在时回退到 `base.user_admin`。
- public 用户改用稳定 XMLID `base.public_user`。
- portal 用户不存在时创建事务内临时 smoke 门户用户，并在脚本结尾 rollback，不污染数据库。
- 本地证据 `doc/evidence/gpc-core-flow-smoke.json` 已验证 `portal_sale_create=AccessError`、`public_sale_create=AccessError`。

## 结论

当前已具备可写 fork 并已触发远端 CI。前三次 run 已连续关闭 CI-only 缺陷；需要重新推送后确认第四轮 run 结果。
