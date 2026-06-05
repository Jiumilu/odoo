# GlobalCloud GPC 浏览器 E2E 证据

日期：2026-06-06

验证工具：Codex in-app browser

## 1. 验证结果

| 页面 | URL | 标题 | 语言 | 品牌 | 旧品牌残留 | 电话 |
|---|---|---|---|---|---|---|
| 首页 | `http://127.0.0.1:8069/?fresh=20260606` | `Home | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |
| 登录页 | `http://127.0.0.1:8069/web/login?fresh=20260606` | `Login | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |
| 404 页 | `http://127.0.0.1:8069/non-existent-gpc-page?fresh=20260606` | `页面未找到 | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |
| 登录后后台 | `http://127.0.0.1:8069/odoo/discuss` 等 9 个入口 | `讨论` / `GlobalCloud GPC` | `zh-CN` | `GlobalCloud GPC` / 中文菜单 | 无 | 不适用 |

## 2. 浏览器读取证据

```json
[
  {
    "url": "http://127.0.0.1:8069/?fresh=20260606",
    "title": "Home | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  },
  {
    "url": "http://127.0.0.1:8069/web/login?fresh=20260606",
    "title": "Login | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  },
  {
    "url": "http://127.0.0.1:8069/non-existent-gpc-page?fresh=20260606",
    "title": "页面未找到 | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  }
]
```

## 3. 登录后后台入口证据

使用本地测试账号登录后，浏览器逐项打开后台主入口并读取 DOM 状态。

```json
[
  {
    "name": "讨论",
    "url": "http://127.0.0.1:8069/odoo/discuss",
    "title": "讨论",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "应用",
    "url": "http://127.0.0.1:8069/odoo/apps",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "联系人",
    "url": "http://127.0.0.1:8069/odoo/contacts",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "CRM",
    "url": "http://127.0.0.1:8069/odoo/crm",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "销售",
    "url": "http://127.0.0.1:8069/odoo/sales",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "采购",
    "url": "http://127.0.0.1:8069/odoo/purchase",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "库存",
    "url": "http://127.0.0.1:8069/odoo/inventory",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "制造",
    "url": "http://127.0.0.1:8069/odoo/manufacturing",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  },
  {
    "name": "项目",
    "url": "http://127.0.0.1:8069/odoo/project",
    "title": "GlobalCloud GPC",
    "hasWebClient": true,
    "hasLoginForm": false,
    "visibleHasLegacyBrand": false,
    "visibleHasChinese": true
  }
]
```

## 4. 结论

公开页面、登录页、错误页和登录后后台主入口均已具备浏览器级中文化与品牌证据。登录后后台入口验证证明当前运行态可进入主要业务模块；具体表单操作闭环由 `gpc_core_flow_smoke.py` 的 ORM 级核心流程 smoke 覆盖。
