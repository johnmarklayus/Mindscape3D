---
id: workflow-blender-assets
group: Workflows
nav: Blender Assets
---

# Blender Assets: Edit, Create and Use Them

Mindscape keeps editable Blender source files in `Blender/Blend Files/` and puts only the Unity-ready export in `Assets/`. Unity watches `Assets/`, imports the export and preserves references to it by its `.meta` file.

| Purpose | Location | Typical format |
| --- | --- | --- |
| Editable source and backups | `Blender/Blend Files/` | `.blend` |
| Static props, furniture and environments | `Assets/Models/<Category>/` | `.glb` |
| Rigged characters or assets whose animation clips are used in Unity | `Assets/Characters/` or `Assets/Models/<Category>/` | `.fbx` |
| Gameplay-ready object with scripts and colliders | `Assets/Prefabs/` | `.prefab` |

The project has Unity glTF support through `com.unity.cloud.gltfast`, so `.glb` files under `Assets/` are imported as model assets. Do not put the working `.blend` file in `Assets/`; it makes Unity depend on a local Blender installation and increases import time.

## Modify an existing asset

1. **Find both halves of the asset.** Locate the exported model in `Assets/`, then open its source in `Blender/Blend Files/`. Examples include `world_new.blend` → `Assets/Models/World/world_new.glb`, `school-grounds.blend` → `Assets/Models/School_Grounds.glb`, and `Academic_Collectibles.blend` → `Assets/Models/Collectibles/Collectible_*.glb`.
2. **Make a recoverable copy for a risky edit.** Save a dated copy under `Blender/Blend Files/Backups/`, or commit the current files before changing geometry, rigs or animation.
3. **Preserve names and hierarchy.** Editor builders find important parts by exact GameObject name. Renaming an anchor, wheel, door leaf, bone or animation action can silently break placement or clip lookup. Search the code in `Assets/Editor/` for the current name before changing it.
4. **Edit at the existing scale and origin.** Do not move the entire scene to the origin or apply a new scale just to make the Blender file look cleaner. The house, school and world have established alignment anchors used by existing scenes.
5. **Apply transforms only where safe.** For a new or independent mesh, use `Ctrl+A ▸ Rotation & Scale` so it exports with scale `(1, 1, 1)`. Do not apply armature transforms, animated-object transforms or a shared environment root without checking the result in Unity.
6. **Export over the same Unity file.** Keeping the same path and filename keeps the existing Unity `.meta` file, GUID, prefab references and scene references. Never delete the `.meta` file just to force a reimport.
7. **Let Unity finish importing**, then run the matching rebuild or sync action from the table below. Test a scene that already uses the asset as well as a clean prefab instance.

> [!WARN] Re-export, do not replace references
>
> If an asset is already used by scenes or prefabs, overwrite its existing `.glb` or `.fbx`. Exporting under a new name creates a different Unity asset, so existing references will continue to use the old model.

## Create a new asset in Blender

### 1. Set up the file

1. Create the `.blend` under a suitable subfolder in `Blender/Blend Files/`.
2. Use real-world proportions. For a normal new prop, treat one Blender unit as one metre and compare it with a roughly `1.8 m` character.
3. Model the asset near the world origin. Put its origin where Unity should position it: on the floor for furniture and characters, at the centre for carried props, and on the hinge for a rotating door or lid.
4. Face the model consistently. Blender exports to Unity with **Y up**; the project export scripts use FBX **Forward −Z, Up Y**. If the asset belongs to a set such as vehicles or characters, match an existing member of that set instead of inventing a new forward direction.
5. Give objects, materials, bones and actions stable descriptive names. Use simple ASCII filenames and avoid Blender's automatic `.001` suffixes on objects the game needs to find.

### 2. Prepare it for a game

- Delete hidden test meshes, unused cameras and lights from the export selection.
- Apply mesh rotation and scale; check face normals with **Viewport Overlays ▸ Face Orientation**.
- Use a sensible polygon count, merge accidental duplicate vertices, and avoid many tiny separate renderers.
- UV unwrap textured meshes. Keep image textures in a durable project folder, not Downloads or a temporary directory. Pack them while working if needed, but confirm the exported GLB contains or references them correctly.
- Prefer Principled BSDF materials with base colour, metallic, roughness, normal and emission. Procedural Blender-only nodes do not automatically become Unity materials, so bake them to textures first.
- For a moving object, make the moving pieces separate objects with correct origins. For a character, skin one armature cleanly and name every action that Unity must expose as a clip.

### 3. Export to Unity

For a static prop or environment, use **File ▸ Export ▸ glTF 2.0**:

- Format: **glTF Binary (`.glb`)**
- Include: **Selected Objects** when the Blender scene contains guides or other assets
- Transform: **+Y Up** and **Apply Modifiers**
- Data: export materials; omit cameras and lights
- Animation: off unless this GLB deliberately contains animation

Export into `Assets/Models/<Category>/`. Use an existing category when one fits; for example, collectibles go in `Assets/Models/Collectibles/` and vehicles in `Assets/Models/Vehicles/`.

For a rigged or animated asset, use **FBX** when the Unity code or prefab expects FBX animation clips:

