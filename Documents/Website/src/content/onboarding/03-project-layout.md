---
id: project-layout
group: Getting Started
nav: Project layout
---

# Project Layout

Where everything lives in the repository, and where to look when you need to change something.

```text
mindscape-3d/
├── Assets/            The game: Scenes, Scripts, Editor tools, Models, Characters, UI Toolkit, Resources …
├── Blender/           Source art (.blend), exports, and Blender Python build/export scripts
├── Builds/            Finished builds, one folder per date (not in git)
├── Documents/         This documentation site, story specs, tester lists, QA reports, concepts
├── Site/              The official public website (Next.js + Chakra UI)
├── Tools/             BuildScripts/, NativePlugins/, QA/
└── supabase/          Online accounts backend (migrations + edge function)
```

| If you need to change… | Look in |
|---|---|
| How story dialogue, choices, camera shots, roaming and save replay work | `Assets/Scripts/Story/AcademicEpisode.cs` (every episode is built on it) |
| The story of one episode (its lines, choices and order) | `Assets/Scripts/Chapters/Chapter N - …/` (one script per episode) |
| Player movement, camera, input | `Scripts/Player`, `Scripts/Camera`, `Scripts/Input` |
| NPCs and their small talk | `Scripts/NPC`, `Scripts/Dialogue` |
| Doors, the bed, collectibles, [E] prompts | `Scripts/Interaction` |
| Breathing, Worry Courtroom and other minigames | `Scripts/Minigames` |
| Saves, progress, accounts, cloud sync | `Scripts/Data` |
| Main menu, pause, loading screen, HUD | `Scripts/UI` |
| Editor tools: the **Mindscape** menu, scene builders, checks | `Assets/Editor/<area>` (never part of a build) |

**Rule:** move or rename assets only in Unity's Project window. Each file's `.meta` holds the ID that scenes and prefabs use to find it, so moving a file outside Unity without its `.meta` breaks every reference to it.

More: [Script Index](/#ref-scripts) · [Conventions & Gotchas](/#ref-conventions)
