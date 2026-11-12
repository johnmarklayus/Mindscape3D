---
id: structure
group: Start Here
nav: Project Structure
---

# Project Structure

Where things live under `Assets/`.

Around `Assets/`, the project folder holds:

```text
mindscape-3d/
├── Assets/ Packages/ ProjectSettings/   The Unity project
├── Blender/        Blend Files/ (.blend sources), Exports/, Models/, Single Objects/, Scripts/ (Blender Python)
├── Builds/         Dated game builds, and webgl-play/ (the WebGL copy deployed to Vercel)
├── Documents/      Website/ (this docs site), Story Specs/, Tester Lists/, Reports/, Concepts/, Captures/, UI Mockups/, Source Media/
├── Tools/          BuildScripts/ (command-line builds), NativePlugins/ (macOS sign-in plugin source), QA/
└── supabase/       Online accounts backend (migrations + the account edge function)
```


```text
Assets/
├── Scripts/                 Every runtime script, by what it does (see Assets/Scripts/README.md):
│   ├── Camera/              PlayerMovement.Camera.cs (the follow camera: orbit, zoom, first person, wall collision), ShotFocus
│   ├── Player/              PlayerMovement (walking), PlayerControls, PlayerAppearance (boy/girl), PlayerOutfit, PlayerBackpack
│   ├── Input/               KeyBindings, PlayerInputBindings, MobileControls, MobileInput, MobileJoystick
│   ├── Interaction/         InteractFocus, InteractOutline, DoorInteraction, BedModeController, CollectibleItem, CollectiblesManager
│   ├── NPC/                 NPC (name + dialogue tree), NPCWander, NPCNameTag
│   ├── Dialogue/            NPCInteractionManager (NPC conversations), NPCAmbientConversation
│   ├── Story/               AcademicEpisode (the story base: Say/Think, Choose, shots, spots, roaming), EpisodeUI, EpisodeReflection
│   ├── Chapters/            One folder per chapter with its episode scripts, plus Prototypes/ (old Chapter 2 scenes)
│   ├── Scene/               Scene pieces shared by several episodes: BedroomDecor, SocialMirror, BusRide, HomeWelcome
│   ├── Quests/              Quest, QuestHUDController, TutorialManager
│   ├── Minigames/           QuestMinigame (base), BreathingMinigame, WorryCourtroom/, ThoughtCourtroom/, Testing/ (Minigame Lab)
│   ├── UI/                  MainMenuNewController, PauseMenu, CreditsRoll, loading screen, stress HUD, UI Toolkit custom controls
│   ├── Audio/               MusicManager, SFXManager, SceneMusicMap
│   ├── Cutscene/            CutscenePlayer and buttons, IntroSequence
│   ├── Vehicles/            CityTrafficVehicle, TrafficObstacle, SchoolBusAnimator
│   ├── Data/                SQLite + local-storage saves, progress, and the optional Supabase cloud sync
│   └── Core/                GraphicsPrefs, IPausable
├── Editor/                  Editor-only tools (menus, inspectors, scene builders), by area (see Assets/Editor/README.md):
│   ├── Chapters/  World/  Characters/  UI/  Menus/  Tests/  Build/
├── AcademicPressure/ … SocialDynamics/   Chapter materials, prefabs and art (their scripts are in Scripts/Chapters/)
├── Prefabs/                 Player, NPC (dummy model, name tag), Minigames (WorryCourtroom), World.prefab and Vehicles/
├── Scenes/                  Intro, main_menu_new, Tutorial, Chapter N - Episode N, Cutscene scenes, WorryCourtroom, MinigameTestLab
├── Resources/               Everything loaded by name at runtime
│   ├── Cutscenes/           Slide art, one folder per episode
│   ├── EpisodeThumbnails/   Episode thumbnails, also the loading-screen backdrops
│   ├── MenuArt/             Menu backgrounds
│   ├── Music/               Background tracks (the playlist) and the credits file
│   ├── MinigameTheme/       Shared fonts (Comic Neue, Story Serif) and the circle sprite
│   ├── EpisodeUI.asset      Points at every story-screen UXML (see Episode Screens)
│   └── SceneMusicMap.asset  Which track each scene plays, and the crossfade length
├── Settings/                URP + build profiles (the input actions are Resources/GameControls.inputactions)
├── UI/                      uGUI sprites/icons for the HUD
├── UI Toolkit/              *.uxml / *.uss: every story screen, the minigames, the Quest HUD, Stress HUD, Pause Menu, and MainMenuNew/ (all menu pages)
├── FamilySet/               Family character models (Mother, Father, Boy, Girl)
└── Models/                  Low-poly location models (classroom, cafeteria, dormitory, home, school grounds)
    ├── World/               world_new.glb: the one shared city used by every episode
    └── Vehicles/            Sedan, SUV, Pickup, SportsCar, DeliveryVan, SchoolBus (with looping wheel and body clips)
```

### Naming conventions worth knowing

- **Gameplay scenes** are named `Chapter <N> - Episode <N>`; story beats before them live in `Cutscene - Episode <N>` scenes played through `CutscenePlayer.cs`.
- **UI Toolkit documents** in the Hierarchy are prefixed `UI_Toolkit_*` (for example `UI_Toolkit_QuestHUD`, `UI_Toolkit_StressHUD`) so they're easy to spot next to legacy `HUDCanvas` uGUI objects.
- **NPCs** are named `NPC - <Name>` in the Hierarchy and live under an `NPC System` object. Their routes live under `NPC Waypoints`.
- **Editor tooling** lives only under `Assets/Editor/` and is never referenced by runtime scripts.
- **Shared theme assets** go in `Resources/MinigameTheme/` so any script can load them by name.
