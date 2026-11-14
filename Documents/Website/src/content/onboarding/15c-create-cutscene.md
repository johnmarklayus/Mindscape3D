---
id: create-cutscene
group: Cutscenes & Cinematics
nav: Create a cutscene
---

# Create a Cutscene, Step by Step

A cutscene is a row of full-screen pictures with words. This tutorial makes one that plays before an episode, click by click.

**The example:** *Morning*, three pictures (the alarm, Joey waking up, the bus), playing before *Chapter 4 · Episode 1*.

> [!TIP] What you need
>
> - The project open in **Unity 6000.5.8f1**, with the Console open (**Window › General › Console**).
> - The pictures: PNG or JPG, wide (16:9 looks best, for example 1920 × 1080). Name them in order (`1.png`, `2.png`, `3.png`) and put them in one folder on your computer.
> - To play it before an episode: the chapter and the episode already made ([Create a chapter](#create-chapter)). Not made yet? You can still make the cutscene and hook it up later (Part 4).

## Part 1: Make the cutscene

1. In the menu bar at the top of Unity, click **Mindscape › Story › New Cutscene…**. A window called **New Cutscene** opens.
2. **Name:** type `Morning`. Only you see this name; players do not.
3. **Add the pictures.** Click **Add every picture in a folder…**, pick the folder with your pictures, and click **Open**. Every PNG and JPG in it is added, in name order. (Or click **Add a picture…** once per picture.)
4. Check the list: it shows *Slide 1*, *Slide 2*, *Slide 3* with the file names.
   - **↑** moves a picture one place up.
   - **✕** removes it from the list.
5. **Use it:** pick **Before an episode**. Two more fields appear:
   - **Chapter:** *Chapter 4 · New Beginnings*
   - **Episode:** *Episode 1 · First Steps*
6. **Saved in** shows `Assets/Story/Cutscenes/Morning/Morning.asset`. Click **Create Cutscene**.

> [!TIP] Check
>
> - The **Project** window jumps to `Assets › Story › Cutscenes › Morning` with the **Morning** asset selected. Next to it are your pictures, renamed *Slide 1*, *Slide 2*, *Slide 3*.
> - The Console shows `[New Cutscene] Plays before Chapter 4 · Episode 1` and `Made … with 3 slide(s)`.
> - At the bottom of the asset's Inspector: *Plays before Chapter 4 · Episode 1 (First Steps)*.

## Part 2: Write the words

Click the **Morning** asset. Its Inspector has a **Slides** list. Click the ▸ arrow in front of **Element 0** to open the first slide:

| Field | What to type | Example |
|---|---|---|
| **Image** | Already set to your picture. Drag another picture here to change it. | *Slide 1* |
| **Speaker** | Who speaks. **Leave it empty for narration.** | *(empty)* |
| **Text** | The words under the picture. `Joey` is replaced by the player's name. | `7:50 in the morning. The alarm rings.` |
| **Auto Advance Seconds** | `0` waits for the player to press Space. A number moves on by itself after that many seconds. | `0` |

Do the same for the other slides, for example:

| Slide | Speaker | Text |
|---|---|---|
| 2 | *(empty)* | `Joey opens his eyes. For a moment there is only the breath, in and out.` |
| 3 | `Mom` | `The bus leaves at eight. Take your time, but not too much!` |

Keep it short: one or two sentences per slide reads well.

## Part 3: Look and sound (optional)

Under the slides, in the same Inspector:

| Field | What it does | Default |
|---|---|---|
| **Fade Seconds** | How long each slide takes to fade in and out. | `0.6` |
| **Music** | A music clip for the cutscene (drag an audio file from the Project window). The game's music pauses and comes back after. Empty: the game's music keeps playing. | *(empty)* |
| **Music Volume** | How loud that music is. | `0.6` |
| **Can Skip** | Lets the player skip the rest with **Esc** (gamepad **Start**). | ✔ |
| **Next Scene** | Only for a cutscene that is a scene of its own (Part 4, option C). Leave it empty here. | *(empty)* |

**To add another slide later:** click **Add a slide from a picture…** at the bottom of the Inspector and pick the picture. **To reorder:** drag a slide by the ☰ handle on its left. **To remove:** select it and click **–** under the list.

The Inspector warns about any slide with neither a picture nor words.

## Part 4: Where it plays

The cutscene was hooked up in Part 1. These are all the ways, if you want to change it:

**A. Before an episode (Chapter 4 and later).** Click the chapter asset (`Assets/Resources/Chapters/Chapter 4`), open the episode in its **Episodes** list, and drag the cutscene asset into **Cutscene Before**. Empty the field to stop it.

**B. In the middle of an episode, or in Chapters 1–3.** Make a cinematic ([Create a cinematic](#create-cinematic)) and give it a step **Screen: play a cutscene** with this cutscene.

**C. As a scene of its own.** In **New Cutscene**, pick **As a scene of its own** and type the scene to open afterwards in **Then open scene** (for example `Chapter 4 - Episode 1`). The tool makes `Assets/Scenes/Cutscene - Morning.unity` and adds it to the build list. Something still has to open that scene (another scene's next scene, or a menu button), so A or B is usually easier.

## Part 5: Try it

1. Open the episode's scene (`Assets/Scenes/Chapter 4 - Episode 1.unity`) and press **Play**.
2. The cutscene starts first: the first picture fades in, with its words at the bottom and *Space Next · Esc Skip* in the corner.
3. Press **Space** (or **Enter**, **E**, the right arrow, a mouse click, a tap, or gamepad **A**) for the next slide.
4. After the last slide the episode begins.
5. Press **Play** again to stop.

> [!WARN] Played when the episode starts, not when a save is loaded
>
> Loading a saved game skips the cutscene, so players do not see it twice.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| **New Cutscene** is not in the Mindscape › Story menu | The scripts have an error. Open the Console, fix the first red line. |
| *A cutscene with that name already exists* | Pick another name, or open the existing one in `Assets/Story/Cutscenes`. |
| *There are no chapters made in the editor yet* | Make one first ([Create a chapter](#create-chapter)), or pick **Nothing yet** and use it from a cinematic. |
| The cutscene does not play before the episode | Open the chapter asset: is it in that episode's **Cutscene Before**? Did you start the episode fresh (not from a save)? |
| A black slide | That slide has no **Image**. |
| The picture is cut off at the sides | It is not 16:9. The picture always fills the screen; use a wider picture or crop it. |
| The words run off the plate | Too much text for one slide. Split it over two slides. |
