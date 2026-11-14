---
id: connect-episode
group: Episodes
nav: Connect it to the game
---

# Connect an Episode to the Game

How an episode becomes reachable from the main menu, and plays after the episode before it.

## Chapter 4 and later: nothing to do

An episode made with **New Episode** is added to its chapter asset (`Assets/Resources/Chapters/Chapter N`), and that is all the game needs. From the chapter asset, by themselves:

| Where | What appears |
|---|---|
| Main menu › Chapter select | The chapter's card (picture, name, progress) |
| Main menu › the chapter's page | One row per episode, in the order of the Episodes list, locked until the one before is finished |
| Loading screen | The episode's picture, number, location, title and briefing, and the chapter badge |
| End of an episode | **Continue** goes to the next episode in the list, or the next chapter's first episode, or the main menu |
| End of Chapter 3 | **Begin Chapter 4** instead of the finale, once Chapter 4 has an episode |
| Journal | A tab per episode under the chapter's name, with the chapter's journal question |

Just fill in each episode's **Location**, **Briefing** and **Thumbnail** in the chapter asset ([Create a chapter](#create-chapter), step 3).

## Chapters 1–3: code changes

The first three chapters keep their lists in code. Adding an episode to one of them still needs these changes (the full checklist is on [Create an Episode or Chapter](/#workflow-episode-chapter)):

- the chapter registry (title, location, briefing) and `MindscapeProgress` episode counts;
- a row in `MainMenuNew.uxml` and, if needed, `MainMenuNewController`;
- the loading screen (`EpisodeLoadingScreen`);
- the previous episode's `NextScene`, and this episode's `NextScene` / `ContinueLabel`;
- the menu thumbnail: **Mindscape › Main Menu › Capture Episode Thumbnails**.
