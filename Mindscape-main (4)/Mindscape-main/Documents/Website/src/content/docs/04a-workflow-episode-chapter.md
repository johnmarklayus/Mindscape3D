---
id: workflow-episode-chapter
group: Workflows
nav: Create an Episode or Chapter
---

# Create an Episode or Chapter

There is no one-click episode wizard. A complete episode is a Unity scene, an `AcademicEpisode` story component, menu/loading metadata, progression data, a thumbnail and a build-profile entry. A complete chapter adds another registry and extends several places that currently know the game has exactly three chapters.

Use [Create a Gameplay Scene](#workflow-scene) for the objects every playable scene needs. This page covers everything that makes that scene part of the story campaign.

## Before implementation: write the episode card

Decide these values first so filenames, save keys and UI stay consistent:

| Field | Example |
| --- | --- |
| Chapter number and theme | `4 · New Beginnings` |
| Episode number and title | `1 · First Steps` |
| Scene name | `Chapter 4 - Episode 1` |
| Location label | `COMMUNITY CENTRE` |
| Three-line loading briefing | What the player will do, in order |
| Starting location and camera | Spawn, facing and first shot |
| Story beats | Dialogue, choices, exploration, minigames, completion |
| Saved choices | Stable keys and which later episodes read them |
| Reflection prompt | Use the default, or state the episode-specific prompt |
| Time limit | Free-roam seconds; dialogue and minigames pause the timer |
| Next destination | Next episode, next chapter, main menu or finale |

Keep the [Writing Guidelines](#story-tone): choices are ways to express the player, not hidden correct answers, and they should not add stress as a reward/punishment system.

## Copy-paste demo: cutscene, conversation, choice and breathing

This example creates a small playable scene using the project's existing player prefab and `AcademicEpisode` UI. It starts with cinematic camera cuts, shows a conversation, asks the player to choose a reply, opens the real Breathing Exercise, then completes the episode with the standard reflection and stress check-in.

No external models are required: the builder uses a capsule as the friend. Replace it with an NPC model after the demo works.

### Step 1: paste the episode script

Create `Assets/Examples/SimpleConversationEpisode.cs` and paste this entire file:

```csharp
using System.Collections;
using Mindscape.AcademicPressure;
using Mindscape.Data;
using UnityEngine;

namespace Mindscape.Examples
{
    // A small, self-contained example built on the same story runtime as the real chapters.
    public sealed class SimpleConversationEpisode : AcademicEpisode
    {
        [Header("Demo cast and camera positions")]
        public Transform friend;
        public Transform openingShot;
        public Transform playerCloseUp;
        public Transform friendCloseUp;
        public string friendName = "Maya";

        // Chapter 9 keeps this demo separate from Chapters 1-3 while testing.
        // Change these values and the save key when turning the demo into real content.
        public override int Chapter => 9;
        public override int Episode => 1;
        protected override float TimeLimit => 300;
        protected override string CompletionKey =>
            MindscapeDatabase.ProfileKey("Mindscape.Examples.SimpleConversationEpisode");
        protected override string NextScene => "";
        protected override string ContinueLabel => "Main menu";
        protected override string CompletionNext => "DEMO COMPLETE  •  RETURN TO THE MAIN MENU";

        protected override IEnumerator Play()
        {
            int reply = -1;
            bool finishedBreathing = false;

            // Opening cutscene: a wide shot followed by alternating close-ups.
            Shot(openingShot.position, Midpoint());
            yield return Card(
                "COPY-PASTE DEMO\n<size=60%>A Conversation and a Quiet Moment</size>",
                "Begin  [Space]");

            yield return Say("Narration",
                "After a busy day, you meet a friend in a quiet place.");

            Shot(friendCloseUp.position, Face(friend));
            yield return Say(friendName,
                "Hey. You seem a little tense. Do you want to talk about it?");

            Shot(playerCloseUp.position, Face(player));
            yield return Think(
                "I don't need to explain everything. I can choose how much I want to share.");

            yield return Choose(
                "Conversation",
                "What do you say?",
                new[]
                {
                    "I've been feeling overwhelmed today.",
                    "I'm okay. I just need a quiet moment."
                },
                picked => reply = picked);

            Record("demo_reply", reply == 0 ? "overwhelmed" : "quiet_moment");

            Shot(friendCloseUp.position, Face(friend));
            if (reply == 0)
            {
                yield return Say(friendName,
                    "Thank you for telling me. You don't have to solve the whole day at once.");
                yield return Me("Maybe I can begin with one small pause.");
            }
            else
            {
                yield return Say(friendName,
                    "That's okay. We can be quiet for a moment. You don't have to perform for me.");
                yield return Me("A quiet moment sounds good.");
            }

            yield return Say(friendName,
                "Would you like to take a few slow breaths together?");

            // Opens the project's existing BreathingMinigame screen.
            yield return Breathe(completed => finishedBreathing = completed, 12f);

            Shot(openingShot.position, Midpoint());
            yield return Think(finishedBreathing
                ? "The day is still here, but I feel a little more settled."
                : "I stopped early, and that's okay. Even one breath was a pause.");

            yield return Say(friendName,
                "You can come back to that pause whenever you need it.");

            Complete(
                "A Quiet Moment",
                "You had a conversation, chose how much to share, and tried a breathing pause.\n\nYour choice and reflection are saved.");
        }

        Vector3 Face(Transform target) => target.position + Vector3.up * 1.5f;

        Vector3 Midpoint() =>
            (player.position + friend.position) * 0.5f + Vector3.up * 1.25f;
    }
}
```

### Step 2: paste the scene builder

Create `Assets/Editor/SimpleConversationEpisodeBuilder.cs` and paste this entire file:

```csharp
using System.IO;
using Mindscape.Examples;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class SimpleConversationEpisodeBuilder
{
    const string ScenePath = "Assets/Scenes/Examples/Simple Conversation Episode.unity";
    const string PlayerPath = "Assets/Prefabs/Player.prefab";
    const string MaterialFolder = "Assets/Examples/Materials";

    [MenuItem("Mindscape/Examples/Create Simple Conversation Episode")]
    public static void Build()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;

        EnsureFolder("Assets/Examples");
        EnsureFolder(MaterialFolder);
        EnsureFolder("Assets/Scenes/Examples");

        var scene = EditorSceneManager.NewScene(
            NewSceneSetup.EmptyScene,
            NewSceneMode.Single);

        // Floor and simple set.
        var floor = Primitive(
            "Floor", PrimitiveType.Cube,
            new Vector3(0f, -0.1f, 1.5f),
            new Vector3(10f, 0.2f, 10f),
            Material("Demo Floor", new Color(0.30f, 0.40f, 0.38f)));

        var lightObject = new GameObject("Sun");
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObject.transform.rotation = Quaternion.Euler(45f, -30f, 0f);

        // Existing project player prefab.
        var playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(PlayerPath);
        if (playerPrefab == null)
            throw new FileNotFoundException("Player prefab not found", PlayerPath);

        var player = (GameObject)PrefabUtility.InstantiatePrefab(playerPrefab);
        player.name = "Player";
        player.transform.SetPositionAndRotation(
            new Vector3(0f, 0.1f, -1.2f),
            Quaternion.Euler(0f, 0f, 0f));

        // A placeholder friend. Replace this capsule with a character prefab later.
        var friend = Primitive(
            "Maya (replace with an NPC model)", PrimitiveType.Capsule,
            new Vector3(0f, 1f, 2.2f),
            new Vector3(0.75f, 1f, 0.75f),
            Material("Demo Friend", new Color(0.86f, 0.62f, 0.30f)));
        friend.transform.rotation = Quaternion.Euler(0f, 180f, 0f);

        // The one camera used for both cinematic shots and normal player view.
        var cameraObject = new GameObject("Story Camera");
        cameraObject.tag = "MainCamera";
        var camera = cameraObject.AddComponent<Camera>();
        cameraObject.AddComponent<AudioListener>();
        cameraObject.transform.position = new Vector3(0f, 2.4f, -5.5f);

        var movement = player.GetComponent<PlayerMovement>();
        if (movement != null) movement.cameraTransform = camera.transform;

        // Empty transforms mark the three camera positions used by the script.
        var shots = new GameObject("Camera Shots").transform;
        var opening = Point(shots, "Opening Shot", new Vector3(4.8f, 3.0f, -4.8f));
        var playerShot = Point(shots, "Player Close-up", new Vector3(1.8f, 1.8f, 0.1f));
        var friendShot = Point(shots, "Friend Close-up", new Vector3(-1.8f, 1.8f, 0.9f));

        var storyObject = new GameObject("Simple Conversation Story");
        var episode = storyObject.AddComponent<SimpleConversationEpisode>();
        episode.player = player.transform;
        episode.storyCamera = camera;
        episode.friend = friend.transform;
        episode.openingShot = opening;
        episode.playerCloseUp = playerShot;
        episode.friendCloseUp = friendShot;
        episode.friendName = "Maya";

        EditorSceneManager.SaveScene(scene, ScenePath);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Selection.activeGameObject = storyObject;
        Debug.Log("Created: " + ScenePath + ". Press Play to test it.");
    }

    static GameObject Primitive(
        string name, PrimitiveType type, Vector3 position,
        Vector3 scale, Material material)
    {
        var go = GameObject.CreatePrimitive(type);
        go.name = name;
        go.transform.position = position;
        go.transform.localScale = scale;
        go.GetComponent<Renderer>().sharedMaterial = material;
        return go;
    }

    static Transform Point(Transform parent, string name, Vector3 position)
    {
        var point = new GameObject(name).transform;
        point.SetParent(parent);
        point.position = position;
        return point;
    }

    static Material Material(string name, Color color)
    {
        string path = MaterialFolder + "/" + name + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material != null) return material;

        var shader = Shader.Find("Universal Render Pipeline/Lit")
            ?? Shader.Find("Standard");
        material = new Material(shader) { name = name, color = color };
        if (material.HasProperty("_BaseColor"))
            material.SetColor("_BaseColor", color);
        AssetDatabase.CreateAsset(material, path);
        return material;
    }

    static void EnsureFolder(string path)
    {
        if (AssetDatabase.IsValidFolder(path)) return;
        string parent = Path.GetDirectoryName(path).Replace('\\', '/');
        string name = Path.GetFileName(path);
        EnsureFolder(parent);
        AssetDatabase.CreateFolder(parent, name);
    }
}
```

### Step 3: generate and play it

1. Return to Unity and wait until script compilation finishes with no red Console errors.
2. Run `Mindscape ▸ Examples ▸ Create Simple Conversation Episode`.
3. Unity creates and opens `Assets/Scenes/Examples/Simple Conversation Episode.unity`.
4. Press **Play**. Use **Space**, **Enter** or the on-screen buttons to advance; click a choice or press `1`/`2`.
5. The breathing screen runs for 12 seconds. Complete it or close it early; both paths continue the story with different text.

> [!TIP] Test the demo offline
>
> The example uses Chapter 9 as a sandbox so it does not mark Chapters 1-3 complete. Test with **Play offline** unless Chapter 9 test records are wanted in Supabase.

### Turn the demo into a real episode

1. Move/rename the runtime class into the real chapter folder and namespace.
2. Replace `Chapter`, `Episode`, `CompletionKey`, `NextScene`, `ContinueLabel` and `CompletionNext` with the real chapter's values—or inherit the chapter's existing base class.
3. Replace the capsule with a character prefab. Keep the assigned `friend` Transform or point it at the new character root.
4. Move the camera-shot transforms in the Scene view until both faces are framed well.
5. Edit the dialogue and choices inside `Play()`. Keep each option player-safe; do not make one choice secretly “correct.”
6. Register the real scene in the chapter registry, menu, progression, loading screen and Build Profile using the checklist below.

The builder recreates the demo scene, so after turning it into real content, give the production scene a different path or stop running the demo builder.

## Add an episode to an existing chapter

### 1. Create the story script

Create the script in that chapter's folder. The normal runtime is `AcademicEpisode`, which supplies dialogue, choices, interaction spots, phone screens, journal/reflection, stress check-in, timeout, saving and completion UI.

Use the chapter's existing base when it has one:

| Chapter | Base/component pattern | Registry |
| --- | --- | --- |
| 1 | One class per episode inheriting `AcademicEpisode` | `AcademicPressureChapter.cs` |
| 2 | Episodes 1-3 inherit `FamilyEpisode`; episodes 4-5 use `FamilyFinaleEpisode` with `episodeNumber` | `FamilyEpisode.cs` |
| 3 | One shared `SocialDynamicsEpisode` component with `episodeNumber` and a `switch` in `Play()` | `SocialDynamicsChapter.cs` |

A minimal one-class episode looks like this:

```csharp
using System.Collections;
using Mindscape.AcademicPressure;

namespace Mindscape.MyChapter
{
    public sealed class MyEpisode : AcademicEpisode
    {
        public override int Chapter => 4;
        public override int Episode => 1;
        protected override float TimeLimit => 720;
        protected override string CompletionKey =>
            Mindscape.Data.MindscapeDatabase.ProfileKey("Mindscape.NewBeginnings.Episode1");
        protected override string NextScene => ""; // no next scene in this one-episode example
        protected override string ContinueLabel => "Main menu";
        protected override string CompletionNext => "CHAPTER 4 COMPLETE  •  RETURN TO THE MAIN MENU";

        protected override IEnumerator Play()
        {
            yield return Card("CHAPTER 4 · NEW BEGINNINGS\n<size=60%>Episode 01 · First Steps</size>");
            yield return Say("Friend", "I'm glad you came.");
            yield return Think("I can take this one step at a time.");
            Complete("First Steps", "You arrived, connected with someone, and chose a first step.");
        }
    }
}
```

For a real multi-episode chapter, copy the nearest existing script so its use of `AddSpot`, `AddArrival`, `RoamUntil`, `Choose`, `Ask`, `PhoneChoose`, `Breathe`, `Record`, `Shot` and `Complete` matches the intended interaction. Put the completion-key and next-scene overrides in a chapter base class rather than duplicating those rules in every episode.

> [!WARN] Every story path must finish
>
> Every branch of `Play()` must eventually reach `Complete(...)` or a deliberate finale. A coroutine that exits early leaves the player in the scene without saved completion or a Continue action.

### 2. Create and wire the scene

1. Duplicate the closest episode scene and rename it exactly `Chapter <N> - Episode <N>.unity` under `Assets/Scenes/`.
2. Remove the old episode component but keep the shared player, camera, environment, UI, audio and lighting that the new episode needs.
3. Add the new episode component to a clearly named story root.
4. Assign its **Player**, **Story Camera**, spawn/view transforms, interaction points and any episode-specific references in the Inspector.
5. Delete or disable old story objects, quests, collectibles and NPC triggers that should not carry into the new episode.
6. Apply the shared world and doors where appropriate. See [Shared City & Traffic](#system-world) and [Doors](#workflow-door).
7. Press Play directly in the episode scene and test every interaction order and choice branch.

If a chapter's scenes are generated by an Editor builder, make the change in its `Assets/Editor/*Builder.cs` file. Hand edits to a generated scene disappear the next time that builder runs.

### 3. Register the episode everywhere

Adding only the scene is not enough. Update each applicable row:

| Area | File/change |
| --- | --- |
| Chapter scene/title data | Add the scene, title, location and briefing to the chapter registry. Chapter 1 uses `AcademicPressureChapter`; Chapter 2 keeps titles/scenes in `FamilyExpectationsChapter` but loading metadata in `EpisodeLoadingScreen`; Chapter 3 uses `SocialDynamicsChapter`. |
| Episode count and unlocking | Update `MindscapeProgress.EpisodeCounts`. The previous count values are `{ 4, 5, 8 }`. |
| Save-key mapping | Confirm `MindscapeProgress.SaveKey` maps the chapter to the same prefix used by the episode's `CompletionKey`. |
| Journal title and prompt | `EpisodeReflection.Title` reads the chapter registry. Add an exception in `EpisodeReflection.Prompt` only when the default prompt does not fit. |
| Main-menu row | Add another episode-row button to `Assets/UI Toolkit/MainMenuNew/MainMenuNew.uxml` with the established naming pattern. |
| Main-menu binding | Extend `MainMenuNewController.BindEpisodes` and `StoryScene` when the existing loop/range does not pick up the new episode. Chapter 2 is currently hard-coded to five episodes. |
| Loading screen | Make sure `EpisodeLoadingScreen` can obtain the title, location, briefing and correct chapter badge. Chapter 2's arrays are currently stored directly in this file. |
| Continue navigation | Update the current last episode's `NextScene`, `ContinueLabel` and completion text, and make the new last episode point to the next chapter or finale. |
| Build profile | Add and enable the scene under **File ▸ Build Profiles ▸ Scene List**, or extend the chapter builder's registration method. |
| Thumbnail | Add `Assets/Resources/EpisodeThumbnails/Chapter<N>_Episode<E>.png`, normally through `Mindscape ▸ Main Menu ▸ Capture Episode Thumbnails`. |
| Story docs | Add the episode to its chapter table and describe its goals, choices and saved consequences. |

The main-menu UXML rows are authored markup, not generated from the registry. Copy the previous row, change its element names, text and thumbnail resource, then verify that the Console does not report a missing row.

### 4. Confirm persistence

`AcademicEpisode` calls `MindscapeDatabase.EpisodeStarted` and `EpisodeCompleted`; it also records the final episode result and reflection. The Supabase RPCs accept chapter and episode numbers, so a new episode normally needs no database migration. Keep chapter numbers between `1` and `9`, which is the current database constraint.

Use stable keys with `Record("choice_key", "value")`. Never reuse a key for a different meaning after players may have saved it. Test both signed-in cloud play and **Play offline**.

## Add a completely new chapter

A fourth chapter is a larger change because the current menu, progress and loading screen contain three-chapter assumptions. Do these steps together; shipping only some of them produces missing menu rows, incorrect save keys or Chapter 2 artwork on the loading screen.

### 1. Add a chapter registry

Create a chapter folder and a registry similar to:

```csharp
public static class NewBeginningsChapter
{
    public const int Number = 4;
    public static readonly string[] Scenes =
    {
        "Chapter 4 - Episode 1",
        "Chapter 4 - Episode 2",
    };
    public static readonly string[] Titles = { "First Steps", "A Place to Return" };
    public static readonly string[] Locations = { "COMMUNITY CENTRE", "CITY PARK" };
    public static readonly string[] Briefings =
    {
        "• Arrive at the centre\n• Meet the group\n• Choose one small first step",
        "• Return to the park\n• Reflect on what changed\n• Complete the chapter",
    };
    public static int EpisodeCount => Scenes.Length;
    public static string SaveKey(int episode) =>
        Mindscape.Data.MindscapeDatabase.ProfileKey("Mindscape.NewBeginnings.Episode" + episode);
}
```

Add a chapter-specific base derived from `AcademicEpisode` that overrides `Chapter`, `CompletionKey`, `NextScene`, `ContinueLabel` and `CompletionNext`. This keeps all of the chapter's episodes on one navigation/save convention.

### 2. Extend every three-chapter assumption

Search for `ChapterCount`, `EpisodeCounts`, `chapter == 3`, `chapter <= 3`, `Chapter 3`, and the current chapter namespaces. At minimum update:

- `MindscapeProgress.EpisodeCounts`, `ChapterCount` and `SaveKey`;
- `EpisodeReflection.ChapterNames`, `Title` and any custom prompts;
- `MainMenuNew.uxml`: chapter card, chapter episode page and one row per episode;
- `MainMenuNewController.BindChapters`, `BindEpisodes` and `StoryScene`;
- `EpisodeLoadingScreen`: episode count, metadata selection, thumbnail selection and chapter badge;
- the last episode of the previous chapter so Continue enters Chapter 4;
- any finale logic that currently treats Chapter 3 as the end of the game;
- Editor builders or verification tools that iterate only Chapters 1-3; and
- documentation, privacy/data descriptions and QA matrices that state the chapter count.

> [!TIP] Prefer registry-driven code
>
> When touching hard-coded chapter switches, move chapter title, scenes, locations and briefings behind one registry/API if practical. That makes a later chapter addition smaller and prevents the menu, loading screen and journal from disagreeing.

### 3. Add menu and loading artwork

1. Add the Chapter 4 card and `page-episodes-4` in `MainMenuNew.uxml`.
2. Follow the existing element-name contracts: `chapter-4`, `chapter-4-state`, and a consistent episode-row prefix that `BindEpisodes` queries.
3. Add `Chapter4_Episode1.png`, `Chapter4_Episode2.png`, and so on under `Assets/Resources/EpisodeThumbnails/`.
4. Update `EpisodeLoadingScreen` so it prints the new chapter name instead of falling into the Chapter 2 default branch.
5. Test narrow/mobile layout; another chapter card or long title can overflow even when desktop looks correct.

### 4. Add a repeatable builder when needed

For a chapter with several related scenes, create an Editor builder under `Assets/Editor/` that:

1. copies a known-good environment scene;
2. removes the old story component and old episode-only content;
3. adds/configures the new component and references;
4. applies the world, doors, ambient life and chapter-specific set dressing;
5. saves each scene to its final name; and
6. registers all scenes in global Editor build settings and every Build Profile that overrides the global scene list.

Make it safe to re-run, and put generated content under one named root where possible. Document clearly whether it replaces an entire scene.

## Definition of done

An episode or chapter is not finished until all of these pass:

- The scene opens with no missing scripts or references.
- It launches from the main menu in a clean Editor session and in a player build.
- Locked episodes cannot be opened early; completion unlocks exactly the next episode/chapter.
- Replay, Continue, Return to menu and timeout all go to the correct place.
- Every dialogue choice and exploration order reaches completion.
- Pause, mobile controls, journal, self-reflection, stress check-in and minigames restore control correctly.
- Local/offline completion survives a restart.
- Signed-in progress, journal, assessment and episode record appear in Supabase and return after a restart.
- The loading screen has the correct chapter, title, location, objectives and thumbnail.
- The scene is enabled in every shipping Build Profile.
- Android and WebGL have acceptable performance, legible UI and no missing assets.
- The chapter story page, handover notes and QA coverage describe the new content.

> [!WARN] Test from the menu and from a build
>
> Direct Play Mode proves the episode coroutine can run, but it does not prove the main-menu binding, lock progression, loading metadata or build-profile registration. Always finish with a menu-to-episode test in an exported build.
