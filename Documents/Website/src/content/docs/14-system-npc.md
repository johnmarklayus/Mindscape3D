---
id: system-npc
group: Core Systems
nav: NPC Dialogue
---

# NPC Dialogue

`NPCInteractionManager` is the single per-scene manager that decides which NPC is "nearby" and owns the dialogue UI; individual `NPC` components are just data (name, dialogue tree, camera framing).

- Dialogue nodes and choices are authored entirely in the Inspector (see [Create an NPC](#workflow-npc)); there is no external dialogue file format.
- `NPCInteractionManager.DialogueActive` and `HasNearbyNPC` are static flags other systems check to suppress their own prompts while a conversation is happening (for example `CollectiblesManager` hides its "F to collect" prompt, and `NPCWander` stops walking).
- Nearby-NPC detection is suspended while the Quest Journal **or a minigame** is open.
- When a conversation starts, the NPC turns to face the player and the camera blends to a close-up in front of the NPC's face; when it ends both return to where they were.
- Choices that change stress show a "(+n stress)" suffix on the button. Episode 1 uses 0 everywhere, so no suffix appears. See the [Writing Guidelines](#story-tone).

### The conversation UI

Built in code in `CreateUI()` and styled to match the pause menu: a parchment panel inside a dark frame with a brass edge, running the full width of the screen along the bottom. The speaker's name is in the serif heading font with a thin rule beneath it, the line is in Comic Neue, and choices are brown buttons with cream text that stack up from the bottom. The "F to talk" prompt is a dark plate with a brass edge. See [UI Theme](#system-theme) for the palette.
