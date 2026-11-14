---
id: create-chapter
group: Chapters
nav: Create a chapter
---

# Create a Chapter, Step by Step

A chapter is a group of episodes with its own card in the main menu. Chapters 1–3 are already in the game; new chapters start at **Chapter 4**. Making one takes a few clicks and no code: everything about it lives in one **chapter asset** that you edit in the Inspector.

**The example:** *Chapter 4 · New Beginnings*, with one episode, *First Steps*.

> [!TIP] What you need
>
> - The project open in **Unity 6000.5.8f1**, with the Console open (**Window › General › Console**).
> - A picture for the chapter: a wide image (16:9), PNG or JPG, for example a screenshot of where the chapter happens. You can add or change it later.

## Part 1: Make the chapter

1. In the menu bar at the top of Unity, click **Mindscape › Story › New Chapter…**. A window called **New Chapter** opens.
2. Fill it in:

   | Field | Type or pick |
   |---|---|
   | Chapter number | `4` (already filled in: the next free number) |
   | Chapter name | `New Beginnings` |
   | Description | `Joey starts something new, one small step at a time.` |

3. **Add the picture.** Click **Import image from your computer…**, find the picture in the file window and click **Open**. The picture appears in the square box on the left.
   (Already in the project? Drag it from the Project window into the box instead.)
4. Leave **Make Episode 1 of this chapter right after** ticked.
5. Under the fields, **Chapter asset** shows `Assets/Resources/Chapters/Chapter 4.asset`. Click **Create Chapter**.

> [!TIP] Check
>
> - The **Project** window jumps to `Assets › Resources › Chapters` with **Chapter 4** selected. Its Inspector shows *Number 4*, *Title New Beginnings*, your description and picture, and an empty **Episodes** list.
> - The **New Episode** window opens by itself with **Chapter 4**, **Episode 1** and *Adds to: Chapter 4 · New Beginnings*.
> - The picture you imported is in `Assets › Resources › Chapters › Images`.

> [!WARN] Do not move the chapter asset
>
> The game finds chapters only in `Assets/Resources/Chapters`. Keep the asset there (you may rename it).

## Part 2: Make its episodes

