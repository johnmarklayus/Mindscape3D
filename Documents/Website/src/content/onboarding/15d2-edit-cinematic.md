---
id: edit-cinematic
group: Cutscenes & Cinematics
nav: Edit a cinematic
---

# Edit a Cinematic, Step by Step

How to change a cinematic that is already in a scene: its words, its shots, its order, when it plays, or turn it off.

**The example:** *Cinematic - Mom greets Joey* in `Chapter 1 - Episode 1` (made in [Create a cinematic](#create-cinematic)). Mom greets Joey in the kitchen when he presses **E**.

## Part 1: Find the cinematic

1. In the Project window, open `Assets/Scenes` and double-click **Chapter 1 - Episode 1**.
2. In the **Hierarchy** search box at the top, type `t:Cinematic`. Only the cinematics in the scene are listed.
3. Click **Cinematic - Mom greets Joey**. Clear the search box (the ✕ in it) to see the whole Hierarchy again; the cinematic stays selected.

In the Scene view, the gold circle on the floor is where it plays, and while it is selected, each blue camera frame is one of its views.

> [!TIP] Check
>
> The Inspector shows **Plays**, **Place**, **[E] prompt**, **Range**, **Only Once**, the **Add a step** buttons and the **Steps** list.

## Part 2: Change the words

1. In **Steps**, click the ▸ arrow of *2. Mom: You're home early! How was school?*
2. In **Words**, change it to `You're back! How did it go today?`
3. **Speaker** sets who speaks: a name, `Joey` (the player), `Thought` (the player's thought) or empty (narration).
4. Click the ▸ arrow again to close the step. Its first line shows the new words.

For a choice (*5. Choice: What do you tell Mom?*): change **Question**, and open **Answers** to change, add (**+**) or remove (**–**) answers. Keep **Save answer as** the same, or the answer is saved under a new name.

If the step is *Conversation …* (a conversation asset), the words are in the asset: double-click the asset in its **Conversation** field to open it ([Create a conversation](#create-conversation)).

## Part 3: Change a camera shot

1. Open the camera step, for example *1. Camera cut → View 1*.
2. Click **Look through it**. The Scene view jumps to what the camera shows now.
3. Fly the Scene view to the new shot (right mouse button + **W A S D**).
4. Click **Set view from Scene view**. The view moves to exactly what the Scene view shows.

For a glide (*Camera glide → View 2*), **Seconds** is how long the camera takes. To swap a cut for a glide, change the step's **Type**.

## Part 4: Add, move or remove steps

| To | Do this |
|---|---|
| Add a common step | Click a button under **Add a step** (it goes at the bottom), then drag it into place |
| Add any other step | Click **+** under the list, open the new step, pick its **Type** ([Every cinematic step](#cinematic-steps)) |
| Move a step | Drag its ☰ handle up or down |
| Copy a step | Right-click it and pick **Duplicate Array Element** |
| Remove a step | Click it, then click **–** under the list |

**Example:** make Mom turn to Joey before she speaks. Click **+**, open the new step, set **Type** to *Person: turn to look at*, drag **Mom** from the Hierarchy into **Person**, drag **Player** into **Look at**, **Seconds** `0.5`. Then drag the step up to be number 2.

## Part 5: Change when and where it plays

At the top of the Inspector:

| To | Do this |
|---|---|
| Change the [E] words | Type in **[E] prompt**, for example `Say hello to Mom` |
| Move where it plays | Select the **Place** object (click it in the **Place** field, then press **F** in the Scene view) and move it with **W**; or click **Here** for a new place at the middle of the Scene view |
| Make the circle bigger or smaller | **Range**, in metres |
| Play without pressing E | **Plays** → *When the player walks to a place* |
| Play when the episode starts | **Plays** → *At the start of the episode* |
| Let it play every time | Untick **Only Once** |

## Part 6: Turn it off, or delete it

- **Turn it off** (keep it for later): untick the checkbox next to its name at the top of the Inspector. A cinematic that is off never plays. Tick it again to turn it back on.
- **Delete it**: right-click it in the Hierarchy and pick **Delete**. Its places and views (its children) go with it.

Save the scene after any change: **Ctrl + S** (Mac **Cmd + S**).

## Part 7: Try it

1. Press **Play** and walk to the kitchen when the house is yours to walk around.
2. Press **E** at the gold circle. Check the new words, the shot and the order.
3. Press **Play** again to stop. Changes made while playing are lost, so edit after you stop.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| `t:Cinematic` lists nothing | The scene has no cinematic yet. Make one: **Mindscape › Story › New Cinematic (in the open scene)**. |
| The old words still show | You edited during Play mode, or did not save. Stop, edit, save. |
| A step shows a yellow warning | It is missing what it needs; the warning says what. |
| The cinematic no longer plays | It is turned off (Part 6), **Only Once** and it already played, or **Place** is empty. |
