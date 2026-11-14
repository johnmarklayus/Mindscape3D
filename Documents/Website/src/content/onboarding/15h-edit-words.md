---
id: edit-words
group: Dialogue & Minigames
nav: Change the dialogue
---

# Change the Dialogue, Step by Step

Every line in the game can be changed in the Unity editor without opening a script. Where you change it depends on where the line is:

| The line is in | Change it in | Part |
|---|---|---|
| Chapters 1–3 (dialogue, thoughts, choices, title cards, objectives, [E] prompts) | **Dialogue Words** | 1–3 |
| A cinematic | The cinematic's step | 4 |
| A conversation asset | The conversation | 4 |
| The Worry Courtroom | The case asset | 5 |
| The examination paper (Chapter 2 · Episode 3) | The exam paper asset | 6 |

## Part 1: Open Dialogue Words

1. Menu bar: **Mindscape › Story › Edit Dialogue Words (Chapters 1-3)**.
2. The first time, this makes `Assets/Resources/Story/Dialogue Words.asset` and reads every Chapter 1–3 script. The Console shows `[Dialogue Words] 439 lines (439 new)` (the number may differ).
3. The asset is selected. Its Inspector lists the lines, 30 per page.

At the top of the list:

| Control | What it does |
|---|---|
| The drop-down (*Everything*) | One chapter (*Chapter 1*) or one part of it (*Chapter 1 · Cafeteria*) |
| **Only changed** | Only the lines you changed |
| **Search** | Lines with these words |
| ◀ ▶ | The previous and next page |

## Part 2: Change a line of dialogue

**The example:** in *Chapter 1 · Episode 3* (the cafeteria), Student 1 says *"I already finished my presentation."* Change it.

1. Pick **Chapter 1 · Cafeteria** in the drop-down.
2. Type `already finished` in **Search**. One line is left: *I already finished my presentation.*, from `CafeteriaEpisode.cs`.
3. Each line has a grey box (the words as the script wrote them; you cannot type there) and **Changed** (what the player sees instead).
4. Click **Copy the original into Changed**, then edit **Changed** to `I finished my slides last night.`
5. Save: **Ctrl + S** (Mac **Cmd + S**).

> [!TIP] Check
>
> Open `Assets/Scenes/Chapter 1 - Episode 3`, press **Play**, walk to the cafeteria and sit at the table. Student 1 says *I finished my slides last night.* Press **Play** to stop.

To go back to the original, click **Undo the change** (it empties **Changed**).

## Part 3: More examples from the game

| Change | Pick in the drop-down | Search for | Notes |
|---|---|---|---|
| The title card of Chapter 1 · Episode 1 | Chapter 1 · House | `Tomorrow Already` | It is on two lines: keep the line break. `<size=60%>` makes the second line smaller |
| The choice at the laptop | Chapter 1 · House | `finish everything` | Changing the words of an answer does not change what is saved, so later episodes still know the choice |
| A spot's [E] words | Chapter 1 · House | `Check your phone` | The prompt shows as **[E] Check your phone** |
| An objective | Chapter 1 · Cafeteria | `Find a seat` | The objective panel at the top |
| The friend's name | – | – | Not a line: it is **Friend Name** on the episode object ([Edit an episode](#edit-episode)) |

**Lines in parts.** A line with a name or an earlier answer in the middle appears as its parts. For example, *"Lunch. "* and *" said they'd save a seat. …"* (the friend's name goes between them). Change each part and keep the spaces at the ends.

**The same words in several places** (for example `Begin  [Space]`) are one line in the list: a change shows everywhere they appear. `Joey` in the words is replaced by the player's name.

**After a script changes**, click **Find every line** to add its new lines; your changes are kept. **Clear lines no longer in a script** removes lines that were deleted.

## Part 4: A line in a cinematic or a conversation

**In a cinematic** (for example *Cinematic - Mom greets Joey* in `Chapter 1 - Episode 1`):

1. Select the cinematic (Hierarchy search `t:Cinematic`).
2. Open the line's step with its ▸ arrow and change **Words** (and **Speaker**).
3. Save the scene.

Full steps: [Edit a cinematic](#edit-cinematic).

**In a conversation asset**: select it in the Project window (`Assets/Story/Conversations`) and change the words on the right of each line ([Create a conversation](#create-conversation)). Every cinematic that plays it shows the new words.

## Part 5: The Worry Courtroom words

**The example:** the worry put on trial in *Chapter 1 · Episode 3*.

1. In the Project window, open `Assets/Minigames/WorryCourtroom/Cases` and click **Chapter1_EveryoneAhead**.
2. In the Inspector:
   - **Case Name**: `Everyone seems ahead`
   - **Worry**: `Everyone is ahead of me, so I'm not good enough.`
   - **Evidence**: each card the player sorts. Change its **Text**. **Is Fact** says whether it is a fact or a thought; keep it right, or the trial no longer makes sense.
3. Change the words, then **File › Save Project**.

## Part 6: The examination questions

**The example:** the paper in *Chapter 2 · Episode 3 · Running Out of Time*.

1. In the Project window, open `Assets/Resources/Story/Exams` and click **Chapter 2 - Episode 3**.
2. Open **Questions** and the first question: *A notebook costs 24 pesos. How much do three notebooks cost?*, with the answers `48 pesos`, `72 pesos`, `96 pesos`.
3. Change the **Question** and the **Answers**. Up to 5 questions with 3 answers each.
4. **Seconds on the clock** is the time; **Worried thought** and **Calm thought** are the lines under the clock.
5. **File › Save Project**.

Press **Play** in `Chapter 2 - Episode 3`, reach your seat in Room 03, and the paper shows the new questions.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| A change does not show | Stop Play mode and press **Play** again. Or **Changed** is the same as the original. |
| A line is not in Dialogue Words | It is built from other text (a list of feelings, a name), or it is a cinematic's line (Part 4). Ask a developer to wrap it in `W("...")` in the script, then click **Find every line**. |
| *(no longer in the script)* next to a line | The script no longer has those words; the change does nothing. Clear it with **Clear lines no longer in a script**. |
| The exam shows the old questions | `Assets/Resources/Story/Exams/Chapter 2 - Episode 3` was renamed or moved: the episode looks for it by that name. Put it back. |
