---
id: system-player
group: Core Systems
nav: Player & Input
---

# Player & Input

Player behaviour is split across three components living together on one GameObject (usually `Assets/Prefabs/Player.prefab`).

| Script | Owns |
| --- | --- |
| `PlayerInputBindings` | Resolves and exposes actions from the shared `GameControls` input actions asset (Move, Run, FreeLook, ZoomIn, ZoomOut, OpenTasks, OpenQuest). Everything else reads from here rather than touching the Input System directly. |
| `PlayerMovement` | Character movement, the orbit camera (collision, zoom, first person), touch look, cursor lock, a stuck-in-geometry safety net, and the crosshair. Freezes while any overlay is open. See [Camera & Story Shots](#system-camera). |
| `PlayerControls` | The "is something open" flags, the HUD button wiring, and the stress meter. `[DefaultExecutionOrder(-1)]` so its state is current before `PlayerMovement` reads it the same frame. |

`PlayerControls.IsOverlayOpen()` is the single source of truth that gameplay systems check before allowing movement, camera look or the cursor to lock. It is true whenever Tasks, Pause, a conversation, the Quest Journal or a **minigame** is open (`tasksOpen`, `pauseOpen`, `dialogueOpen`, `questOpen`, `minigameOpen`). A new overlay only has to set its own flag.

### Movement notes

- Walking and falling go through **one** `CharacterController.Move` per frame, so the player slides along walls and kerbs instead of stopping dead. The controller's skin width (at least 0.08) and step offset (at least 0.5) are raised at start-up so old scenes do not snag on corners or kerbs.
- If walking is asked for but the player has not moved for about a second, `CheckStuck` nudges them out along the surface they were pressing into and logs `Player snagged on '<collider>'`, so a snagged corner never holds them for good.
- The crosshair is a small UI Toolkit dot (`Crosshair.uxml`); `showCrosshair`, `crosshairSize` and `crosshairColor` still style it.

### Steve's animation setup

`Tools ▸ Steve ▸ Set Up Walk and Run` builds an Animator Controller with Idle, Walk and Run states and connects it to player objects. The editor startup check only runs setup or validation when `Assets/1_Steve.fbx` exists. `Tools ▸ Steve ▸ Validate Animation Playback` also checks for that model first and logs a warning if it is missing, instead of attempting to instantiate it. Stop Play Mode before running either tool.

### Keys

| Key | Action |
| --- | --- |
| W A S D | Move |
| Shift | Run |
| Mouse, trackpad or arrow keys | Turn the camera |
| Scroll wheel or two-finger swipe | Zoom, and switch between third and first person |
| E or F | Open doors, talk, collect |
| T | Tasks panel |
| Q | Quest Journal |
| Esc | Pause menu |

### Key bindings

All bindings live in one `GameControls.inputactions` asset under a `Resources` folder, loaded lazily by the static `KeyBindings` class. The rebinding UI in the Main Menu calls `KeyBindings.SaveOverrides()` and `ResetToDefaults()`, persisted through `PlayerPrefs`.
