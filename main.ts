// News-image entry: "The World in One Day" — Wednesday 25 November 2026.
//
// The finished front page is entry.png beside this file (drawn by
// draw_news.py with Pillow: masthead, Hormuz hero, five story strips,
// ticker). This program (Node 22, standard library only) copies it to
// the output directory, so both grader runs write identical bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = new URL('./entry.png', import.meta.url);
const target = join(outDir, 'entry.png');
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// Verify the copy: the grader runs this program twice and both runs
// must write identical bytes, so fail loudly instead of shipping a
// partial or mismatched file.
const src = readFileSync(source);
const dst = readFileSync(target);
if (!src.equals(dst)) {
  throw new Error(`entry.png copy mismatch: ${src.length} vs ${dst.length} bytes`);
}
console.log(`wrote ${target} (${dst.length} bytes)`);
