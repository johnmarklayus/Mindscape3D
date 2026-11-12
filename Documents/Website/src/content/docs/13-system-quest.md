---
id: system-quest
group: Core Systems
nav: Quest System
---

# Quest System

See [Create a Quest](#workflow-quest) for the authoring workflow. This is the runtime shape.

- `Quest.Update()` calls `EvaluateNow()` every frame while active and not completed, and ticks down the episode timer using `Time.unscaledDeltaTime` (so it keeps counting even if something else scales time). **The timer is skipped while `PlayerControls.minigameOpen` is true.**
- `HasCriteria` guards against a quest with nothing configured silently "completing": at least one collectible, stress-range, NPC or minigame requirement must be set.
- NPC progress arrives through the static `QuestProgress.NPCConversationCompleted` event rather than the Quest polling NPCs directly. Any conversation ending anywhere reports here. Repeating a conversation also re-checks that NPC's minigame trigger.
- Collectible progress is read live from `CollectiblesManager.GetItemCount(itemId)`; the Quest never keeps its own copy.
- **Minigames** are held as `QuestMinigame` references. `CheckMinigameTriggers()` opens each one when its trigger fires, `NotifyMinigameCompleted()` marks it done, and `NotifyMinigameClosed()` puts a minigame the player left early back to "not triggered" so it can open again.
- When every criterion is met the quest completes once: it raises `Mindscape.ChapterUnlocked`, fires **On Quest Completed**, freezes time and shows the completion screen.
