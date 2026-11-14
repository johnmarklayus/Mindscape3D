# Mindscape 3D: From Scratch to Deployment

This guide follows Mindscape 3D through its whole life: setting up a computer, making the art, building scenes and episodes, connecting online accounts, testing, building for every platform, and publishing. Read it once from top to bottom to see how the parts fit together. After that, use it as a checklist.

Each section points to the detailed page on the documentation site (`Documents/Website/src/content/docs/`) when you need more depth.

---

## 1. What you are building

Mindscape 3D is a third-person story game made in **Unity 6** about the everyday pressures students face. The player plays as Joey (boy or girl) through a tutorial and three chapters:

| Chapter | Episodes | Setting |
|---|---|---|
| Tutorial | 1 | Movement, the menu and the journal |
| 1 · Academic Pressure | 4 | House, classroom, cafeteria, dormitory |
| 2 · Family Expectations | 5 | An examination day and the family at home |
| 3 · Social Dynamics | 8 | A reunion with old friends, the walk home, the mirror |

The game ships on **WebGL (browser), Android, macOS and Windows**. Progress is saved on the device. With an optional online account (Supabase), progress and the journal are also kept in the cloud.

### The pipeline at a glance

```text
 Blender (.blend)  ──export FBX/GLB──▶  Unity Assets/Models, Assets/Characters
                                              │
 Story spec (PDF) ──▶ episode script (C#) ──▶ │  Mindscape menu builders place everything
                                              ▼
                                    Assets/Scenes/*.unity  (one scene per episode)
                                              │
                         Play-test in the editor + tester lists + QA workbook
                                              │
                     Tools/BuildScripts/*.sh  (Unity in batch mode)
                                              ▼
                    Builds/<date>/  APK · macOS app · Windows exe · WebGL
                                              │
           ┌──────────────────────────────────┼──────────────────────────────┐
           ▼                                  ▼                              ▼
  Builds/webgl-play → Vercel         Site/ (official website)       Documents/Website
  (play in the browser)              downloads + /play page          (documentation site)

 supabase/ (database migrations + "account" edge function) ◀── game talks to it over HTTPS
```

---

## 2. Set up your computer

### Software

| Tool | Version | Used for |
|---|---|---|
| Unity Hub + **Unity 6000.5.8f1** | exactly this version | The game |
| Unity modules | Web Build Support, Android Build Support (with OpenJDK, SDK & NDK), Windows Build Support (Mono), Mac Build Support | Building each platform |
| Blender | 4.x | Models, characters, animation |
| Node.js | 20.9 or newer | Documentation site and official website |
| Git | any recent version | Version control |
| Vercel CLI | `npm i -g vercel` | Publishing the websites and the web build |
| Supabase CLI | optional | Rebuilding the online backend |
| An IDE | VS Code with the Unity extension, or Rider | Editing C# |

On a Mac you can build all four platforms. Windows builds use the **Mono** backend, because IL2CPP cannot cross-compile from a Mac.

### Get the project

```bash
git clone <repository-url> mindscape-3d
cd mindscape-3d
```

In Unity Hub choose **Add › Add project from disk** and select the folder. The first time the project opens, Unity spends several minutes rebuilding `Library/`.

### Main Unity packages

- **Universal Render Pipeline (URP) 17.5**, with separate PC and Mobile render assets in `Assets/Settings/`
- **Input System 1.20**: keyboard, mouse, gamepad and the on-screen touch controls (`Resources/GameControls.inputactions`)
- **UI Toolkit**: every screen is a `.uxml` layout with a `.uss` style in `Assets/UI Toolkit/`
- **AI Navigation**: NPC walking
- **TextMesh Pro** and **uGUI**, both still used in a few places

### First run

Open `Assets/Scenes/Intro.unity` and press **Play**. You see what a player sees: the intro video, the title, then the main menu. To test a single episode, open its scene (for example `Chapter 2 - Episode 1.unity`) and press Play.

> Detailed pages: `00c-beginner-guide.md`, `02-structure.md`, `03-tech-stack.md`.

---

## 3. Project layout

```text
mindscape-3d/
├── Assets/            The game: Scenes, Scripts, Editor tools, Models, Characters, UI Toolkit, Resources …
├── Blender/           Source art (.blend), exports, and Blender Python build/export scripts
├── Builds/            Finished builds, one folder per date (not in git)
├── Documents/         Documentation site, story specs, tester lists, QA reports, concepts
├── Site/              Official public website (Next.js + Chakra UI)
├── Tools/             BuildScripts/, NativePlugins/, QA/
└── supabase/          Online accounts backend (migrations + edge function)
```

