---
id: deploy-site
group: Build & Deploy
nav: Official website and downloads
---

# Official Website and Downloads

The public site in `Site/`, and where players download the game.

A Next.js 16 + Chakra UI site with a landing page, downloads with system requirements, a contact form, legal pages and a `/play` page that runs the WebGL build.

1. Set the environment variables from `Site/.env.example` in Vercel. They include `NEXT_PUBLIC_SITE_URL` and the download links `NEXT_PUBLIC_DOWNLOAD_WINDOWS` / `_MACOS` / `_ANDROID`. The build files are over Vercel's 100 MB file limit, so host them elsewhere (for example GitHub Releases or cloud storage) and link to them.
2. Copy the latest WebGL build into the site: run `npm run sync-game` in `Site/`.
3. Deploy from your computer: `npx vercel --prod`. A Git-connected deploy does not include the game files, which are not in git.
4. Add your domain under **Vercel › Settings › Domains**.

## Native downloads

Upload the APK and the macOS and Windows zips to your file host, then update the download links in the official website's environment variables and redeploy.
