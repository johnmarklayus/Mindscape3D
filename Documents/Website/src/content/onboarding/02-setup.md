---
id: setup
group: Getting Started
nav: Set up your computer
---

# Set Up Your Computer

The software to install, how to open the project, and the Unity packages it uses.

## Software

| Tool | Version | Used for |
|---|---|---|
| Unity Hub + **Unity 6000.5.8f1** | exactly this version | The game |
| Unity modules | Web Build Support, Android Build Support (with OpenJDK, SDK & NDK), Windows Build Support (Mono), Mac Build Support | Building each platform |
| Blender | 4.x | Models, characters, animation |
| Node.js | 20.9 or newer | This documentation site and the official website |
| Git | any recent version | Version control |
| Vercel CLI | `npm i -g vercel` | Publishing the websites and the web build |
| Supabase CLI | optional | Rebuilding the online backend |
| Code editor | VS Code with the Unity extension, or Rider | Editing C# |

On a Mac you can build all four platforms. Windows builds use the **Mono** backend, because IL2CPP cannot cross-compile from a Mac.

## Get the project and open it

```bash
git clone <repository-url> mindscape-3d
cd mindscape-3d
```

1. In Unity Hub choose **Add › Add project from disk** and select the `mindscape-3d` folder.
2. The first time the project opens, Unity spends several minutes rebuilding `Library/`.
3. Open `Assets/Scenes/Intro.unity` and press **Play**. You see what a player sees: the intro video, the title, then the main menu.
4. To test a single episode, open its scene (for example `Assets/Scenes/Chapter 2 - Episode 1.unity`) and press Play.

## Main Unity packages

| Package | What it does here |
|---|---|
| Universal Render Pipeline 17.5 | Rendering, with PC and Mobile render assets in `Assets/Settings/` |
| Input System 1.20 | Keyboard, mouse, gamepad and the on-screen touch controls (`Resources/GameControls.inputactions`) |
| UI Toolkit | Every screen: a `.uxml` layout with a `.uss` style in `Assets/UI Toolkit/` |
| AI Navigation | NPC walking |
| TextMesh Pro, uGUI | Still used in a few places |

More: [Beginner Start Here](/#beginner-guide) · [Tech Stack](/#tech-stack) · [Project Structure](/#structure)