Where code lives:

| Area | Folder |
|---|---|
| Story base: dialogue, choices, camera shots, free roaming, save replay | `Assets/Scripts/Story/AcademicEpisode.cs` |
| One script per episode (lines, choices, order) | `Assets/Scripts/Chapters/Chapter N - …/` |
| Player, camera, input | `Scripts/Player`, `Scripts/Camera`, `Scripts/Input` |
| NPCs and conversations | `Scripts/NPC`, `Scripts/Dialogue` |
| Doors, bed, collectibles, [E] prompts | `Scripts/Interaction` |
| Minigames (breathing, Worry Courtroom …) | `Scripts/Minigames` |
| Saves, progress, accounts, cloud sync | `Scripts/Data` |
| Editor tools: the **Mindscape** menu, scene builders, checks | `Assets/Editor/<area>` (never part of a build) |

**Rule:** move or rename assets only in Unity's Project window. Each file's `.meta` holds the ID that scenes and prefabs use to find it, so moving a file outside Unity without its `.meta` breaks every reference to it.

---

## 4. Make the art (Blender → Unity)

All 3D art starts in `Blender/Blend Files/`:

| Blend file | Becomes |
|---|---|
| `world_new.blend` | The shared city (`Assets/Models/World/world_new.glb`), used in every story scene |
| `house-and-lot-cozy.blend` | Joey's house |
| `school-grounds.blend` | School, cafeteria, dormitory, reunion hall |
| `Main_Character_Outfit_Lineup.blend` | Boy and girl player models, outfits, the worn backpack |
| `NPC_Roster.blend` | The 20 NPCs |
| `Boy_Sleeping_In_Bed.blend` | Joey's bed with sleeping / messy / neat states |
| vehicles, furniture, doors, logo | Props and the 3D title |

### Workflow

1. Edit the `.blend` file. Keep a copy in `Backups/` before large changes.
2. Export over the matching file in `Assets/Models/…` or `Assets/Characters/…`. Scripts in `Blender/Scripts/` (`export-world.py`, `export-family.py` …) can run Blender headless: `blender -b file.blend -P script.py`.
3. FBX settings that matter:
   - **Apply Scalings: FBX Units Scale**. Without it, NPCs import 100× too big.
   - **Bake space transform** has to match the model. If a mesh arrives lying on its side (Z-up), re-export, then refit any colliders that were sized on the old import.
4. In Unity, run the matching **Mindscape** menu sync (for example *World › Sync*, *House › Install Joey Bed*). It places the new model in every scene that uses it and repairs references, so you don't fix each scene by hand.

> Detailed page: `03a-workflow-blender-assets.md`.

---

## 5. Build scenes and episodes

### How an episode works

Every story scene contains one **episode component**: a C# class that derives from `AcademicEpisode`. Its `Play()` coroutine is the episode's script:

```csharp
yield return Card("CHAPTER 3 · SOCIAL DYNAMICS\nEpisode 04 · The Corner of the Room");
yield return Visit(4, "A little space", "Sit by the window", "Maybe I shouldn't have come.");
yield return Choose(prompt, question, options, i => Response = i);
Complete(title, "You took another step through the evening.");
```

The base class handles the rest:

- **Spots** (`AddSpot`, `AddArrival`): a place in the world with an [E] prompt or an arrival trigger.
- **Roaming** (`RoamUntil`): free movement until a condition is met.
- **Dialogue** (`Say`, `Me`, `Think`, `DialogueSequence`): the dialogue box with its "x / n" counter.
- **Camera** (`Shot`, `ShotOver`, `Glide`): story shots that keep clear of walls.
- **Poses**: `SitAt` / `StandUpAt`, `LieInBed` / `GetUp`.
- **Save replay**: every spot the player uses is recorded, so loading a save replays those steps and resumes where the player left off.

### Making or changing an episode

1. Read the chapter spec in `Documents/Story Specs/`. Follow the tone rules: neutral, non-triggering language (`01c-story-tone.md`).
2. Write or edit the episode script in `Assets/Scripts/Chapters/Chapter N - …/`.
3. Run the chapter builder from the **Mindscape** menu. It creates or updates the scene: the world model, spots, cameras, NPCs and props. Builders are safe to re-run.
4. Add ambient life with **Mindscape › NPCs › Add Ambient Life**: walkers, joggers, and the family in the house.
5. Add the scene to **File › Build Profiles**. The game currently ships 22 scenes: Intro, main_menu_new, Tutorial, Ch1 1–4, Cutscene – Episode 1, Ch2 1–5, MinigameTestLab, Ch3 1–8.

