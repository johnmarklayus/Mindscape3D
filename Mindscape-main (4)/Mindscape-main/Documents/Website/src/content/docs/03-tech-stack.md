---
id: tech-stack
group: Start Here
nav: Tech Stack
---

# Tech Stack

- **Unity 6** (6000.x) with the Universal Render Pipeline. A PC and a Mobile quality level each have their own pipeline asset and renderer under `Assets/Settings/`.
- **New Input System**: all gameplay bindings live in one `GameControls.inputactions` asset (loaded from `Resources` by `KeyBindings.cs`), not per-script `Input.GetKey` calls.
- **UI Toolkit (runtime UIDocument)** for nearly every screen: all the story-episode screens, the NPC conversation panel, the Worry Courtroom and Breathing Exercise, the Quest Journal, Stress HUD, Pause Menu, crosshair and every page of the Main Menu. See [Episode Screens (UI Toolkit)](#system-episode-ui).
- **uGUI (Canvas)** is left for the mobile controls overlay, the loading screen, the intro, the Tutorial HUD, cutscene slides and the "F to collect" prompt.
- **TextMeshPro** for the remaining uGUI text, using saved font assets (Comic Neue and Story Serif) in `Resources/MinigameTheme/`.
- **ScriptableObjects** for authored content that isn't scene-specific, such as Worry Courtroom cases.
- **Prefabs** for shared building blocks: the NPC name tag and the whole Worry Courtroom.
- **Accounts and cloud saves**: Supabase Auth (email code) through one edge function, with SQLite and PlayerPrefs saves on the device. See [Accounts, Progress & Saves](#system-accounts).
- **Targets**: desktop, Android (touch controls on by default), and a WebGL build that this site can play. The header's **Download APK** and **Play Game (Web)** always serve the latest release (see `src/data/build.ts`).
- **glTFast** imports the `.glb` models (the shared city, the school grounds and the vehicles). It converts glTF's right-handed axes to Unity's, so the vehicle models face local −X.
- **Editor builders** generate the scenes: `AcademicPressureBuilder`, `FamilyExpectationsBuilder`, `SocialDynamicsBuilder`, and the world step `WorldModelSync` that every one of them calls before saving. See [Shared City & Traffic](#system-world).
