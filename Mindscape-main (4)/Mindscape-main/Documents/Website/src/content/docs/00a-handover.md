---
id: handover
group: Handover
nav: Handover Guide (English)
---

# Handover Guide

The short version of everything you need to change this project yourself. Each section links to the longer page. If Unity and programming are new to you, read [Beginner Start Here](#beginner-guide) first. **Tagalog:** [Gabay sa Handover](#handover-tl).

## 1. Open the project

1. Install **Unity 6000.5.8f1** with Unity Hub (add *Android*, *WebGL* and *Windows/Mac Build Support* if you will build for them).
2. Unity Hub ▸ **Add** ▸ pick the `mindscape-3d` folder. The first open takes several minutes (it imports everything).
3. Open `Assets/Scenes/Intro.unity` and press **Play**. The game starts like a real build: intro → main menu.

> [!TIP] Play one episode directly
>
> Open any `Assets/Scenes/Chapter N - Episode N.unity` and press Play. It starts that episode without the menu.

## 2. Where things are

| Folder | What is inside |
| --- | --- |
| `Assets/Scripts/` | Shared scripts: `Player/`, `UI/` (menus, pause, loading), `Mobile/`, `Audio/`, `Cutscene/`, `Core/` (doors, graphics, tutorial) |
| `Assets/AcademicPressure/` | Chapter 1 episodes **and** `AcademicEpisode.cs`, the base every story episode uses |
| `Assets/FamilyExpectations/`, `Assets/FamilyFinale/` | Chapter 2 episodes |
| `Assets/SocialDynamics/` | Chapter 3 (all 8 episodes share one script plus `SocialDynamicsChapter.cs`) |
| `Assets/Database/` | Saves (SQLite / local storage) and Supabase cloud sync |
| `Assets/Editor/` | Menu tools that build scenes and prefabs (never shipped in the game) |
| `Assets/UI Toolkit/` | Every screen layout (`.uxml`) and style (`.uss`) |
| `Assets/Scenes/` | All scenes. `Prototypes/` holds old ones not in the build |
| `supabase/` | Database migrations and the `account` edge function |
| `Documents/Website/` | This site |

Full tree: [Project Structure](#structure).

## 3. Configure the Supabase connection

The game talks to Supabase in **one file**: `Assets/Scripts/Data/MindscapeCloud.cs`, lines 21-23. The complete, current procedure—including migrations, the Edge Function, OTP templates, SMTP, Google OAuth, secrets, verification and troubleshooting—is in [Supabase Connection Setup and Settings](#workflow-supabase).

```csharp
const string RpcUrl        = "https://<PROJECT_REF>.supabase.co/rest/v1/rpc/";
const string AccountUrl    = "https://<PROJECT_REF>.supabase.co/functions/v1/account";
const string PublishableKey = "sb_publishable_...";
```

**Use your own Supabase project:**

1. Create a project at [supabase.com](https://supabase.com). Copy the **Project ref** (Settings ▸ General) and the **Publishable key** (Settings ▸ API Keys).
2. Install the [Supabase CLI](https://supabase.com/docs/guides/cli), then in the `mindscape-3d` folder run:

   ```sh
   supabase login
   supabase init                                      # run once if supabase/config.toml is missing
   supabase link --project-ref <PROJECT_REF>
   supabase db push --dry-run --remote                # preview pending migrations
   supabase db push --remote                          # create/update tables and functions
   supabase functions deploy account --no-verify-jwt  # the login / sign-up gateway
   supabase secrets set RESEND_API_KEY=<key> MAIL_FROM="Mindscape <no-reply@yourdomain.com>"
   ```

   (`RESEND_API_KEY` / `MAIL_FROM` are only for the "account deleted" email from [Resend](https://resend.com). Leave them out and deletion still works, without the email.)
3. In the Supabase dashboard:
   - **Authentication ▸ Sign In / Providers ▸ Email**: turn **Confirm email** ON.
   - **Authentication ▸ Email Templates**: in *Confirm signup* and *Reset password*, put `{{ .Token }}` in the message (that is the 6-digit code players type).
   - **Authentication ▸ SMTP Settings**: add your own SMTP before real players use it. The built-in mailer only sends to team members and is heavily rate-limited.
   - If Google login is enabled, configure the Google provider plus both callback/redirect entries described in [Google sign-in setup](#workflow-supabase).
4. Paste the new ref and key into the three lines of `MindscapeCloud.cs`, save, and rebuild the game.

> [!WARN] Never put the secret key in the game
>
> Only the **publishable** key goes in `MindscapeCloud.cs`. The service role / secret key stays in Supabase (the edge function reads it automatically).

**Turn online accounts off:** players can always choose *Play offline*. Everything then saves on the device only.

**See player data:** Supabase dashboard ▸ Table Editor: `players`, `episode_progress`, `journal_entries`, `assessments`, `episode_records`. Deleted accounts have `status = archived` and are purged after 30 days. More: [Accounts, Progress & Saves](#system-accounts).

## 4. Edit a scene

1. Open the scene from `Assets/Scenes/`.
2. Select objects in the **Hierarchy**, move them with **W** (move), **E** (rotate), **R** (scale), change values in the **Inspector**.
3. **Ctrl/Cmd + S** to save. Press Play to test.

| I want to... | Do this |
| --- | --- |
| Move a person, item or marker | Select it in the Hierarchy (NPCs are under `NPC System` or named after the person) and move it |
| Move where the player starts | Move the object named `Player` |
| Change the city, house or school model | Edit in Blender, re-export over the same file, then run the matching `Mindscape ▸ World / House / School ▸ Sync...` menu ([Editor Menu Items](#ref-menu-items)) |
| Add a new NPC | `GameObject ▸ NPC` ([Create an NPC](#workflow-npc)) |
| Add a pickup | `GameObject ▸ Collectible` ([Create a Collectible](#workflow-collectible)) |
| Add a door | `Mindscape ▸ Doors ▸ Apply Doors to Open Scene` ([Doors](#workflow-door)) |

> [!WARN] Builder menus rebuild scenes
>
> `Mindscape ▸ Chapter N ▸ Build ...` regenerates those scenes from code. **Anything you placed by hand in that scene is lost.** After you start editing a scene by hand, do not run its Build menu again (or make the change in the builder script in `Assets/Editor/` instead). Always commit to git first.

## 5. Change story text, timers and choices

Story episodes are written **in code**, not in the scene. Open the episode's script in any editor (VS Code, Rider or Visual Studio):

| Chapter | Episode scripts |
| --- | --- |
| 1 | `Scripts/Chapters/Chapter 1 - Academic Pressure/HouseEpisode.cs`, `ClassroomEpisode.cs`, `CafeteriaEpisode.cs`, `DormitoryEpisode.cs` |
| 2 | `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyAfterSchoolEpisode.cs`, `FamilyMorningEpisode.cs`, `FamilyExamEpisode.cs`, `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyFinaleEpisode.cs` |
| 3 | `Scripts/Chapters/Chapter 3 - Social Dynamics/SocialDynamicsEpisode.cs` (titles/goals in `SocialDynamicsChapter.cs`) |

- **Dialogue line:** search the script for the sentence and edit the text inside `Say("Name", "text")`, `Me("text")` or `Think("text")`. Keep the [Writing Guidelines](#story-tone).
- **Episode titles, briefings:** `AcademicPressureChapter.cs`, `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyEpisode.cs` (`FamilyExpectationsChapter.Titles`), `SocialDynamicsChapter.cs`.
- **Time limit:** `protected override float TimeLimit => 720;` near the top of each episode script (seconds). The default is 600 in `AcademicEpisode.cs`.
- **Stress changes:** the numbers passed to `AddStress(...)` / `EaseStress(...)`.

Save the file; Unity recompiles automatically. Check the **Console** for red errors.

## 6. Configure scripts in the Inspector

Most settings are fields on a component: select the object, change the value in the **Inspector**, save the scene.

| Setting | Where |
| --- | --- |
| Walk / run speed, camera | `Player` object ▸ `PlayerMovement` (`moveSpeed`, `runSpeed`) |
| Starting stress, max stress | `Player` ▸ `PlayerControls` (`stressLevel`, `stressMax`) |
| NPC name, dialogue tree, stress per choice | the NPC ▸ `NPC` ([NPC Dialogue](#system-npc)) |
| Quest goals and timer (prototype scenes) | the `Quest` object ([Create a Quest](#workflow-quest)) |
| Which music plays in which scene | `Assets/Resources/SceneMusicMap.asset` |
| Music playlist | `Assets/Resources/Music/` ([Music & SFX](#system-audio)) |
| Key bindings | `Assets/Resources/GameControls.inputactions` (double-click to open) |
| Screen layout, colours, fonts | the `.uxml` / `.uss` in `Assets/UI Toolkit/`, opened in **Window ▸ UI Toolkit ▸ UI Builder** ([Episode Screens](#system-episode-ui), [UI Theme](#system-theme)) |
| Graphics quality | `Assets/Settings/PC_RPAsset.asset` and `Mobile_RPAsset.asset` |
| App name, version, icon | `Edit ▸ Project Settings ▸ Player` |

Every script starts with a comment that says what it does. The list is in [Script Index](#ref-scripts).

## 7. Add or remove an episode

Full checklist: [Create an Episode or Chapter](#workflow-episode-chapter).

1. Duplicate the nearest episode scene, rename it `Chapter N - Episode N`.
2. Copy its episode script, rename the class, change the text.
3. Add the scene name to the chapter's list (`AcademicPressureChapter.Scenes` and `Titles`, `FamilyExpectationsChapter.Scenes` in `FamilyEpisode.cs`; Chapter 3 uses `EpisodeCount` and `Titles` in `SocialDynamicsChapter.cs`) so the main menu shows it.
4. Add the scene in **File ▸ Build Profiles ▸ Scene List**.

Details: [Create a Gameplay Scene](#workflow-scene).

## 8. Build and publish

| Target | How |
| --- | --- |
| Android APK | `File ▸ Build Profiles ▸ Android ▸ Switch Platform`, then **Build** |
| Web (WebGL) | Same with **Web**. Upload the output folder to any static host (it is hosted on Vercel now) |
| Windows / Mac | Same with **Windows** / **macOS** |

Before a Play Store release: change the package name (currently the template `com.UnityTechnologies...`) and create a release keystore in **Project Settings ▸ Player ▸ Publishing Settings**.

The docs site: `cd docs && npm install && npm run dev` to preview, `npm run build` for production, deployed with `vercel --prod`. Pages are Markdown files in `Documents/Website/src/content/docs/`.

## 9. If something breaks

| Problem | Fix |
| --- | --- |
| Pink materials | Wrong render pipeline: check `Edit ▸ Project Settings ▸ Graphics` uses the URP asset in `Assets/Settings/` |
| "Missing script" on an object | A script was renamed or its `.meta` file lost. Restore it from git |
| Login fails with "email not confirmed" | The player must enter the 6-digit code. Check the email template has `{{ .Token }}` |
| No sign-up emails arrive | Built-in mailer limit: add custom SMTP (step 3) |
| Scene changes vanished | A Build menu regenerated it (step 4 warning). Restore from git |
| Build fails "scripts are compiling" | Wait for the spinner (bottom right) to stop after switching platform, then build again |

> [!TIP] Rule of thumb
>
> Commit to git before every big change. When a file move is needed, move it **inside Unity** (Project window), never in Finder, so its `.meta` file goes with it.