- Include only the required **Mesh** and **Armature** objects
- Transform: **Forward −Z**, **Up Y**, **Apply Unit Scale**
- Armature: disable **Add Leaf Bones**
- Bake animation at a step of `1`; export the intended NLA strips/actions only

Several asset families already have repeatable exporters under `scripts/`, including `export-world.py`, `export-family.py`, `export_individual_vehicles.py`, `export_mindscape_title.py` and the scripts in `Blender/Scripts/blender/`. Prefer the matching script when it exists because it encodes the filenames, selection and animation settings expected by Unity.

## Use the asset in the game

### One-off prop or environment piece

1. Wait for the model to appear in Unity's Project window, then inspect its materials, scale and animation clips.
2. Drag the model into a test scene and reset its transform. A normal newly made asset should look correct at scale `(1, 1, 1)`.
3. Add gameplay components to a parent GameObject, not to the imported model asset itself. Add only the collider shapes the player needs; prefer primitive colliders for small props and reserve `MeshCollider` for static environment geometry.
4. Drag the configured parent from the Hierarchy into the appropriate `Assets/Prefabs/` folder to create a prefab.
5. Place prefab instances in scenes. Edit the prefab when every instance should change; use a scene override only for that one placement.

### NPC or collectible visual

- For an NPC, assign the imported model or a model prefab to **NPC ▸ 3D Model**, then click **Refresh 3D Model**. See [Create an NPC](#workflow-npc).
- For a collectible, assign it to **Collectible Item ▸ 3D Model**, click **Refresh 3D Model**, and keep the interaction collider on the parent. See [Create a Collectible](#workflow-collectible).
- To add a model to the project's generated NPC or collectible roster, also add its stable ID, filename and gameplay settings to `NPCPrefabBuilder.cs` or `CollectiblePrefabBuilder.cs`; then run the relevant build menu.

### Existing generated asset families

| Changed export | Run in Unity after import |
| --- | --- |
| `Assets/Models/World/world_new.glb` | `Mindscape ▸ World ▸ Rebuild World Prefab`, then **Apply World to Open Scene** for a test; use **Apply World to All Story Scenes** after verification |
| `Assets/Models/School_Grounds.glb` | `Mindscape ▸ School ▸ Sync Updated Campus in All Scenes` |
| `Assets/house-and-lot-cozy.fbx` | `Mindscape ▸ House ▸ Sync House Model (open scene)` first, then the all-scenes action after checking it |
| `Assets/Models/Vehicles/<Name>.glb` | `Mindscape ▸ World ▸ Rebuild Vehicle Prefabs` |
| `Assets/Models/Doors/<Name>.fbx` | `Mindscape ▸ Doors ▸ Rebuild Door Prefabs`, then apply doors to the required scenes |
| `Assets/Characters/NPCs/NPC_*.fbx` | `Mindscape ▸ NPCs ▸ Build All 20 NPC Prefabs`; rebuild family talk controllers too if those clips changed |
| `Assets/Models/Collectibles/Collectible_*.glb` | `Mindscape ▸ Collectibles ▸ Build All 12 Collectible Prefabs`, then **Use Collectible Models (Chapters 1-2)** |
| `Assets/Models/Vehicles/School_Bus.fbx` | `Mindscape ▸ Vehicles ▸ Build School Bus Prefabs` |

> [!WARN] All-scenes tools save scenes
>
> Save or commit scene work before running a menu item that applies or syncs an asset to every story scene. Do not run a chapter's **Build Episode** command merely to refresh a model; episode builders can replace hand-edited scene content.

## Verify before committing

1. Open the imported model and check that materials are not pink, the scale is plausible, and the hierarchy contains the expected names.
2. Check normals and shadows from several angles. Walk around the asset in Play Mode and confirm colliders do not trap or block the player unexpectedly.
3. For animation, preview every required clip and confirm that the object does not jump, rotate 90 degrees, change scale or slide away from its root.
4. Test one scene on the target platform quality level. Large texture, renderer, triangle or collider increases matter most on Android and WebGL.
5. In version control, include the `.blend`, the exported model, and any new Unity-generated `.meta` files. Existing `.meta` files should remain unchanged unless Unity intentionally changed their importer settings.

## Common problems

| Symptom | Check |
| --- | --- |
| Model is tiny or huge | Blender unit scale, unapplied object scale, FBX **Apply Unit Scale**, and whether an existing scene intentionally scales the model root |
| Model lies on its side or faces backward | Export Y-up/FBX axes and the forward direction used by the rest of that asset family |
| Pink or missing material | Use URP-compatible Unity materials; bake unsupported Blender nodes; confirm texture files were exported or copied |
| Dark or invisible faces | Recalculate normals outside and remove negative object scale before export |
| Existing scenes did not update | Confirm that the export overwrote the exact referenced path, then run the family-specific rebuild/sync menu |
| Builder cannot find a part or clip | Restore the exact object, bone or action name expected by `Assets/Editor/` code |
| Animation contains every Blender action | Limit the export to the intended NLA tracks/actions, then inspect the Unity model's **Animation** tab |
| Player catches on detailed geometry | Replace or simplify the collider; decorative meshes often need no collider |
