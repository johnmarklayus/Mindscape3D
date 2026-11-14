---
id: create-episode
group: Episodes
nav: Create an episode
---

# Create an Episode, Step by Step

This tutorial makes one small, complete episode from nothing, click by click. Follow it once exactly as written; after that, change the words and places to make your own.

**The example episode:** *Chapter 4 · Episode 1 · First Steps*. Joey comes home, talks with Mom, picks a reply, then goes to the desk. It takes about 30 minutes.

> [!TIP] What you need
>
> - **Chapter 4 made first** ([Create a chapter](#create-chapter), 5 minutes). Every new episode belongs to a chapter; the chapter is what puts it in the main menu.
> - The project open in **Unity 6000.5.8f1** (Unity Hub › Projects › *mindscape-3d*).
> - **VS Code** (or Rider) to edit one script file.
> - Unity's Console open: **Window › General › Console**. Red lines there are errors; read them first if anything goes wrong.

## Part 1: Create the scene

1. In the menu bar at the very top of Unity, click **Mindscape › Story › New Episode…**. A small window called **New Episode** opens.
2. Fill it in exactly like this:

   | Field | Type or pick |
   |---|---|
   | Chapter | `4` |
   | Episode | `1` |
   | Title | `First Steps` |
   | Template scene | `Chapter 3 - Episode 7` (Joey's house in the evening) |
   | New story script | ✔ ticked |
   | Script class | leave it as `Chapter4Episode1FirstSteps` |

   Under the fields, the window shows:
   - **Adds to** *Chapter 4 · New Beginnings (as Episode 1)*: the chapter it joins. If it says *There is no Chapter 4 yet* instead, click **Make Chapter 4 first…** and do [Create a chapter](#create-chapter).
   - **Scene** `Assets/Scenes/Chapter 4 - Episode 1.unity` and **Script** `Assets/Scripts/Chapters/Chapter 4/Chapter4Episode1FirstSteps.cs`: where the files go.

   (Opening the window from the chapter's Inspector, **Make Episode 1 of this chapter…**, fills in Chapter and Episode for you.)
3. Click **Create Episode**.
4. If Unity asks to save the scene that is open, click **Save** (or **Don't Save** if you changed nothing).
5. **Wait.** The bottom-right corner of Unity shows a spinning icon while it compiles the new script (10–60 seconds). Do not click anything until it stops.
6. The new scene opens by itself.

> [!TIP] Check
>
> - The tab above the Scene view says **Chapter 4 - Episode 1**.
> - In the **Hierarchy** (the list on the left) there is a new object **Episode - First Steps**, already selected.
> - The Console shows lines starting with `[New Episode]`: *Added to Chapter 4 as Episode 1* and, last, *is ready with Chapter4Episode1FirstSteps*.

> [!WARN] If the scene did not open
>
> Look at the Console. A red line means the script did not compile: double-click it, fix it, save, and come back. Then open the scene yourself (**Project** window › `Assets/Scenes` › double-click *Chapter 4 - Episode 1*), select **Episode - First Steps**, and check its Inspector shows the *Chapter4 Episode1 First Steps (Script)* component. If it is missing, click **Add Component** and type `Chapter4Episode1FirstSteps`.

## Part 2: Look at what you got

Click **Episode - First Steps** in the Hierarchy, then click the small arrow ▸ in front of it. It holds two empty objects:

| Object | What it is |
|---|---|
| **Start** | Where Joey stands when the episode begins. Its blue arrow is the way Joey faces. |
| **Opening view** | Where the camera is for the title card. |

The **Inspector** (the panel on the right) shows the story component:

| Field | Leave or set |
|---|---|
| Player, Story Camera | Already filled in. Leave them. |
| Dialogue Override, Choice Override | Empty. Leave them. |
| **Chapter and episode**: Chapter Number, Episode Number | `4` and `1`, already filled in. They must match the episode's place in the chapter asset. |
| Time Limit | Seconds of free walking before time runs out (600 = 10 minutes). Dialogue and minigames pause it. |
| Spawn | *Start* (already filled in) |
| Opening View | *Opening view* (already filled in) |
| Spots | Empty list. You fill it in Part 4. |

Below the fields there are two extra lists: **Scene points** (every place the episode uses, each with a **Select** button) and **Story markers** (empty for a new episode).

Everything else in the scene (the house, the city, the people) was copied from the template. The template's old story is gone; its objects are still there and are cleaned up in Part 8.

## Part 3: Set where Joey starts and the first camera

**Move the start point**

1. In the Hierarchy, click **Start**.
2. Hover over the **Scene view** (the big 3D view) and press **F**. The view jumps to the Start point.
3. Press **W** (the Move tool). Coloured arrows appear on Start. Drag the **red** and **blue** arrows to slide it along the floor to where Joey should begin, for example just inside the front door. Keep it on the floor: do not drag the green (up) arrow below the floor.
4. Press **E** (the Rotate tool). Drag the **green** ring to turn it. The blue arrow is the way Joey will face. (If you do not see a blue arrow, set the toggle at the top of the Scene view from *Global* to *Local*.)

**Aim the opening camera**

1. Move around the Scene view until it shows what the first shot should show:
   - hold the **right mouse button** and use **W A S D** to fly, **Q / E** to go down / up;
   - scroll the mouse wheel to move forward and back.
2. In the Hierarchy, click **Opening view**.
3. Menu bar: **GameObject › Align With View** (shortcut **Ctrl + Shift + F**, on Mac **Cmd + Shift + F**). Opening view now looks exactly where the Scene view looks.

> [!TIP] Check
>
> In the Scene view, Start has a gold circle and Opening view a blue camera frame (select *Episode - First Steps* to see their names).

## Part 4: Add the places Joey visits (spots)

A **spot** is a place with a gold marker and an **[E]** prompt. The example needs two: one next to Mom, one at Joey's desk.

**Find Mom**

1. In the search box at the top of the Hierarchy, type `Mother`. Double-click **Mother** in the results: the Scene view jumps to her.
2. Clear the search box.

**Make the first spot**

1. In the Hierarchy, **right-click Episode - First Steps › Create Empty**. A new object called *GameObject* appears inside it.
2. Rename it: with it selected press **F2** (on Mac press **Return**), type `Talk to Mom`, press **Enter**.
3. Put it next to Mom. Easiest way: in the Scene view, look at Mom from about two steps away, select *Talk to Mom*, then **GameObject › Move To View** (**Ctrl + Alt + F**, Mac **Cmd + Option + F**). Then press **W** and drag the green arrow so it sits on the floor about one metre in front of her.

**Make the second spot**

1. Do the same again: right-click **Episode - First Steps › Create Empty**, rename it `Your desk`, and place it in front of the desk in Joey's room (search the Hierarchy for `desk` to find it).

**Put them in the Spots list (order matters: first spot first)**

1. Click **Episode - First Steps** in the Hierarchy.
2. In the Inspector, find **Spots** and click the **+** button under it **twice**. You now have *Element 0* and *Element 1*, both *None*.
3. Drag **Talk to Mom** from the Hierarchy onto **Element 0**.
4. Drag **Your desk** from the Hierarchy onto **Element 1**.

5. Save the scene: **Ctrl + S** (Mac **Cmd + S**).

> [!TIP] Check
>
> Spots shows *Element 0: Talk to Mom* and *Element 1: Your desk*. In the **Scene points** list below, both appear with a **Select** button.

## Part 5: Write the story

The words, the order of events and the choices are in the episode script. The New Episode tool already made it.

1. In the **Project** window (bottom of Unity), go to `Assets › Scripts › Chapters › Chapter 4` and **double-click** `Chapter4Episode1FirstSteps`. It opens in VS Code.
2. Select everything in the file (**Ctrl + A**, Mac **Cmd + A**) and **delete it**.
3. Paste this whole script, then save the file (**Ctrl + S**, Mac **Cmd + S**):

   ```csharp
   using System.Collections;
   using Mindscape.AcademicPressure;
   using UnityEngine;

   namespace Mindscape.Story
   {
       // Chapter 4 · Episode 1 · First Steps
       public sealed class Chapter4Episode1FirstSteps : StoryEpisode
       {
           [Header("Scene points (drag them in the Scene view)")]
           public Transform spawn;
           public Transform openingView;
           [Tooltip("Places the player walks to, in order. Each gets an [E] prompt and the lines below.")]
           public Transform[] spots = new Transform[0];

           [Header("My episode")]
           public Transform momView;   // where the camera looks from while Joey talks with Mom

           protected override IEnumerator Play()
           {
               if (spawn != null) Teleport(spawn.position, spawn.eulerAngles.y);
               if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 8);
               yield return Card("CHAPTER 4\n<size=60%>Episode 01 · First Steps</size>");
               yield return Say("Narration", "You get home a little earlier than usual.");

               // Stop 1: talk to Mom (the first spot in the Spots list)
               bool talked = false;
               AddSpot(spots[0], "Talk to Mom", () => !talked, () => TalkToMom(() => talked = true));
               SetObjective("First Steps", Check(false, "Talk to Mom"));
               yield return RoamUntil(() => talked);

               // Stop 2: your desk (the second spot in the Spots list)
               bool rested = false;
               AddSpot(spots[1], "Sit at your desk", () => !rested, () => AtTheDesk(() => rested = true));
               SetObjective("First Steps", Check(true, "Talk to Mom") + Check(false, "Go to your desk"));
               yield return RoamUntil(() => rested);

               // Free walking until every cinematic set to play at a place has played (see Create a cinematic).
               yield return RoamUntilCinematicsDone();

               Complete("First Steps", "You came home and shared a little about your day.");
           }

           IEnumerator TalkToMom(System.Action done)
           {
               if (momView != null) Shot(momView.position, momView.position + momView.forward * 4);
               yield return Say("Mom", "You're home early! How was your day?");
               int reply = -1;
               yield return Choose("Reply", "What do you say?", new[] { "It was fine.", "It was a lot, honestly." }, i => reply = i);
               Record("ch4_ep1_reply", reply == 0 ? "fine" : "a_lot");
               if (reply == 0) yield return Me("It was fine. Nothing special.");
               else yield return Me("It was a lot, honestly.");
               yield return Say("Mom", "Thank you for telling me. Get some rest, okay?");
               done();
           }

           IEnumerator AtTheDesk(System.Action done)
           {
               yield return Think("Okay. One small thing at a time.");
               done();
           }
       }
   }
   ```

4. Go back to Unity. It compiles again (spinner, bottom-right). Wait for it to stop. The Console must show **no red lines**.

**How to read the script** (you only change the parts in quotes and the order of lines):

| Line | What the player sees |
|---|---|
| `yield return Card("…");` | A full-screen title card. The player presses Space. |
| `yield return Say("Narration", "…");` | A narration box. |
| `yield return Say("Mom", "…");` | Mom speaks. Any name works: `"Dad"`, `"Tim"`, `"Justin"`. |
| `yield return Me("…");` | Joey speaks (the player's chosen name is shown). |
| `yield return Think("…");` | Joey's inner thought. |
| `AddSpot(spots[0], "Talk to Mom", …)` | A gold marker on the first spot with the prompt **[E] Talk to Mom**. |
| `SetObjective("First Steps", Check(false, "Talk to Mom"));` | The objective panel: title and a checklist line (`true` = ticked). |
| `yield return RoamUntil(…);` | The player walks freely until that stop is done. |
| `yield return Choose("Reply", "What do you say?", new[] { "…", "…" }, i => reply = i);` | A choice screen with the listed answers. |
| `Record("ch4_ep1_reply", …);` | Saves the answer under a key (never reuse a key for something else). |
| `Complete("First Steps", "…");` | The end screen, then the journal and self-assessment. |

> [!TIP] Rules when editing the script
>
> - Every line ends with `;`. Text goes between straight quotes `"…"`.
> - To use a `"` inside a line, write `\"`. To start a new line inside a text, write `\n`.
> - `spots[0]` is Element 0 of the Spots list, `spots[1]` is Element 1, and so on. Using `spots[2]` needs a third element.
> - Keep the class name `Chapter4Episode1FirstSteps` the same as the file name, and keep `: StoryEpisode` after it.
> - The chapter and episode numbers, the time limit, what comes next and the save are not in the script: they come from the Inspector and the chapter asset.

## Part 6: Add a camera for the talk with Mom

The script has a field **Mom View**: a camera position used while Joey talks with Mom.

1. In the Scene view, frame Joey's spot and Mom the way the conversation should look.
2. Right-click **Episode - First Steps › Create Empty**, rename it `Mom view`.
3. With *Mom view* selected: **GameObject › Align With View** (**Ctrl/Cmd + Shift + F**).
4. Click **Episode - First Steps**. In the Inspector, under **My Episode**, drag **Mom view** from the Hierarchy into the **Mom View** field.
5. Save the scene.

## Part 7: Play it

1. Press the **Play** button (▶, top centre of Unity).
2. What should happen, in order:
   1. The title card *CHAPTER 4 · Episode 01 · First Steps*. Press **Space**.
   2. The narration line. Press **Space** to continue.
   3. You can walk (**W A S D**, mouse to look). The objective says *Talk to Mom*. Walk to the gold marker next to her.
   4. **[E] Talk to Mom** appears. Press **E**. The camera cuts to *Mom view*, Mom speaks, the choice screen appears. Click an answer.
   5. The objective changes to *Go to your desk*. Walk to the desk marker and press **E**. Joey's thought appears.
   6. The completion screen, then the reflection journal.
3. Press **Play** again to stop.

> [!WARN] Changes made while playing are lost
>
> While the Play button is blue, anything you move or change is undone when you stop. Stop first, then edit.

## Part 8: Clean up the template's leftovers

The scene still holds objects from the template episode (Chapter 3 - Episode 7), for example its story object **Chapter 3 - The Walk Home** with people and props from that episode.

1. Click **Chapter 3 - The Walk Home** in the Hierarchy.
2. At the top of the Inspector, **untick the checkbox** next to its name. This hides it without deleting it.
3. Press Play and test again.
4. If everything still works, you can delete it (right-click › **Delete**). If something broke, tick the box again: something in it was needed.

Do the same for anything else you do not want (walkers in **Ambient Life**, cars in **City Traffic**).

> [!WARN] Keep the family
>
> In this template, Mom, Dad and Tim (*Mother*, *Father*, *Tim*) are inside the object **Chapter 2 · Episode 5 - What I Left Behind**. Hiding or deleting that object removes them too, and the *Talk to Mom* stop has nobody to talk to.

## Part 9: Save and connect

1. Save the scene (**Ctrl/Cmd + S**).
2. Commit the new files: `Assets/Scenes/Chapter 4 - Episode 1.unity` and `Assets/Scripts/Chapters/Chapter 4/` (with their `.meta` files).
3. Select the chapter asset (`Assets/Resources/Chapters/Chapter 4`) and fill in this episode's **Location**, **Briefing** and, if you like, its own **Thumbnail** (step 3 of [Create a chapter](#create-chapter)). The episode is already in the main menu under Chapter 4: see [Connect it to the game](#connect-episode).

## Make your own next

Repeat the same parts with your own episode card ([Plan an episode](#plan-episode)):

- pick the template from this list:

  | Place | Template scene |
  |---|---|
  | Joey's house, evening/night | Chapter 3 - Episode 7 |
  | Joey's house, daytime | Chapter 2 - Episode 1 |
  | Classroom | Chapter 1 - Episode 2 |
  | Cafeteria | Chapter 1 - Episode 3 |
  | Dormitory | Chapter 1 - Episode 4 |
  | Reunion hall | Chapter 3 - Episode 2 |

- one spot per place the player visits, in the order they visit them;
- one stop in the script per spot (copy the *Stop 1* block, change `spots[0]` to the next number and the words);
- more lines you can use: `yield return Breathe(done => { });` for the breathing exercise. See [How an episode works](#how-episodes-work) for the rest.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| The **Mindscape** menu is missing | The scripts have an error. Open the Console, fix the first red line, save. |
| New Episode says *That scene already exists* | Pick another episode number, or delete the old scene first. |
| New Episode says *That script already exists* | A script with that name is left over. Delete it in the Project window (or change **Script class**). |
| The episode is not in the main menu | Open the chapter asset: the box under **In the game** says what is missing (no episodes, a missing chapter before it, a scene not in the build list). |
| Play stops with `IndexOutOfRangeException` | The script uses `spots[1]` but the Spots list has only one element. Add the element (Part 4). |
| No **[E]** prompt at a spot | Walk closer (within about 3 m). Check the spot is on the floor, not inside a wall or under the floor. |
| Joey falls through the floor at the start | **Start** is below the floor. Raise it a little with the green arrow. |
| The camera shows a wall | Re-aim that view: move the Scene view, select the view object, **Align With View**. |
| The words did not change | The script was not saved, or Unity has not finished compiling. Save in VS Code, wait for the spinner, play again. |
| Something moved back after testing | It was changed while playing. Stop, change it again, save. |
