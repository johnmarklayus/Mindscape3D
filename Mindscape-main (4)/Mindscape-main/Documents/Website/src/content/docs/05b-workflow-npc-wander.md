---
id: workflow-npc-wander
group: Workflows
nav: NPC Wandering & Name Tags
---

# NPC Wandering & Name Tags

Two optional pieces that make an NPC feel like part of the house: a route to walk, and a floating name plate.

## Making an NPC walk

> [!MENU] Mindscape ▸ Episode 1 ▸ Add NPC Wandering
>
> Places waypoints for Mom, Dad and Tim and adds an `NPCWander` component to each. Re-running it replaces the `NPC Waypoints` object and each NPC's `NPCWander`.

To do it by hand for any NPC:

1. Create an empty **NPC Waypoints** object, and under it a group per NPC with child objects for each stop (`WP 1`, `WP 2`, ...). Place them on the floor; rugs are a few centimetres higher, so snap to the surface.
2. Select the NPC and add the **NPC Wander** component (`Add Component ▸ Mindscape ▸ NPC Wander`).
3. Drag the waypoint objects into **Waypoints**, in walking order.
4. Pick a **Pattern**:

   - **Loop**: 1, 2, 3, 1, 2, 3 (good for circling a table)
   - **Ping Pong**: 1, 2, 3, 2, 1 (good for a corridor)
   - **Random**: any point next; every pair of points needs a clear straight line
5. Tune **Walk Speed**, **Pause Seconds** (a random rest at each stop) and **Move Angle** (how far the NPC must be turned toward the target before it starts walking).
6. Select the NPC in the Scene view to see its route drawn as gold spheres and lines.

### Rules that keep it from looking broken

- **Straight lines must be clear.** NPCs walk directly from one waypoint to the next with no pathfinding. The Episode 1 tool checks every segment with a capsule cast and warns about any that touch a wall or furniture; do the same by eye for hand-placed routes.
- **They wait for the player.** While the player is inside the NPC's **Interaction Radius** the NPC stands still and turns to face them (`pauseWhenPlayerNear`, `facePlayerWhenNear`). During any conversation every wandering NPC does nothing, so the dialogue system can turn the NPC without a fight.
- **A kinematic Rigidbody is added automatically.** That lets the NPC move every frame without Unity rebuilding static physics.
- **Keep waypoints off collectibles.** A route through a pickup's collider counts as blocked.

## Name tags

Each NPC in Episode 1 has a **Name Tag** child: a dark plate with cream text that floats above the head and always faces the camera.

- It is an instance of `Assets/Prefabs/NPC/NPCNameTag.prefab`, a world-space canvas with a plate image and a Comic Neue label.
- The `NPCNameTag` component copies **NPC Name** into the label (even in Edit mode) and keeps the tag **Height** metres above the NPC's feet. Untick **Control Height** to place it by hand, or **Face Camera** to fix its angle.
- Tweak the look once on the prefab and every tag follows: font, plate colour, size.
- For a shorter NPC, lower **Height** (Tim's is 1.7 m; the adults' is 2.4 m).
