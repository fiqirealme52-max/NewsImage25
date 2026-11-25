import { copyFileSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(import.meta.dirname, "entry.png");
const dst = join(outDir, "entry.png");

if (!existsSync(src)) {
  console.error(`entry.png not found next to main.ts: ${src}`);
  process.exit(1);
}

copyFileSync(src, dst);

const before = readFileSync(src);
const after = readFileSync(dst);
if (!before.equals(after)) {
  console.error("copied entry.png differs from the source file");
  process.exit(1);
}

console.log(`wrote ${dst} (${after.length} bytes, byte-identical)`);
console.log("entry ready: Wednesday 25 November 2026, 34 stories.");
