// News 25 — Wednesday 25 November 2026.
// Copies entry.png into MAKEFUN_OUTPUT_DIR (default /output) and verifies
// the copy is byte-identical to the shipped file. Exits non-zero on any
// mismatch, so a bad copy can never pass silently.
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dest = join(outDir, "entry.png");

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

if (!existsSync(src)) {
  console.error("entry.png is missing next to main.ts");
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);
if (sha256(src) !== sha256(dest)) {
  console.error("copied entry.png differs from the shipped entry.png");
  process.exit(1);
}
console.log(`entry.png copied to ${dest} (sha256 ${sha256(dest)})`);
