"""Export the actual Unity FBX clips for browser playback.

Run from tools/npc-maker with:
  blender -b -t 2 --python scripts/export-game-animations.py
"""

from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "tools/npc-maker/public/models"
CLIPS = {"Idle", "Walk", "Run", "Conversation"}

for base, source, armature_name in [
    ("boy", ROOT / "Assets/Characters/BaldCharacter/Joey_Actions.fbx", "BaldCharacter_Rig"),
    ("girl", ROOT / "Assets/Characters/NPCs/NPC_17_Penelope.fbx", "Armature_NPC_17_Penelope"),
]:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    bpy.ops.import_scene.fbx(filepath=str(source))
    for action in list(bpy.data.actions):
        clip = action.name.split("|")[-1]
        if clip in CLIPS and action.name.startswith(armature_name + "|"):
            action.name = clip
        else:
            bpy.data.actions.remove(action)
    target = OUT / f"{base}-animations.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(target),
        export_format="GLB",
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_force_sampling=True,
    )
    print("EXPORTED", base, [a.name for a in bpy.data.actions], target)
