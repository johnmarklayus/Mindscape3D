# MindScape 3D: official website

The public site for MindScape 3D, built with **Next.js 16 (App Router) + Chakra UI v3**, ready for Vercel.

| Page | What it is |
|---|---|
| `/` | Landing page: hero (Play on the web / Download), project overview and purpose, features, chapters and screenshots, download cards (version, size, minimum and recommended requirements), about and team, support hotlines, contact form |
| `/play` | Web play: runs the WebGL build in the page (loads only when the visitor presses Start) |
| `#privacy`, `#terms` | Privacy Policy and Terms and Conditions, in a modal on any page (linked from the cookie banner, contact form and footer; `/privacy` and `/terms` redirect there) |

Also included: a dark theme only (the game's look; there is no light mode), a cookie consent banner with
settings (analytics only load after consent), SEO metadata, Open Graph / Twitter images, `sitemap.xml`, `robots.txt`,
a web manifest, icons, and structured data (schema.org `VideoGame`).

## Run it locally

```bash
npm install
npm run sync-game   # copy the latest WebGL build from ../Builds/webgl-play into public/game
npm run dev         # http://localhost:3000
```

## Where to change things

| To change | Edit |
|---|---|
| Colors, fonts | `src/theme.ts` (taken from the game's main menu: ink, wood, paper, brass, gold) |
| Site name, domain, version, tagline | `src/lib/site.ts` |
| Download cards (version, size, requirements) | `src/data/downloads.ts` |
| Landing sections | `src/components/` (`hero`, `overview`, `downloads`, `about`, `contact`) |
| Privacy Policy / Terms | `src/components/legal-content.tsx` (text) and `legal-modal.tsx` (the modal) |
| Images | `public/images/` (hero, logo, chapter shots) and `src/app/opengraph-image.jpg` (social preview) |

## Deploy to Vercel

1. Fill in the environment variables from `.env.example` in **Vercel > Project > Settings > Environment Variables**:
   - `NEXT_PUBLIC_SITE_URL`: your final domain, for example `https://mindscape3d.com` (used for canonical links,
     the sitemap and social previews).
   - `NEXT_PUBLIC_DOWNLOAD_WINDOWS` / `_MACOS` / `_ANDROID`: links to the build files. They are over Vercel's 100 MB
     upload limit, so host them elsewhere (GitHub Releases, Google Drive, a storage bucket). A platform with no link
     shows "Coming soon".
   - `RESEND_API_KEY`, `CONTACT_TO_EMAIL`, `CONTACT_FROM_EMAIL`: the contact form sends mail through
     [Resend](https://resend.com) (the same service the game's account emails use). `CONTACT_FROM_EMAIL` must be on a
     domain verified in Resend. `NEXT_PUBLIC_CONTACT_EMAIL` (optional) is shown if sending fails.
2. Run `npm run sync-game`, then deploy from this folder: `npx vercel --prod`. The first time, it asks to create or
   link a project; set the **Root Directory** to `Site` if you later connect the Git repository instead.
3. Add your domain in **Vercel > Project > Settings > Domains** and follow the DNS steps there.
4. Optional: turn on **Web Analytics** in the Vercel project (the site only loads it for visitors who accept analytics
   cookies), then submit `https://your-domain/sitemap.xml` in Google Search Console.

**About the game files:** `public/game` (about 136 MB) is not in git, so a Git-connected deployment will not have it
and `/play` will show an error. Either deploy with `vercel --prod` from your computer after `npm run sync-game`, or
host the WebGL build elsewhere and set `NEXT_PUBLIC_GAME_URL` to it (that host must send `Content-Encoding: br` for the
`.br` files and allow cross-origin requests).
