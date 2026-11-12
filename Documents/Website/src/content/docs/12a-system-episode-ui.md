---
id: system-episode-ui
group: Core Systems
nav: Episode Screens (UI Toolkit)
---

# Episode Screens (UI Toolkit)

Every screen a story episode shows is a **UI Toolkit** file in `Assets/UI Toolkit/` (a `.uxml` layout and a `.uss` style), so it can be restyled in **UI Builder** without touching code. Each screen is its own file: the pause menu and the dialogue bar are not merged.

## The files

| Screen | File | Used for |
| --- | --- | --- |
| Objective, status | `EpisodeObjective`, `EpisodeStatus` | Top-left objective and checklist; time left and the stress meter |
| Dialogue | `Dialogue` | The Say / Think / Me bar |
| Choices | `Choice` | A choice, and the stress check-ins |
| Story card | `StoryCard` | Full-screen title and ending cards |
| Text entry | `TextEntry` | Name prompt and journal prompts (`.multiline` for long answers) |
| Complete | `EpisodeComplete` | Episode complete and "Out of time" |
| Pause | `PauseMenu` | Shared by the episodes and the Tutorial |
| NPC conversation | `NPCDialogue`, `InteractPrompt` | The conversation panel and the "[ F ]  Talk to" / "[ E ]" prompt |
| Phone | `PhoneChat` | Chat view and lock-screen view in one phone |
| Photograph | `Photograph` | A close-up picture with a caption |
| Flashback frame | `FlashbackIndicator` | Sepia frame and the "FLASHBACK" badge |
| Overlays | `ExamPaper`, `ThoughtJournal`, `LaptopTasks` | The exam paper, the Chapter 2 journal, the laptop task list |
| Fade, crosshair | `ScreenFade`, `Crosshair` | The screen fade and the centre dot |
| Minigames | `Breathing`, `WorryCourtroom` | See [Minigames](#system-minigames) |
| Main menu | `MainMenuNew/MainMenuNew.uxml` | Every menu page, see below |

They share `EpisodeScreens.uss` (the ink-and-gold look, with `.screen` colour variables and `.btn` / `.pale` / `.teal` buttons) and one Panel Settings, `EpisodePanelSettings` (1280x720, match 0.5).

## How they are found

`Assets/Resources/EpisodeUI.asset` (a `Mindscape.AcademicPressure.EpisodeUI` ScriptableObject, loaded with `EpisodeUI.Load()`) points at every one of those assets. It is the only Resources piece, because episodes are built at runtime with nothing to drag files onto. `AcademicEpisode.BuildScreens()` makes one UIDocument per file; other code (the minigames, the crosshair, the door prompt) uses `EpisodeUI.Spawn(name, tree, order, parent)`. See the sort-order table in [Conventions & Gotchas](#ref-conventions).

## Story verbs

- `OpenPhone(contact)`, `PhoneMessage(fromMe, text, wait)`, `PhoneChoose`, `ClosePhone()`: the chat. `OpenPhoneLock(time, date, dim)` and `PhoneNotification(app, title, body)`: the lock screen. Every phone moment in the story uses this one phone.
- `ShowPhoto(texture, caption)` / `HidePhoto()`.
- `Ask(...)` for text entry (one question line and a single-line field; the journal uses the multiline layout).
- `ShowFlashback("The night before")` / `EndFlashback()` mark a memory. For a fade in and out, use `FlashbackIn(when, whileBlack)` and `FlashbackOut(whileBlack)`: they fade to black, swap the scene while it is black, then fade back, so a memory never cuts. An episode set in the past overrides `FlashbackLabel` ("Examination morning") to keep the frame on for the whole episode.
- `Overlay(tree, name, order)` adds a full-screen overlay document (default order -3).

## The main menu

Every page of the main menu lives in `MainMenuNew.uxml` under `#stage` as `page-<name>`; all but home carry `.hidden` (remove it in the Inspector to preview a page). `MainMenuNewController` binds elements by name (`open-*`, `back-*`, `chapter-N`, `academic-episode-N`, `episode-N`, `social-episode-N`, sliders named after their PlayerPrefs key, `key-0` to `key-7`). A new episode needs a row in the UXML; the controller logs a warning for a missing one. The Continue slot, journal text, lock text and account line are still filled in from code.

## Gotchas

- USS has no `:first-child`. A rule like `.card Label` outranks single-class rules, so do not set margins there; the reset is `.unity-label {}`.
- Labels and Buttons need `white-space: pre-wrap` to keep the double-space gaps.
- `%` margins and padding resolve against **width**.
- Buttons are `focusable = false` so Space and Enter cannot re-click them, and document roots use `pickingMode = Ignore` so clicks pass through while nothing is open.
- USS rotates clockwise, uGUI counter-clockwise.
- `Cursor` is ambiguous once `using UnityEngine.UIElements` is in: write `UnityEngine.Cursor`.
- If you edit a UXML in UI Builder, keep the element names the code looks up.
