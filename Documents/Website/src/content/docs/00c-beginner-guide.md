---
id: beginner-guide
group: Handover
nav: Beginner Start Here
---

# Beginner Start Here: Modify the Game Safely

This page is for someone opening Unity for the first time. You do **not** need to understand the whole project before making a small change. Follow one recipe at a time, test immediately, and keep a recoverable copy.

> [!TIP] Your first goal
>
> Do not start by creating a new chapter or changing Supabase. First learn to open a scene, move one object, change one sentence, press Play, read the Console and restore a mistake.

## The safest learning order

| Stage | Practice task | What it teaches |
| --- | --- | --- |
| 1 | Open an existing episode and press Play | Scenes, Game view and stopping Play Mode |
| 2 | Move a harmless prop, save and test | Hierarchy, Scene view, Inspector and transforms |
| 3 | Change one existing dialogue sentence | Finding a file, editing only text, compilation and Console errors |
| 4 | Duplicate a scene before experimenting | Safe copies and recovery |
| 5 | Add one NPC through `GameObject ▸ NPC` | Components, Inspector fields and prefabs |
| 6 | Replace one image or audio file without renaming it | Asset references and import |
| 7 | Make a development build | Build Profiles and testing outside the Editor |
| 8 | Follow a copy-paste example | Scripts and generated scenes |

Only after those steps should you attempt a new episode, Blender export, database migration or authentication change.

## Learn these six Unity areas

| Unity area | Plain-language meaning | What you do there |
| --- | --- | --- |
| **Project** | All files belonging to the game | Open scenes, scripts, images, audio, prefabs and models |
| **Hierarchy** | Objects inside the currently open scene | Select the Player, NPCs, furniture, lights and UI objects |
| **Scene** | The editable 3D workspace | Move, rotate and inspect objects |
| **Game** | What the player sees | Test the game after pressing Play |
| **Inspector** | Settings for the selected object/file | Change position, dialogue, speed, references and import settings |
| **Console** | Errors, warnings and useful messages | Read red errors before doing more work |

The small triangle beside an object expands its children. A checkbox beside a GameObject enables/disables it. The three Transform values are:

- **Position** — where it is;
- **Rotation** — which way it faces; and
- **Scale** — how large it is.

Unity shortcuts: **W** moves, **E** rotates, **R** scales, **F** frames the selected object, and **Ctrl/Cmd+S** saves.

## Golden safety rules

1. **Stop Play Mode before editing.** Changes made while the Play button is blue normally disappear when Play Mode stops.
2. **Save and back up before a builder or large change.** Commit with Git/GitHub Desktop, or duplicate the specific scene/file first.
3. **Change one thing at a time.** Test it before changing something else. This makes the cause of a problem obvious.
4. **Never delete `.meta` files.** Unity uses them to keep references. Move assets inside Unity's Project window so the `.meta` travels with them.
5. **Do not rename objects casually.** Builders and scripts find objects such as `Player`, `HUDCanvas`, anchors, doors and animation clips by exact name.
6. **Do not edit generated scenes after planning to rebuild them.** Chapter builder menus can replace the entire scene. Put the change in its builder script or stop using that builder for the scene.
7. **Never paste secret keys into Unity.** Only a Supabase publishable key may be included in the game. Database passwords, secret/service-role keys, SMTP passwords and OAuth secrets stay server-side.
8. **Treat the first red Console error as the real problem.** Later red errors may be consequences. Double-click the first one to open the file and line.
9. **Do not update Unity or packages during ordinary content editing.** Version upgrades can change the whole project and should be a separate backed-up task.
10. **Never publish without testing a real build.** Play Mode does not catch every Android, WebGL, scene-list or file-path problem.

## What is safe without programming?

### Green: good beginner changes

- Move an existing object, NPC, interaction marker or player start.
- Change Inspector values such as movement speed, interaction distance or light intensity.
- Edit an NPC's Inspector-authored name and dialogue choices.
- Replace an image, audio clip or model by exporting over the same filename.
- Edit UXML/USS visually in UI Builder while preserving element names.
- Add an NPC, collectible, quest or supported minigame with the project's menu commands.
- Change which music plays through `SceneMusicMap.asset`.
- Test episodes and fill in the QA workbook.

### Yellow: follow a checklist and make a backup

