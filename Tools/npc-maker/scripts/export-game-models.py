"""Run with Blender: blender -b -t 2 --python scripts/export-game-models.py"""

from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "Assets/Characters/Player/Girl_Home.fbx"
TARGET = ROOT / "tools/npc-maker/public/models/girl-default.glb"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(SOURCE))
bpy.ops.export_scene.gltf(filepath=str(TARGET), export_format="GLB", export_animations=False)
print(f"Exported game model {SOURCE} -> {TARGET}")
