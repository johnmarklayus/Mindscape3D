---
id: ref-menu-items
group: Reference
nav: Editor Menu Items
---

# Editor Menu Items

Every custom Editor tool in the project, and what it does.

## GameObject menu

| Menu Path | What it does |
| --- | --- |
| `GameObject ▸ NPC` | Adds an NPC (with the shared dummy model) and ensures NPCInteractionManager exists. |
| `GameObject ▸ Quest` | Adds a Quest and ensures the Quest HUD exists. |
| `GameObject ▸ Quest HUD` | Builds the Quest Journal UI Toolkit panel directly. |
| `GameObject ▸ Collectible` | Adds a Collectible and ensures CollectiblesManager exists. |
| `GameObject ▸ Minigame ▸ Breathing Minigame` | Adds a Breathing Minigame object. It spawns its screen from `Breathing.uxml` when the scene starts. |
| `GameObject ▸ Cutscene ▸ Slides / Slide / Text / Next Button / Play Episode Button` | Builds cutscene scaffolding piece by piece. |

## Mindscape menu

| Menu Path | What it does |
| --- | --- |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ Build Cutscene Slides` | Rebuilds Episode 1's four-slide cutscene with art and narration. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ Populate House NPCs` | Places Mom, Dad and Tim with name tags and their dialogue, and sets the Quest's required people. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ Add NPC Wandering` | Places waypoints and `NPCWander` on the three NPCs, and checks each route for obstacles. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ Add Worry Courtroom and Breathing Screen` | Adds the courtroom prefab and presentation case and registers both minigames on the Quest. |
| `Mindscape ▸ Minigame Lab ▸ Create or Open Test Scene` | Creates or opens the ten-minigame practice lab. |
| `Mindscape ▸ Minigame Lab ▸ Verify All Games (Play Mode)` | Runs automated checks on the lab minigames. |
| `Mindscape ▸ Main Menu New ▸ Create Scene` | Builds the newer main menu scene. The menu's pages themselves live in `MainMenuNew.uxml`; edit them in UI Builder. |
| `Mindscape ▸ Verify ▸ Story Shot Clearance` | Walks the player around every story shot target at every interaction distance and fails if a shot ends up inside the body's clearance (see [Camera & Story Shots](#system-camera)). |

### Story (making and editing episodes)

