#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const args = {
    baseUrl: "http://127.0.0.1:8069",
    login: "gpc.e2e@example.invalid",
    password: "GpcE2E-2026!",
  };
  for (let index = 2; index < argv.length; index += 1) {
    const key = argv[index];
    const value = argv[index + 1];
    if (key === "--base-url") {
      args.baseUrl = value;
      index += 1;
    } else if (key === "--login") {
      args.login = value;
      index += 1;
    } else if (key === "--password") {
      args.password = value;
      index += 1;
    } else if (key === "--report-json") {
      args.reportJson = value;
      index += 1;
    } else if (key === "--report-md") {
      args.reportMd = value;
      index += 1;
    } else if (key === "--screenshot") {
      args.screenshot = value;
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${key}`);
    }
  }
  return args;
}

function resolvePlaywright() {
  const candidates = [
    process.env.GPC_PLAYWRIGHT_MODULE,
    path.resolve(ROOT, "node_modules/playwright"),
  ].filter(Boolean);

  for (const candidate of candidates) {
    try {
      return { module: require(candidate), source: require.resolve(candidate) };
    } catch (error) {
      if (error.code !== "MODULE_NOT_FOUND") {
        throw error;
      }
    }
  }
  throw new Error("Playwright module not found. Set GPC_PLAYWRIGHT_MODULE to an existing playwright package path.");
}

async function run(args) {
  const playwright = resolvePlaywright();
  const { chromium } = playwright.module;
  const base = args.baseUrl.replace(/\/$/, "");
  const contactName = `GPC Browser Form E2E ${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}`;
  const email = "browser-form-e2e@gc-gpc.example.com";
  const phone = "13900000002";
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ locale: "zh-CN", timezoneId: "Asia/Shanghai" });
  const steps = [];

  try {
    await page.goto(`${base}/web/login`, { waitUntil: "domcontentloaded" });
    await page.locator('input[name="login"]').fill(args.login);
    await page.locator('input[name="password"]').fill(args.password);
    await Promise.all([
      page.waitForURL(/\/odoo\//, { timeout: 20000 }),
      page.locator("form.oe_login_form button.btn-primary").click(),
    ]);
    await page.locator(".o_web_client").waitFor({ state: "visible", timeout: 20000 });
    steps.push({ name: "login", ok: true, url: page.url(), title: await page.title() });

    await page.goto(`${base}/odoo/contacts`, { waitUntil: "domcontentloaded" });
    await page.locator("button.o_list_button_add").waitFor({ state: "visible", timeout: 20000 });
    steps.push({ name: "open_contacts", ok: true, url: page.url(), title: await page.title() });

    await page.locator("button.o_list_button_add").click();
    await page.getByPlaceholder("例如：木材公司").waitFor({ state: "visible", timeout: 20000 });
    await page.getByPlaceholder("例如：木材公司").fill(contactName);
    await page.getByPlaceholder("邮箱").fill(email);
    await page.getByPlaceholder("电话").fill(phone);
    steps.push({ name: "fill_contact_form", ok: true, contactName, email, phone });

    await page.locator("button.o_form_button_save").click();
    await page.waitForTimeout(2500);
    const savedText = await page.locator("body").innerText();
    const recordIdMatch = page.url().match(/\/contacts\/(\d+)/);
    const recordId = recordIdMatch ? Number(recordIdMatch[1]) : null;
    const recordRead = recordId
      ? await page.evaluate(async (id) => {
          const response = await fetch("/web/dataset/call_kw/res.partner/read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              jsonrpc: "2.0",
              method: "call",
              params: {
                model: "res.partner",
                method: "read",
                args: [[id], ["name", "email", "phone"]],
                kwargs: {},
              },
            }),
          });
          return response.json();
        }, recordId)
      : null;
    const savedRecord = recordRead && recordRead.result ? recordRead.result[0] : null;
    steps.push({
      name: "save_contact",
      ok: Boolean(savedRecord) && savedRecord.name === contactName && savedRecord.email === email && savedRecord.phone === phone,
      url: page.url(),
      title: await page.title(),
      recordId,
      hasContactName: savedText.includes(contactName),
      savedRecord,
    });

    await page.goto(`${base}/odoo/contacts`, { waitUntil: "domcontentloaded" });
    await page.locator("input.o_searchview_input").waitFor({ state: "visible", timeout: 20000 });
    await page.locator("input.o_searchview_input").fill(contactName);
    await page.keyboard.press("Enter");
    await page.waitForTimeout(2500);
    const searchText = await page.locator("body").innerText();
    steps.push({
      name: "search_contact",
      ok: searchText.includes(contactName),
      url: page.url(),
      title: await page.title(),
      hasContactName: searchText.includes(contactName),
      visibleHasLegacyBrand: /\bOdoo\b/.test(searchText) || /\bOdoo\b/.test(await page.title()),
    });

    if (args.screenshot) {
      fs.mkdirSync(path.dirname(args.screenshot), { recursive: true });
      await page.screenshot({ path: args.screenshot, fullPage: true });
    }
  } finally {
    await browser.close();
  }

  const result = {
    timestamp: new Date().toISOString(),
    baseUrl: base,
    playwrightSource: playwright.source,
    contactName,
    steps,
    ok: steps.every((step) => step.ok) && steps.every((step) => !step.visibleHasLegacyBrand),
  };
  return result;
}

function markdownReport(result) {
  const lines = [
    "# GlobalCloud GPC 浏览器表单级 E2E 报告",
    "",
    `执行时间戳：\`${result.timestamp}\``,
    `基础地址：\`${result.baseUrl}\``,
    `测试联系人：\`${result.contactName}\``,
    `总体结果：\`${result.ok ? "通过" : "失败"}\``,
    "",
    "| 步骤 | 结果 | 证据 |",
    "|---|---|---|",
  ];
  for (const step of result.steps) {
    lines.push(`| ${step.name} | ${step.ok ? "通过" : "失败"} | \`${JSON.stringify(step)}\` |`);
  }
  return `${lines.join("\n")}\n`;
}

(async () => {
  try {
    const args = parseArgs(process.argv);
    const result = await run(args);
    if (args.reportJson) {
      fs.mkdirSync(path.dirname(args.reportJson), { recursive: true });
      fs.writeFileSync(args.reportJson, `${JSON.stringify(result, null, 2)}\n`);
    }
    if (args.reportMd) {
      fs.mkdirSync(path.dirname(args.reportMd), { recursive: true });
      fs.writeFileSync(args.reportMd, markdownReport(result));
    }
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.ok ? 0 : 1);
  } catch (error) {
    console.error(error.stack || error.message || String(error));
    process.exit(1);
  }
})();
