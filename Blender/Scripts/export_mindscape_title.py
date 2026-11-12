"""Export the 3D MindScape3D Title Logo and its 2 animations to Unity-ready FBX & GLB files.

Target directory:
  /Users/arieljerickogacilo/mindscape-3d/Assets/Models/Title/

Exports:
  1. MindScape3D_Title.glb & MindScape3D_Title.fbx
     - Combined asset containing BOTH animations:
       * IntroScreen (Frames 1-120: 3D pop-in, float & glow)
       * MainMenu_GlowOnly (Frames 121-240: 100% stationary + radial golden glow loop)
  2. MindScape3D_IntroScreen.glb & MindScape3D_IntroScreen.fbx
     - Dedicated Intro Screen animation (Frames 1-120)
  3. MindScape3D_MainMenu_GlowOnly.glb & MindScape3D_MainMenu_GlowOnly.fbx
     - Dedicated Main Menu Glow-Only loop animation (Frames 121-240, slid to 0)
"""

import bpy
import os

OUT_DIR = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Title"
os.makedirs(OUT_DIR, exist_ok=True)

scn_intro = bpy.data.scenes.get("IntroScreen")
scn_menu  = bpy.data.scenes.get("MainMenu_GlowOnly")
logo_root = bpy.data.objects.get("MindScape3D_Root")

if not logo_root or not scn_intro or not scn_menu:
    raise RuntimeError("MindScape3D_Root or scenes not found. Run build_mindscape_logo.py first.")


def select_logo_hierarchy(scene):
    bpy.context.window.scene = scene
    bpy.context.view_layer.update()
    for obj in scene.objects:
        obj.select_set(False)

    def _recurse(ob):
        if ob.type in {'EMPTY', 'MESH'}:
            ob.select_set(True)
        for ch in ob.children:
            _recurse(ch)

    _recurse(logo_root)
    bpy.context.view_layer.objects.active = logo_root


# ---------------------------------------------------------------------------
# 1. Export Combined Multi-Animation GLB & FBX (MindScape3D_Title.glb / .fbx)
# ---------------------------------------------------------------------------
scn_intro.frame_start = 1
scn_intro.frame_end = 120
scn_menu.frame_start = 121
scn_menu.frame_end = 240

select_logo_hierarchy(scn_intro)

combined_glb = os.path.join(OUT_DIR, "MindScape3D_Title.glb")
bpy.ops.export_scene.gltf(
    filepath=combined_glb,
    export_format='GLB',
    use_selection=True,
    use_active_scene=False,
    export_apply=False,
    export_yup=True,
    export_materials='EXPORT',
    export_animations=True,
    export_animation_mode='SCENE',
    export_anim_scene_split_object=False,
    export_frame_range=True,
    export_force_sampling=True,
    export_anim_slide_to_zero=True,
    export_cameras=False,
    export_lights=False
)
print("Exported Combined GLB (2 scenes/clips):", combined_glb)

# For Combined FBX, bake full 1-240 range on IntroScreen so Unity's clipAnimations can split 1-120 & 121-240
scn_intro.frame_start = 1
scn_intro.frame_end = 240
scn_intro.frame_set(120)
select_logo_hierarchy(scn_intro)

combined_fbx = os.path.join(OUT_DIR, "MindScape3D_Title.fbx")
bpy.ops.export_scene.fbx(
    filepath=combined_fbx,
    use_selection=True,
    object_types={'EMPTY', 'MESH'},
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=False,
    bake_anim=True,
    bake_anim_use_all_bones=False,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    path_mode='AUTO'
)
print("Exported Combined FBX (frames 1-240):", combined_fbx)

# Restore IntroScreen range to 1-120
scn_intro.frame_start = 1
scn_intro.frame_end = 120
scn_intro.frame_set(120)

# ---------------------------------------------------------------------------
# 2. Export Dedicated Animation 1: MindScape3D_IntroScreen (.glb & .fbx)
# ---------------------------------------------------------------------------
select_logo_hierarchy(scn_intro)

intro_glb = os.path.join(OUT_DIR, "MindScape3D_IntroScreen.glb")
bpy.ops.export_scene.gltf(
    filepath=intro_glb,
    export_format='GLB',
    use_selection=True,
    use_active_scene=True,
    export_apply=False,
    export_yup=True,
    export_materials='EXPORT',
    export_animations=True,
    export_animation_mode='SCENE',
    export_anim_scene_split_object=False,
    export_frame_range=True,
    export_force_sampling=True,
    export_anim_slide_to_zero=True,
    export_cameras=False,
    export_lights=False
)

intro_fbx = os.path.join(OUT_DIR, "MindScape3D_IntroScreen.fbx")
bpy.ops.export_scene.fbx(
    filepath=intro_fbx,
    use_selection=True,
    object_types={'EMPTY', 'MESH'},
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=False,
    bake_anim=True,
    bake_anim_use_all_bones=False,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    path_mode='AUTO'
)
print("Exported IntroScreen GLB & FBX:", intro_glb, intro_fbx)

# ---------------------------------------------------------------------------
# 3. Export Dedicated Animation 2: MindScape3D_MainMenu_GlowOnly (.glb & .fbx)
# ---------------------------------------------------------------------------
scn_menu.frame_start = 121
scn_menu.frame_end = 240
scn_menu.frame_set(121)
select_logo_hierarchy(scn_menu)

menu_glb = os.path.join(OUT_DIR, "MindScape3D_MainMenu_GlowOnly.glb")
bpy.ops.export_scene.gltf(
    filepath=menu_glb,
    export_format='GLB',
    use_selection=True,
    use_active_scene=True,
    export_apply=False,
    export_yup=True,
    export_materials='EXPORT',
    export_animations=True,
    export_animation_mode='SCENE',
    export_anim_scene_split_object=False,
    export_frame_range=True,
    export_force_sampling=True,
    export_anim_slide_to_zero=True,
    export_cameras=False,
    export_lights=False
)

menu_fbx = os.path.join(OUT_DIR, "MindScape3D_MainMenu_GlowOnly.fbx")
bpy.ops.export_scene.fbx(
    filepath=menu_fbx,
    use_selection=True,
    object_types={'EMPTY', 'MESH'},
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=False,
    bake_anim=True,
    bake_anim_use_all_bones=False,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    path_mode='AUTO'
)
print("Exported MainMenu_GlowOnly GLB & FBX:", menu_glb, menu_fbx)

bpy.ops.wm.save_mainfile()
print("All Unity-ready exports in Assets/Models/Title completed successfully!")
