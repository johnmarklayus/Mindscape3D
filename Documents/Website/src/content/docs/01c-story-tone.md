---
id: story-tone
group: Story
nav: Writing Guidelines
---

# Writing Guidelines

Mindscape 3D is played by people who may be having a hard time themselves. Everything the game says should be safe to read on a bad day. These rules apply to dialogue, narration, minigame wording and menu text.

> [!WARN] The one-line version
>
> Be **neutral**: not negative, not positive. Notice, wonder, and let the player decide what it means.

## Principles

- **Observe, don't interpret.** Say what is there ("a message appears on the screen") rather than what it means ("a terrible reminder").
- **Neutral, not cheerful.** No "you'll do great", no "everything will be fine". Reassurance can feel like pressure.
- **Never name the player's feelings for them.** Don't tell Joey he is scared, anxious or relieved.
- **A little philosophical, always plain.** Short sentences and everyday images (doors, roads, tables, the breath). No jargon.
- **No time pressure in the words.** Nobody says "hurry" or "you're late". The clock is on screen; the writing stays calm.
- **No judgement words.** Avoid fail, wrong, bad, stupid, weak, ruined, terrible, always, never.
- **Equal choices.** Reply options should carry the same weight. Don't make one choice obviously the "good" one.
- **Stress change is 0 in conversation.** Stress should not be something the player can win or lose by being "nice" to an NPC.
- **Invite, don't instruct.** "Shall we look at a thought together?" rather than "You need to calm down."
- **Not a replacement for care.** The game states that it is educational and reflective, and shows the NCMH Crisis Hotline (1553) on its support screens.

## Examples

| Instead of | Write |
| --- | --- |
| "Don't worry, you'll be fine." | "A presentation is a few minutes of speaking placed inside a long day." |
| "You're going to be late!" | "The bus comes down the street, goes to school, and comes back again." |
| "Calm down and breathe." | "Come and sit beside me for a moment." |
| "You failed that one." | "Try a response that acknowledges the setback and offers a realistic next step." (minigame feedback) |
| "You look stressed." | "When a door is open, is the room inside or outside?" |

## Where the rules apply in the project

- **NPC dialogue** is edited in each NPC's Inspector. Keep every `stressChange` at 0.
- **Cutscene narration** is edited on each slide's `CutsceneText`.
- **Worry Courtroom and Breathing Exercise wording** is on the component (see [Worry Courtroom](#minigame-courtroom) and [Breathing Exercise](#minigame-breathing)), so you can adjust it without touching code.
- Anything new you add (a notification, a loading line, a tutorial hint) should pass the same read-it-on-a-bad-day test.
