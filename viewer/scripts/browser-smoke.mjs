import { chromium } from "@playwright/test";
import { writeFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
mkdirSync("reports/browser-screenshots", { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || undefined,
  headless: true,
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--enable-unsafe-swiftshader",
    "--use-angle=swiftshader",
  ],
});
const devices=process.env.TEST_DEVICE==='desktop'?[false]:process.env.TEST_DEVICE==='mobile'?[true]:[true,false];
const results = process.env.TEST_DEVICE && existsSync("reports/browser-results.json") ? JSON.parse(readFileSync('reports/browser-results.json','utf8')).filter(r=>!devices.includes(r.mobile)) : [];
const save = () =>
  writeFileSync(
    "reports/browser-results.json",
    JSON.stringify(results, null, 2),
  );
for (const mobile of devices) {
  const tag = mobile ? "mobile" : "desktop";
  const context = await browser.newContext({
    viewport: mobile
      ? { width: 390, height: 844 }
      : { width: 1280, height: 800 },
    isMobile: mobile,
    hasTouch: mobile,
    deviceScaleFactor: Number(process.env.TEST_DPR || (mobile ? 1 : 0.5)),
  });
  const page = await context.newPage();
  page.setDefaultTimeout(120000);
  const errors = [];
  const warnings = [];
  const result = { mobile, errors, warnings };
  results.push(result);
  save();
  page.on("pageerror", (e) => {
    errors.push(e.message);
    save();
  });
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
    if (m.type() === "warning") warnings.push(m.text());
  });
  async function stats() {
    return JSON.parse(await page.locator(".debug").textContent());
  }
  async function screenshot(name) {
    await page.addStyleTag({ content: ".debug{display:none!important}" });
    await page.screenshot({
      path: `reports/browser-screenshots/${tag}-${name}.png`,
      timeout: Number(process.env.TEST_CAPTURE_TIMEOUT || 120000),
    });
  }
  try {
    const begin = Date.now();
    await page.goto(
      `${process.env.VIEWER_URL || "http://localhost:3000"}/?debug`,
    );
    await page
      .getByRole("button", { name: "Explore the property" })
      .waitFor({ timeout: 240000 });
    await page.waitForTimeout(1500);
    result.initial = await stats();
    result.loadMs = Date.now() - begin;
    save();
    console.log(tag, "loaded", result.loadMs);
    await screenshot("entry");
    await page.getByRole("button", { name: "Rooms", exact: true }).click();
    result.locations = await page.locator(".room").allTextContents();
    await screenshot("rooms");
    await page.getByRole("button", { name: "Master Bedroom" }).click();
    await page.waitForTimeout(1500);
    await page.waitForFunction(
      () => {
        const el = document.querySelector(".debug");
        return (
          el && JSON.parse(el.textContent).stats?.room === "Master Bedroom"
        );
      },
      {},
      { timeout: 120000 },
    );
    result.master = await stats();
    console.log(tag, "master");
    save();
    await screenshot("master");
    await page.getByRole("button", { name: "Explore the property" }).click();
    await page.waitForTimeout(1500);
    result.before = await stats();
    if (mobile) {
      const cdp = await context.newCDPSession(page);
      const b = await page
        .getByRole("button", { name: "Forward", exact: true })
        .boundingBox();
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchStart",
        touchPoints: [{ x: b.x + 24, y: b.y + 24, id: 1 }],
      });
      await page.waitForTimeout(4000);
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchEnd",
        touchPoints: [],
      });
      await page.waitForTimeout(1200);
      result.afterMovement = await stats();
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchStart",
        touchPoints: [{ x: 280, y: 380, id: 2 }],
      });
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [{ x: 220, y: 400, id: 2 }],
      });
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchEnd",
        touchPoints: [],
      });
    } else {
      result.pointerLocked = await page.evaluate(
        () => !!document.pointerLockElement,
      );
      await page.keyboard.down("w");
      await page.waitForTimeout(4000);
      await page.keyboard.up("w");
      await page.waitForTimeout(1200);
      result.afterMovement = await stats();
      await page.mouse.move(650, 420);
      await page.keyboard.press("Escape");
      result.nativeEscapeReleased = await page.evaluate(
        () => !document.pointerLockElement,
      );
      if (!result.nativeEscapeReleased)
        await page.evaluate(() => document.exitPointerLock());
      await page.waitForFunction(() => !document.pointerLockElement);
    }
    save();
    await screenshot("explore");
    await page.getByRole("button", { name: "Settings", exact: true }).click();
    await screenshot("settings");
    await page.locator("select").selectOption("LOW");
    await page.getByRole("button", { name: "Close panel" }).click();
    await page.getByRole("button", { name: "Layout", exact: true }).click();
    await screenshot("layout");
    result.overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    );
    result.final = await stats();
    save();
    console.log(tag, "done");
  } catch (e) {
    result.failure = e.message;
    save();
    console.log(tag, e.message);
  } finally {
    await context.close();
  }
}
await browser.close();
if (results.some((r) => r.failure || r.errors.length)) process.exitCode = 1;
