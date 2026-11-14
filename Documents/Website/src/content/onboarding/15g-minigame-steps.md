---
id: minigame-steps
group: Dialogue & Minigames
nav: Add a minigame
---

# Add a Minigame, Step by Step

Every minigame is a **cinematic step**. You add it in the Inspector like any other step; no code is needed.

| Minigame | Step type | What it needs |
|---|---|---|
| Examination paper (with the 5-4-3-2-1 grounding break) | **Minigame: exam paper** | An **Exam Paper** asset |
| Worry Courtroom (a worry put on trial) | **Minigame: Worry Courtroom** | A case from `Assets/Minigames/WorryCourtroom/Cases` |
| Practice games (memory match, focus challenge, grounding, schedule puzzle…) | **Minigame: practice game** | A prefab from `Assets/Prefabs/Minigames` |
| Breathing exercise | **Breathing exercise** | Seconds |
| Phone chat | **Phone: open a chat**, **Phone: a message**, **Phone: pick a reply**, **Phone: close** | A contact name and messages |
| Journal / written answer | **Dialogue: write an answer** | A question |
| Stress meter | **Stress: raise or lower** | An amount |

> [!TIP] What you need
>
> An episode scene open in Unity with a cinematic in it ([Create a cinematic](#create-cinematic)). Select the cinematic in the Hierarchy before each part below.

## Part 1: An examination paper

**The example:** Joey takes a three-question maths quiz.

1. Menu bar: **Mindscape › Story › New Exam Paper**. The Project window jumps to `Assets/Story/Exams` with a new **Exam Paper** selected.
2. Rename it: **F2** (Mac **Return**), type `Maths quiz`, **Enter**.
3. In its Inspector:

   | Field | Set it to |
   |---|---|
   | **Seconds on the clock** | `120` |
   | **Grounding break** | ✔ (the player can take the 5-4-3-2-1 break; it also opens by itself after two answers) |
   | **Worried thought** | `What if I can't finish?` |
   | **Calm thought** | `I'm here. One question at a time.` |

4. Open **Questions**. Each question has a **Question** box and up to three **Answers**. Change the two examples, then click **+** under Questions for a third. Up to **5 questions** with **3 answers** each.
5. Keep the **Maths quiz** asset selected in the Project window, then select the cinematic in the Hierarchy.
6. Under **Add a step**, click **Exam paper**. The step *Minigame: exam Maths quiz* is added. (If it says *(none)*, open it and drag the asset into **Exam paper**.)
7. Optional: **Save number answered as** `ch4_quiz_answered`, to use the number later.

No score is shown to the player: they answer what they can and hand the paper in.

## Part 2: The Worry Courtroom

1. Under **Add a step**, click **Worry Courtroom**. The **Courtroom prefab** is filled in by itself.
2. Open the step and drag a case from `Assets/Minigames/WorryCourtroom/Cases` into **Case** (for example *Chapter1_EveryoneAhead*).
3. Optional: **Save balanced thought as** `ch4_balanced_thought`. The thought the player reaches is saved there.

To write a new worry, duplicate a case (**Ctrl + D**, Mac **Cmd + D**), rename it, and edit its words in the Inspector.

## Part 3: A practice game

1. Under **Add a step**, click **Practice minigame**.
2. Open the step and drag a prefab from `Assets/Prefabs/Minigames` into **Minigame**, for example **MemoryMatchMinigame**. (Not *WorryCourtroom*: that one has its own step.)
3. The step plays the game and waits until the player closes it. Finishing it lowers the stress a little.

## Part 4: A phone chat

1. Under **Add a step**, click **Phone chat**. Four steps are added: open the chat, a message, a reply, close.
2. **Phone: open a chat**, **Chat with:** `Mom`.
3. **Phone: a message**: **From** `Mom`, **Message** `Don't forget your lunch!`. A message **From** `Joey` is sent by the player.
4. **Phone: pick a reply**: change the **Replies**. The one the player picks is sent as their message. **Save reply as** is optional.
5. More messages: right-click a message step and pick **Duplicate Array Element**, or add one with **+** and pick its **Type**.

## Part 5: A journal question and the stress meter

- **Dialogue: write an answer**: **Title** `Journal`, **Question** `What helped you today?`, **Save answer as** `ch4_journal`. The player types an answer (it may be empty).
- **Stress: raise or lower**: **Amount** `10` raises the stress meter, `-10` lowers it. The meter goes from 0 to 100.

## Try it

Save the scene (**Ctrl + S**, Mac **Cmd + S**), press **Play** and start the cinematic. Each minigame opens in turn; the cinematic carries on when it closes.

> [!WARN] Played once per save
>
> A loaded save does not ask again: the answers the player gave the first time are kept.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| The step shows a yellow warning | It is missing what it needs (the warning says what). The step is skipped until it is set. |
| *That prefab is not a practice minigame* | Use a prefab from `Assets/Prefabs/Minigames` other than WorryCourtroom. |
| Only five questions show | An exam paper holds up to 5 questions with 3 answers each. Make a second paper and a second step. |
| The exam shows no grounding button | **Grounding break** is unticked on the Exam Paper. |
