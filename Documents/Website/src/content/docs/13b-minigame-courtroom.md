---
id: minigame-courtroom
group: Minigames
nav: Worry Courtroom
---

# Worry Courtroom

The player is the judge. A worry has been brought to court, and the player weighs the evidence, hears what a friend would say, and gives a verdict. The lesson is one line: *a worry is a thought, not a fact.*

In Episode 1 the worry on trial is **"I'll mess up my presentation and everyone will laugh."** It opens when Mom's conversation ends.

## The six rounds

| Step | What the player does | Wrong answers |
| --- | --- | --- |
| **Charge** | Reads the worry the Worry (a purple creature in the dock) is making. | none |
| **Prosecution** | Six evidence cards, one at a time: is each a **fact** the court can check, or a **feeling or guess**? Guesses reveal the *thinking trap* behind them (mind reading, fortune telling, all-or-nothing, catastrophizing, emotional reasoning, labeling). | A strike |
| **Defence** | Picks three real facts that weigh against the worry from six options. | A strike, with a reason it doesn't help |
| **Friend** | "A friend has the same worry. What would you tell them?" | A strike, with a reason |
| **Verdict** | Picks the more balanced thought. | A strike, with a reason |
| **Plan** | Picks one small, specific action, then when to do it (Today, Tomorrow, This week). | A strike, with a reason |

Then **Case dismissed** shows a case file (the worry, the balanced thought, the plan, the traps spotted, total strikes) and a rating of 1 to 3 stars.

### Feedback you can feel

- Each right answer lowers the **worry meter** (100% at the start, 0% at the end), and the Worry figure shrinks, fades and changes from a scowl to a calm face.
- Each wrong answer lights a **gavel strike** and shakes the stage.
- After three strikes the judge calls a **Recess**: a short breathing break, after which the helpful answers are outlined. Nobody can fail the trial.

## Editing the content (no code)

The trial is a **ScriptableObject** asset. Episode 1's is `Assets/Minigames/WorryCourtroom/Cases/Chapter1_Presentation.asset`. Select it to edit:

- the **worry** and the case name
- every **evidence card**: text, a *Is Fact* tick, and a trap dropdown for the guesses
- the **Defence**, **Friend**, **Verdict** and **Plan** answers: text, a *Is Good* tick, and a *Why Not* explanation shown when it is picked wrongly
- the **thinking-trap names and explanations**
- optional per-case wording for the intro and each round's prompt

Make another with `Assets ▸ Create ▸ Mindscape ▸ Worry Courtroom Case`. Add it to the component's **Cases** list; with two or more, case tabs appear.

## Editing how it plays

Select the **Worry Courtroom** object. The component groups everything:

| Group | What it holds |
| --- | --- |
| **Rules** | Strike limit; how much each right answer lowers the worry; how many defence facts are needed; shuffling; star thresholds; meter speed; the shake; the Worry's smallest size and opacity; the mood thresholds. |
| **Texts** | Every sentence the game writes: speaker names and lines, headings, button labels, feedback, the case-file layout, the recess text. `{placeholders}` like `{trap}` and `{n}` are filled in at runtime. |
| **Colors** | Correct and wrong answers, tabs, step pills, strike dots, stars. |
| **Screen parts** | References to the real objects: the stage, the Worry figure, the step bar, and one panel per round. |

The screen is one UI Toolkit file, `Assets/UI Toolkit/WorryCourtroom.uxml` with its `.uss`, loaded through `Resources/EpisodeUI`. Open it in UI Builder to move things, change colours or swap the font. The script finds every element by name (`court-stage`, `p-sort`, `sort-fact` and so on), so keep the names. See [Episode Screens (UI Toolkit)](#system-episode-ui).

> [!TIP] Use your own art for the Worry
>
> The Worry is drawn from simple shapes. Assign three sprites (scowl, neutral, calm) to **Mood Sprites** and a sprite Image to **Sprite Image** on the component, and the drawn face is replaced by your art.

## How it runs

- It is one **prefab**, `Assets/Prefabs/Minigames/WorryCourtroom.prefab`, which is now just the component (the screen is loaded from the UXML at runtime). It is used by Chapter 1 Episode 3 and the standalone `WorryCourtroom` scene.
- **Start Open** decides how it behaves. *On* (the standalone scene): it runs by itself and shows case tabs and an Exit button. *Off* (Episode 1): it waits for the Quest to call `Open()`, and the result screen shows a single **Continue** button that closes it and tells the Quest it is done.
- A **Close** button is always available in Episode 1. Closing before the result screen leaves the requirement open, so talking to Mom again reopens it.
- When a case is dismissed the component fires **On Case Dismissed (stars)** if you want something else to react.
- Finished cases are remembered in `PlayerPrefs["Mindscape.WorryCourtroom.Done"]` and shown with a "(Done)" mark on their tabs.

> [!TIP] The old scene builder is gone
>
> The `Mindscape ▸ Worry Courtroom` menu (which built the uGUI scene and prefab) was removed with the move to UI Toolkit. Edit `WorryCourtroom.uxml` / `.uss` instead; the standalone scene keeps working through the prefab.

> [!MENU] Mindscape ▸ Chapter 2 - Family Expectations ▸ Episode 1 ▸ Add Worry Courtroom and Breathing Screen
>
> Places the courtroom prefab in the original Episode 1 scene with the presentation case and registers it on the Quest to open after Mom.

The wording follows the [Writing Guidelines](#story-tone): the feedback explains rather than scolds.
