---
id: system-stress
group: Core Systems
nav: Stress System
---

# Stress System

A meter (`PlayerControls.stressLevel`, 0 to `stressMax`) that only moves when something deliberately moves it.

- It starts at **10** and does **not** rise on its own.
- `PlayerControls.ChangeStress(amount)` is the one entry point for changing it, and it clamps to `[0, stressMax]`. Dialogue choices call it with their `stressChange`, and quests or minigames can call it too.
- **Critical stress.** If stress reaches the maximum it starts a countdown (`criticalStressDuration`, 10 seconds by default). Dropping below the maximum cancels it; running out shows the stress game-over screen through `QuestHUDController.ShowStressGameOver()`.
- Shown by the **Stress HUD**: a fill bar and a state label (STEADY, RISING, OVERLOAD, CRITICAL), turning green, amber and red. See [HUD, Journal & Pause](#system-hud).
- A Quest can require the player to stay within a stress range. Episode 1 requires 0 to 30.
- In Episode 1 no conversation choice changes stress (every `stressChange` is 0), so the number stays where it started unless a system you add moves it.

### In the story episodes

Every `AcademicEpisode` (Chapters 1 to 3) has its **own** stress meter, separate from the one above: 0 to 100, moved by `AddStress` and `EaseStress` (the breathing exercise eases it by 15 to 30), shown top centre next to the time left. The player also answers a 1 to 5 stress check-in before the first free-roam stretch and after the episode, and both are saved. See [Accounts, Progress & Saves](#system-accounts).

> [!TIP] Hooking stress to a minigame
>
> The Worry Courtroom fires `onCaseDismissed(stars)` and the Breathing Exercise fires `onCompleted`. Point either UnityEvent at `PlayerControls.ChangeStress` (with a negative number) if finishing it should ease stress.
