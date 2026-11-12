---
id: system-accounts
group: Core Systems
nav: Accounts, Progress & Saves
---

# Accounts, Progress & Saves

> [!TIP] Connecting your own Supabase project
>
> The URL and publishable key are in `Assets/Scripts/Data/MindscapeCloud.cs` (lines 21-23). Follow [Supabase Connection Setup and Settings](#workflow-supabase) for migrations, the Edge Function, email OTP, SMTP, Google OAuth, secrets and verification.
>
> To add a new cloud data feature, follow the copy-paste [Supabase Table → Unity guide](#workflow-supabase-data).

## Where data is saved

- **Locally**: `Assets/Database/` has a P/Invoke binding to the operating system's SQLite plus a `PlayerPrefs` mirror. The WebGL build uses local storage only.
- **In the cloud** (optional, when signed in): a Supabase project holds `players`, `episode_progress`, `journal_entries`, `assessments` and `episode_records`. Tables have row-level security with no policies; the game only calls `SECURITY DEFINER` functions (`start_episode`, `complete_episode`, `get_progress`, `save_journal`, `get_journal`, `save_assessment`, `get_assessments`, `save_episode_record`, `get_episode_records`). The advisor warnings about those are by design.

## Accounts

Sign-up uses **Supabase Auth with a one-time code**: username, email and password, then a six-digit code emailed to confirm. Resetting a password works the same way (who, then code, then new password).

The game never talks to Supabase Auth directly. It calls one edge function, `account` (`supabase/functions/account/index.ts`), whose actions include sign-up, availability checks, code verification, login, password recovery, token refresh, logout, archive/recovery and Google sign-in. Login accepts a username **or** email without exposing which email belongs to a username. `MindscapeCloud.cs` keeps the access and refresh tokens in PlayerPrefs, refreshes them before they expire and retries once on a 401. The UI is `page-register`, the `account-modal` and the "Forgot password?" button in `MainMenuNew.uxml`, driven by `MainMenuNewController`.

> [!WARN] Dashboard settings
>
> These cannot be set from Unity: turn **Confirm email** on, put `{{ .Token }}` (the six-digit code) in the *Confirm signup* and *Reset password* email templates, add custom SMTP before real players use it, and configure both Google redirect URLs if Google sign-in is offered. See the [settings checklist](#workflow-supabase).

New episodes must call `MindscapeCloud.EpisodeStarted` / `EpisodeCompleted`; new journal prompts go through `MindscapeDatabase.SaveJournal`. Schema changes go through migrations.

## Progression

`MindscapeProgress` decides what is unlocked: Chapter 1 Episode 1 is always open; an episode opens when the previous one is complete; a chapter opens when the whole previous chapter is complete. Signed-in players use their account's progress, offline players the device's PlayerPrefs completion keys. The main menu shows locked rows and cards (`.locked` in `MainMenuNew.uss`).

## In an episode

Every `AcademicEpisode` (Chapters 1 to 3) has:

- a **time limit** (`TimeLimit`, default 600 seconds, overridden per episode) that counts down only while the player is free to roam; at zero the episode ends with "Out of time" (Replay / Main menu);
- a **stress meter** from 0 to 100 (`AddStress`, `EaseStress`; the breathing exercise eases it) at the top centre, and a 1 to 5 **stress check-in** after the episode completes.

When an episode finishes, `MindscapeDatabase.SaveEpisodeRecord` stores it (SQLite `episode_records`, plus PlayerPrefs, plus the cloud when signed in) and `SaveAssessment` stores the check-ins. The Main Menu > Journal > **Self-reflection** tab shows them.
