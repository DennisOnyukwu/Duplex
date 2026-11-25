#!/usr/bin/env node
// Renders a page in headless Chromium and prints its text, social links and
// (for Shopify stores) the product catalogue. Use when a plain fetch is
// blocked by a JavaScript challenge.
//   node tools/fetch_page.js <url> [--products] [--max 6000]
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const url = args.find((a) => /^https?:\/\//.test(a));
const wantProducts = args.includes('--products');
const maxIdx = args.indexOf('--max');
const max = maxIdx >= 0 ? Number(args[maxIdx + 1]) : 6000;
if (!url) {
  console.error('usage: fetch_page.js <url> [--products] [--max N]');
  process.exit(2);
}

const SOCIAL = /(instagram|facebook|tiktok|twitter|youtube|linkedin|pinterest|threads|snapchat)\.(com|net)|\/\/x\.com|wa\.me/;

(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({
      userAgent:
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
    });
    const res = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(8000); // let bot checks and client rendering settle
    const out = {
      url: page.url(),
      status: res ? res.status() : null,
      title: await page.title(),
      description: await page
        .$eval('meta[name="description"]', (m) => m.content)
        .catch(() => null),
      socials: await page.evaluate(
        (src) => [...new Set([...document.querySelectorAll('a[href]')].map((a) => a.href).filter((h) => new RegExp(src).test(h)))],
        SOCIAL.source,
      ),
      text: (await page.evaluate(() => document.body.innerText)).replace(/\n{2,}/g, '\n').slice(0, max),
    };
    if (wantProducts) {
      out.products = await page.evaluate(async () => {
        try {
          const r = await fetch('/products.json?limit=250');
          if (!r.ok) return `unavailable (HTTP ${r.status})`;
          const j = await r.json();
          return j.products.map((p) => ({
            title: p.title,
            type: p.product_type,
            variants: p.variants.map((v) => `${v.title}: ${v.price}`),
          }));
        } catch (e) {
          return `unavailable (${e.message})`;
        }
      });
    }
    console.log(JSON.stringify(out, null, 2));
  } catch (e) {
    console.log(JSON.stringify({ url, error: e.message }));
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
