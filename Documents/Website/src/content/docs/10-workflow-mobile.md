---
id: workflow-mobile
group: Workflows
nav: Mobile Controls
---

# Mobile Controls

**Mobile mode** is `MobileControls.Enabled`: on by default on phones and tablets (including mobile browsers running the web build), and switched on or off by **Options ▸ General ▸ Mobile controls** (`PlayerPrefs["Mindscape.MobileControls"]`). Switch it on to test the touch layout on desktop.

## What it adds

- **Move stick** (bottom left) streams a Vector2 into `MobileInput.SetMoveAxis` while dragging.
- **Look stick** (bottom right) turns the camera at a steady rate (`MobileInput.LookAxis`, `PlayerMovement.touchLookSpeed`). A finger dragged on open screen orbits the camera too; touches that start on a stick or a button belong to that control.
- **Interact (E)** calls `MobileInput.TriggerInteract`, the same signal the F and E keys produce. **Journal** opens the Quest Journal and hides when the scene has no `QuestHUDController`.
- **VIEW** (above the look stick) switches between third and first person. It is the phone's version of scrolling in and out; see [Camera & Story Shots](#system-camera). The choice is saved, and **Options ▸ General ▸ First-person view** sets it from the menu.
- **Pause** (top right) calls whichever `IPausable` the scene has (an episode, or the Tutorial's pause menu), and hides while the game is paused.

## Where the overlay comes from

Only the Tutorial and the original Chapter 2 Episode 1 carry a hand-placed overlay (`Tools ▸ Build Mobile Controls`). In every other scene with a `PlayerMovement`, `MobileControls` builds the same themed overlay at runtime when the scene loads. It also adds the look stick, the VIEW button and the pause button to the hand-placed overlays, so they all match.

- Other UI follows mobile mode: the main menu is drawn **1.6x larger** (a cloned Panel Settings at 800x450 plus a `.mobile` root class, with `.mobile` rules at the end of `MainMenuNew.uss`), the loading screen is bigger, and the flashback badge and episode HUD get `.mobile` classes.
- `PlayerMovement`, `DoorInteraction`, `CollectiblesManager` and `NPCInteractionManager` all OR `MobileInput` in alongside WASD, E and F, so nothing needs a separate "mobile" branch. In mobile mode `PlayerMovement` ignores the pointer-delta Look action, because a finger on a stick would otherwise also swing the camera.
- New pause menus should implement `IPausable`. New menu pages must fit about 890x400 logical pixels in mobile mode.

> [!TIP] Force it on for testing
>
> The `MobileControls` component has a **Force Enable On Desktop** checkbox that shows the overlay even if the Settings checkbox is off.

> [!WARN] If you add another Canvas to a scene
>
> Any tool that looks up "the Canvas in the scene" needs to target `HUDCanvas` by name once more than one `Canvas` exists (mobile controls, the conversation UI and minigames all add one). See [Conventions & Gotchas](#ref-conventions).
