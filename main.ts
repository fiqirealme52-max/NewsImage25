// News 25 — "The World in One Day — 25 November 2026".
// Copies the rendered front page (entry.png, 1024x1024) into the grader
// output directory. Node standard library only; no network, no deps.
import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = join(here, 'entry.png');
const dst = join(outDir, 'entry.png');

if (!existsSync(src)) {
  console.error('missing entry.png next to main.ts');
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });

copyFileSync(src, dst);
const a = readFileSync(src);
const b = readFileSync(dst);
if (!a.equals(b)) {
  console.error('copy is not byte-identical');
  process.exit(1);
}
console.log('wrote %s (%d bytes)', dst, b.length);
