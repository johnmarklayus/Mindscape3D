# Mindscape 3D — Project Docs

A React + Vite + Tailwind (shadcn-style components) documentation site for the Mindscape 3D
Unity project. It covers the **story** (Chapter 1 · Academic Pressure, Chapters 2 and 3, a Chapter 2
episode's full dialogue and the writing guidelines), workflows (creating scenes, NPCs, quests,
collectibles, cutscenes, wandering NPCs, and creating or modifying Blender assets), core systems (player, HUD, quests, stress, UI theme,
lighting, and the **shared open-world city with its sidewalk walkers and traffic**), the
**minigames** (Worry Courtroom, Breathing Exercise), an editor menu-item reference, and
line-by-line annotated walkthroughs of the core gameplay scripts.

The site has a **light and dark theme**: use the sun/moon button in the header. It follows your
system setting the first time and remembers your choice after that.

## Pages

Pages are Markdown files in `src/content/docs/`, ordered by filename. Each starts with front matter:

```md
---
id: my-page          # the #hash used in links, e.g. [text](#my-page)
group: Workflows     # sidebar heading
nav: My Page         # sidebar label
---
```

Callouts: a blockquote starting `[!TIP] Title`, `[!WARN] Title` or `[!MENU] Title`.
Use letters in the filename (`05b-...`) to slot a page between two numbered ones.

## Develop

```sh
npm install
npm run dev
```

## Build

```sh
npm run build
npm run preview
```

## Play and download builds

The header's **Download APK** link uses `src/data/build.ts` (`apkUrl`; empty hides the button). Vercel rejects
files over 100 MB, so an APK that big (the 0.2.0 one is 189 MB, kept in `public/game-builds/2026-10-17/` but
excluded in `.vercelignore`) must be hosted elsewhere and its full URL put in `apkUrl`. **Play Game (Web)** loads the matching WebGL
files from `public/game-builds/2026-10-17/Build/`. Keep both paths in `src/data/build.ts` in
sync when replacing a release. `vercel.json` supplies the content encoding headers required
for the compressed WebGL files. The game's intro video is loaded from `public/StreamingAssets/` (copy the
`StreamingAssets` folder of the WebGL build there when it changes).

## Adding another annotated script

Add an entry to `src/data/scripts.ts`:

```ts
{
  id: "my-script",
  title: "MyScript.cs",
  path: "Assets/MyScript.cs",
  summary: "One or two sentences on what this script owns.",
  lines: [`using UnityEngine;`, ``, `public class MyScript : MonoBehaviour`, `{`, `}`],
  notes: {
    1: "Explains line 1.",
    "3-4": "One note spanning lines 3 through 4.",
  },
}
```

It'll automatically show up in the sidebar under **Scripts (Line by Line)** and on the Scripts
page.

## Where the content lives

- **Prose** — one Markdown file per section in `src/content/docs/` (ordered by filename). Front
  matter sets `id` (anchor), `group` and `nav` (sidebar). Use `> [!TIP] Label`, `> [!WARN] Label`
  or `> [!MENU] Label` blockquotes for callouts, and an ordered list for step-by-step workflows.
- **Script walkthroughs** — shown read-only in Monaco with the explanations in a panel beside it.
  `npm run dev` / `npm run build` first run `npm run sync`, which copies each annotated script from
  `../Assets/` into `src/content/code/` (commit those copies; if `Assets/` isn't there, as on
  Vercel, the committed copies are used). Annotations are in `src/content/scripts/<id>.json` and
  the display order in `src/content/scripts/index.json`. A note is anchored to the trimmed text of
  a line (`match`, plus `nth`/`span` when needed), not a line number, so edits to a script don't
  misplace it. In dev, the console warns about any note whose line no longer exists.
