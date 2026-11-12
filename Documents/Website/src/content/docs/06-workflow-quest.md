---
id: workflow-quest
group: Workflows
nav: Create a Quest
---

# Create a Quest

A Quest is the win/lose condition for an episode. It evaluates its criteria continuously and can end the round by success or by timing out.

> [!MENU] GameObject
>
> `GameObject ▸ Quest`: creates a GameObject with the `Quest` component and automatically ensures the Quest HUD (Journal) exists in the scene.

1. Set **Quest ID**, **Quest Name** and **Description**. These show up in the in-game Journal (press `Q`, or use the Journal HUD button).
2. Add criteria (a quest with none configured will never auto-complete, and the Inspector warns you):

   - **Required Collectibles**: drag a `CollectibleItem` (from the scene or a prefab) and a quantity. Matched against what the player has collected, through `CollectiblesManager.GetItemCount`.
   - **Require Stress Range**: the player's stress must be between Minimum and Maximum at the moment of evaluation. Episode 1 uses 0 to 30.
   - **NPC Names To Talk To**: plain strings matched against every NPC's `npcName` once its conversation ends. Episode 1 requires **Mom**, **Dad** and **Tim**.
   - **Required Minigames**: every minigame in the list must be completed. See below.
3. **Episode Timer**: minutes and seconds. Set both to `0` to disable the countdown. When it hits zero before the quest completes, the episode fails. Episode 1 uses 5 minutes. The clock **pauses while any minigame is open**.
4. Hook up **On Quest Completed** and **On Episode Failed** UnityEvents for anything extra (unlocking the next chapter already happens automatically).

## Required Minigames

Each row has a **Minigame** (anything that derives from `QuestMinigame`: the [Breathing Exercise](#minigame-breathing), the [Worry Courtroom](#minigame-courtroom), or your own) and a **Trigger** that says when the quest opens it:

| Trigger | Opens the minigame |
| --- | --- |
| On Quest Start | As soon as the episode begins |
| At Timer | After the given minutes and seconds of the episode |
| When Stress | When stress rises to (or falls to) a threshold |
| When Talk To NPC | When the named NPC's conversation ends (Episode 1 uses this) |
| Manual | Only when something calls `Quest.TriggerMinigame(index)` |

If the player closes a minigame before finishing it, the requirement stays open and the same trigger can open it again; with *When Talk To NPC*, talking to that person once more does it. The quest only counts a minigame once the player finishes it.

### What happens automatically

- On success: `PlayerPrefs["Mindscape.ChapterUnlocked"]` is raised, `Time.timeScale` is set to `0`, and `QuestHUDController.ShowEpisodeComplete(this)` shows the completion screen.
- On timeout: `Time.timeScale = 0` and `QuestHUDController.ShowGameOver(this)` shows the failure screen instead.
- Progress toward every criterion, including each minigame as DONE or PENDING, is visible live in the Journal and, while the Quest is selected in the Editor during Play mode, in its Inspector.

> [!TIP] Multiple quests
>
> Nothing stops a scene from having more than one active `Quest`; each evaluates and can complete or fail independently.