- Edit story dialogue inside a `.cs` script.
- Run a menu command that rebuilds scenes or prefabs.
- Create an episode from the copy-paste example.
- Export a modified Blender model.
- Change Build Profiles or platform settings.
- Configure Supabase dashboard settings or apply a reviewed migration.

### Red: ask a programmer or technical maintainer

- Change login, account deletion, token storage or cloud authorization.
- Change database ownership rules, RLS, security-definer functions or production data.
- Modify `AcademicEpisode`, `MindscapeCloud`, `MindscapeDatabase`, player input or save-key rules without a tested guide.
- Upgrade Unity, render pipeline, input system or packages.
- Resolve merge conflicts in scenes, prefabs or `.meta` files.
- Change shaders, native plugins, platform signing, Android manifests or WebGL hosting headers.
- Delete/migrate production accounts or reset a remote database.

## Recipe: open and test one episode

1. In the Project window, open `Assets/Scenes/Chapter 1 - Episode 1.unity`.
2. Wait until the spinner finishes and the Console has no red errors.
3. Press the Play button at the top.
4. Test movement and the first interaction.
5. Press Play again to stop.

If the game starts in the wrong scene, double-click the intended scene again. If it remains dark, check the Game view is active and wait for compilation/import to finish.

## Recipe: move an object safely

1. Stop Play Mode.
2. Save the scene, then duplicate it if this is an experiment.
3. Select the object in the Hierarchy.
4. In the Inspector, write down or screenshot its original Transform values.
5. Press **W** and drag one coloured arrow. Red is X, green is Y (height), blue is Z.
6. Press **Ctrl/Cmd+S**.
7. Press Play and walk around it. Check the player is not trapped and interactions still work.
8. To undo immediately, press **Ctrl/Cmd+Z**. To restore later, enter the original Transform values or restore the scene from version control.

Do not move the parent of an entire house, school or world unless the relevant guide says to; many story points depend on those coordinate systems.

## Recipe: change one story sentence

Story dialogue is usually in the chapter's `.cs` episode file. This is a text change, but C# punctuation must remain valid.

1. Stop Play Mode and commit/back up the script.
2. Search the project for the exact sentence. In Unity use the Project search; in VS Code use **Ctrl/Cmd+Shift+F**.
3. Find the sentence inside a call such as:

   ```csharp
   yield return Say("Maya", "You look worried. Everything okay?");
   ```

4. Change only the words inside the second pair of quotation marks:

   ```csharp
   yield return Say("Maya", "You seem quiet today. Would you like to talk?");
   ```

5. Keep the surrounding `"`, parentheses `()`, semicolon `;` and `yield return` unchanged.
6. Save. Return to Unity and wait for compilation.
7. If the Console is clear, open that episode and play to the sentence.

Common text mistakes:

| Mistake | Correct form |
| --- | --- |
| A quotation mark inside dialogue ends the string | Write `\"quoted words\"` |
| A new line is typed directly into a quoted string | Use `\n` where the new line should appear |
| The final quote/parenthesis/semicolon was removed | End like `");` |
| Smart/curly quote used as C# punctuation | Keep code delimiters as straight `"`; curly quotes may be inside the text |

