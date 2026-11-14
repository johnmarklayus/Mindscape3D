---
id: edit-episode
group: Episodes
nav: Edit an episode
---

# Edit an Episode, Step by Step

You can change an episode that already exists in the Unity editor: who is in it, where things are, where the camera looks, and what the loading screen says. The examples below use real scenes of the game.

> [!TIP] What you need
>
> - The project open in **Unity 6000.5.8f1**, with the Console open (**Window › General › Console**).
> - The Scene view visible. To fly: hold the **right mouse button** and use **W A S D** (**Q / E** down / up). To jump to an object: select it in the Hierarchy and press **F** with the mouse over the Scene view.

## Part 1: Open the episode and find its Inspector

**The example:** *Chapter 1 · Episode 3 · Everyone Seems Ahead* (the cafeteria).

1. In the **Project** window, open `Assets/Scenes` and double-click **Chapter 1 - Episode 3**. If Unity asks to save the scene that was open, click **Save** (or **Don't Save** if you changed nothing).
2. In the **Hierarchy**, click the object at the top called **Chapter 1 · Episode 3 - Cafeteria**. This object holds the episode.
3. The **Inspector** now shows the episode: its fields, then two lists, **Scene points** and **Story markers**.

Every episode has one object like this. Its name starts with the chapter, for example:

| Scene | Episode object |
|---|---|
| `Chapter 1 - Episode 1` | **Chapter 1 · Episode 1 - House** |
| `Chapter 1 - Episode 3` | **Chapter 1 · Episode 3 - Cafeteria** |
| `Chapter 2 - Episode 1` | **Chapter 2 · Episode 1 - After School** |
| `Chapter 3 - Episode 4` | **Chapter 3 - The Corner of the Room** |
| `Chapter 3 - Episode 7` | **Chapter 3 - The Walk Home** |

> [!TIP] Check
>
> The Inspector of **Chapter 1 · Episode 3 - Cafeteria** has a field **Friend Name** set to `Sam`.

## Part 2: Change a setting in the Inspector

The fields at the top are the episode's settings. In the cafeteria:

1. Click in **Friend Name**, change `Sam` to `Ana`, press **Enter**.
2. Save the scene: **Ctrl + S** (Mac **Cmd + S**).

Every line that says the friend's name now says *Ana* ("Ana said they'd save a seat", "Ana is waving from the table near the door"). Other fields work the same way: point at a field and wait a moment, and its tooltip says what it does.

## Part 3: Move a spot, the player's start or a camera

**Scene points** lists every object the episode uses: the spots with the gold marker, where the player starts, the camera views. In the cafeteria:

| Scene point | What it is |
|---|---|
| **Spawn** → *Outside Room 03* | Where Joey starts the episode |
| **Table** → *Join the table* | The gold spot where **[E] Sit with your classmates** appears |
| **Table View** → *Table view* | The camera at the table |
| **Inside** → *Inside the cafeteria* | Walking past it counts as arriving in the cafeteria |
| **Student One**, **Student Two**, **Friend** | Where the camera looks when each one speaks |

**To move the table spot:**

1. In **Scene points**, click **Select** next to **Table**. *Join the table* is selected and the Scene view jumps to it.
2. Press **W** (Move tool) with the mouse over the Scene view. Drag the red and blue arrows to move it along the floor.
3. Save the scene.

**To aim the table camera:**

1. Click **Select** next to **Table View**.
2. Press **E** (Rotate tool) to turn it and **W** to move it. Its blue arrow is where the camera looks.
3. To aim it exactly: fly the Scene view to the shot you want, keep *Table view* selected, and use **GameObject › Align With View** (**Ctrl + Shift + F**, Mac **Cmd + Shift + F**).
4. Save the scene.

> [!TIP] Check
>
> Press **Play**, walk to the cafeteria and to the table. **[E] Sit with your classmates** appears where you put the spot, and the camera at the table shows the new shot. Press **Play** again to stop.

## Part 4: Move people the code places (story markers)

Some positions are worked out by the episode's script, for example where the family stands. **Story markers** take them over, so you can drag them instead.

**The example:** in *Chapter 3 · Episode 7* the family waits outside the house. Move Mom further from the door.

1. Open `Assets/Scenes/Chapter 3 - Episode 7` and select **Chapter 3 - The Walk Home** in the Hierarchy.
2. In the Inspector, open **Story markers**. It lists `Family/Mom`, `Family/Dad`, `Family/Tim`, `Welcome/Mom step` and `Welcome/Tim step`, each marked *in scene*.
3. Click **Select** next to `Family/Mom`. The marker **Family Mom** is selected.
4. Move it with **W** and turn it with **E**. The blue arrow is the way Mom faces.
5. Save the scene.

A marker marked *built-in* is not in the scene yet: click **Create missing markers at their built-in positions**, then move it. To return to the built-in position, delete the marker (select it, **Delete**).

## Part 5: The loading screen, the time and the order

| What to change | Chapter 4 and later | Chapters 1–3 |
|---|---|---|
| Episode title, location, briefing, picture | The chapter asset (Part 6) | Written in the chapter's script (ask a developer) |
| Time to finish | **Time Limit** on the episode object | Written in the episode's script |
| A cutscene before the episode | **Cutscene Before** in the chapter asset | A cinematic set to *At the start of the episode* ([Create a cinematic](#create-cinematic)) |
| The words people say | Cinematics and conversations | **Dialogue Words** ([Change the dialogue](#edit-words)) |
| Add a new moment | A cinematic ([Create a cinematic](#create-cinematic)) | A cinematic, too: it works in every episode |

## Part 6: Chapter 4 and later: the chapter asset

1. In the Project window, open `Assets/Resources/Chapters` and click the chapter (for example **Chapter 4**).
2. The Inspector shows the chapter: **Title**, **Description**, **Thumbnail** (the menu card), **Journal Prompt**, and the **Episodes** list.
3. Open an episode in **Episodes** with its ▸ arrow:

   | Field | What it changes |
   |---|---|
   | **Title** | The episode's name in the menu and on the loading screen |
   | **Scene** | The scene that plays (its name, as in File › Build Profiles) |
   | **Location** | The place shown on the loading screen, for example `JOEY'S HOUSE` |
   | **Briefing** | What the player will do, on the loading screen |
   | **Thumbnail** | The episode's picture (empty: the chapter's picture) |
   | **Cutscene Before** | A slide cutscene that plays first ([Create a cutscene](#create-cutscene)) |

4. **To reorder episodes**, drag them by the ☰ handle. Also change **Episode Number** on each scene's episode object so they match (1 = first).
5. Under **In the game** the Inspector checks the chapter: a yellow or red box says what is wrong. **Open scene** next to an episode opens it.

Assets save by themselves; use **File › Save Project** to be sure.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| A spot moved but nothing changed in Play | The scene was not saved, or you moved it while playing. Stop Play mode, move it again, save. |
| A person still stands in the old place | That position comes from a story marker: move the marker (Part 4), not the person. |
| The camera shows a wall | Re-aim the view (Part 3). Keep the view inside the room, a little above head height. |
| *Episode 2: there is no scene called …* | **Scene** in the chapter asset does not match the scene's name. Copy the name exactly. |
