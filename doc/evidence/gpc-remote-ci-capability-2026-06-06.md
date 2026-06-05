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
| `Jiumilu/odoo` fork | 不存在 |

## 结论

当前本机没有可写远端仓库可触发 GitHub Actions。项目已具备 `.github/workflows/gpc-quality.yml`，并已把 Playwright 标准化到 `package.json/package-lock.json`；远端 CI 实跑仍需要先创建/授权可写 fork 或切换到项目交付远端。
