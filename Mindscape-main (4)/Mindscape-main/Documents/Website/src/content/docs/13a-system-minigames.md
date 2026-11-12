---
id: system-minigames
group: Minigames
nav: Minigame System
---

# Minigame System

Minigames are short, self-contained screens the quest can open and wait on. Two are used in the story today, and a separate lab holds ten practice ones.

| Minigame | Where | Opened by |
| --- | --- | --- |
| [Breathing Exercise](#minigame-breathing) | Chapter 1 Episode 2 and the original Episode 1 | A conversation or a story beat |
| [Worry Courtroom](#minigame-courtroom) | Chapter 1 Episode 3, the original Episode 1, and its own scene | A conversation or a story beat |
| Minigame Lab (ten practice games) | `MinigameTestLab` scene | A launcher menu |

## The contract: `QuestMinigame`

Anything the Quest can open derives from `QuestMinigame` (`Assets/Scripts/Minigames/QuestMinigame.cs`):

```csharp
public abstract class QuestMinigame : MonoBehaviour
{
    public abstract bool IsOpen { get; }
    public abstract void Open(Quest quest);
    public abstract void Close();
    public virtual string QuestDisplayName { get; }   // shown in the Journal
}
```

A minigame is expected to do four things:

1. **Set `PlayerControls.minigameOpen = true` while it is on screen** (and false when it closes). That freezes movement, hides NPC prompts and pauses the Quest's episode timer.
2. **Call `quest.NotifyMinigameCompleted(this)` when the player finishes.** Only that counts toward the Quest.
3. **Call `quest.NotifyMinigameClosed(this)` if the player leaves early**, so the same trigger can open it again.
4. **Draw above everything else.** Minigame screens are UI Toolkit documents with sorting order 10, above the story panels and the pause menu (5).

## Adding a new minigame to a quest

1. Write a component that derives from `QuestMinigame` and follows the four points above.
2. Build its screen as a UXML + USS file in `Assets/UI Toolkit/`, in the [theme](#system-theme), and spawn it with `EpisodeUI.Spawn(name, tree, 10, transform)`. Reuse `EpisodeScreens.uss` for the ink-and-gold look. `BreathingMinigame.BuildUI()` is the short example.
3. On the Quest, add a row under **Required Minigames**, drag the component into **Minigame**, and pick a **Trigger** (see [Create a Quest](#workflow-quest)).

> [!TIP] Make it customisable
>
> Both shipped minigames put their numbers, wording and colours in serialized fields (a `rules`, `texts` and `colors` group) so a designer can change them without code. Do the same for new ones.

## The Minigame Lab

`Assets/Scenes/MinigameTestLab.unity` is a launcher with ten small practice minigames (breathing rhythm, thought reframing, task prioritisation, focus challenge, memory match, grounding, schedule puzzle, emotion check, stress meter, quick sequence). They derive from `MinigamePopup`, a lighter base that builds a popup in code and is not wired to the Quest. `MinigameUI` (in the same folder) holds the shared helpers and theme colours.

> [!MENU] Mindscape ▸ Minigame Lab ▸ Create or Open Test Scene
>
> Creates or opens the lab. **Verify All Games (Play Mode)** runs automated interaction checks and writes results to `Temp/MinigameLabVerification.txt`.
