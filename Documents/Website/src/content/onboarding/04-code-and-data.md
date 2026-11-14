---
id: code-and-data
group: Getting Started
nav: What is code and what is data
---

# What Is Code and What Is Data

What you change in the Unity editor, and what is still written in C#.

The **scenes** are edited in Unity: where everything is, who stands where, where the story camera goes. The **order of events and the words** are still written in C#. (Moving the dialogue into Inspector assets is the next step of the project.)

| Content | Where it lives | How to change it |
|---|---|---|
| Episode story: order, dialogue, choices, objectives, camera shots, minigames | One C# script per episode in `Scripts/Chapters/` | Edit the text inside `"..."` in the script |
| Chapter 4 and later: name, picture, episodes, locations, briefings, journal question | The **chapter asset** in `Assets/Resources/Chapters/` | Inspector ([Create a chapter](#create-chapter)) |
| Chapters 1–3: titles, descriptions, journal prompts | The chapter's `…Chapter.cs` | Code |
| Scene setup: spots, cameras, NPC positions, props | The episode's `.unity` scene | Scene view and Inspector (see [Edit a scene](#edit-scene)) |
| Positions the code works out (family at the door, Joey's seat, some story cameras) | **Story Markers** in the scene | Drag the marker in the Scene view |
| Player movement and camera (speed, zoom, sensitivity, crosshair) | **Player Settings** assets in `Assets/Settings/Player/` | Inspector |
| NPC small talk ([E] Talk in the street) | The *NPC* component's **Dialogue Nodes** list | Inspector |
| Cutscenes (pictures with words) | **Cutscene assets** in `Assets/Story/Cutscenes/` | Inspector ([Create a cutscene](#create-cutscene)) |
| Cinematics (camera, dialogue, people moving in the scene) | **Cinematic** objects in the episode scene | Inspector ([Create a cinematic](#create-cinematic)) |
| Worry Courtroom cases | `WorryCourtroomCase` ScriptableObject assets | Inspector |
| Music for each scene | The `SceneMusicMap` asset | Inspector |
| How each screen looks | `.uxml` / `.uss` files | UI Builder |
| World layout, furniture, the house | Scene view, or Blender then export | Editor / Blender |

A dialogue line in an episode script looks like this. `Me` is Joey, any other name is the speaker, and a line without `|` is Joey's inner thought:

```csharp
yield return Lines("Justin|Hey! You made it!", "Me|I'm okay. How about you?", "I almost turned around at the door.");
```
