---
id: cinematic-steps
group: Cutscenes & Cinematics
nav: Every cinematic step
---

# Every Cinematic Step

Pick a step's **Type** in the Inspector; only the fields that type uses are shown. A step with an empty required field is skipped.

## Camera

| Type | Fields | What happens |
|---|---|---|
| **Camera: cut to a view** | View | The camera jumps to the view object: its position, looking along its blue arrow. Buttons: **Set view from Scene view** (makes or moves the view to what the Scene view shows), **Look through it** (moves the Scene view there to check). |
| **Camera: glide to a view** | View, Seconds | The camera moves smoothly from where it is to the view. Same buttons. |

The camera goes back behind the player by itself when the player can walk again.

## Dialogue

| Type | Fields | What happens |
|---|---|---|
| **Dialogue: a line** | Speaker, Words | One line in the dialogue box. Speaker: a name, `Joey` (the player), `Thought` (the player's thought) or empty (narration). Lines in a row share one *x / n* counter. `Joey` in the words becomes the player's name. |
| **Dialogue: a choice** | Title, Question, Answers, Save answer as | The choice screen. The picked answer is saved under *Save answer as* (optional). |
| **Dialogue: a conversation (asset)** | Conversation | Plays a conversation asset, all its lines with one counter ([Create a conversation](#create-conversation)). |
| **Dialogue: write an answer** | Title, Question, Save answer as | The player types an answer (it may be empty), saved under *Save answer as*. |

## Phone

| Type | Fields | What happens |
|---|---|---|
| **Phone: open a chat** | Chat with | The phone comes up with a chat with that contact. |
| **Phone: a message** | From, Message | A message arrives (after "typing…"). **From** `Joey`: sent by the player. |
| **Phone: pick a reply** | Replies, Save reply as | The player picks a reply on the phone; it is sent as their message. |
| **Phone: close** | – | Puts the phone away. |

## Minigames

| Type | Fields | What happens |
|---|---|---|
| **Minigame: exam paper** | Exam paper, Save number answered as | The examination paper with its clock and grounding break ([Add a minigame](#minigame-steps)). |
| **Minigame: Worry Courtroom** | Case, Courtroom prefab, Save balanced thought as | A worry put on trial. The prefab fills in by itself. |
| **Minigame: practice game** | Minigame, Save result as | A practice game from `Assets/Prefabs/Minigames`. Saves `completed` or `closed`. |
| **Breathing exercise** | Seconds | The breathing minigame (15 seconds if left at 1). |
| **Stress: raise or lower** | Amount | `10` raises the stress meter, `-10` lowers it. |

## Screen

| Type | Fields | What happens |
|---|---|---|
| **Screen: title card** | Words | A full-screen card; the player presses Space. Press **Enter** in the Words box for a new line. |
| **Screen: fade to black** | Seconds | The screen fades to black and stays black. |
| **Screen: fade from black** | Seconds | The screen fades back in. Use it after a fade to black. |
| **Screen: show a picture** | Picture, Caption | A photograph held up on screen (lines can play while it shows). |
| **Screen: hide the picture** | – | Hides it. |
| **Screen: play a cutscene** | Cutscene | Plays a slide cutscene ([Create a cutscene](#create-cutscene)), then carries on. |
| **Screen: start a flashback** | Label, Fade seconds | Fades to a memory: the flashback frame shows with the label (for example `The night before`). |
| **Screen: end the flashback** | Fade seconds | Fades back to the present. |

## People and the player

| Type | Fields | What happens |
|---|---|---|
| **Person: walk to a place** | Person, Walk to, Seconds | The person walks there in that many seconds, then faces the way the place points. Button: **New place at Scene view centre**. |
| **Person: stand at a place** | Person, Stand at | The person is put there at once, facing the way the place points. |
| **Person: turn to look at** | Person, Look at, Seconds | The person turns toward a place or another person. |
| **Person: play an animation** | Person, Animation | Plays an animation state: `Idle`, `Walk`, `Talk` for the family and the cast. |
| **Player: move to a place** | Move to | Joey is put there at once, facing the way the place points (do it during a fade to black). |

**Person** is any character in the scene: drag them from the Hierarchy (in Chapter 1 · Episode 1 they are *Mom*, *Dad* and *Tim*; some scenes call them *Mother* and *Father*). A **place** is an empty object: make one with **New place at Scene view centre**, then move it with **W** and turn it with **E**.

## Objects and the rest

| Type | Fields | What happens |
|---|---|---|
| **Object: show** | Object | Turns an object on (a gift appears, a light comes on). |
| **Object: hide** | Object | Turns it off. |
| **Wait** | Seconds | A pause. |

A step that is missing what it needs shows a yellow warning in the Inspector that says what to set.

## When a cinematic plays

| Plays | Needs | Notes |
|---|---|---|
| **At the start of the episode** | – | Before the episode's own story, after the chapter's *Cutscene Before*. Several play top to bottom in the Hierarchy. Not replayed when a save is loaded. |
| **When the player walks to a place** | Place, Range | Starts when the player comes within Range while walking freely. |
| **When the player presses E at a place** | Place, [E] prompt, Range | Shows **[E] prompt** within Range while walking freely. |
| **Only when a script plays it** | – | `yield return PlayCinematic(cinematic);` in the episode script. |

**Only Once** (ticked by default) plays it the first time only.
