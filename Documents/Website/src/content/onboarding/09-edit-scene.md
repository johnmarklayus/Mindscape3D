---
id: edit-scene
group: Scenes
nav: Edit a scene (no code)
---

# Edit a Scene (No Code)

Move spots, cameras, people and props of an existing episode in the Unity editor.

1. Open the scene, for example `Assets/Scenes/Chapter 3 - Episode 4.unity`.
2. In the **Hierarchy**, select the episode object (the one named after the chapter, for example *Chapter 3 - The Corner of the Room*). Its Inspector shows the story component, then two lists:
   - **Scene points**: every spot, start point and camera view the episode uses. Click **Select** next to one, then move it with the Move tool (**W**) and turn it with the Rotate tool (**E**). Gold spheres in the Scene view are spots; blue frames are camera views.
   - **Story markers**: positions the code works out (the family at the door, Joey's seat, some story cameras). The first time, click **Create missing markers at their built-in positions**. Then drag them (see [Story markers](#story-markers)). The blue arrow is the way a person faces or a camera looks.
3. To aim a camera view or a camera marker: move the Scene view until it looks right, select the view or marker, then use **GameObject › Align With View** (Ctrl/Cmd + Shift + F).
4. Move furniture, props and NPCs the usual way. New NPCs come from **Mindscape › NPCs**; doors from the door tools ([Create an Interactable Door](/#workflow-door)).
5. **Save the scene** (Ctrl/Cmd + S) and press **Play** to test.
