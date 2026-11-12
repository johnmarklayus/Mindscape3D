// Copies the latest WebGL build into public/game so the Play page can run it from this site.
// Source: ../Builds/webgl-play (the folder the WebGL build script and release steps keep up to date).
// Run after every new WebGL build:  npm run sync-game
// public/game is ignored by git (about 110 MB); deploy it with `vercel --prod` from this folder.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const source = path.resolve(site, "..", "Builds", "webgl-play")
const target = path.join(site, "public", "game")

if (!fs.existsSync(path.join(source, "Build"))) {
  console.error(`sync-game: no WebGL build at ${source}/Build. Build the game first (Tools/BuildScripts/build-webgl.sh).`)
  process.exit(1)
}

fs.rmSync(target, { recursive: true, force: true })
for (const folder of ["Build", "StreamingAssets"]) {
  const from = path.join(source, folder)
  if (fs.existsSync(from)) fs.cpSync(from, path.join(target, folder), { recursive: true })
}

let bytes = 0
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(p)
    else bytes += fs.statSync(p).size
  }
}
walk(target)
const loader = fs.readdirSync(path.join(target, "Build")).find((f) => f.endsWith(".loader.js"))
console.log(`sync-game: copied ${(bytes / 1048576).toFixed(1)} MB into public/game (loader: ${loader})`)
