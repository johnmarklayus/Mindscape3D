---
id: minigame-breathing
group: Minigames
nav: Breathing Exercise
---

# Breathing Exercise

Fifteen seconds of guided breathing. A circle opens as the player breathes in, rests while they hold, and settles as they breathe out. There is nothing to click and nothing to get wrong; the exercise just runs. In Episode 1 it opens when Dad's conversation ends.

## What the player sees

- A dark blue panel in the game's theme, with a small eyebrow line at the top and the serif title **BREATHE**.
- A large **circle** made of three layers: a faint fixed outer ring (the space the breath can fill), the moving circle (small and gold on the out-breath, larger and cream on the in-breath), and a dark core in the middle holding a big **number** that counts the seconds left in the current phase.
- The **phase name** in the serif font (*Breathe in*, *Hold*, *Breathe out*) and a one-line hint underneath: *Let the air arrive.* / *Rest here for a moment.* / *Let it leave on its own.*
- A thin gold **progress bar** with the time left, and a **Close** button.
- When the time is up, a closing line stays for a couple of seconds, *That is the whole exercise.*, and then the screen closes.

The default rhythm is **5 seconds in, 3 held, 7 out**, which is exactly one 15-second breath, so the exercise never ends in the middle of an in-breath. All of it is adjustable on the component.

## Editing it

Select the `Breathing Minigame` object in the scene:

| Group | What you can change |
| --- | --- |
| **Breathing Exercise** | Total duration; seconds for inhale, hold and exhale; how long the closing line stays. |
| **Text** | The eyebrow, the title, the three phase names and hints, the closing line and hint, the Close button. |
| **Look** | The circle's smallest and largest size, and its small, large, ring, core and text colours. |
| **Sorting Order** | Where the screen's UI document sits (10, above the story panels and the pause menu). |

The screen is a UI Toolkit file, `Assets/UI Toolkit/Breathing.uxml` with its `.uss`, loaded through `Resources/EpisodeUI`. Open it in UI Builder to restyle or move things; the script finds each element by name (`breathing-circle`, `breathing-phase`, `breathing-count` and so on), so keep the names. See [Episode Screens (UI Toolkit)](#system-episode-ui).

## How it runs

- It derives from [`QuestMinigame`](#system-minigames), so the Quest opens it from a conversation, a timer or a stress level, and lists it in the Journal as **Breathing Exercise**.
- While it is open, `PlayerControls.minigameOpen` is true: movement and the cursor stop, NPC prompts hide, and the episode timer waits.
- Timing uses unscaled time, so it runs even if the game is paused elsewhere.
- **Finishing** (after the closing line) tells the Quest it is done and fires **On Completed**. **Closing early** fires **On Closed** and leaves the requirement open; talking to Dad again reopens it.
- The screen is spawned from `Breathing.uxml` when the scene starts. If that file is missing from `Resources/EpisodeUI`, the exercise logs a warning and has no screen.

> [!TIP] Easing stress with it
>
> Point **On Completed** at `PlayerControls.ChangeStress` with a negative number if finishing the exercise should lower stress. See [Stress System](#system-stress).

The hint wording is deliberately plain and neutral: see the [Writing Guidelines](#story-tone).
