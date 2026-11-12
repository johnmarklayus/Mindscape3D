---
id: overview
group: Start Here
nav: Overview
---

# Mindscape 3D

A third-person narrative exploration game built in Unity about everyday pressure and meeting it calmly. You play a student (in Chapter 1 under the name you choose, in Chapter 2 as **Joey**), moving through ordinary places (a house, a classroom, a cafeteria, a dormitory), talking with the people there, collecting small story items, and trying short, gentle wellbeing exercises. This site documents the story and how the project is put together, so you can add scenes, NPCs, quests, minigames and episodes without reverse-engineering the codebase first.

> [!TIP] Who this is for
>
> Anyone working in this Unity project. If you have never used Unity or written code, begin with [Beginner Start Here](#beginner-guide). Writers can continue to the [Story](#story-ch1) section, designers can use the custom `GameObject` and `Mindscape` menu tools, and programmers can extend the gameplay scripts.

> [!WARN] Not a replacement for care
>
> Mindscape 3D is an educational, reflective experience. It is not a substitute for professional care, and its support screens show the NCMH Crisis Hotline (1553). Keep that in mind when writing anything the player will read. The [Writing Guidelines](#story-tone) explain the tone.

## How the game is structured

- **Chapters and episodes.** Three chapters and 17 playable episodes. Chapter 1 ("Academic Pressure", 4 episodes: House, Classroom, Cafeteria, Dormitory) is built around one research-project deadline. Chapter 2 ("Family Expectations", 5 episodes) follows Joey from the family house to school and back for an evening at home. Chapter 3 ("Social Dynamics", 8 episodes) takes him to a school reunion and home again. See [Chapter 1 · Academic Pressure](#story-ch1) and [Chapters 2 and 3](#story-ch2-ch3).
- **All 17 episodes run on one story base.** Every episode derives from `AcademicEpisode`: title cards, dialogue, choices, free exploration with E-to-interact markers, a free-play countdown (dialogue, choices and minigames do not use it up), a stress meter with a check-in before and after, and a failure screen if time runs out.
- **One shared city.** Every episode and the Tutorial sits inside the same open-world city model, with sidewalk walkers and driving vehicles. See [Shared City & Traffic](#system-world).
- **The older `Quest` flow still exists.** The Worry Courtroom and its quest-based Chapter 2 prototypes are kept in `Scenes/Prototypes/`; the quest is the win/lose condition there: talk to specific people, collect items, finish minigames, keep stress in range, and beat a timer.
- **Minigames.** The [Breathing Exercise](#minigame-breathing) appears in Chapter 1 Episode 2 and in Chapter 2, the Thought Courtroom in Chapter 1 Episode 3, and the [Worry Courtroom](#minigame-courtroom) in Chapter 2. See [Minigames](#system-minigames).
- **Everything is themed.** Dialogue, the pause menu and the minigames share one warm parchment, ink and brass look. See [UI Theme](#system-theme).

## Where to start

| If you want to... | Read |
| --- | --- |
| Learn Unity safely with no programming experience | [Beginner Start Here](#beginner-guide) |
| Take over the project (setup, Supabase, editing, building) | [Handover Guide](#handover) · [Tagalog](#handover-tl) |
| Understand the story | [Chapter 1 · Academic Pressure](#story-ch1), then [Chapter 2 · Episode 1](#story-ch1-ep1) |
| Write or edit dialogue | [Writing Guidelines](#story-tone), then [Create an NPC](#workflow-npc) |
| Add a person who walks around | [NPC Wandering & Name Tags](#workflow-npc-wander) |
| Add a new scene or episode | [Create a Gameplay Scene](#workflow-scene) |
| Understand or update the city, sidewalks and traffic | [Shared City & Traffic](#system-world) |
| Add a win condition | [Create a Quest](#workflow-quest) |
| Add or change a minigame | [Minigames](#system-minigames) |
| Change the camera, first person or what the player's body hides | [Camera & Story Shots](#system-camera) |
| Edit a story screen in UI Builder | [Episode Screens (UI Toolkit)](#system-episode-ui) |
| Understand accounts, progress and saves | [Accounts, Progress & Saves](#system-accounts) |
| Find a menu command | [Editor Menu Items](#ref-menu-items) |
| Read a script line by line | [Scripts](#scripts) |

## Two UI systems, on purpose

**UI Toolkit** (UXML + USS + UIDocument) now draws almost everything: every story screen, the NPC conversation panel, the minigames, the Quest Journal, Pause Menu, Stress HUD, the crosshair and every page of the Main Menu. Legacy **uGUI** (Canvas + Image + Button) remains for the mobile controls overlay, the loading screen, the intro, the Tutorial HUD, cutscene slides and the "F to collect" prompt. See [HUD, Journal & Pause](#system-hud) and [Episode Screens (UI Toolkit)](#system-episode-ui) for the split.
