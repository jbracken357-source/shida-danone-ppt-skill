#!/usr/bin/env node
/**
 * export_deck_pptx.mjs — 把多文件 slide deck 导出为 PPTX（图片铺底模式）
 *
 * 用法：
 *   node export_deck_pptx.mjs --slides <dir> --out <file.pptx> [--width 1920] [--height 1080]
 *
 * 特点：
 *   - 每张 slide 截图成 PNG，满铺一张 PPTX 页面
 *   - 视觉 100% 保真（因为就是图片）
 *   - 文字不可编辑
 *   - HTML 随便写，不挑格式
 *
 * 依赖：npm install playwright pptxgenjs
 *
 * 按文件名排序（01-xxx.html → 02-xxx.html → ...）。
 */

import { chromium } from 'playwright';
import pptxgen from 'pptxgenjs';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

function parseArgs() {
  const args = { width: 1920, height: 1080 };
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, '');
    args[k] = a[i + 1];
  }
  if (!args.slides || !args.out) {
    console.error('用法: node export_deck_pptx.mjs --slides <dir> --out <file.pptx> [--width 1920] [--height 1080]');
    process.exit(1);
  }
  args.width = parseInt(args.width);
  args.height = parseInt(args.height);
  return args;
}

async function exportImage({ slidesDir, outFile, files, width, height }) {
  console.log(`Rendering ${files.length} slides as PNG...`);

  const browser = await chromium.launch({ channel: 'chromium' });
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();

  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'deck-pptx-'));
  const pngs = [];
  for (const f of files) {
    const url = 'file://' + path.join(slidesDir, f);
    await page.goto(url, { waitUntil: 'networkidle' }).catch(() => page.goto(url));
    await page.waitForTimeout(1200);
    const out = path.join(tmpDir, f.replace(/\.html$/, '.png'));
    await page.screenshot({ path: out, fullPage: false });
    pngs.push(out);
    console.log(`  [${pngs.length}/${files.length}] ${f}`);
  }
  await browser.close();

  const pres = new pptxgen();
  const slideW = width / 96;
  const slideH = height / 96;
  pres.defineLayout({ name: 'DECK', width: slideW, height: slideH });
  pres.layout = 'DECK';
  for (const png of pngs) {
    const s = pres.addSlide();
    s.addImage({ path: png, x: 0, y: 0, w: slideW, h: slideH });
  }
  await pres.writeFile({ fileName: outFile });

  for (const p of pngs) await fs.unlink(p).catch(() => {});
  await fs.rmdir(tmpDir).catch(() => {});

  console.log(`\n✓ Wrote ${outFile}  (${files.length} slides)`);
}

async function main() {
  const { slides, out, width, height } = parseArgs();
  const slidesDir = path.resolve(slides);
  const outFile = path.resolve(out);

  const files = (await fs.readdir(slidesDir))
    .filter(f => f.endsWith('.html'))
    .sort();
  if (!files.length) {
    console.error(`No .html files found in ${slidesDir}`);
    process.exit(1);
  }

  await exportImage({ slidesDir, outFile, files, width, height });
}

main().catch(e => { console.error(e); process.exit(1); });
