# GlobalCloud GPC 中文化表面抽查证据

日期：2026-06-06

## 抽查范围

| 表面 | 检查方式 | 结果 |
|---|---|---|
| 联系人导出字段 | Odoo ORM `fields_get` 中文上下文 + `export_data` | `名称`、`电子邮件`、`电话` |
| 导出文件编码 | 生成 `doc/evidence/gpc-contact-export-sample.csv` | UTF-8 BOM，包含 1 条浏览器 E2E 联系人记录 |
| 邮件模板旧品牌 | 搜索 `mail.template` 的 `name/subject/body_html` | 无 `OdooBot`、`YourCompany`、`Powered by Odoo` 命中 |
| 报表动作旧品牌 | 搜索 `ir.actions.report` 的 `name/report_name/print_report_name` | 无 `OdooBot`、`YourCompany`、`Powered by Odoo` 命中 |

## 样本记录

```json
{
  "id": 101,
  "name": "GPC Browser Form E2E 20260605225526",
  "email": "browser-form-e2e@gc-gpc.example.com",
  "phone": "13900000002"
}
```

## 结论

导出字段、邮件模板和报表动作的关键旧品牌残留抽查通过。该证据不代表上游 Odoo 所有深层翻译均达到人工审校级，但覆盖了当前 GPC 交付路径的关键中文化表面。
