"""Export the urbanized world_new scene to Unity-ready assets in Assets/Models/World/

Exports both:
- GLB (glTF 2.0 binary): Y-up, applied transforms, PBR materials with emissive strengths.
- FBX: Unity standard (Forward: -Z, Up: Y, unit scale applied).
"""

import bpy
import os
import shutil

OUT_DIR = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/World"
os.makedirs(OUT_DIR, exist_ok=True)

# Deselect all
for obj in bpy.data.objects:
    obj.select_set(False)

# Select all exportable geometry and empties
guides_col = bpy.data.collections.get("World | Layout guides - non-export")
guide_objects = set(guides_col.objects) if guides_col else set()

for obj in bpy.context.scene.objects:
    if obj.type in {'MESH', 'EMPTY'} and obj not in guide_objects and not obj.name.startswith("Guide |"):
        obj.select_set(True)

# 1. Export GLB (Unity-ready glTF 2.0)
glb_path = os.path.join(OUT_DIR, "world.glb")
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False
)
print("Exported GLB to:", glb_path)

# Also keep world_new.glb copy
glb_new_path = os.path.join(OUT_DIR, "world_new.glb")
shutil.copyfile(glb_path, glb_new_path)

# 2. Export FBX (Unity-ready Autodesk FBX)
fbx_path = os.path.join(OUT_DIR, "world.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    object_types={'EMPTY', 'MESH'},
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=True
)
print("Exported FBX to:", fbx_path)
print("Export completed successfully!")
