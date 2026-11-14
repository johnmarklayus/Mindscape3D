---
id: cutscenes-overview
group: Cutscenes & Cinematics
nav: Cutscene or cinematic?
---

# Cutscene or Cinematic?

There are two ways to tell part of the story without the player walking around. Both are made in the Unity editor and edited in the Inspector; neither needs code.

| | **Cutscene** | **Cinematic** |
|---|---|---|
| What the player sees | Full-screen **pictures** with words, one after another, like a picture book | The **3D scene** itself: the camera moves, people talk, walk and turn, things appear |
| Made with | **Mindscape › Story › New Cutscene…** | **Mindscape › Story › New Cinematic (in the open scene)** |
| Lives in | An asset in `Assets/Story/Cutscenes/` | An object inside the episode's scene |
| Good for | Memories, time passing, dreams, the start of a chapter, places you have no 3D model of | Conversations, someone arriving, a camera showing a place, a moment at an object |
| When it plays | Before an episode (set in the chapter asset), from a cinematic step, or as a scene of its own | At the start of the episode, when the player walks to a place, or presses **E** at a place |

They work together: a cinematic can play a cutscene as one of its steps.

## The order at the start of an episode

1. The loading screen.
2. The chapter asset's **Cutscene Before** for this episode, if any (Chapter 4 and later).
3. Every cinematic set to **At the start of the episode**, top to bottom in the Hierarchy.
4. The episode's own story script.

Cinematics set to play **at a place** wait the whole episode for the player to get there.

Next: [Create a cutscene](#create-cutscene) · [Create a cinematic](#create-cinematic) · [Edit a cinematic](#edit-cinematic) · [Every cinematic step](#cinematic-steps)
