---
id: workflow-door
group: Workflows
nav: Create an Interactable Door
---

# Create an Interactable Door

Doors are real, animated doors: **E** swings the door open (away from the player), **E** again swings it shut. The swing is the door model's own hinge and handle clips from Blender (`Assets/Models/Doors`), baked into the prefab. The leaf's collider moves with it, so an open door is a free doorway and a closed one blocks it.

1. **Rebuild the door prefabs** after changing the door model: `Mindscape ▸ Doors ▸ Rebuild Door Prefabs` (writes `Assets/Prefabs/Doors`).
2. **Place doors in a scene:** open it and run `Mindscape ▸ Doors ▸ Apply Doors to Open Scene`, or `Apply Doors to All Story Scenes`. Each doorway's old static panel is switched off (renamed `<name> (old panel)`) and a door sized to the opening takes its place. A doorway the story walks through gets a door that starts open.
3. **Tweak one door:** select it and change the `DoorInteraction` fields in the Inspector. Safe to re-run step 2; it reuses the doors already placed.

The player uses it with E or the on-screen Interact button. A `[ E ]  Use Door` prompt (the shared `InteractPrompt` UI
Toolkit screen) shows while a door is in reach; with two doors in reach only the nearer answers. The player cannot use
a door during a conversation, a menu or a story shot.
