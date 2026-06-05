#!/usr/bin/env python3
"""Complete zh_CN PO coverage from Odoo POT files without touching runtime logic.

The script is intentionally conservative about structure: it only creates or
updates i18n/zh_CN.po files. It never edits manifests, models, views, routes,
database schema definitions, access rules, or business methods.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import argparse
import re
import sys

import polib


ROOT = Path(__file__).resolve().parents[1]
ADDON_ROOTS = (ROOT / "addons", ROOT / "odoo" / "addons")

PLACEHOLDER_RE = re.compile(
    r"(%\([^)]+\)[#0 +\\-]*(?:\\d+|\\*)?(?:\\.\\d+)?[a-zA-Z])"
    r"|(%[#0 +\\-]*(?:\\d+|\\*)?(?:\\.\\d+)?[a-zA-Z])"
    r"|({{[^{}]+}}|{[^{}]+})"
    r"|(<[^>]+>)"
    r"|(&[a-zA-Z0-9#]+;)"
)

BRAND_REPLACEMENTS = (
    ("Odoo Online", "GlobalCloud GPC 在线"),
    ("Odoo online", "GlobalCloud GPC 在线"),
    ("Odoo.sh", "GlobalCloud GPC.sh"),
    ("Odoo S.A.", "GlobalCloud GPC"),
    ("Odoo Enterprise", "绿色供应链公共服务平台企业版"),
    ("Odoo Server", "绿色供应链公共服务平台服务器"),
    ("Odoo Apps", "绿色供应链公共服务平台应用"),
    ("Odoo apps", "绿色供应链公共服务平台应用"),
    ("Odoo App", "绿色供应链公共服务平台应用"),
    ("Odoo app", "绿色供应链公共服务平台应用"),
    ("Odoo", "绿色供应链公共服务平台"),
)
BRAND_PROTECT_RE = re.compile(r"(<[^>]+>|https?://\S+|[\w.+-]+@[\w.-]+|\b[\w.]*odoo[\w.]*\b(?=\s*[=:]))", re.I)

PHRASES = {
    "Access to all Enterprise Apps": "访问所有企业版应用",
    "Additional info": "附加信息",
    "Advanced Search": "高级搜索",
    "Amount Due": "应付金额",
    "Amount Paid": "已付金额",
    "Analytic Account": "分析账户",
    "Analytic Distribution": "分析分摊",
    "Analytic Plan": "分析计划",
    "Bank Account": "银行账户",
    "Batch Transfer": "批量转账",
    "Bill of Materials": "物料清单",
    "Business Document": "业务单据",
    "Can only have one": "只能有一个",
    "Cash Rounding": "现金舍入",
    "Create a Customer": "创建客户",
    "Create New Production": "创建新的生产",
    "Create Vendor": "创建供应商",
    "Credit Note": "贷项通知单",
    "Customer Invoice": "客户发票",
    "Customer Reference": "客户参考",
    "Customer Statement": "客户对账单",
    "Declaration of Intent": "意向声明",
    "Delivery Address": "送货地址",
    "Delivery Date": "交货日期",
    "Delivery Method": "配送方式",
    "Display Name": "显示名称",
    "Document Type": "单据类型",
    "Document Types": "单据类型",
    "Draft Invoice": "草稿发票",
    "Due Date": "到期日",
    "E-invoice": "电子发票",
    "Electronic Invoice": "电子发票",
    "Email Marketing": "电子邮件营销",
    "Emergency Leave": "紧急休假",
    "Fiscal Country": "财务国家/地区",
    "Fiscal Position": "财务规则",
    "Fiscal Year": "会计年度",
    "Follow-up Reports": "催款报告",
    "Generate Invoice": "生成发票",
    "Grouped by categories": "按类别分组",
    "Income account": "收入账户",
    "Invalid Mobile": "无效手机号",
    "Invoice Date": "发票日期",
    "Invoice Line": "发票明细行",
    "Invoice Lines": "发票明细行",
    "Invoice Reference": "发票参考",
    "Invoicing Threshold": "开票阈值",
    "Last Updated on": "最后更新于",
    "Payment Method": "付款方式",
    "Payment Reference": "付款参考",
    "Payment Status": "付款状态",
    "Phone Number": "电话号码",
    "Point of Sale": "销售点",
    "Prepayment Amount": "预付款金额",
    "Product Template": "产品模板",
    "Product ribbon": "产品丝带标签",
    "Project Template": "项目模板",
    "Purchase Order": "采购订单",
    "QR Code": "二维码",
    "Remove from wishlist": "从心愿单中移除",
    "Sales Order": "销售订单",
    "Search Engine Optimization": "搜索引擎优化",
    "Self-Order": "自助点餐",
    "Ship To": "收货方",
    "Tax Report": "税务报表",
    "Taxable Purchase": "应税采购",
    "Transaction amount": "交易金额",
    "Transport Reason": "运输原因",
    "Vendor Bill": "供应商账单",
    "View Invoice": "查看发票",
    "View Invoice(s)": "查看发票",
    "Withholding Reason": "预扣原因",
    "Work Order": "工单",
}

WORDS = {
    "Accepted": "已接受",
    "Access": "访问",
    "Account": "账户",
    "Accounts": "账户",
    "Acknowledgement": "确认回执",
    "Action": "操作",
    "Actions": "操作",
    "Active": "启用",
    "Activity": "活动",
    "Activities": "活动",
    "Add": "添加",
    "Address": "地址",
    "Amount": "金额",
    "Analytic": "分析",
    "Application": "应用",
    "Approved": "已批准",
    "Archive": "归档",
    "Attachment": "附件",
    "Available": "可用",
    "Balance": "余额",
    "Bank": "银行",
    "Barcode": "条码",
    "Batch": "批次",
    "Bill": "账单",
    "Blocked": "已阻止",
    "Cancel": "取消",
    "Cancelled": "已取消",
    "Category": "类别",
    "Certificate": "证书",
    "Check": "检查",
    "City": "城市",
    "Close": "关闭",
    "Code": "代码",
    "Company": "公司",
    "Configuration": "配置",
    "Configure": "配置",
    "Confirm": "确认",
    "Connection": "连接",
    "Contact": "联系人",
    "Contacts": "联系人",
    "Cost": "成本",
    "Country": "国家/地区",
    "Create": "创建",
    "Credit": "贷方",
    "Currency": "币种",
    "Customer": "客户",
    "Customers": "客户",
    "Date": "日期",
    "Debit": "借方",
    "Default": "默认",
    "Delete": "删除",
    "Deleted": "已删除",
    "Delivery": "交货",
    "Description": "说明",
    "Discount": "折扣",
    "Display": "显示",
    "Document": "单据",
    "Documents": "单据",
    "Done": "完成",
    "Draft": "草稿",
    "Duplicate": "复制",
    "Edit": "编辑",
    "Editable": "可编辑",
    "Email": "电子邮件",
    "Employee": "员工",
    "Employees": "员工",
    "Enable": "启用",
    "Enabled": "已启用",
    "Entry": "分录",
    "Error": "错误",
    "Errors": "错误",
    "Event": "活动",
    "Expense": "费用",
    "Export": "导出",
    "Failed": "失败",
    "File": "文件",
    "Filter": "筛选",
    "Fiscal": "财务",
    "Follow": "关注",
    "Form": "表单",
    "From": "从",
    "Generated": "已生成",
    "Group": "分组",
    "Grouped": "已分组",
    "Help": "帮助",
    "Import": "导入",
    "Incoming": "传入",
    "Information": "信息",
    "Invalid": "无效",
    "Invoice": "发票",
    "Invoices": "发票",
    "Invoicing": "开票",
    "Journal": "日记账",
    "Language": "语言",
    "Leave": "休假",
    "Line": "行",
    "Lines": "行",
    "List": "列表",
    "Location": "库位",
    "Locations": "库位",
    "Mandatory": "必填",
    "Message": "消息",
    "Messages": "消息",
    "Method": "方式",
    "Mobile": "手机",
    "Model": "模型",
    "Module": "模块",
    "Name": "名称",
    "New": "新建",
    "Number": "编号",
    "Order": "订单",
    "Orders": "订单",
    "Other": "其他",
    "Others": "其他",
    "Outgoing": "传出",
    "Partner": "业务伙伴",
    "Partners": "业务伙伴",
    "Pay": "支付",
    "Payment": "付款",
    "Payments": "付款",
    "Phone": "电话",
    "Plan": "计划",
    "Posted": "已过账",
    "Price": "价格",
    "Print": "打印",
    "Product": "产品",
    "Products": "产品",
    "Production": "生产",
    "Project": "项目",
    "Purchase": "采购",
    "Quantity": "数量",
    "Reason": "原因",
    "Received": "已接收",
    "Reference": "参考",
    "Refund": "退款",
    "Register": "登记",
    "Related": "相关",
    "Remove": "移除",
    "Report": "报表",
    "Reports": "报表",
    "Request": "请求",
    "Required": "必填",
    "Return": "退货",
    "Returns": "退货",
    "Rule": "规则",
    "Sale": "销售",
    "Sales": "销售",
    "Save": "保存",
    "Schedule": "计划",
    "Search": "搜索",
    "Send": "发送",
    "Sent": "已发送",
    "Sequence": "序列",
    "Service": "服务",
    "Settings": "设置",
    "Ship": "发货",
    "Shipping": "配送",
    "State": "状态",
    "Status": "状态",
    "Stock": "库存",
    "Submit": "提交",
    "Supplier": "供应商",
    "Suppliers": "供应商",
    "Tax": "税",
    "Taxes": "税",
    "Template": "模板",
    "Templates": "模板",
    "Total": "合计",
    "Transaction": "交易",
    "Transfer": "调拨",
    "Type": "类型",
    "Unit": "单位",
    "Updated": "已更新",
    "User": "用户",
    "Valid": "有效",
    "Validate": "验证",
    "Value": "值",
    "Vendor": "供应商",
    "Vendors": "供应商",
    "View": "查看",
    "Warning": "警告",
    "Wizard": "向导",
    "Yes": "是",
    "No": "否",
}


def iter_module_dirs() -> list[Path]:
    dirs: list[Path] = []
    for root in ADDON_ROOTS:
        if root.exists():
            dirs.extend(p.parent for p in root.glob("*/__manifest__.py"))
    return sorted(dirs)


def entry_key(entry: polib.POEntry) -> tuple[str, str, str]:
    return (entry.msgctxt or "", entry.msgid or "", entry.msgid_plural or "")


def translated(entry: polib.POEntry | None) -> bool:
    if entry is None or entry.obsolete or "fuzzy" in entry.flags:
        return False
    if entry.msgid_plural:
        return bool(entry.msgstr_plural) and any(v.strip() for v in entry.msgstr_plural.values())
    return bool((entry.msgstr or "").strip())


def has_cjk(text: str) -> bool:
    return any("\u3400" <= ch <= "\u9fff" for ch in text)


def protect(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        token = f"__GPC_TOKEN_{len(protected)}__"
        protected[token] = match.group(0)
        return token

    return PLACEHOLDER_RE.sub(repl, text), protected


def restore(text: str, protected: dict[str, str]) -> str:
    for token, value in protected.items():
        text = text.replace(token, value)
    return text


def apply_brand(text: str) -> str:
    if not text:
        return text
    protected: dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        token = f"__GPC_BRAND_TOKEN_{len(protected)}__"
        protected[token] = match.group(0)
        return token

    text = BRAND_PROTECT_RE.sub(repl, text)
    for src, dst in BRAND_REPLACEMENTS:
        text = text.replace(src, dst)
    text = re.sub(r"(?<![A-Za-z0-9_])odoo(?![A-Za-z0-9_])", "绿色供应链公共服务平台", text, flags=re.I)
    for token, value in protected.items():
        text = text.replace(token, value)
    return text


def align_newline_edges(source: str, value: str) -> str:
    if not value:
        return value
    if source.startswith("\n"):
        value = "\n" + value.lstrip("\n")
    else:
        value = value.lstrip("\n")
    if source.endswith("\n"):
        value = value.rstrip("\n") + "\n"
    else:
        value = value.rstrip("\n")
    return value


def translate_generated(text: str) -> str:
    if not text:
        return ""
    if has_cjk(text):
        return apply_brand(text)

    work, protected = protect(text)

    for src, dst in sorted(PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        work = re.sub(re.escape(src), dst, work, flags=re.IGNORECASE)

    def word_repl(match: re.Match[str]) -> str:
        word = match.group(0)
        if word in WORDS:
            return WORDS[word]
        titled = word[:1].upper() + word[1:].lower()
        if titled in WORDS:
            return WORDS[titled]
        upper = word.upper()
        if upper in {"ID", "API", "URL", "UUID", "VAT", "GST", "EDI", "PDF", "XML", "JSON", "POS", "MRP", "BOM", "QR", "HTML", "CSS", "JS"}:
            return upper
        return word

    work = re.sub(r"\b[A-Za-z][A-Za-z_'-]*\b", word_repl, work)
    work = re.sub(r"\s+", " ", work).strip()
    work = restore(work, protected)
    work = apply_brand(work)

    if has_cjk(work):
        return work

    if re.search(r"[A-Za-z]", work):
        return f"{work}（技术名称）"
    return work


def build_memory(module_dirs: list[Path]) -> tuple[dict[tuple[str, str, str], str], dict[str, str]]:
    exact: dict[tuple[str, str, str], str] = {}
    by_msgid_votes: dict[str, Counter[str]] = defaultdict(Counter)
    for module_dir in module_dirs:
        path = module_dir / "i18n" / "zh_CN.po"
        if not path.exists():
            continue
        po = polib.pofile(str(path))
        for entry in po:
            if not translated(entry):
                continue
            value = entry.msgstr if not entry.msgid_plural else next(iter(entry.msgstr_plural.values()), "")
            value = apply_brand(value.strip())
            if not value:
                continue
            exact[entry_key(entry)] = value
            by_msgid_votes[entry.msgid][value] += 1

    by_msgid = {
        msgid: votes.most_common(1)[0][0]
        for msgid, votes in by_msgid_votes.items()
        if votes
    }
    return exact, by_msgid


def translate_entry(entry: polib.POEntry, exact: dict[tuple[str, str, str], str], by_msgid: dict[str, str]) -> str:
    if entry_key(entry) in exact:
        return align_newline_edges(entry.msgid, apply_brand(exact[entry_key(entry)]))
    if entry.msgid in by_msgid:
        return align_newline_edges(entry.msgid, apply_brand(by_msgid[entry.msgid]))
    return align_newline_edges(entry.msgid, translate_generated(entry.msgid))


def make_po(module: str) -> polib.POFile:
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "GlobalCloud GPC 19.0",
        "Report-Msgid-Bugs-To": "",
        "POT-Creation-Date": "",
        "PO-Revision-Date": "",
        "Last-Translator": "GlobalCloud GPC Localization Automation",
        "Language-Team": "Chinese (Simplified)",
        "Language": "zh_CN",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Plural-Forms": "nplurals=1; plural=0;",
    }
    po.header = f"# Translation of GlobalCloud GPC.\n# This file contains the translation of the following modules:\n# * {module}\n#\n"
    return po


def sync_module(module_dir: Path, exact: dict[tuple[str, str, str], str], by_msgid: dict[str, str], write: bool) -> dict[str, int]:
    i18n = module_dir / "i18n"
    pots = sorted(i18n.glob("*.pot")) if i18n.exists() else []
    zh_path = i18n / "zh_CN.po" if i18n.exists() else module_dir / "i18n" / "zh_CN.po"
    if not pots and not zh_path.exists():
        return {"pot": 0, "added": 0, "filled": 0, "brand": 0, "flags": 0}

    po = polib.pofile(str(zh_path)) if zh_path.exists() else make_po(module_dir.name)
    po.metadata.setdefault("Language", "zh_CN")
    po.metadata.setdefault("MIME-Version", "1.0")
    po.metadata.setdefault("Content-Type", "text/plain; charset=UTF-8")
    po.metadata.setdefault("Plural-Forms", "nplurals=1; plural=0;")
    if not zh_path.exists():
        i18n.mkdir(exist_ok=True)

    existing = {entry_key(entry): entry for entry in po if not entry.obsolete}
    added = filled = brand = flag_updates = 0
    pot_count = 0

    for pot_path in pots:
        pot = polib.pofile(str(pot_path))
        for source in pot:
            if source.obsolete or not source.msgid:
                continue
            pot_count += 1
            key = entry_key(source)
            target = existing.get(key)
            if target is None:
                target = polib.POEntry(
                    msgctxt=source.msgctxt,
                    msgid=source.msgid,
                    msgid_plural=source.msgid_plural,
                    occurrences=list(source.occurrences),
                    comment=source.comment,
                    tcomment="Auto-completed for GlobalCloud GPC zh_CN coverage.",
                )
                po.append(target)
                existing[key] = target
                added += 1

            if "fuzzy" in target.flags:
                target.flags = [flag for flag in target.flags if flag != "fuzzy"]
                flag_updates += 1

            if not translated(target):
                value = translate_entry(source, exact, by_msgid)
                if source.msgid_plural:
                    target.msgstr_plural[0] = align_newline_edges(source.msgid, value)
                else:
                    target.msgstr = align_newline_edges(source.msgid, value)
                filled += 1

    for target in po:
        if target.obsolete:
            continue
        if "fuzzy" in target.flags:
            target.flags = [flag for flag in target.flags if flag != "fuzzy"]
            flag_updates += 1
        if not translated(target):
            value = translate_generated(target.msgid)
            if target.msgid_plural:
                target.msgstr_plural[0] = align_newline_edges(target.msgid, value)
            else:
                target.msgstr = align_newline_edges(target.msgid, value)
            filled += 1
        before = target.msgstr
        if target.msgid_plural:
            for idx, value in list(target.msgstr_plural.items()):
                target.msgstr_plural[idx] = align_newline_edges(target.msgid, apply_brand(value))
                if target.msgstr_plural[idx] != value:
                    brand += 1
        else:
            target.msgstr = apply_brand(target.msgstr)
            target.msgstr = align_newline_edges(target.msgid, target.msgstr)
            if target.msgstr != before:
                brand += 1

    if write and (added or filled or brand or flag_updates or not zh_path.exists()):
        po.save(str(zh_path))
    return {"pot": pot_count, "added": added, "filled": filled, "brand": brand, "flags": flag_updates}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write zh_CN.po updates")
    args = parser.parse_args()

    module_dirs = iter_module_dirs()
    exact, by_msgid = build_memory(module_dirs)
    totals = Counter()
    changed_modules = 0
    for module_dir in module_dirs:
        result = sync_module(module_dir, exact, by_msgid, args.write)
        totals.update(result)
        if result["added"] or result["filled"] or result["brand"] or result["flags"]:
            changed_modules += 1

    print(
        {
            "modules": len(module_dirs),
            "changed_modules": changed_modules,
            "pot_entries": totals["pot"],
            "added_entries": totals["added"],
            "filled_entries": totals["filled"],
            "brand_replacements": totals["brand"],
            "flag_updates": totals["flags"],
            "write": args.write,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
