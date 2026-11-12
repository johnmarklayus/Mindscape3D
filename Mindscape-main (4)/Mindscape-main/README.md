# Mindscape 3D

Mindscape 3D is a third-person story game about the everyday pressures students face. The player plays as Joey, as a boy or a girl. Joey explores the house, the school and the city, talks with family and friends, makes choices, and practises coping skills: guided breathing, grounding, and putting a worried thought "on trial" in the Worry Courtroom. After each episode, the player writes in a reflection journal and fills in a short self-assessment.

| Chapter | Episodes | Theme |
|---|---|---|
| Tutorial | 1 | Movement, the menu and the journal |
| Chapter 1 · Academic Pressure | 4 | One school deadline: House, Classroom, Cafeteria, Dormitory |
| Chapter 2 · Family Expectations | 5 | An examination day, and what the family expects |
| Chapter 3 · Social Dynamics | 8 | A reunion with old friends, ending with a group photograph |

The game runs on WebGL (browser), Android, macOS and Windows. Progress is saved on the device (SQLite and local storage), and players can also create an online account (Supabase) to keep their progress and journal in the cloud.

---

## Getting started

1. Install **Unity 6000.5.8f1** with Unity Hub. Add the build support modules for the platforms you need: Web, Android, Windows (Mono) and/or Mac.
2. In Unity Hub, choose **Add > Add project from disk** and select this folder (`mindscape-3d`).
3. The first time you open the project, Unity rebuilds its `Library/` folder. This takes several minutes.
4. Open `Assets/Scenes/Intro.unity` and press **Play**. The game starts the way a player sees it: intro video, title, then the main menu. To test one episode directly, open its scene (for example `Assets/Scenes/Chapter 1 - Episode 1.unity`) and press Play.

The full guide is the documentation site in `Documents/Website`. It explains every system, every workflow and the main scripts line by line, in English and in Tagalog for the handover.

---

## Project structure

```text
mindscape-3d/
├── Assets/             The game itself (everything Unity builds into the game)
├── Packages/           Unity package list
├── ProjectSettings/    Unity project settings
├── Blender/            Source art: Blender projects, exports, and the scripts that build them
├── Builds/             Finished game builds (not in git)
├── Documents/          Documentation site, story specs, tester lists, reports, design images
├── Site/               The official website (landing page, downloads, web play), deployed on Vercel
├── Tools/              Command-line build scripts, native plugin source, QA script
├── supabase/           Online accounts backend
└── README.md           This file
```

Unity also creates `Library/`, `Logs/`, `UserSettings/` and the `.csproj` / `.slnx` files. They are not in git and can be deleted at any time; Unity rebuilds them the next time the project opens.

### `Assets/`: the game

| Folder | What is in it |
|---|---|
| `Scenes/` | One scene per episode, named `Chapter N - Episode N.unity`, plus `Intro` (the first scene), `main_menu_new` (the main menu), `Tutorial`, `Cutscene - Episode 1`, `MinigameTestLab` and `WorryCourtroom`. `Scenes/Prototypes/` holds the first versions of Chapter 2, which are not in the game. |
| `Scripts/` | Every runtime script, grouped by what it does. See the table below and `Assets/Scripts/README.md`. |
| `Editor/` | Editor-only tools: the **Mindscape** menu, custom Inspectors, scene builders and checks. They are never part of a build. See `Assets/Editor/README.md`. |
| `Characters/` | The player (boy and girl), the 20 NPCs, and their animations |
| `Models/` | The shared city (`World/world_new.glb`), the house, the school grounds, furniture, doors, vehicles, collectibles and the 3D title |
| `Prefabs/` | Reusable objects: the Player, NPCs, doors, furniture, collectibles, vehicles, the school bus, minigames |
| `Resources/` | Everything the game loads by name while running: episode thumbnails, cutscene slides, menu art, music, fonts, the input actions (`GameControls.inputactions`), and `EpisodeUI.asset`, which points to every story screen |
| `UI Toolkit/` | The layout (`.uxml`) and style (`.uss`) of every screen: dialogue, choices, journal, pause menu, HUD, minigames, and `MainMenuNew/` with all the main menu pages. Edit them in **Window > UI Toolkit > UI Builder**. |
| `StreamingAssets/` | The intro video, re-encoded small enough for builds and GitHub |
| `Settings/` | URP render pipeline assets (PC and Mobile) and build profiles |
| `Shaders/` | The blue interaction outline shaders |
| `Plugins/` | Native plugins for Android and macOS (sign-in) |
| `AcademicPressure/`, `FamilyFinale/`, `SocialDynamics/`, `EpisodeOne/`, `EpisodeTwo/`, `EpisodeThree/` | Materials, animators and prefabs that belong to one chapter. Their scripts are in `Scripts/Chapters/`. |
| `FamilySet/` | Models of the family (mother, father, brother) |
| `Minigames/` | Assets for the Worry Courtroom and the Minigame Lab |
| `TextMesh Pro/`, `Adaptive Performance/` | Unity package assets. Leave them alone. |

### `Assets/Scripts/`: where to find a script

