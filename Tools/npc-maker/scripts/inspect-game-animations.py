from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
print("EXPORT_MODES", [(item.identifier, item.name) for item in bpy.ops.export_scene.gltf.get_rna_type().properties['export_animation_mode'].enum_items])
for name, path in [
    ("boy", ROOT / "Assets/Characters/BaldCharacter/Joey_Actions.fbx"),
    ("girl", ROOT / "Assets/Characters/NPCs/NPC_17_Penelope.fbx"),
]:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(path))
    print("MODEL", name)
    print("ARMATURES", [o.name for o in bpy.data.objects if o.type == "ARMATURE"])
    print("ACTIONS", [(a.name, tuple(a.frame_range)) for a in bpy.data.actions])