| Menu Path | What it does |
| --- | --- |
| `Mindscape ▸ Story ▸ New Chapter…` | Makes a chapter (Chapter 4 and later) as an asset in `Assets/Resources/Chapters/`: number, name, description and an imported picture. The main menu, loading screen, progress and journal read it by themselves. See [Onboarding](/onboarding#create-chapter). |
| `Mindscape ▸ Story ▸ New Cutscene…` | Makes a slide cutscene (pictures with words) from pictures on your computer, and can set it to play before an episode or as a scene of its own. See [Onboarding](/onboarding#create-cutscene). |
| `Mindscape ▸ Story ▸ New Cinematic (in the open scene)` | Adds a cinematic to the open episode scene: a place, a camera view from the Scene view and a first line, edited as a list of steps in the Inspector. See [Onboarding](/onboarding#create-cinematic). |
| `Mindscape ▸ Story ▸ New Conversation` | Makes a conversation asset in `Assets/Story/Conversations` (lines with who speaks and the words), played by a cinematic step. See [Onboarding](/onboarding#create-conversation). |
| `Mindscape ▸ Story ▸ New Exam Paper` | Makes an exam paper in `Assets/Story/Exams` (up to 5 questions, 3 answers each) for the cinematic step *Minigame: exam paper*. See [Onboarding](/onboarding#minigame-steps). |
| `Mindscape ▸ Story ▸ Edit Dialogue Words (Chapters 1-3)` | Lists every line the Chapter 1–3 scripts show in `Assets/Resources/Story/Dialogue Words.asset`, where each can be changed in the Inspector. See [Onboarding](/onboarding#edit-words). |
| `Mindscape ▸ Story ▸ New Episode…` | Makes a new episode scene by copying an existing one (place, lighting, player, camera), adds it to the build list and, if asked, writes a starter story script and puts it in the scene. See [Onboarding](/onboarding#create-episode). |
| `Mindscape ▸ Story ▸ Create Missing Story Markers (All Episode Scenes)` | Adds a Story Marker for every position an episode works out in code (people at the door, the sofa seat, story cameras), at its built-in place, so it can be dragged in the Scene view. Episodes also have a button for this in their Inspector. |
| `Mindscape ▸ House ▸ Refit Joey Bed Colliders (all scenes)` | Fits the bed's collision boxes to its meshes in every house scene, without moving the bed. |

### Chapters (legacy builders)

The chapter builders generated the episode scenes once. The scenes are now edited by hand, so a rebuild replaces those edits; every rebuild asks first (in batch mode it needs the `-mindscapeRebuild` flag).

| Menu Path | What it does |
| --- | --- |
| `Mindscape ▸ Legacy Builders ▸ Chapter 1 - Academic Pressure ▸ Build All Episodes` | Rebuilds the four Chapter 1 scenes. Each episode also has its own item (`Build Episode 1 - House` to `Build Episode 4 - Dormitory`). Save unrelated scene work first. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 1 - Academic Pressure ▸ Episode 4 - Add the Walk From the Cafeteria` | Adds the cafeteria start, the route to the dorm and the three studying roommates to the existing Episode 4 scene. Safe to re-run. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 1 - Academic Pressure ▸ Populate Episode 1 Street` | Rebuilds the Street Life NPCs, their sidewalk routes and the Nia and Hana conversation in the open house scene. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 1 - Academic Pressure ▸ Move Family Expectations to Chapter 2` | One-off move of the old family scenes into Chapter 2. |
| `Mindscape ▸ Reveal Database File` | Shows the SQLite save file in the file manager. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Build All Episodes` | Rebuilds the five Chapter 2 scenes (per-episode items, and `Episode 4 - Update the Dinner Table`, are listed beside it). |
| `Mindscape ▸ Legacy Builders ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ ...` | Bedroom layout, house NPCs, NPC wandering, cutscene slides and the courtroom for the original Episode 1. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 3 - Social Dynamics ▸ Build All Eight Episodes` | Generates the eight Chapter 3 scenes. |
| `Mindscape ▸ Legacy Builders ▸ Chapter 3 - Social Dynamics ▸ Rebuild the Reunion Episodes (2-6)` | Rebuilds only the five reunion scenes. |
| `Mindscape ▸ Chapter 3 - Social Dynamics ▸ Verify All Episodes (Play Mode)` | Runs every Chapter 3 story coroutine and reports to `Temp/SocialDynamicsVerification.txt`. |

### The shared city and its people

| Menu Path | What it does |
| --- | --- |
| `Mindscape ▸ World ▸ Rebuild World Prefab` | Re-wraps `Models/World/world_new.glb` as `Prefabs/World.prefab` with colliders. |
| `Mindscape ▸ World ▸ Rebuild Vehicle Prefabs` | Rebuilds the six vehicle prefabs from `Models/Vehicles/`. |
| `Mindscape ▸ World ▸ Apply World to Open Scene` | Fits the city, opens the world, and adds street NPCs and traffic in the open scene. |
| `Mindscape ▸ World ▸ Apply World to All Story Scenes` | Does it for every `Chapter N - Episode N` scene and the Tutorial. See [Shared City & Traffic](#system-world). |
| `Mindscape ▸ NPCs ▸ Add Ambient Life to All Story Scenes` | Adds five walkers or joggers, the family where missing, and "F to talk" on every character, in every story scene. Safe to re-run. |
| `Mindscape ▸ NPCs ▸ Build Family Talk Controllers` | Builds Idle, Talk and Walk animator controllers for Mom, Dad and Tim in `Resources/FamilyTalk`, used by the welcome-home scenes. Re-run after changing their clips. |
| `Mindscape ▸ NPCs ▸ Build All 20 NPC Prefabs` | Builds the NPC prefabs from the character roster. |
| `Mindscape ▸ NPCs ▸ Give the Family Their Cast Models (All Scenes)` | Swaps Mom, Dad and Tim to the cast models in every scene. |
| `Mindscape ▸ Doors ▸ Rebuild Door Prefabs` | Rebuilds `Prefabs/Doors` from the Blender door models and their swing clips. |
| `Mindscape ▸ Doors ▸ Apply Doors to Open Scene / All Story Scenes` | Puts an animated door in every doorway. Safe to re-run. See [Doors](#workflow-door). |
| `Mindscape ▸ House ▸ Sync House Model (open scene / all house scenes)` | Adds the house model's newer parts to scenes that hold an older copy. |
| `Mindscape ▸ School ▸ Sync Updated Campus in All Scenes` | Repairs colliders and roofs after the school model changes. |
| `Mindscape ▸ Vehicles ▸ Build School Bus Prefabs` | Builds the story's `SchoolBus.prefab` (the one used in the Episode 1 bus ride). |
| `Mindscape ▸ Collectibles ▸ Build All 12 Collectible Prefabs` and `Use Collectible Models (Chapters 1-2)` | Builds the pickup prefabs and applies their models. |
| `Mindscape ▸ Animations ▸ ...` | Audits and validates shared animation bindings and classroom seating. |

## Tools menu

| Menu Path | What it does |
| --- | --- |
| `Tools ▸ Build HUD Panels` | Builds HUDCanvas with the Tasks panel and wires PlayerControls. |
| `Tools ▸ Build HUD Buttons` | Adds the Tasks and Menu buttons to HUDCanvas. |
| `Tools ▸ Build Mobile Controls` | Rebuilds a hand-placed on-screen controls overlay (its own Canvas). Gameplay scenes without one get the same overlay built at runtime by `MobileControls`. |
| `Tools ▸ Setup UI Toolkit Quest HUD` | Creates or repairs the Quest Journal UIDocument. |
| `Tools ▸ Setup UI Toolkit Pause Menu` | Creates or repairs the Pause Menu UIDocument. |
| `Tools ▸ Steve ▸ Set Up Walk and Run` | Configures the player's Animator states and transitions for `Assets/1_Steve.fbx`; requires the model and Edit Mode. |
| `Tools ▸ Steve ▸ Validate Animation Playback` | Checks Idle, Walk and Run on a temporary model instance; warns and returns if the model is missing. |

## Component right-click menus

The Breathing Exercise and Worry Courtroom no longer have component right-click builders. Their screens are UXML files in `Assets/UI Toolkit/` that you edit in UI Builder.

## Assets ▸ Create

| Item | What it creates |
| --- | --- |
| `Mindscape ▸ Worry Courtroom Case` | A new trial (worry, evidence, answers) as an asset. |