### UI

Every screen is a UXML file in `Assets/UI Toolkit/`, listed in `Resources/EpisodeUI.asset`. Edit layouts in **Window › UI Toolkit › UI Builder**. Controllers look up elements by `name`, so keep names unchanged when you restyle a screen.

> Detailed pages: `04-workflow-scene.md`, `04a-workflow-episode-chapter.md`, `05-workflow-npc.md`, `08-workflow-door.md`, `09-workflow-cutscene.md`, `12a-system-episode-ui.md`, `13a-system-minigames.md`, `17-ref-menu-items.md`.

---

## 6. Saves and online accounts (Supabase)

**Offline:** progress, choices and the journal are saved on the device with SQLite (local storage in the browser), separately for each profile.

**Online (optional):** `Assets/Scripts/Data/MindscapeCloud.cs` talks to a Supabase project:

- **Database**: tables for players, progress, journal entries, assessments and episode records. The tables are closed to the public key, so the game reads and writes only through RPC functions.
- **Edge function `account`**: sign-up with an email code (OTP), sign-in, Google sign-in hand-off, a 30-day account archive (delete) and recovery.

### Set up a new Supabase project

```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push                                  # runs supabase/migrations in order
supabase functions deploy account
supabase secrets set RESEND_API_KEY=... MAIL_FROM="Mindscape <no-reply@your-domain>"
```

`SUPABASE_URL`, `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` are provided to the function automatically. Then put the new project URL and publishable key in `MindscapeCloud.cs`. Never put the service-role key in the game.

> Detailed pages: `03b-workflow-supabase.md`, `03c-workflow-supabase-data.md`, `12b-system-accounts.md`.

---

## 7. Test

1. **In the editor:** play the episode scene directly, then the full flow from `Intro`. Check it with keyboard and mouse, with a gamepad, and in mobile mode (the touch overlay).
2. **Tester lists:** feedback is collected in `Documents/Tester Lists/`. Each fix is checked against the list item.
3. **QA workbook:** `Tools/QA/` writes the master workbook to `Documents/Reports/`.
4. **Batch probe (no editor open):** `Assets/Editor/Tests/ShotProbe.cs` opens a scene in batch mode to render shots, cast rays or run builders. It's useful for checking where things are placed without opening Unity:

   ```bash
   /Applications/Unity/Hub/Editor/6000.5.8f1/Unity.app/Contents/MacOS/Unity -batchmode \
     -projectPath "$PWD" -executeMethod ShotProbe.Run \
     -probeFile cmds.txt -probeOut out/ -logFile out/unity.log -quit
   ```

5. **Before every build:** check the Console for errors, and check that the scene list in Build Profiles is complete.

---

## 8. Build

### Version numbers

Set them in **Project Settings › Player** before a release:

- **Version** (`bundleVersion`), for example `0.3.0`
- **Android Bundle Version Code**: raise it by 1 for every APK you hand out, or installs over an older APK fail

### Command-line builds (recommended)

**Close Unity first.** Only one Unity can have the project open at a time. Then, from the project folder:

```bash
./Tools/BuildScripts/build-android.sh   # ~2–10 min → Builds/<date>/Mindscape-<date>.apk
./Tools/BuildScripts/build-mac.sh       # ~8 min     → Builds/<date>/Mindscape-macOS-<date>.zip
./Tools/BuildScripts/build-windows.sh   # ~9 min     → Builds/<date>/Mindscape-Windows-<date>.zip
./Tools/BuildScripts/build-webgl.sh     # ~15–26 min → Builds/<date>/Mindscape-WebGL-<date>.zip
```

Each script starts Unity in batch mode with `CommandLineBuild.<Platform>` (`Assets/Editor/Build/CommandLineBuild.cs`), shows progress lines, and writes a log to `Builds/<date>/logs/`. To build all four in a row:

```bash
for p in android mac windows webgl; do ./Tools/BuildScripts/build-$p.sh || break; done
```

You can also build from the editor with **File › Build Profiles › Build**. If you switch platform first, wait until scripts have finished compiling, or the build fails with "scripts are compiling".

### Platform notes

