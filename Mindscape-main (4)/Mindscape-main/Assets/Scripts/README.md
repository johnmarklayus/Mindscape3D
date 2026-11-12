# Scripts: where to find what

Every runtime script in the game is in this folder, grouped by what it does. Editor-only tools (menus, scene builders, checks) are in `Assets/Editor/` instead (see the README there).

| If you are asked to change... | Look in |
|---|---|
| The player camera (orbit, zoom, mouse/touch look, first person, the camera bumping into walls) | `Camera/PlayerMovement.Camera.cs`. Its settings are the **Camera** and **Zoom** fields on the player's *PlayerMovement* component. |
| Hiding the player when they block a story shot or a conversation | `Camera/ShotFocus.cs` |
| Walking, running, gravity, getting unstuck | `Player/PlayerMovement.cs` |
| Boy or girl model, outfits, the school bag | `Player/PlayerAppearance.cs`, `Player/PlayerOutfit.cs`, `Player/PlayerBackpack.cs` |
| Keys, gamepad, on-screen touch controls | `Input/` (`KeyBindings.cs` holds the default keys) |
| The [E] prompt, the blue outline, doors, the bed, collectibles | `Interaction/` |
| An NPC's name, dialogue tree, or walking route | `NPC/` |
| How NPC conversations run (talk prompt, conversation panel, conversation camera) | `Dialogue/NPCInteractionManager.cs` |
| What a character says in a story episode | That episode's script in `Chapters/` (the lines are written there) |
| How story dialogue, choices, cards, shots and free roaming work | `Story/AcademicEpisode.cs` (the base every episode uses) |
| A specific chapter or episode | `Chapters/Chapter N - .../` (one script per episode) |
| Scene pieces several episodes share (bedroom decor, mirrors, the bus home, the family welcome) | `Scene/` |
| Quests, objectives, the tutorial | `Quests/` |
| Breathing, Worry Courtroom and the other minigames | `Minigames/` |
| Main menu, pause menu, loading screen, credits, HUD | `UI/` (layouts and styles are the `.uxml` / `.uss` files in `Assets/UI Toolkit/`) |
| Music and sound effects | `Audio/` |
| Intro video and cutscene slides | `Cutscene/` |
| City traffic and buses | `Vehicles/` |
| Saves, progress, accounts and cloud sync | `Data/` |
| Graphics settings and other app-wide pieces | `Core/` |

Notes

- `Chapters/Prototypes/` holds the first versions of Chapter 2. They are used only by the scenes in `Assets/Scenes/Prototypes` and the old cutscene scene, not by the game itself.
- Moving or renaming a script file in Unity is safe as long as its `.meta` file moves with it, because scenes and prefabs find scripts by the GUID in the `.meta` file. Always move scripts inside the Unity Project window, which moves the `.meta` too.
- A script that holds a component must keep the same file name as its class (for example `PlayerMovement.cs` for `PlayerMovement`).
