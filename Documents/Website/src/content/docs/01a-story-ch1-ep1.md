---
id: story-ch1-ep1
group: Story
nav: Chapter 2 · Episode 1
---

# Chapter 2 · Episode 1: A New Day

> [!TIP] Now Chapter 2
>
> This episode opened the game before the chapters were reordered. It is now the first episode of Chapter 2, "Family Expectations", in the scene `Chapter 2 - Episode 1`. Chapter 1 is [Academic Pressure](#story-ch1).

Joey wakes up late on the morning of a presentation. Nothing dramatic happens. He moves through his family's house, talks with his brother, his mother and his father, and gets ready for the day, one small step at a time.

> [!TIP] How this episode sounds
>
> Every line is deliberately **neutral**: it neither alarms nor reassures. The writing notices things, asks gentle questions and leaves the meaning to the player. The rules behind that are on the [Writing Guidelines](#story-tone) page.

## At a glance

| Detail | Value |
| --- | --- |
| Chapter theme | Family Expectations |
| Setting | The family house (Chapter 2, Episode 1 of 3) |
| You play | Joey |
| Also in the house | Mom (kitchen), Dad (living room), Tim, Joey's little brother (hallway) |
| Opening | A four-slide cutscene set at 7:50 in the morning |
| Objectives | Talk to Mom, Dad and Tim. Collect the School Bag and the Lunchbox. Finish the Worry Courtroom and the Breathing Exercise. Keep stress between 0 and 30. |
| Time limit | 5:00. The clock pauses while a minigame is open. |
| Stress | Starts at 10. No conversation choice changes it. |
| Unlocks | Chapter 2 · Episode 2 |

## The morning, step by step

1. **The cutscene.** Four slides, each with a short line of narration (full text below). The alarm rings at 7:50, Joey wakes, a phone reminder says *Important Presentation Today*, and his thoughts pile up: the presentation, lunch, the school bag, a word with Mom, the bus at eight.
2. **Arriving.** Joey starts on the path outside the front gate and walks into the house. The family is already up and moving about: Mom circles the dining table, Dad strolls the living room, Tim paces the hallway. Each of them stops and turns to face Joey when he comes close enough to talk.
3. **Tim, the hallway.** A small, curious question about doors. It sets the tone of the whole episode: wondering rather than worrying.
4. **Mom, the kitchen.** She mentions breakfast and lunch, and when Joey brings up the presentation she invites him to look at the thought together, *the way a judge looks at a case*. When the conversation ends the **Worry Courtroom** opens.
5. **Dad, the living room.** He talks about the one thing a person carries everywhere, the breath. When the conversation ends the **Breathing Exercise** opens.
6. **The two items.** The **School Bag** is near the front of the living room and the **Lunchbox** is by the sofa. Both are picked up with F (or the on-screen Interact button).
7. **The end.** When everything is done and stress is still in range, the *Episode Complete* screen appears and Chapter 2 unlocks.

The order is free. Only the objectives matter, and a minigame that is closed early can be opened again by talking to the same person.

## The opening cutscene

| Slide | Picture | Narration |
| --- | --- | --- |
| 1 | Joey asleep, the clock reads 7:50 AM | 7:50 in the morning. The alarm rings, and the day begins the way days do. A day does not ask whether we are ready. It simply arrives. |
| 2 | Joey wakes with a start | Joey opens his eyes. Between sleeping and waking there is a small pause. In that pause there is only the breath, moving in and out. |
| 3 | The phone: *Important Presentation Today* | A message appears on the screen: Important Presentation Today. It is written in plain words. What it means to Joey is something he can discover a little at a time. |
| 4 | Thought bubbles: presentation, lunch, school bag, talk to Mom, catch the school bus 8AM | Many things sit in his mind at once: a presentation, lunch, a school bag, a word with Mom, the bus at eight. A crowded table can be cleared one dish at a time. |

The slide art lives in `Assets/Resources/Cutscenes/Episode 1/`. See [Create a Cutscene](#workflow-cutscene) for how the slides are built.

## The people

| Who | Where | What they are for |
| --- | --- | --- |
| **Joey** | Player | The viewpoint. His thoughts are narrated in the cutscene; in play he is the person you move. |
| **Mom** | By the kitchen counter, walking around the dining table | Names the presentation without making it bigger, then opens the **Worry Courtroom**. |
| **Dad** | Living room, beside the coffee table | Introduces the breath, then opens the **Breathing Exercise**. |
| **Tim** | Hallway between the front door and the bedrooms | Curiosity. A child's question that has no wrong answer. |

All three share one placeholder model for now (a capsule), with a floating name tag so you always know who is who. They walk their own routes through the house; see [NPC Wandering & Name Tags](#workflow-npc-wander). Their exact words are on the [Episode 1 Dialogue](#story-ch1-ep1-dialogue) page.

## The two minigames

- **Worry Courtroom** puts the thought *"I'll mess up my presentation and everyone will laugh"* on trial. Joey sorts facts from guesses, picks the facts that weigh against the worry, imagines what he would tell a friend, chooses a more balanced thought and one small step. See [Worry Courtroom](#minigame-courtroom).
- **Breathing Exercise** is thirty seconds of guided breathing: *breathe in, hold, breathe out*, with a circle that opens and settles. See [Breathing Exercise](#minigame-breathing).

## Themes

- **Thoughts are not facts.** The courtroom is the clearest form of this idea, but Mom's and Tim's lines point at it too.
- **One thing at a time.** The cutscene ends on the image of a crowded table cleared one dish at a time.
- **The breath is always there.** Dad's lesson, and the cutscene's second slide.
- **Company helps.** Every conversation is gentle, and the family keeps still when Joey comes near.

## Where the story goes next

| Chapter | Theme | Status |
| --- | --- | --- |
| 1 | Academic Pressure | All four episodes (House, Classroom, Cafeteria, Dormitory) are playable. |
| 2 | Family Expectations | All five episodes are playable. |
| 3 | Social Dynamics | All eight episodes are playable. |

See [Chapter 1](#story-ch1) and [Chapters 2 and 3](#story-ch2-ch3). The loading screens and menus carry the artwork and names for every episode location, so a new episode needs its scene, story script and cast.
