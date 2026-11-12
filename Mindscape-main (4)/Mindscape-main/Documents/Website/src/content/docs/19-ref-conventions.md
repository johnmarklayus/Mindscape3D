---
id: ref-conventions
group: Reference
nav: Conventions & Gotchas
---

# Conventions & Gotchas

### Singletons

`QuestHUDController`, `PauseMenu`, `MusicManager` and `SFXManager` follow the same pattern: a static `Instance` set in `Awake()`, with any duplicate destroying itself. Always null-check `.Instance` before use. It can legitimately be null in scenes that don't include that panel (for example cutscene scenes have no Quest Journal).

### "Find the Canvas" lookups

> [!WARN] Only ever one Canvas assumption
>
> Several Editor tools and `TutorialManager`'s runtime-created "Play Game" button used to call `FindAnyObjectByType<Canvas>()`, which is non-deterministic once a scene has more than one `Canvas`. They look up `GameObject.Find("HUDCanvas")` first. Keep that name if you touch this again, or update every caller together. `CollectiblesManager` still falls back to the first Canvas it finds.

### Canvas sort orders

The story screens are UI Toolkit documents on one shared Panel Settings (`EpisodePanelSettings`, 1280x720), ordered by each document's `sortingOrder`:

| UIDocument | Order |
| --- | --- |
| Overlays (exam paper, journal, laptop list) | -3 |
| Screen fade | -2 |
| Flashback frame | -1 |
| Objective, status, phone chat, photograph, NPC talk prompt | 0 |
| Dialogue bar, NPC conversation panel | 1 |
| Choices, text entry | 2 |
| Story card | 3 |
| Episode complete / out of time | 4 |
| Pause menu | 5 |
| Minigames (Breathing, Worry Courtroom) | 10 |

The few screens that are still uGUI canvases (the mobile controls overlay at 50, the pause button at 230, the loading screen, the intro) sit on their own canvas sort orders. Give a new full-screen overlay an order that places it where it belongs.

### Overlays set a flag

Anything full-screen should set its flag on `PlayerControls` (`tasksOpen`, `pauseOpen`, `dialogueOpen`, `questOpen`, `minigameOpen`) and clear it on close. `IsOverlayOpen()` is what freezes movement, so a screen that forgets its flag lets the player walk around behind it.

### Toggling UI Toolkit panels: prefer SetVisible(false) over Toggle*()

When code needs to force a panel closed (rather than respond to user input), call the explicit `SetVisible(false)` or `Close()` method rather than a `Toggle*()` method. A toggle assumes it knows the current state; if that assumption is wrong for even one frame, it flips the wrong way.

### Interact key vs. on-screen Interact button

`DoorInteraction`, `CollectiblesManager` and `NPCInteractionManager` each OR their own keyboard check (E or F) with `MobileInput.InteractPressed`. If you add a new interactable, follow the same pattern instead of inventing a separate mobile path.

### Stress is clamped and only moves on purpose

Stress does not climb by itself. `ChangeStress()` clamps it to `[0, stressMax]`, and sitting at the maximum for `criticalStressDuration` seconds ends the run. If you add something that moves stress, route it through `ChangeStress()` so the HUD and the critical countdown stay correct. See [Stress System](#system-stress).

### Builders are re-runnable, but not all are safe

The `Mindscape ▸ Episode 1` tools rebuild their own content (NPCs, waypoints, cutscene slides, minigame setup) and are safe to re-run, but they **replace** what they own, so hand-edits to those objects are lost. `Mindscape ▸ Worry Courtroom ▸ Rebuild Scene From Scratch` also regenerates the shared prefab. Edit the prefab or scene directly for one-off changes.

### Write for a bad day

All player-facing text follows the [Writing Guidelines](#story-tone): neutral, plain, never alarming or falsely reassuring.
