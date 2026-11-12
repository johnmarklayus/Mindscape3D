---
id: system-theme
group: Core Systems
nav: UI Theme
---

# UI Theme

The game's in-game UI shares one look: warm **parchment** panels in a dark **ink** frame with a **brass** edge, **brown** buttons with **cream** text, a serif heading and a rounded friendly body font. The pause menu is the reference; the conversation panel, the Breathing Exercise and the Worry Courtroom follow it.

## Palette

| Role | Colour (RGB) | Used for |
| --- | --- | --- |
| Parchment | 227, 212, 178 | Panel and speech-bubble fills |
| Ink | 48, 45, 40 | Frames, dark plates, text on parchment |
| Brass edge | 181, 153, 105 | Panel edges, button outlines |
| Brass accent | 209, 168, 79 | Headings, active tabs, progress fills, stars |
| Brown button | 118, 92, 58 | Choice and action buttons |
| Cream text | 247, 232, 204 | Text on dark and brown surfaces |
| Muted | 188, 171, 141 | Secondary text on dark surfaces |
| Calm / Rising / Alert | 88,112,83 / 157,111,47 / 149,58,43 | Stress HUD states |

## Fonts

Saved TextMeshPro font assets in `Assets/Resources/MinigameTheme/`:

- **Comic Neue** (Regular and Bold): body text, buttons, hints.
- **Story Serif**: headings (speaker names, "BREATHE", the pause menu's "PAUSED").
- `MinigameUI.Font(bold)` and `MinigameUI.SerifFont()` load them by name, so any script can use the same fonts.

The new Main Menu's root USS style loads Comic Neue Regular from `Resources/MinigameTheme`; its headings use Story Serif. The collectible prompt uses `MinigameUI.Font(true)` for Comic Neue Bold.

Also in that folder: `Circle.png`, a smooth round sprite used for the breathing circle.

## Where it is applied

| Screen | Built by |
| --- | --- |
| NPC conversation panel and "[ F ] Talk to" prompt | `NPCDialogue_new.uxml` and `InteractPrompt.uxml`, found by `NPCInteractionManager.CreateUI()` |
| Breathing Exercise, Worry Courtroom | `Breathing.uxml`, `WorryCourtroom.uxml` (UI Toolkit) |
| Every story screen (dialogue, choices, objective, status, cards, phone, exam paper, journal, fade, flashback frame, crosshair, door prompt) | One `.uxml` + `.uss` each in `Assets/UI Toolkit/`, sharing `EpisodeScreens.uss`. See [Episode Screens (UI Toolkit)](#system-episode-ui). |
| "F to collect" prompt | `CollectiblesManager.CreatePrompt()` (still uGUI), using the shared Comic Neue Bold font |
| Pause Menu, Quest Journal, Stress HUD, Main Menu | UI Toolkit `.uxml` and `.uss` |

## Theming something new

1. Use the palette above (copy the colours from `NPCInteractionManager` or `MinigameUI`).
2. Load fonts through `MinigameUI`, not `TMP_Settings.defaultFontAsset`.
3. Prefer a **UXML + USS file** over UI built only in code, so designers can adjust it in UI Builder. Put colours, text and numbers in serialized fields.
4. Give the document a sorting order that matches its job (see [Conventions & Gotchas](#ref-conventions)).
5. Keep text short and plain; see the [Writing Guidelines](#story-tone).
