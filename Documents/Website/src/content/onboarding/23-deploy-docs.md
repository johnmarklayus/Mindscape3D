---
id: deploy-docs
group: Build & Deploy
nav: Documentation site
---

# Documentation Site

This site, in `Documents/Website/`.

A Vite + React site. Its pages are the Markdown files in `src/content/docs/`, ordered by filename. Each page starts with `id`, `group` and `nav`.

```bash
cd Documents/Website
npm install
npm run dev          # local preview
npm run build        # copies the current script sources, then checks it builds
vercel --prod
```

APKs and other large files are listed in `.vercelignore`, because Vercel rejects any single file over 100 MB. The annotated script pages anchor each note to a line of code. When that line changes, re-anchor the note.

The onboarding pages are the Markdown files in `src/content/onboarding/`, also ordered by filename, with `id`, `group` (the sidebar section) and `nav` (the sidebar label).
