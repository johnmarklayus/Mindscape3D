---
id: ref-scripts
group: Reference
nav: Script Index
---

# Script Index

Every gameplay script and its role. The annotated ones also have a full line-by-line walkthrough on the [Scripts](#scripts) page.

| Script | Role |
| --- | --- |
| `PlayerControls.cs` | Overlay state, HUD buttons, stress and the critical-stress countdown. |
| `PlayerInputBindings.cs` | Resolves Input Actions once per player. |
| `PlayerMovement.cs` | Movement, orbit and first-person camera, touch look, cursor, stuck safety net, crosshair. |
| `ShotFocus.cs` | Hides the player's body (and what they carry) when it blocks a story shot, a conversation or the first-person view. |
| `KeyBindings.cs` | Static access to the shared Input Actions asset and rebind persistence. |
| `MobileInput.cs / MobileControls.cs / MobileJoystick.cs` | Touch sticks and the Interact, Journal, View and pause buttons, bridged into the same input paths as the keyboard; `MobileControls` also builds the overlay at runtime. |
| `StressLevelUIController.cs` | The always-visible Stress HUD (UI Toolkit). |
| `Scripts/Quests/Quest.cs` | Win/lose criteria, minigame triggers and the episode timer. |
| `Scripts/Quests/QuestHUDController.cs` | Quest Journal panel and the completion and game-over screens. |
| `Scripts/NPC/NPC.cs` | Per-NPC data: name, dialogue tree, camera framing. |
| `Scripts/Dialogue/NPCInteractionManager.cs` | Finds the nearby NPC, drives the conversation panel (UI Toolkit) and blends the conversation camera. |
| `Scripts/NPC/NPCWander.cs` | Walks an NPC between waypoints; waits for the player. |
| `Scripts/NPC/NPCNameTag.cs` | Floating name plate that faces the camera. |
| `Scripts/Interaction/CollectibleItem.cs` | Per-item data and pickup. |
| `Scripts/Interaction/CollectiblesManager.cs` | Nearby-item prompt, per-item counts for quests. |
| `Scripts/Minigames/QuestMinigame.cs` | Base class for anything the Quest can open. |
| `Scripts/Minigames/BreathingMinigame.cs` | The guided breathing exercise. |
| `Scripts/Minigames/WorryCourtroom/WorryCourtroomMinigame.cs` | The Worry Courtroom. |
| `Scripts/Minigames/WorryCourtroom/WorryCourtroomCase.cs` | One trial's data (ScriptableObject). |
| `Scripts/Minigames/WorryCourtroom/WorryCourtroomSettings.cs` | The courtroom's rules, texts and colors groups. |
| `Scripts/Minigames/Testing/MinigameUI.cs` | Shared minigame helpers, theme colours and fonts. |
| `DoorInteraction.cs` | Standalone interactable door: fades out, moves the player through the doorway, fades back in. |
| `PauseMenu.cs` | Pause panel, settings sliders, Main Menu exit. |
| `MainMenuController.cs / MainMenuNewController.cs` | Main Menu UI Toolkit flow (chapter and episode select, journal, options, resources). |
| `EpisodeLoadingScreen.cs` | Location artwork and the quest briefing while an episode loads. |
| `MusicManager.cs / SceneMusicMap.cs / SFXManager.cs` | Self-bootstrapping persistent audio singletons; the music crossfades between per-scene tracks. |
| `Scripts/Data/MindscapeDatabase.cs / MindscapeProgress.cs / MindscapeCloud.cs` | SQLite and PlayerPrefs saves, episode unlock rules, and the Supabase account and cloud sync. See [Accounts, Progress & Saves](#system-accounts). |
| `Scripts/Story/EpisodeUI.cs` | Loads `Resources/EpisodeUI` and spawns the UI Toolkit screens. See [Episode Screens (UI Toolkit)](#system-episode-ui). |
| `CutscenePlayer.cs + Cutscene*.cs` | Slide-based cutscene playback. |
| `TutorialManager.cs` | Step-by-step onboarding (move, Tasks, pause) in the Tutorial scene. |
| `Scripts/Story/AcademicEpisode.cs` | The story base every episode of every chapter runs on: cards, dialogue, choices, spots, the free-play countdown, stress and check-ins. |
| `AcademicPressure/*Episode.cs`, `FamilyExpectations/*.cs`, `FamilyFinale/*.cs`, `SocialDynamics/*.cs` | One script per episode (or per group of episodes) holding that episode's story coroutine. |
| `Scripts/Chapters/Chapter 1 - Academic Pressure/DormitoryEpisode.cs` | Chapter 1 Episode 4: the walk from the cafeteria, the roommates, and plan A (all four tasks, breathing when exhausted) or plan B (one task). |
| `Scripts/Scene/BusRide.cs` | Borrows a school bus from the city traffic and drives it along the lane past the bus shelter (Chapter 2 Episode 1's ride home). |
| `Scripts/Scene/HomeWelcome.cs` | The family greeting inside the front door: places Mom, Dad and Tim, plays their Talk and Walk clips, and finds a camera spot inside the house. |
| `Scripts/Chapters/Chapter 3 - Social Dynamics/SocialDynamicsEnding.cs` | Chapter 3 Episodes 6 to 8: the group photo, the walk home, falling asleep, the dream and the mirror ending; also the reunion names. |
| `Scripts/Chapters/Chapter 3 - Social Dynamics/SocialStaging.cs` | Builds at runtime: memory frames, the dream space, photo capture, the pencil-sketch filter and the kept group photo. |
| `Scripts/Scene/SocialMirror.cs` + `Resources/Shaders/MirrorBlend.shader` | The live mirror; for the ending, a second reflection that also sees the younger self, cross-faded by the shader. |
| `Scripts/Vehicles/CityTrafficVehicle.cs` | Drives a vehicle round a road loop for ever and loops its wheel and body clips. See [Shared City & Traffic](#system-world). |
| `Editor/WorldModelSync.cs` | Fits the shared city to a scene, opens the world, and puts street NPCs on the sidewalk. |
| `Editor/CityTrafficBuilder.cs` | Builds the vehicle prefabs and places the 18 vehicles on block loops. |
| `Editor/AmbientLifeBuilder.cs` | Adds walkers, joggers and the family to every story scene. |
| `Editor/StreetLifeBuilder.cs` | The Chapter 1 street NPCs, their sidewalk routes and their dialogue. |
