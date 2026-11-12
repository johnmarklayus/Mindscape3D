---
id: story-ch1-ep1-dialogue
group: Story
nav: Ch. 2 · Episode 1 Dialogue
---

# Chapter 2 · Episode 1 Dialogue

Everything Mom, Dad and Tim say, exactly as it is in the game. Each conversation is a short tree: the NPC speaks, the player picks a reply, and the reply leads to the next line.

> [!TIP] Stress and choices
>
> Every choice here has a stress change of **0**, so the usual "(+n stress)" label never appears on a button. Choices are about *how Joey wants to answer*, not about winning or losing points. The same lines are authored in each NPC's Inspector (see [Create an NPC](#workflow-npc)).

## Mom

Kitchen. After this conversation ends, the [Worry Courtroom](#minigame-courtroom) opens.

| # | Mom says | Joey can answer |
| --- | --- | --- |
| 0 | Good morning, Joey. There is breakfast on the table and lunch beside the door. A morning holds many small things, and each of them is only what it is. | "What is today like?" goes to 1. "I have a presentation today." goes to 2. |
| 1 | Today is a day like any other, made of hours. Some of what fills them is planned, and some of it is not. Days have always been this way. | "I see." goes to 3. |
| 2 | Yes, I know. A presentation is a few minutes of speaking placed inside a long day. The rest of the day keeps going, as days do. | "That is one way to see it." goes to 3. |
| 3 | Your father is in the living room, and your brother is somewhere in the house. Before you go, shall we look at a thought together, the way a judge looks at a case, one piece of evidence at a time? | "Alright." ends the conversation. |

## Dad

Living room. After this conversation ends, the [Breathing Exercise](#minigame-breathing) opens.

| # | Dad says | Joey can answer |
| --- | --- | --- |
| 0 | Joey. Come and sit beside me for a moment. There is one thing a person carries everywhere, and it is the breath. | "Why the breath?" goes to 1. "I only have a moment." goes to 2. |
| 1 | Because it is always here, in every kind of day. We do not have to find it or earn it. We only have to notice it. | "How do I notice it?" goes to 3. |
| 2 | A moment is enough. A single breath takes only a few seconds, and it can be taken anywhere. | "Alright." goes to 3. |
| 3 | Then let us breathe together. In, and out, and we will see what we see. | "Let's breathe." ends the conversation. |

## Tim

Hallway. Joey's little brother. No minigame; he is simply company.

| # | Tim says | Joey can answer |
| --- | --- | --- |
| 0 | Joey! When a door is open, is the room inside or outside? | "Inside, I think." goes to 1. "Maybe both." goes to 2. |
| 1 | Then a door is neither. It is the place where one room turns into another. | "That makes sense." goes to 3. |
| 2 | Both. Then a door is where two places meet. | "It might be." goes to 3. |
| 3 | The bus comes down the street, goes to school, and comes back again. It keeps moving, and the road stays where it is. | "Goodbye, Tim." ends the conversation. |

## How the lines are built

- Each conversation uses **Enable Dialogue Chaining**, so a choice can jump to any later line. Every path ends with a choice that has **Ends Dialogue** ticked.
- Branches always rejoin: whichever of the first two replies the player picks, the conversation arrives at the same closing line. Nobody gets a "wrong" branch.
- Conversations finish by reporting to the quest (`QuestProgress.ReportNPCConversationCompleted`), which is what ticks "Talk to Mom" and triggers her minigame.
- The three NPCs are created by `Mindscape ▸ Episode 1 ▸ Populate House NPCs`, which also holds this text in code (`Episode1Builder.cs`) if you want to regenerate or edit it in bulk.
