---
id: system-camera
group: Core Systems
nav: Camera & Story Shots
---

# Camera & Story Shots

Two cameras share one `Camera.main`: the **follow camera** that `PlayerMovement` drives while you walk, and the **story shots** that an episode or a conversation moves the same camera to. `ShotFocus` keeps your own body from getting in the way of either.

## The follow camera

`PlayerMovement` orbits the camera freely around the player (a full 360 degrees; the character turns to face the way it walks).

- **Look:** mouse or trackpad movement, the arrow keys, a gamepad stick, or on mobile the right-hand look stick and a finger dragged on open screen. A two-finger swipe left or right turns it too.
- **Zoom:** scroll wheel or a two-finger swipe up and down, or the ZoomIn / ZoomOut keys. The distance stays between *Min Distance* and *Max Distance*.
- **Collision:** a sphere cast from the player to the wanted camera position pulls the camera in front of any wall in the way.
- **Reset:** a cinematic that repositions the player (a door, a teleport) calls `ResetView(yaw)` so the camera cuts to its place behind them instead of easing across the room.

### First person

Scroll in past the closest third-person distance and the camera glides to the player's **eyes**; scroll out to return. The same switch is available without a scroll wheel:

| Way to switch | Where |
| --- | --- |
| Scroll wheel or two-finger swipe | In play |
| **VIEW** button above the look stick | The mobile controls overlay |
| **First-person view** toggle | Options > General, beside *Mobile controls* |

All three write the same saved choice (`PlayerPrefs["Mindscape.FirstPerson"]`), so the next scene starts in the view you last used. A scene can switch the feature off with **Allow First Person** on `PlayerMovement`.

- **Eye height** is measured from the character model (a little below the top of the head), so it follows the player's scale. **First Person Eye Height** overrides it. It is separate from *Camera Target Height*, which sits above the head so the shoulder view clears it.
- In first person you can look right up at the sky, the body turns with the view, and the camera is at the eyes, so your own body and anything you carry (the plate in Chapter 1 Episode 1) are hidden from it.

## Story shots

Story code never moves the camera directly. It goes through `AcademicEpisode.Shot`, `ShotOver` and `Glide`, which do three things: they pass the position through `ShotFocus.ClearOfBody`, shorten the near clip plane so close-ups do not slice through furniture, and tell `ShotFocus` what the shot is looking at (`ShotFocus.Set`). `ShotOver(target, back, up)` is the usual examine shot: it frames a target from roughly where the player stands, backing off toward them.

## ShotFocus: stepping out of the shot

Your character is hidden (its renderers switch to *shadows only*, so the shadow stays) whenever it would block the view:

- **A story shot or NPC conversation is up:** the body is hidden when the line from the camera to the subject passes through it, or the camera is inside it. A shot of the player themselves (the target is on their body, as in a mirror) is left alone. An item *beside* the player is not a shot of the player, so the body still steps aside.
- **First person:** the body stays hidden while you walk, while you are locked for a line of dialogue with no shot up (the camera is still inside the head), and during any story shot taken from near you, so you never see yourself or what you carry in your own view.
- **Third person with no shot:** nothing is hidden.

`ShotFocus.ClearOfBody` also pushes a story camera sideways out of the player's head when a shot backs off toward them. New story camera code should go through `Shot` / `ShotOver` / `Glide` (or call `ShotFocus.Set`); moving the story camera directly reports no focus, so the body will not step aside.

> [!MENU] Mindscape ▸ Verify ▸ Story Shot Clearance
>
> Walks the player around every shot target at every distance an interaction allows, for every `(back, up)` pair the episodes use, and fails if a shot ends up inside the body's clearance. Run it after adding a new `ShotOver` pair.

> [!TIP] Examine close-ups show the item
>
> The thing a shot frames must still be on screen when the shot is up: hide a collected item *after* its thought, not before (the Chapter 2 Episode 2 Student ID close-up used to frame an empty spot).