| If you need to change... | Look in |
|---|---|
| The player camera (orbit, zoom, mouse or touch look, first person, the camera stopping at walls) | `Camera/PlayerMovement.Camera.cs`. Its settings are the **Camera** and **Zoom** fields of the *PlayerMovement* component on the Player. |
| Walking, running, gravity | `Player/PlayerMovement.cs` |
| Boy or girl model, outfits, the school bag | `Player/` |
| Keys, gamepad, on-screen touch controls | `Input/` |
| The [E] prompt, outlines, doors, the bed, collectibles | `Interaction/` |
| An NPC's name, dialogue tree or walking route | `NPC/` |
| How NPC conversations run | `Dialogue/NPCInteractionManager.cs` |
| How story dialogue, choices, camera shots and free roaming work | `Story/AcademicEpisode.cs` (the base every episode is built on) |
| The story of one episode (its lines, choices and order) | `Chapters/Chapter N - .../` (one script per episode) |
| Scene pieces several episodes share (bedroom decor, mirrors, the bus home) | `Scene/` |
| Quests, objectives, the tutorial | `Quests/` |
| Breathing, Worry Courtroom and the other minigames | `Minigames/` |
| Main menu, pause menu, loading screen, credits, HUD | `UI/` |
| Music and sound effects | `Audio/` |
| Intro video and cutscene slides | `Cutscene/` |
| City traffic and buses | `Vehicles/` |
| Saves, progress, accounts, cloud sync | `Data/` |
| Graphics settings | `Core/` |

### `Blender/`: source art

| Folder | What is in it |
|---|---|
| `Blend Files/` | The Blender projects the game's models come from: the house (`house-and-lot-cozy.blend`), the school (`school-grounds.blend`), the city (`world_new.blend`), the player outfits (`Main_Character_Outfit_Lineup.blend`), the NPCs (`NPC_Roster.blend`), vehicles, furniture, doors and the logo. `Backups/` holds earlier versions. |
| `Exports/` | Exported copies (FBX, material colours) kept next to the sources |
| `Models/`, `Single Objects/` | Source models (vehicles, single props) used when building the Blender scenes |
| `Scripts/` | Blender Python scripts that build and export the models, run with Blender in the background |

To change a model, edit its `.blend` file and export it over the matching file in `Assets/Models` or `Assets/Characters`. The export settings for each model are in the documentation site on the *Blender Assets* page.

### `Builds/`: finished games

Each build goes into a folder named by date, for example `Builds/2026-11-11/`, with `WebGL/`, `Android/Mindscape.apk`, `macOS/Mindscape.app` or `Windows/Mindscape.exe`, a zip ready to share, and the build log. `webgl-play/` is the copy of the WebGL build that is published on Vercel. This folder is not in git.

### `Documents/`: everything to read

| Folder | What is in it |
|---|---|
| `Website/` | The documentation site (React + Vite), published on Vercel. Its pages are Markdown files in `src/content/docs/`. |
| `Story Specs/` | The chapter scripts (PDF) for Chapters 1, 2 and 3 |
| `Tester Lists/` | The capstone list, tester issue lists and the change and bug list |
| `Reports/` | The QA master workbook and check images |
| `Concepts/`, `UI Mockups/`, `Captures/` | Concept art, interface mockups and in-game screenshots |
| `Source Media/` | The full-size intro video (the game uses the smaller copy in `Assets/StreamingAssets`) |
| `PRIVACY_POLICY_DECISION.md` | Notes on the privacy policy |

### `Site/`: the official website

The public website for players, built with Next.js and Chakra UI in the game's colors. It has a landing page (hero, overview, features, chapters, downloads with system requirements, about, contact form, cookie consent, privacy policy and terms) and a `/play` page that runs the WebGL build. `Site/README.md` explains how to run it, change it and deploy it to Vercel with your own domain.

### `Tools/`

| Folder | What is in it |
|---|---|
| `BuildScripts/` | Builds the game without opening the Unity editor: `build-webgl.sh`, `build-android.sh`, `build-mac.sh`, `build-windows.sh` |
| `NativePlugins/` | Source of the macOS sign-in plugin (`build.sh` compiles it into `Assets/Plugins/macOS`) |
| `QA/` | The script that writes the QA master workbook in `Documents/Reports` |

### `supabase/`

The online accounts backend: `migrations/` rebuilds the database, and `functions/account/` is the edge function for sign-up, the email code (OTP), sign-in and deleting or recovering an account. The game connects to it in `Assets/Scripts/Data/MindscapeCloud.cs`.

---

## Common tasks

**Build the game.** Close Unity first, then run one of these from the project folder (Terminal on a Mac, Git Bash on Windows):

```bash
./Tools/BuildScripts/build-webgl.sh
./Tools/BuildScripts/build-android.sh
./Tools/BuildScripts/build-mac.sh
./Tools/BuildScripts/build-windows.sh
```

The result is written to `Builds/<today>/`. You can also build from Unity with **File > Build Profiles**.

**Run the documentation site.**

```bash
cd Documents/Website
npm install
npm run dev
```

**Rebuild scenes after a model changes.** Use the **Mindscape** menu in Unity. For example, the chapter builders and *World* sync tools place the new model in every scene. The documentation site's *Editor Menu Items* page lists every menu item.

---

## Good to know

- **Moving scripts and assets:** always move or rename them in Unity's Project window. Unity keeps each file's `.meta` file with it, and scenes and prefabs find files through the ID stored in that `.meta`. If you move a file outside Unity without its `.meta`, every reference to it breaks.
- **File names:** a script that holds a component must have the same name as its class (`PlayerMovement.cs` holds `PlayerMovement`).
- **Before building:** the scenes in the build are listed in **File > Build Profiles**. The game starts at `Intro`.
- **Large files:** GitHub allows at most 100 MB per file, so builds and the full-size intro video are kept out of git (see `.gitignore`).