1. In the **New Episode** window that opened, type the episode's **Title** (`First Steps`), pick a **Template scene**, and click **Create Episode**.
2. Then follow [Create an episode](#create-episode) from Part 2: place the start point, the camera, the spots, and write the story.
3. **For the next episodes:** click the chapter asset (`Assets/Resources/Chapters/Chapter 4`) and, at the bottom of its Inspector, click **Make Episode 2 of this chapter…**. The New Episode window opens with Chapter 4 and Episode 2 filled in.

Every episode made this way is added to the chapter's **Episodes** list by itself, with its title and scene.

## Part 3: Fill in the chapter in the Inspector

Click the chapter asset. Everything the game shows about the chapter is here:

| Field | What it is | Example |
|---|---|---|
| **Number** | The chapter's number. Chapters follow each other: 4, then 5, then 6. | `4` |
| **Title** | The chapter's name: chapter card, loading screen badge, journal. | `New Beginnings` |
| **Description** | One or two sentences, under the name on the chapter's episode page. | `Joey starts something new…` |
| **Thumbnail** | The chapter card picture, and the loading screen picture of any episode without its own. | *(your picture)* |
| **Journal Prompt** | The journal question after each episode. Empty: the usual question. | `What helped you take a first step today?` |
| **Episodes** | The episodes, in order. Click the ▸ arrow in front of one to open it. | |

Each episode in the list has:

| Field | What it is | Example |
|---|---|---|
| **Title** | The episode's name: menu row, loading screen, journal tab. | `First Steps` |
| **Scene** | The scene's name. Filled in by New Episode; leave it. | `Chapter 4 - Episode 1` |
| **Location** | Where it happens, on the loading screen. Capital letters look best. | `JOEY'S HOUSE` |
| **Briefing** | What the player will do, on the loading screen (one to three short lines). | `Come home. Talk with Mom. Rest at your desk.` |
| **Thumbnail** | This episode's own picture (menu row and loading screen). Empty: the chapter's picture. | *(optional)* |

**To give an episode its own picture:** drag the image file from your computer (Finder / File Explorer) into the Project window, into `Assets/Resources/Chapters/Images`. Then drag it from the Project window onto the episode's **Thumbnail** field.

Changes in the Inspector are saved by themselves. Press **Ctrl + S** (Mac **Cmd + S**) to be sure.

## Part 4: Read the "In the game" box

Below the fields, the Inspector says whether players can reach the chapter:

| The box says | What to do |
|---|---|
| *In the game as Chapter 4 · New Beginnings, with 1 episode. It unlocks when Chapter 3 is finished.* | Nothing: it is in the game. |
| *No episodes yet* | Click **Make Episode 1 of this chapter…** at the bottom. |
| *Players cannot reach this chapter: Chapter N is missing or has no episodes* | Make the chapter before it first (a Chapter 5 needs a Chapter 4). |
| *Another chapter asset also has number N* | Two assets share a number. Change one of them. |
| *Episode N … is not in File › Build Profiles* | Open **File › Build Profiles**, click **Add Open Scenes** with that scene open, or drag the scene into the Scene List. |
| *Episode N: there is no scene called …* | The scene was renamed or deleted. Fix the **Scene** field to the scene's exact name. |

Each episode also has an **Open scene** button.

## Part 5: Try it

**Play one episode straight away:** click **Open scene** next to it in the chapter's Inspector (or double-click the scene in `Assets/Scenes`) and press **Play**.

**See it in the main menu:**

1. Open `Assets/Scenes/Intro.unity` and press **Play**. Skip the intro. If the game asks you to sign in, choose **Play offline**.
2. Click **Play Game**. The **CHAPTER SELECT** page now has four cards. **Chapter 4 · New Beginnings** shows your picture and *LOCKED · finish Chapter 3*: chapters unlock in order, so a player reaches it after Chapter 3.
3. Once Chapter 3 is finished, the card opens the chapter's page with one row per episode. The loading screen shows the episode's picture, location, title and briefing, and the badge *CHAPTER 04 · NEW BEGINNINGS*.
4. At the end of Chapter 3, the button now says **Begin Chapter 4** (instead of the finale) and goes straight to its first episode.

## Part 6: Change the order, rename or remove episodes

- **Rename:** change the episode's **Title** in the chapter asset. (The scene's file name can stay.)
- **Change the order:** drag an episode by the ☰ handle on its left in the Episodes list. Then open each moved episode's scene, select its episode object, and set **Episode Number** in the Inspector to its new place (1 = first). The two must match, or the episode saves its progress under the wrong number.
- **Remove:** select the episode in the list and click **–** under it. Delete its scene too if you no longer need it, and remove it from **File › Build Profiles**.

## Part 7: The next chapter

Do Part 1 again: **Mindscape › Story › New Chapter…** fills in **5** by itself. Chapter 5 unlocks after Chapter 4, and the last episode of Chapter 4 continues into it.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| **New Chapter** is not in the Mindscape › Story menu | The scripts have an error. Open the Console, fix the first red line. |
| *Chapter 4 already exists* | There is already a chapter asset with that number in `Assets/Resources/Chapters`. Open it instead, or pick the next number. |
| The chapter card has no picture | The **Thumbnail** field is empty. Drag a picture into it. |
| A grey or empty loading screen | Neither the episode nor the chapter has a **Thumbnail**. |
| The chapter card is not in the main menu | Read the box under **In the game** in the chapter's Inspector (Part 4). |
| Continue at the end of an episode goes to the main menu | It is the last episode of the last chapter. Add the next episode or chapter. |
| Progress jumps or an episode stays locked | An episode's **Episode Number** does not match its place in the Episodes list (Part 6). |
