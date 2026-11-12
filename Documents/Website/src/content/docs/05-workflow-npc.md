---
id: workflow-npc
group: Workflows
nav: Create an NPC
---

# Create an NPC

NPCs are conversation triggers with an optional branching dialogue tree. Talking to one can satisfy a Quest's "talk to this person" criterion, and can open a minigame.

> [!MENU] GameObject
>
> Right-click in the Hierarchy (or use the `GameObject` menu) → **NPC**.

1. This creates (or reuses) an `NPC System` GameObject holding `NPCInteractionManager`, and adds a child `NPC` GameObject with a `CapsuleCollider` and the `NPC` component, pre-wired to the shared placeholder model (`Assets/Prefabs/NPC/DefaultNPCModel.prefab`, a capsule).
2. Set **NPC Name** in the Inspector. This is the string Quests reference under "NPC Names To Talk To", matched case-insensitively, and it is what the floating name tag shows.
3. Assign a **3D Model** prefab (or leave the shared dummy). Click **Refresh 3D Model** any time you change it. Colliders on the model are disabled automatically so they don't fight the NPC's own interaction collider, and the model's feet are snapped to the NPC's position.
4. Tune **Interaction Radius** (how close the player must be) and the **Conversation Camera** fields (face height, camera distance and height) that frame the close-up during dialogue. A shorter NPC needs a lower **Face Height** and a smaller **Camera Distance**.
5. Write dialogue under **Dialogue Nodes**: each node is one line of NPC speech plus a list of player-facing choices. Each choice has:

   - `playerChoice`: the button text
   - `stressChange`: added to the player's stress when picked (leave at 0; see the [Writing Guidelines](#story-tone))
   - `nextDialogueIndex`: jump to another node, or `-1`
   - `endsDialogue`: ends the conversation immediately

   Enable **Enable Dialogue Chaining** if choices should be able to branch to other nodes rather than always ending the conversation.
6. Give them a name tag and, if you like, a route: see [NPC Wandering & Name Tags](#workflow-npc-wander).

> [!TIP] Making an NPC open a minigame
>
> In the Quest's **Required Minigames** list, add the minigame, set **Trigger** to *When Talk To NPC* and type the NPC's name. The minigame opens when that conversation ends. See [Create a Quest](#workflow-quest).

### How it's wired at runtime

`NPCInteractionManager` finds the nearest in-range NPC every frame and shows an **F to talk** prompt (it also accepts the on-screen Interact button, see [Mobile Controls](#workflow-mobile)). Finishing a conversation calls `QuestProgress.ReportNPCConversationCompleted(npcName)`, a static event any active `Quest` listens for. The prompt and conversation panel are hidden while a minigame is open. The whole conversation UI is themed: see [UI Theme](#system-theme).
