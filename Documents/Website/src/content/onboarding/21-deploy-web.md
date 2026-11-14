---
id: deploy-web
group: Build & Deploy
nav: Publish the web build
---

# Publish the Web Build

There are three web destinations, each its own Vercel project: the playable web build (this page), the [official website](#deploy-site) and the [documentation site](#deploy-docs).

`Builds/webgl-play/` is the published copy of the web build. It contains a customised `index.html` (full-window on every device) and a `vercel.json` that sends `Content-Encoding: br` and the right content types for `/Build/*.br`.

```bash
rsync -a --delete \
  --exclude index.html --exclude vercel.json --exclude .vercel --exclude '*_DoNotShip' \
  Builds/<date>/WebGL/Mindscape/ Builds/webgl-play/
cd Builds/webgl-play
vercel --prod --yes
curl -sI https://<your-deployment>/Build/Mindscape.wasm.br | grep -i content-encoding   # expect: br
```

Keep `index.html` and `vercel.json` when you sync. Build files are named `Mindscape.*`.
