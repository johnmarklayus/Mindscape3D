---
id: workflow-scene
group: Workflows
nav: Create a Gameplay Scene
---

# Create a Gameplay Scene

There's no single "New Episode" wizard: a gameplay scene is assembled from the same handful of pieces every time. The fastest reliable path is duplicating an existing episode scene and stripping it down; the checklist below is what that scene needs to contain either way.

For the story script, chapter registry, progression, menu row, loading metadata, thumbnail, save keys and build-profile work that turns this scene into a campaign episode, follow [Create an Episode or Chapter](#workflow-episode-chapter).

1. **Duplicate a template scene.** Copy `Assets/Scenes/Tutorial.unity` (simplest) or `Chapter 1 - Episode 1.unity` and rename it following the `Chapter <N> - Episode <N>` convention.
2. **Confirm the Player exists.** Drag in `Assets/Prefabs/Player.prefab` if it isn't already present. It carries `CharacterController`, `PlayerControls`, `PlayerInputBindings` and `PlayerMovement` together; don't split these across objects, they fetch each other via `GetComponent`.
3. **Set up the UI Toolkit panels.** Run each of these once per scene from the **Tools** menu (they create their `UIDocument` GameObject and are safe to re-run):

   - `Tools ▸ Setup UI Toolkit Quest HUD` (also runs automatically the first time you add a [Quest](#workflow-quest))
   - `Tools ▸ Setup UI Toolkit Pause Menu`
   - The Stress HUD is a `UI_Toolkit_StressHUD` object with `StressLevelUIController`; copy it from the Episode 1 scene.
4. **Build the HUD chrome.** Run `Tools ▸ Build HUD Panels` then `Tools ▸ Build HUD Buttons` to create `HUDCanvas` with the Tasks panel and the Tasks and Menu buttons, wired onto the Player's `PlayerControls`.
5. **Add an EventSystem** if Unity didn't already add one (needed for uGUI button clicks: `GameObject ▸ UI ▸ Event System`).
6. **Add gameplay content** using the workflows below: [NPCs](#workflow-npc) (and [wandering](#workflow-npc-wander)), [a Quest](#workflow-quest), [Collectibles](#workflow-collectible), [minigames](#system-minigames) and any [interactable doors](#workflow-door).
7. **Light it.** Episode 1 uses flat, shadowless lighting; see [Lighting & Rendering](#system-lighting).
8. **(Optional) Add mobile controls**: see [Mobile Controls](#workflow-mobile).
9. **Add a cutscene and loading art** for the episode: see [Create a Cutscene](#workflow-cutscene).
10. **Register the scene in Build Settings** (`File ▸ Build Profiles`) so `SceneManager.LoadScene("your scene name")` calls from the Main Menu, a cutscene or a completed Quest can find it.

> [!WARN] Watch out for
>
> Editor tools that locate the HUD canvas by name (`GameObject.Find("HUDCanvas")`) rather than "the first Canvas in the scene". This matters as soon as a scene has more than one `Canvas` (the conversation UI, minigames and mobile controls each add their own). Keep the HUD canvas named exactly `HUDCanvas`. See [Conventions & Gotchas](#ref-conventions) for canvas sort orders.
