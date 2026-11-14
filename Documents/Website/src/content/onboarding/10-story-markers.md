---
id: story-markers
group: Scenes
nav: Story markers
---

# Story Markers

Some positions are worked out by the code while the episode plays: where the family waits at the door, where Joey sits, some story camera shots. A **Story Marker** in the scene takes such a position over, so you can move it by dragging instead of editing code.

## How to use them

1. Select the episode object. In its Inspector, the **Story markers** list shows every marker id the episode reads, and whether the scene has it (*in scene*) or uses the built-in position (*built-in*).
2. Click **Create missing markers at their built-in positions**. The markers appear under *Story Markers* inside the episode object, exactly where the code would put things.
3. Drag a marker. Its position is the spot (for a seat: the top of the cushion) and its blue arrow is the way a person faces or a camera looks. Orange figures are people, green boxes are seats, blue frames are cameras.
4. Save the scene and press Play.

For every episode scene at once: **Mindscape › Story › Create Missing Story Markers (All Episode Scenes)**.

> [!TIP] Going back to the built-in position
>
> Delete a Story Marker and the episode uses its built-in position again. Disabling the marker's GameObject does the same.

## Markers in the game now

| Scene | Marker ids |
|---|---|
| Chapter 2 - Episode 1 | `Family/Mom`, `Family/Tim` (waiting inside the front door) |
| Chapter 3 - Episode 4 | `Corner/Seat` (top of the sofa cushion), `Corner/Seat camera`, `Corner/Thinking camera`, `Corner/Phone camera` |
| Chapter 3 - Episode 7 | `Family/Mom`, `Family/Dad`, `Family/Tim` (inside the front door), `Welcome/Mom step`, `Welcome/Tim step` (where they step to when Joey comes in) |
