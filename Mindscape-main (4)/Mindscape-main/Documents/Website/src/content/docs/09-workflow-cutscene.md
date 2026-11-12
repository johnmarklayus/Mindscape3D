---
id: workflow-cutscene
group: Workflows
nav: Create a Cutscene
---

# Create a Cutscene

Cutscenes are their own scenes (named `Cutscene - Episode N`) built from slides of art and a line of text, played back by `CutscenePlayer.cs`. Episode 1's has four slides.

## What a slide is made of

```text
CutsceneCanvas
├── Background
└── Slides
    ├── Slide 1                  CanvasGroup (what CutscenePlayer fades)
    │   ├── Slide Image          the artwork (a Sprite from Resources/Cutscenes/Episode N/)
    │   ├── Caption Backing      a dark plate so the text reads over bright art
    │   ├── Slide Text           TextMeshPro + CutsceneText (speaker name, dialogue)
    │   └── Next Button          CutsceneNextButton (Target Slide Index)
    ├── Slide 2 ...
    └── Slide 4                  Play Episode Button instead of Next
CutsceneController               CutscenePlayer (the Slides list, fade times, episode scene)
```

## Building one

1. `GameObject ▸ Cutscene ▸ Slides` creates the slide container.
2. `GameObject ▸ Cutscene ▸ Slide` adds a slide (image + text).
3. Put each slide's art in the slide's **Image** (set the texture import to *Sprite*) and write its words in the **Slide Text**'s `CutsceneText` (the text renders live in Edit mode too).
4. `GameObject ▸ Cutscene ▸ Next Button` adds a button; set **Target Slide Index** to the slide it should jump to (0-based).
5. `GameObject ▸ Cutscene ▸ Play Episode Button` adds the button that loads the gameplay scene; set **Scene Name**.
6. On the `CutscenePlayer`, drag each slide's `CanvasGroup` into **Slides**, in play order, and set **Episode Scene Name**.

> [!MENU] Mindscape ▸ Episode 1 ▸ Build Cutscene Slides
>
> Rebuilds Episode 1's cutscene to four slides from the art in `Resources/Cutscenes/Episode 1/`: assigns each image, writes the narration, adds the caption plate, wires the Next buttons and the final Play Episode button, and fills the player's Slides list. Safe to re-run.

## Things to know

- Slides fade in and out (1 second each by default) and the player advances manually; there is no autoplay and no going back.
- `CutscenePlayer.PlayEpisode()` loads the episode through `EpisodeLoadingScreen` (with location artwork), but the **Play Episode Button** component calls `SceneManager.LoadScene` directly, so it skips the loading screen.
- Write the words to the [Writing Guidelines](#story-tone). Episode 1's slides are in the [story](#story-ch1-ep1).
