---
id: story-ch2-ch3
group: Story
nav: Chapters 2 · 3
---

# Chapters 2 and 3

Chapter 2 and Chapter 3 follow **Joey**, the same student from the family house, and are built the same way as Chapter 1: every episode is a story scene on `AcademicEpisode`, with title cards, gentle dialogue, choices, free exploration, a free-play countdown, and a stress check-in at the end. Both chapters are written to the [Writing Guidelines](#story-tone): calm, neutral and non-triggering.

All episodes sit inside the same [shared city](#system-world), so the street outside the house in Chapter 2 is the same street Joey walks home along in Chapter 3.

## Chapter 2 · Family Expectations

Five episodes (`Chapter 2 - Episode 1` to `5`). The family (Mom, Dad and Tim) lives in the house of Chapter 1 Episode 1, and the school episode is set in the same classroom as Chapter 1 Episode 2.

| Episode | Title | Script | Where |
| --- | --- | --- | --- |
| 1 | The Paper on the Desk | `FamilyAfterSchoolEpisode` | The house, after school |
| 2 | Before the Bell | `FamilyMorningEpisode` | The house, in the morning |
| 3 | Running Out of Time | `FamilyExamEpisode` | The classroom (Room 03) |
| 4 | The Weight Behind the Worry | `FamilyFinaleEpisode` | The house in the evening, with the family dinner |
| 5 | What I Left Behind | `FamilyFinaleEpisode` | The house; it continues into Chapter 3 |

> [!MENU] Mindscape ▸ Chapter 2 - Family Expectations ▸ Build All Episodes
>
> Rebuilds all five scenes. Each episode also has its own build item, and `Episode 4 - Update the Dinner Table` rebuilds only the dinner set. Save unrelated scene work first.

### Episode 1 · coming home from the examination

Episode 1 opens on the bus home: a school bus from the city traffic comes down the street and stops at the shelter, Joey gets off, and the walk up to the house is playable. Mom (and Tim) wait just inside the front door; Mom walks up and asks how the examination went, Joey says he arrived late, and she suggests they talk at dinner, which leads into Episode 4. The camera stays inside the house beside them. The ride is `BusRide` (it borrows the nearest school bus and drives it along the traffic lane past the shelter) and the greeting is `HomeWelcome`.

## Chapter 3 · Social Dynamics

Eight episodes (`Chapter 3 - Episode 1` to `8`) about an invitation to a school reunion, being among old classmates, and getting home again. They are adapted from the chapter's design document. The reunion rooms are the **Reunion Hall** inside the school-grounds model, and the walk home runs along the city street outside Joey's house.

| Episode | Title | Where |
| --- | --- | --- |
| 1 | The Invitation | Bedroom |
| 2 | Arriving at the Reunion | Reunion, entrance |
| 3 | Everyone Seems to Be Moving Forward | Reunion, conversations |
| 4 | The Corner of the Room | Reunion, quiet corner |
| 5 | A Friend Checks In | Reunion, with a friend |
| 6 | Choosing to Rejoin the Group | Reunion, group photo |
| 7 | The Walk Home | The street at night, then home |
| 8 | The Mirror | Bedroom, at the mirror |

Episode 1 lets the player look at the phone, the photograph and the desk in any order, then choose a reply. Episode 6 saves an appreciation to the reflection journal's **One Thing About Me** tab.

The old friends at the reunion are **Bea, Aaron, Andrea and Kim** (the script's Friend 1 to 4, `SocialDynamicsChapter.FriendNames`). Other boys in Chapter 3 use the names from the capstone list: Sky, Marc, Jefferson and Jahmir (`BoyNames`). Justin stays Justin.

### The end of the chapter

The last three episodes are played out rather than told (`SocialDynamicsEnding.cs`, with the pieces it builds at runtime in `SocialStaging.cs`, so the scenes need no extra set-up):

| Episode | What happens |
| --- | --- |
| 6 · group photo | Joey walks up onto the stage while the friends wave him over; the camera moves to the phone on its stand, Justin sets the timer, 3-2-1 counts down by itself, the shutter fires with a white flash, and the real shot is shown and kept for the profile. |
| 7 · walk home | The street is empty of walkers. Memories of the reunion come back at three places along the sidewalk (no keys, no markers), then Joey stops by himself to look at the photograph from Episode 6. Mom, Dad and Tim wait inside the front door and greet him, each by name, with the camera inside the house. He puts his phone on the desk, lies down on his bed thinking about the day, and falls asleep. |
| 8 · the dream and the mirror | He wakes in a dim, open dream with a light far ahead. The music starts with his first slow steps, and seven framed memories of good things he did light up one by one. Reaching the light, he wakes in his room. "That's me." comes on the way up to the mirror; facing it starts the monologue, while memory frames appear around the mirror and the camera drifts over them. A younger Joey fades into the reflection only (`SocialMirror` cross-fades two reflection cameras with the `Mindscape/MirrorBlend` shader), "IT'S YOU!", "Despite everything, it's still you!", then the camera pulls back into the dark, a pencil drawing made from the last frame fades in and out, and **The End**. |

> [!MENU] Mindscape ▸ Chapter 3 - Social Dynamics ▸ Build All Eight Episodes
>
> Generates the eight scenes, their preview images and their build-profile entries from the earlier chapters' scenes (which it only reads). Rebuilding replaces the generated scenes, so keep custom edits elsewhere. `Rebuild the Reunion Episodes (2-6)` rebuilds only the reunion. `Verify All Episodes (Play Mode)` runs every story coroutine, alternate exploration orders, all the choices, pause and journal saving; it checks story progression, not an exported build.

## Progress, journal and menu

The main menu lists the episodes of each chapter. A chapter unlocks when the one before it is finished, and an episode unlocks when the one before it is finished; finished episodes can be replayed. **Continue** resumes from the latest saved episode. Progress, choices and the reflection journal are saved on the device (SQLite where the platform has it, local storage on WebGL), and to the cloud when the player has signed in.
