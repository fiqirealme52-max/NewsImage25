// News 25 R3 entrypoint: copies entry.png into the output directory and
// verifies the copy is byte-identical. Exits non-zero on any failure.
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dst = join(outDir, "entry.png");

if (!existsSync(src)) {
  console.error("entry.png is missing next to main.ts");
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);
const a = readFileSync(src);
const b = readFileSync(dst);
if (!a.equals(b)) {
  console.error("copied entry.png differs from the source");
  process.exit(1);
}
console.log(`wrote ${dst} (${b.length} bytes, identical)`);
