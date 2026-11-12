import bpy
import os
import shutil
from mathutils import Vector

# Target directories
proj_root = "/Users/arieljerickogacilo/mindscape-3d"
dir_unity = os.path.join(proj_root, "Assets", "Models", "Vehicles")
dir_models = os.path.join(proj_root, "models", "vehicles")

os.makedirs(dir_unity, exist_ok=True)
os.makedirs(dir_models, exist_ok=True)

vehicles = [
    ("Sedan", "Car_Sedan"),
    ("SUV", "Car_SUV"),
    ("SportsCar", "Car_Sports"),
    ("Pickup", "Car_Pickup"),
    ("DeliveryVan", "Car_Van"),
    ("SchoolBus", "SchoolBus")
]

def select_hierarchy(obj):
    obj.select_set(True)
    for child in obj.children:
        select_hierarchy(child)

print("Starting individual vehicle exports...")

for file_stem, root_name in vehicles:
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f"Error: Could not find {root_name}")
        continue
    
    # 1. Temporarily move to origin (0, 0, 0) so individual asset pivot is at (0, 0, 0)
    orig_loc = root.location.copy()
    root.location = Vector((0, 0, 0))
    bpy.context.view_layer.update()
    
    # 2. Select only this vehicle hierarchy
    bpy.ops.object.select_all(action='DESELECT')
    select_hierarchy(root)
    bpy.context.view_layer.objects.active = root
    
    selected_names = [o.name for o in bpy.context.selected_objects]
    print(f"Exporting {file_stem} (Root: {root_name}) with objects: {selected_names}")
    
    # Export paths
    glb_unity = os.path.join(dir_unity, f"{file_stem}.glb")
    fbx_unity = os.path.join(dir_unity, f"{file_stem}.fbx")
    
    # Export GLB
    bpy.ops.export_scene.gltf(
        filepath=glb_unity,
        export_format='GLB',
        use_selection=True,
        export_apply=False,
        export_animations=True,
        export_yup=True
    )
    print(f"  -> Exported GLB: {glb_unity}")
    
    # Export FBX
    bpy.ops.export_scene.fbx(
        filepath=fbx_unity,
        use_selection=True,
        object_types={'EMPTY', 'MESH'},
        bake_anim=True,
        bake_anim_use_all_actions=True,
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True
    )
    print(f"  -> Exported FBX: {fbx_unity}")
    
    # Also copy to models/vehicles/
    shutil.copy2(glb_unity, os.path.join(dir_models, f"{file_stem}.glb"))
    shutil.copy2(fbx_unity, os.path.join(dir_models, f"{file_stem}.fbx"))
    
    # 3. Restore original location in the fleet scene
    root.location = orig_loc
    bpy.context.view_layer.update()

# Deselect all
bpy.ops.object.select_all(action='DESELECT')
print("All individual vehicles exported successfully!")
