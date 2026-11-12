---
id: workflow-collectible
group: Workflows
nav: Create a Collectible
---

# Create a Collectible

Pickups that the player collects and a Quest can require. (The old Bag panel is gone: collected items are simply counted.)

> [!MENU] GameObject
>
> `GameObject ▸ Collectible`: creates (or reuses) a `collectibles` GameObject with `CollectiblesManager`, and adds a child with a `SphereCollider` trigger and the `CollectibleItem` component.

1. Assign a **3D Model** prefab and click **Refresh 3D Model** (same pattern as NPCs: the root keeps the interaction collider, the model's own colliders get disabled).
2. Set **Collectible Name**. It is shown in the "F to collect" prompt and in the Quest Journal. Episode 1 has two: **School Bag** and **Lunchbox**.
3. Set a stable **Item ID**. This is what a Quest's "Required Collectibles" list actually matches against, so keep it consistent if you rename the display name later.
4. Tune **Interaction Radius**.

Picking one up (F, or the on-screen Interact button) calls `CollectibleItem.Collect()`, which routes through `CollectiblesManager`: the manager adds one to that item's count, plays a short shrink-away animation and hides the object. Quests read the count with `GetItemCount(itemId)`.

The manager creates the yellow pickup prompt at runtime under its assigned Canvas. It uses the shared Comic Neue Bold font through `MinigameUI.Font(true)`, and hides the prompt while a conversation or Quest Journal is open.

> [!TIP] Keep NPC routes clear of pickups
>
> A collectible has a solid collider, so a wandering NPC's route through it counts as blocked. See [NPC Wandering & Name Tags](#workflow-npc-wander).
