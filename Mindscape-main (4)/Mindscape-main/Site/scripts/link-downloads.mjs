// Development only: links the newest builds in ../Builds/<date>/ into public/downloads so the download buttons
// work on `npm run dev` before the real links exist. Runs by itself before `npm run dev` (the "predev" script).
// Links (not copies), so nothing large is duplicated. public/downloads is ignored by git and by `vercel`;
// in production the buttons use the NEXT_PUBLIC_DOWNLOAD_* variables instead.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const builds = path.resolve(site, "..", "Builds")
const target = path.join(site, "public", "downloads")

// Stable names the site points to -> pattern of the build script's dated file.
const files = {
  "Mindscape-Windows.zip": /^Mindscape-Windows-\d{4}-\d{2}-\d{2}\.zip$/,
  "Mindscape-macOS.zip": /^Mindscape-macOS-\d{4}-\d{2}-\d{2}\.zip$/,
  "Mindscape.apk": /^Mindscape-\d{4}-\d{2}-\d{2}\.apk$/,
}

const days = fs.existsSync(builds)
  ? fs.readdirSync(builds).filter((d) => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort().reverse()
  : []

fs.rmSync(target, { recursive: true, force: true })
fs.mkdirSync(target, { recursive: true })
for (const [name, pattern] of Object.entries(files)) {
  let found = null
  for (const day of days) {
    const hit = fs.readdirSync(path.join(builds, day)).find((f) => pattern.test(f))
    if (hit) { found = path.join(builds, day, hit); break }
  }
  if (!found) { console.log(`link-downloads: no build for ${name} yet (button shows "Coming soon")`); continue }
  fs.symlinkSync(found, path.join(target, name))
  console.log(`link-downloads: /downloads/${name} -> ${path.relative(site, found)}`)
}
