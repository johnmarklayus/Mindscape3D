---
id: create-conversation
group: Dialogue & Minigames
nav: Create a conversation
---

# Create a Conversation, Step by Step

A conversation is a list of lines (who speaks and the words) kept in its own asset. You write it in the Inspector and play it from a cinematic, with no code. The lines share one *1 / 3, 2 / 3…* counter.

**The example:** Mom and Joey talk in the kitchen. The conversation plays when Joey presses **E** near Mom.

> [!TIP] What you need
>
> - The project open in Unity, with the Console open.
> - For Part 3: an episode scene with a cinematic ([Create a cinematic](#create-cinematic)).

## Part 1: Make the conversation

1. Menu bar: **Mindscape › Story › New Conversation**.
2. The **Project** window jumps to `Assets/Story/Conversations` with the new **Conversation** asset selected. It already has three example lines.
3. Rename it: press **F2** (Mac **Return**), type `Mom in the kitchen`, press **Enter**.

> [!TIP] Check
>
> - The Console shows `[Mindscape] Made Assets/Story/Conversations/Conversation.asset`.
> - The Inspector shows **Lines (3)**: *Mom*, *Joey* and *Thought*, each with a words box on the right.

## Part 2: Write the lines

Each row is one line. On the left is **who speaks**, on the right are **the words**:

| Type on the left | Shown as |
|---|---|
| a name (`Mom`, `Dad`, `Tim`, `Justin`…) | that person speaking |
| `Joey` | the player speaking (with the player's chosen name) |
| `Thought` | the player's inner thought |
| *(empty)* | narration |

1. Click in the first words box and type `You're home early! How was school?`
2. Second line: `It was okay. A long day.`
3. Third line: `It feels good to be home.`
4. To add a line, click one of the buttons under the list: **+ Someone speaks** (makes a *Mom* line, so change the name), **+ Joey speaks**, **+ A thought** or **+ Narration**.
5. To move a line, drag the ☰ handle on its left. To remove one, select it and click **–** under the list.

Press **Enter** in a words box for a new line inside the same bubble. `Joey` in the words becomes the player's name.

## Part 3: Play it from a cinematic

1. Open the episode scene and select the cinematic (for example **Cinematic - Mom greets Joey**).
2. In the Project window, click the **Mom in the kitchen** asset once (so it is selected), then select the cinematic again in the Hierarchy.
3. In the cinematic's Inspector, under **Add a step**, click **Conversation (asset)**. A step *Conversation Mom in the kitchen* is added at the bottom.
4. If the step says *Conversation (none)*, open it with its ▸ arrow and drag the conversation asset from the Project window into **Conversation**.
5. Save the scene: **Ctrl + S** (Mac **Cmd + S**).

> [!TIP] Check
>
> Press **Play** and start the cinematic. The three lines play one after another with *1 / 3*, *2 / 3*, *3 / 3*.

## Use one conversation in several places

A conversation asset can be used by many cinematics, in any scene. Change it once and every cinematic that uses it shows the new words.

## From a script (optional)

In an episode script: add the field `public Conversation momTalk;`, drag the asset into the field in the episode's Inspector, and play it with `yield return Talk(momTalk);`.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| The step warns *Drag a Conversation asset here* | The step has no conversation. Drag the asset into **Conversation**. |
| A line shows as narration | Its speaker is empty. Type a name on the left. |
| The player's name does not show | Type `Joey` exactly (any capitals) as the speaker. |
