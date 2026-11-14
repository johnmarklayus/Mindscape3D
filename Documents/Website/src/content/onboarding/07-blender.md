---
id: blender-to-unity
group: Art
nav: Blender to Unity
---

# Make the Art: Blender to Unity

All 3D art starts in `Blender/Blend Files/` and is exported into Unity.

| Blend file | Becomes |
|---|---|
| `world_new.blend` | The shared city (`Assets/Models/World/world_new.glb`), used in every story scene |
| `house-and-lot-cozy.blend` | Joey's house |
| `school-grounds.blend` | School, cafeteria, dormitory, reunion hall |
| `Main_Character_Outfit_Lineup.blend` | Boy and girl player models, outfits, the worn backpack |
| `NPC_Roster.blend` | The 20 NPCs |
| `Boy_Sleeping_In_Bed.blend` | Joey's bed with sleeping / messy / neat states |
| Vehicles, furniture, doors, logo | Props, traffic and the 3D title |

## Workflow

1. Edit the `.blend` file. Keep a copy in `Backups/` before large changes.
2. Export over the matching file in `Assets/Models/…` or `Assets/Characters/…`. Scripts in `Blender/Scripts/` (`export-world.py`, `export-family.py` …) can run Blender without a window: `blender -b file.blend -P script.py`.
3. FBX settings that matter:
   - **Apply Scalings: FBX Units Scale**. Without it, NPCs import 100× too big.
   - **Bake space transform** has to match the model. If a mesh arrives lying on its side (Z-up), re-export, then refit any colliders that were sized on the old import.
4. In Unity, run the matching **Mindscape** menu tool (for example the World sync, or **House › Install Joey Bed**). It places the new model in every scene that uses it and repairs references, so you don't fix each scene by hand.
5. Performance: models use **LOD groups**, and the player can change quality in the graphics settings (`GraphicsPrefs`). Lighting is real-time; baked lighting and occlusion culling were removed on purpose.

For a new character based on the game's boy or girl model, follow [Create an NPC model](#create-npc-model).

More: [Blender Assets](/#workflow-blender-assets) · [Shared City & Traffic](/#system-world) · [Lighting & Rendering](/#system-lighting)