| Platform | Notes |
|---|---|
| Android | Debug-signed unless you set up a release keystore (**Player › Publishing Settings**). Install with `adb install -r <apk>`. Set a real `applicationIdentifier` before publishing to a store. |
| macOS | ARM64, Mono, ad-hoc signed, not notarised. The first time, players right-click the app and choose **Open**. |
| Windows | Mono. Players unzip and run `Mindscape.exe` with its files beside it. |
| WebGL | IL2CPP, Brotli compression. The web host must serve `.br` files with `Content-Encoding: br`. |

Leave the `*_BurstDebugInformation_DoNotShip` folders out of anything you share.

---

## 9. Deploy

There are three web destinations. Each is its own Vercel project.

### 9a. Play in the browser (WebGL build)

`Builds/webgl-play/` is the published copy of the web build. It contains a customised `index.html` (full-window on every device) and a `vercel.json` that sends `Content-Encoding: br` and the right content types for `/Build/*.br`.

```bash
rsync -a --delete \
  --exclude index.html --exclude vercel.json --exclude .vercel --exclude '*_DoNotShip' \
  Builds/<date>/WebGL/Mindscape/ Builds/webgl-play/
cd Builds/webgl-play
vercel --prod --yes
curl -sI https://<your-deployment>/Build/Mindscape.wasm.br | grep -i content-encoding   # expect: br
```

Keep `index.html` and `vercel.json` when you sync. Build files are named `Mindscape.*`.

### 9b. The official website (`Site/`)

A Next.js 16 + Chakra UI site with a landing page, downloads, a contact form, legal pages and a `/play` page that runs the WebGL build.

1. Set the environment variables from `Site/.env.example` in Vercel. They include `NEXT_PUBLIC_SITE_URL` and the download links `NEXT_PUBLIC_DOWNLOAD_WINDOWS` / `_MACOS` / `_ANDROID`. The build files are over Vercel's 100 MB file limit, so host them elsewhere (for example GitHub Releases or cloud storage) and link to them.
2. Copy the latest WebGL build into the site: `npm run sync-game` (in `Site/`).
3. Deploy from your computer: `npx vercel --prod`. A Git-connected deploy does not include the game files, which are not in git.
4. Add your domain under **Vercel › Settings › Domains**.

### 9c. The documentation site (`Documents/Website/`)

A Vite + React site. Its pages are the Markdown files in `src/content/docs/`.

```bash
cd Documents/Website
npm install
npm run sync         # copies current script sources for the annotated code pages
npm run build        # check it builds
vercel --prod
```

APKs and other large files are listed in `.vercelignore`, because Vercel rejects any single file over 100 MB.

### 9d. Native downloads

Upload the APK and the macOS and Windows zips to your file host, then update the download links in the official website's environment variables and redeploy.

---

## 10. Release checklist

- [ ] All tester-list items for this release are fixed and re-tested
- [ ] Console has no errors; all 22 scenes are enabled in Build Profiles
- [ ] Version and Android version code raised
- [ ] Unity closed → four builds run → each log ends with `Build Finished, Result: Success`
- [ ] APK installed on a phone; macOS and Windows builds launched once
- [ ] WebGL synced to `Builds/webgl-play` → `vercel --prod` → `.br` headers checked
- [ ] Native downloads uploaded; website links updated; `Site/` redeployed
- [ ] Supabase migrations and the `account` function up to date (if backend changed)
- [ ] Documentation pages updated for anything that changed
- [ ] Changes committed and pushed (builds stay out of git)

---

## 11. Common problems

| Symptom | Cause and fix |
|---|---|
| Build stops immediately: "another Unity instance" | The editor still has the project open. Close it, or delete a stale `Temp/UnityLockfile`. |
| Build fails with "scripts are compiling" | It started straight after a platform switch. Wait for compiling to finish, then build again. |
| Web build shows a decompression error | The host isn't sending `Content-Encoding: br`. Use the `vercel.json` in `Builds/webgl-play`. |
| Vercel: "File size limit exceeded (100 MB)" | An APK or zip was included. Add it to `.vercelignore` and host it elsewhere. |
| NPCs 100× too big after an export | FBX scale setting. Re-export with *FBX Units Scale*, or run the NPC scale repair. |
| Objects float or the player bumps into invisible walls near a model | Its colliders were sized on an older import. Refit them (for the bed: **Mindscape › House › Refit Joey Bed Colliders**). |
| Broken references after moving files | The `.meta` was not moved with the file. Move files only inside Unity. |
| GitHub rejects a push | A file is over 100 MB (builds, the full-size intro video). Keep them in `.gitignore`. |
