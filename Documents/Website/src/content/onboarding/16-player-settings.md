---
id: player-settings
group: Player & Camera
nav: Player and camera settings
---

# Player and Camera Settings

Movement, camera, zoom and crosshair values live in **Player Settings** assets in `Assets/Settings/Player/`, one per kind of place (the cast and rooms are scaled differently):

| Asset | Used by |
|---|---|
| Player Settings - House | Ch1 Ep1, Ch2 Ep1, Ep2, Ep4, Ep5, Tutorial |
| Player Settings - School | Ch1 Ep2–4, Ch2 Ep3 |
| Player Settings - House at Night | Ch3 Ep1, Ep7, Ep8 |
| Player Settings - Reunion Hall | Ch3 Ep2–6 |
| Player Settings - Default | `Player.prefab` (new scenes made from it) |

- **Change the feel everywhere a place is used:** select the asset in the Project window and edit it, for example *Max Distance* for how far the camera zooms out, or *Mouse Sensitivity*.
- **One scene only:** make a copy of the asset (Ctrl/Cmd + D), edit the copy, and drag it into the **Settings** field of that scene's Player (*PlayerMovement* component).
- On the Player itself, the values that come from the asset are greyed out. Clear the **Settings** field to use the Player's own values again.
- A few episodes still change a value for a moment while they play (for example, no running in the Chapter 3 mirror dream).

More: [Create an Episode or Chapter](/#workflow-episode-chapter) · [Create a Gameplay Scene](/#workflow-scene) · [Camera & Story Shots](/#system-camera) · [Editor Menu Items](/#ref-menu-items)
