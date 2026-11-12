---
id: story-ch1
group: Story
nav: Chapter 1 · Academic Pressure
---

# Chapter 1 · Academic Pressure

The whole chapter happens around one school deadline: a research project due tomorrow at 11:59 PM. The player character uses the name the player types at the start of Episode 1 (the default is "Joey"). Every episode is told through short scenes, choices and free exploration, with a free-play countdown per episode (dialogue, choices and minigames do not use it up), a stress meter with a check-in at the end, and a failure screen if the time runs out.

> [!TIP] How to build it
>
> `Mindscape > Chapter 1 - Academic Pressure > Build All Episodes` rebuilds the four scenes. Each episode also has its own build item. Save unrelated scene work first.

## The four episodes

| Episode | Scene | Script | Where |
| --- | --- | --- | --- |
| 1 · Tomorrow Already? | `Chapter 1 - Episode 1` | `HouseEpisode` | The house, the street and the bus stop |
| 2 · The Announcement | `Chapter 1 - Episode 2` | `ClassroomEpisode` | The school gate, the yard and Room 03 |
| 3 · Everyone Seems Ahead | `Chapter 1 - Episode 3` | `CafeteriaEpisode` | The corridor and the cafeteria |
| 4 · One Step at a Time | `Chapter 1 - Episode 4` | `DormitoryEpisode` | The dormitory |

Episodes 2 to 4 share one school grounds model (`Models/School_Grounds.glb`): the street and bus stop outside the gate, the yard with a library and a hall, Rooms 01 to 04 on a covered corridor, the cafeteria at one end and the dormitory at the other.

### 1 · Tomorrow Already? (house)

Enter a name. Check the phone: "Research Project Submission, Tomorrow 11:59 PM". Open the laptop and choose a plan (finish everything tonight, or start with one task first), then name the feeling behind "What if I fail this project?". Pack the books and the school bag, make the bed, clear and wash the breakfast plate, leave by the front door, follow the blue markers to the bus stop and ride the school bus.

### 2 · The Announcement (classroom)

The bus stops at the school gate. Follow the blue markers across the yard and along the corridor to Room 03, walk in and take your seat. The teacher announces the deadline and a classmate is almost finished; the morning's plan changes one inner line. Talk to Sam (three replies that come back together), take a moment, and try the Breathing Exercise.

### 3 · Everyone Seems Ahead (cafeteria)

Start outside Room 03 and follow the corridor to the cafeteria. Two students seem ahead, and the thought "Everyone is ahead of me, so I'm not good enough" goes to the **Thought Courtroom**: evidence for, evidence against, and a balanced thought (pick one or write your own).

### 4 · One Step at a Time (dormitory)

After lunch, walk the corridor from the cafeteria to the dormitory (gold markers; hold Shift to run). The dorm door opens and closes from both sides, so you can step out and back in. Inside, three roommates (Zara, Noah and Mei) are studying at the shared table; walk up and press E to talk to them.

Sit at the desk and look at the unfinished project. What happens next follows the plan chosen at the laptop in Episode 1:

| Episode 1 plan | In the dorm |
| --- | --- |
| A · "I'll finish everything tonight." | No break on arrival. All four tasks are worked through back to back; each takes longer than the last, the status line gets more tired and stress rises. When the fourth is done Joey is exhausted, and the breathing exercise opens. |
| B · "I'll start with one task first." | A breathing exercise on arrival, then one small task from the list. |

A profile with no Episode 1 choice follows plan A. Then write a reflection journal entry, answer the short self-reflection (how overwhelmed, which coping strategy helped most), and read "Your Reflection" (not a medical diagnosis). Episode 4 ends with "Begin Chapter 2".

> [!MENU] Mindscape ▸ Chapter 1 - Academic Pressure ▸ Episode 4 - Add the Walk From the Cafeteria
>
> Adds the start outside the cafeteria, the route markers and the three roommates to the existing Episode 4 scene (safe to re-run; the "Dorm walk" group is rebuilt). `Build Episode 4 - Dormitory` runs it too.

## Playing

| Action | Control |
| --- | --- |
| Move | W A S D |
| Look around | Move on the trackpad or mouse, or use the arrow keys |
| Turn / zoom | Two-finger swipe sideways / up and down |
| Run | Hold Shift |
| Interact | E (gold markers over objects) |
| Talk to people on the street | F |
| Advance / choose | Space or Enter, or click; 1 to 9 for choices |
| Pause (hint and full controls list) | Esc |

The bottom of the screen only shows a prompt when something can be used ("[ E ] Check your phone"). The current hint and the full controls live in the pause menu.

## What is in the world

- **People.** Everyone is built at 1.4 times the original rig, so the player stands slightly taller than the kitchen sink. Classmates, the teacher, the cook and the street neighbours are scaled the same way, so nobody looks out of proportion.
- **The street (Episode 1).** Neighbours walk the sidewalk with walk and idle animations; press F to talk to them.
- **The school bus.** One bus model with rolling wheels, engine idle and suspension sway drives the trip to school in Episodes 1 and 2.
- **Story items.** The phone, laptop, books, school bag, breakfast plate, notebook, examination paper, student ID and research notes use the collectible models in `Assets/Models/Collectibles`.
- **Route markers.** Glowing blue discs show the way when the story asks you to walk somewhere.

## Saved data

Choices, the journal entry and the self-reflection are saved by `MindscapeDatabase`: SQLite on desktop and mobile, local storage in the web build. Choice keys are listed in `AcademicPressureChapter` (`laptop_plan` (`finish_everything` or `one_task`, read again in Episode 4), `feeling`, `friend_reply`, `breathing`, `balanced_thought`, `first_task`, plus `evidence_for` and `evidence_against`).
