// Copies every script that has a walkthrough from the Unity project into src/content/code/ so the
// docs build on their own (e.g. on Vercel, where Assets/ may not be checked out). The copies are
// meant to be committed. If Assets/ isn't there, the committed copies are used as they are.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const docsDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const repoRoot = path.resolve(docsDir, "..", "..")
const scriptsDir = path.join(docsDir, "src/content/scripts")
const outDir = path.join(docsDir, "src/content/code")

if (!fs.existsSync(path.join(repoRoot, "Assets"))) {
  console.log("sync-code: no Assets/ next to docs/, keeping the committed copies")
  process.exit(0)
}

const ids = JSON.parse(fs.readFileSync(path.join(scriptsDir, "index.json"), "utf8"))
let copied = 0
for (const id of ids) {
  const { path: rel } = JSON.parse(fs.readFileSync(path.join(scriptsDir, `${id}.json`), "utf8"))
  const src = path.join(repoRoot, rel)
  if (!fs.existsSync(src)) {
    console.warn(`sync-code: ${rel} is missing from the Unity project, keeping the old copy`)
    continue
  }
  const dest = path.join(outDir, rel)
  fs.mkdirSync(path.dirname(dest), { recursive: true })
  const text = fs.readFileSync(src, "utf8").replace(/^﻿/, "").replace(/\r\n/g, "\n")
  if (!fs.existsSync(dest) || fs.readFileSync(dest, "utf8") !== text) {
    fs.writeFileSync(dest, text)
    copied++
  }
}
console.log(`sync-code: ${ids.length} scripts checked, ${copied} updated`)