Follow [Writing Guidelines](#story-tone) and test every choice branch affected by the edit.

## Recipe: change Inspector-authored NPC dialogue

1. Stop Play Mode and open the scene.
2. Expand `NPC System` in the Hierarchy and select `NPC - <Name>`.
3. In the Inspector, find the `NPC` component and **Dialogue Nodes**.
4. Edit `NPC Name`, speech and player-facing choices.
5. Keep `nextDialogueIndex` within the list, or use `-1` when the choice ends.
6. Save, press Play, walk close and press **F** to test every choice.

See [Create an NPC](#workflow-npc) before adding/removing nodes. A typo in the NPC name can also break a Quest that expects that exact name.

## Recipe: replace an image or audio clip

The safest replacement keeps the same path and filename, so existing references remain connected.

1. Find the asset in Unity and note its folder, filename, dimensions/length and Inspector settings.
2. Back up the original.
3. Prepare the replacement in the same format when possible (`.png`, `.wav`, and so on).
4. Replace the file **without deleting its `.meta` file**.
5. Return to Unity and wait for reimport.
6. Select it and compare import settings with the original screenshot.
7. Test every screen/scene using it and make a target build.

Do not replace a large file with a different filename and expect scenes to update automatically. See [Blender Assets](#workflow-blender-assets) for 3D models.

## Recipe: add an NPC or collectible without writing code

Use the supported menu commands rather than constructing all components manually:

- `GameObject ▸ NPC` — then set name, model, interaction radius and dialogue. See [Create an NPC](#workflow-npc).
- `GameObject ▸ Collectible` — then set model, display name, stable item ID and range. See [Create a Collectible](#workflow-collectible).

Save the scene and test the interaction from the player's real height and approach direction. If the object came from a generated scene, remember that rebuilding may remove the hand-added object.

## Understanding scripts without learning all of C#

You only need a few patterns for content edits:

| Pattern | Meaning |
| --- | --- |
| `"some words"` | Text shown or stored by the game |
| `720` | A number; here it might mean seconds |
| `true` / `false` | On / off |
| `// comment` | Explanation for humans; Unity ignores it |
| `Say("Name", "Words")` | Spoken dialogue |
| `Think("Words")` | Player's inner thought |
| `Choose(...)` | A list of player choices |
| `Breathe(...)` | Opens the breathing exercise |
| `Complete(...)` | Marks the episode finished |

Do not change class names, namespaces, braces `{}`, method names or variable names during a text-only edit.

## When Unity shows a red error

1. Stop. Do not keep editing other files.
2. Open **Window ▸ General ▸ Console** if it is hidden.
3. Clear the Console once, then wait. Focus on the first red item that returns.
4. Double-click it. Note the filename, line number and full message.
5. If the error appeared after your last edit, undo that edit and save.
6. Wait for Unity to compile again.
7. If it remains, restore the changed file from version control or send the error report below to the maintainer.

| Error text contains | Usually means |
| --- | --- |
| `; expected` | A semicolon was removed, or the line above has broken quotes/parentheses |
| `Newline in constant` | Dialogue quotation marks are broken or a real line break was inserted inside text |
| `} expected` | A closing brace was removed |
| `does not exist in the current context` | A name was misspelled or code was pasted in the wrong place |
| `MissingReferenceException` | A scene/prefab field points at something deleted |
| `NullReferenceException` | A required Inspector reference or runtime object is missing |
| `Scene ... couldn't be loaded` | Scene is absent/disabled in the active Build Profile |

## How to report a problem so it can be fixed quickly

Send all of these together:

1. What you were trying to change.
2. Exact steps from opening Unity until the problem.
3. What you expected and what happened instead.
4. The scene name and object selected.
5. Screenshot of the full Unity window and Inspector.
6. The first red Console error expanded, including its stack trace.
7. Whether it happens in Editor, Android, WebGL or all of them.
8. The last known working commit/build and the files changed.
9. A short screen recording for movement, camera or timing problems.

Avoid sending only “it does not work”; the scene, first error and reproduction steps usually reveal the cause.

## Before every release

- Start from `Intro.unity` and test intro → login/offline → menu → episode.
- Test a new account, existing account, password recovery and Play offline when account code changed.
- Verify every changed episode from its menu card, not only direct Play Mode.
- Check Continue, Replay, pause, mobile controls, choices, minigames and completion.
- Confirm changed scenes are enabled in every target Build Profile.
- Test at least one Android/WebGL build when those platforms are being delivered.
- Check the Console and player logs for errors.
- Update the QA workbook with build number, tester, date, result and notes.
- Keep the previous working build until the new build is accepted.

## Where to go next

| Goal | Guide |
| --- | --- |
| Full project setup and release | [Handover Guide](#handover) |
| Understand folders and files | [Project Structure](#structure) |
| Modify a scene | [Create a Gameplay Scene](#workflow-scene) |
| Add an episode/chapter | [Create an Episode or Chapter](#workflow-episode-chapter) |
| Copy a simple conversation/choice/breathing scene | [Copy-paste episode demo](#workflow-episode-chapter) |
| Modify/create 3D models | [Blender Assets](#workflow-blender-assets) |
| Configure accounts | [Supabase Setup](#workflow-supabase) |
| Add a cloud table | [Supabase Table → Unity](#workflow-supabase-data) |
| Find a custom menu command | [Editor Menu Items](#ref-menu-items) |
| Test systematically | [QA Test Cases](#ref-qa) |

> [!TIP] A good handover result
>
> The client does not need to become a programmer. They should be able to make green-level content changes, test and recover them, and recognize when a yellow/red task needs the detailed guide or technical help.
