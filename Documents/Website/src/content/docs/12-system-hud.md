---
id: system-hud
group: Core Systems
nav: HUD, Journal & Pause
---

# HUD, Journal & Pause

Almost everything on screen is **UI Toolkit / UIDocument** now: the Quest Journal, Pause Menu, Stress HUD, the NPC conversation panel, the minigame screens, every story-episode screen and the Main Menu. Each is a `.uxml` + `.uss` pair under `Assets/UI Toolkit/` plus a controller script (see [Episode Screens (UI Toolkit)](#system-episode-ui)).

**uGUI / Canvas** remains for a few things: the Tutorial's HUD button row, the mobile controls overlay (the joystick, look stick, Interact, Journal, View and pause buttons), the loading screen, the intro and cutscene slides, and the "F to collect" prompt. Built by the `Assets/Editor` builder tools or by the scripts themselves.

| Panel | Controller | Toggle |
| --- | --- | --- |
| Quest Journal | `QuestHUDController` (singleton `Instance`) | Q / HUD journal button |
| Pause Menu | `PauseMenu` (singleton `Instance`) | Esc / HUD menu button |
| Stress HUD | `StressLevelUIController` | Always visible during an episode |
| Tasks (legacy uGUI panel) | `PlayerControls` | T / HUD tasks button |

(The old Bag panel was removed. Collected items are now just counted by `CollectiblesManager`; see [Create a Collectible](#workflow-collectible). The Tutorial scene no longer shows the Bag / Task / Menu button row either: its prompts still teach the T and Esc keys.)

All the UI Toolkit panels follow the same pattern: a `.hidden` USS class (`display: none`) toggled from C#, with elements queried once via `UIDocument.rootVisualElement.Q<T>("element-name")` in an `InitializeUI()` method. Opening Tasks, the Journal or Pause closes the others so only one full-screen panel is ever up at a time; this is coordinated through `PlayerControls`.

### Stress HUD

An always-visible card showing the stress fill and a label that follows the level: **STEADY** (under 50%), **RISING** (50 to 80%), **OVERLOAD** (80% and up) and **CRITICAL** when the player has sat at maximum, with a seconds countdown. Colours are calm green, amber and red. See [Stress System](#system-stress).

### Quest Journal

Lists every criterion of the active quest with DONE or PENDING (collectibles by name, "Talk to Mom", each minigame by its display name), the remaining time, and shows the *Episode Complete*, *Game Over* and *Stress Game Over* screens. Opening it hides the mobile controls and suppresses NPC and pickup prompts.

> [!TIP] Adding a field to a panel
>
> Edit the panel's `.uxml` and `.uss`, give the new element a `name`, then query it in the controller's `InitializeUI()` the same way existing elements are queried.
