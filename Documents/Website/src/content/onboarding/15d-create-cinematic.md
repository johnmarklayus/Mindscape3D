---
id: create-cinematic
group: Cutscenes & Cinematics
nav: Create a cinematic
---

# Create a Cinematic, Step by Step

A cinematic is a moment played out in the 3D scene: the camera cuts and glides, people talk, walk and turn, the screen fades. You build it as a list of **steps** in the Inspector, and pick **when** it plays.

**The example:** in *Chapter 1 · Episode 1* (Joey's house), when Joey presses **E** in the kitchen, Mom greets him. The camera frames them, they talk, Joey picks a reply, the camera glides, and Mom walks to the counter.

> [!TIP] What you need
>
> - The scene `Assets/Scenes/Chapter 1 - Episode 1.unity` open in Unity (double-click it in the Project window). Any episode works the same way, including your own ([Create an episode](#create-episode)).
> - The Scene view visible (the big 3D view) and the Console open.

> [!TIP] Moving around the Scene view (used a lot below)
>
> - Hold the **right mouse button** and use **W A S D** to fly, **Q / E** to go down / up. Scroll to move forward and back.
> - Select an object in the Hierarchy and press **F** (mouse over the Scene view) to jump to it.

## Part 1: Make the cinematic

1. In the Scene view, fly to the kitchen and look at the spot where Joey and Mom should talk, the way the first shot should look. (Find the kitchen: type `Kitchen sink` in the Hierarchy search box and double-click it. Find Mom the same way: type `Mom`. Clear the search box after.)
2. Menu bar: **Mindscape › Story › New Cinematic (in the open scene)**.

3. Rename it: select **Cinematic - New**, press **F2** (Mac **Return**), type `Cinematic - Mom greets Joey`, press **Enter**.

> [!TIP] Check
>
> - In the Hierarchy, inside the episode object, there is the new cinematic, now **Cinematic - Mom greets Joey**, selected. It holds **Place 1** (on the floor in the middle of the Scene view) and **View 1** (exactly what the Scene view showed).
> - In the Scene view: a **gold circle** at Place 1, labelled *Cinematic - Mom greets Joey  [E] Look*, and, while the cinematic is selected, a **blue camera frame** at View 1.
> - The Inspector shows **Plays: When the player presses E at a place** and two steps: *1. Camera cut → View 1* and *2. Narration: Write the first line here.*

## Part 2: Choose when it plays

In the Inspector, at the top:

| Field | Set it to | What it means |
|---|---|---|
| **Plays** | *When the player presses E at a place* | The other choices: *At the start of the episode*, *When the player walks to a place* (no E needed), *Only when a script plays it*. |
| **Place** | *Place 1* (already set) | Where the player must be. Move **Place 1** with the Move tool (**W**) next to Mom, or click **Here** to put a new place at the middle of the Scene view. |
| **[E] prompt** | `Talk to Mom` | The words next to **[E]**. |
| **Range** | `2.5` | How close the player must be, in metres (the gold circle on the floor). |
| **Only Once** | ✔ | Untick to let it play every time. |

## Part 3: Add the steps

Each step is one thing that happens. Steps play top to bottom. Click a step's ▸ arrow to open it; its first line always says what it does.

**The buttons under "Add a step"** add the most common ones at the bottom of the list:

| Button | Adds |
|---|---|
| **Camera view from Scene view** | A camera cut to a new view, set to what the Scene view shows right now |
| **Line of dialogue** | A line, with Speaker and Words to fill in |
| **Choice** | A question with two answers |
| **Fade out + in** | Two steps: fade to black, fade back |
| **Wait** | A pause of 1 second |
| **Conversation (asset)** | A conversation asset (the one selected in the Project window) ([Create a conversation](#create-conversation)) |
| **Phone chat** | Four steps: open a chat, a message, a reply, close |
| **Exam paper**, **Worry Courtroom**, **Practice minigame**, **Breathing** | A minigame ([Add a minigame](#minigame-steps)) |

For any other step, click **+** under the list, then open the new step and pick its **Type** (see [Every cinematic step](#cinematic-steps)).

Now build the example:

**Step 1 – the first shot (already there).** Open *1. Camera cut → View 1*. To change the shot: fly the Scene view to the new framing and click **Set view from Scene view**. To check it: click **Look through it**; the Scene view jumps to the view.

**Step 2 – Mom speaks.** Open the second step (*Narration: …*):
- **Speaker:** `Mom`
- **Words:** `You're home early! How was school?`

**Steps 3 and 4 – Joey answers and thinks.** Click **Line of dialogue** twice, then fill them in:

| Step | Speaker | Words |
|---|---|---|
| 3 | `Joey` | `It was okay. A long day.` |
| 4 | `Thought` | `It feels good to be home.` |

**Who speaks** is set by the Speaker:

| Speaker | Shown as |
|---|---|
| a name (`Mom`, `Dad`, `Tim`, `Justin`…) | that person speaking |
| `Joey` | the player speaking (with the player's chosen name) |
| `Thought` | the player's inner thought |
| *(empty)* | narration |

Lines that follow each other become one conversation with a shared *1 / 3, 2 / 3…* counter.

**Step 5 – a choice.** Click **Choice** and fill it in:
- **Title:** `Reply` (small heading over the question)
- **Question:** `What do you tell Mom?`
- **Answers:** open the list and change the two answers to `I'm just tired.` and `Actually, it was a lot.` (**+** adds a third.)
- **Save answer as:** `ch4_mom_reply` (the answer is saved under this name; never reuse a name for something else)

**Step 6 – the camera glides.** Fly the Scene view to a second framing (for example from behind Mom toward the counter). Click **Camera view from Scene view**: this adds *Camera cut → View 2*. Open it and change **Type** to **Camera: glide to a view**, and **Seconds** to `2`. The camera now moves smoothly from the last shot to View 2.

**Step 7 – Mom walks to the counter.** Click **+** under the list, open the new step and set:
- **Type:** *Person: walk to a place*
- **Person:** drag **Mom** from the Hierarchy into the field
- **Walk to:** click **New place at Scene view centre** (look at the counter in the Scene view first). A **Place 2** is made on the floor there; move it with **W** if needed. Turn it with **E**: the way it points is the way Mom faces when she arrives.
- **Seconds:** `2`

**Step 8 – end with a fade.** Click **Fade out + in**.

Save the scene: **Ctrl + S** (Mac **Cmd + S**).

> [!TIP] Check
>
> The Steps list reads, top to bottom:
> 1. Camera cut → View 1
> 2. Mom: You're home early! How was school?
> 3. Joey: It was okay. A long day.
> 4. Thought: It feels good to be home.
> 5. Choice: What do you tell Mom?
> 6. Camera glide → View 2 (2 s)
> 7. Mom walks to Place 2
> 8. Fade to black (0.6 s)
> 9. Fade from black (0.6 s)

**Reorder** a step by dragging its ☰ handle. **Remove** one: select it and click **–** under the list.

## Part 4: Make sure the player can reach it

A cinematic at a place only starts **while the player is walking freely**. Episodes made with **New Episode** have this line near the end of their script, which lets the player walk until every cinematic at a place has played:

```csharp
yield return RoamUntilCinematicsDone();
```

The objective panel then lists each one (*Talk to Mom*). Chapters 1–3 have their own walking parts: in *Chapter 1 · Episode 1* the player walks around the house after waking up, so a cinematic in the kitchen plays when Joey gets there.

## Part 5: Try it

1. Press **Play**.
2. Go through the opening (the alarm, getting up) until you can walk around the house. Walk to the gold circle: **[E] Talk to Mom** appears. Press **E**.
3. The camera cuts to View 1, the three lines play (Space to continue), the choice appears (click an answer), the camera glides to View 2, Mom walks to the counter, and the screen fades out and back in.
4. You can walk again. Press **Play** to stop.

> [!WARN] Changes made while playing are lost
>
> Stop Play mode before editing the cinematic.

## Other ways to use it

- **At the start of the episode:** set **Plays** to *At the start of the episode*. It plays before the episode's own story (after the chapter's *Cutscene Before*, if any). No Place needed.
- **When the player walks somewhere:** *When the player walks to a place*. No E prompt; it starts as soon as the player is within **Range**.
- **From a script:** set *Only when a script plays it*. In the episode script add the field `public Cinematic momScene;`, drag the cinematic into that field in the episode's Inspector, and play it where you want with `yield return PlayCinematic(momScene);`.
- **A picture-book moment inside it:** add a step **Screen: play a cutscene** ([Create a cutscene](#create-cutscene)).
- **Several cinematics in one scene:** make one per moment (**New Cinematic** again). At the start of an episode they play top to bottom as listed in the Hierarchy.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| No **[E]** prompt at the place | The player is not walking freely at that moment (Part 4), or is outside **Range**, or **Only Once** is ticked and it already played. |
| The Inspector warns *Set the Place* | **Plays** needs a place. Click **Here** next to Place. |
| The camera shows a wall or the inside of something | Re-aim that view: fly the Scene view, open the step, **Set view from Scene view**. |
| A person does not move or turn | **Person** is empty, or the **Walk to** / **Look at** place is empty. |
| *Person: play an animation* does nothing | That person's Animator has no state with that name. `Idle`, `Walk` and `Talk` work for the family and the cast. |
| The cinematic plays at the start but the episode looks wrong after | The episode's own script moves the camera and the player when it starts. Put **Player: move to a place** and a camera step at the end of the cinematic, or let the episode's script frame its first shot. |
| Nothing happens and the Console has a red line | Read it: a step with an empty required field is skipped, but a broken script stops everything. |
