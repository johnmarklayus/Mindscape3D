"""Build and animate the Sunset & Starry Sky Overlook scene in Blender:
- Seated rigged Boy (left, dark navy hoodie) & Girl (right, dusty-pink sweater, long wavy hair)
  swaying gently on the cobblestone overlook and taking turns pointing up at the stars.
- Foreground flowering bushes (lavender, blue, pink, and golden wildflowers) and
  overarching framing trees with leaf clusters slightly swaying/rustling in the evening breeze.
- 3D cobblestone path, midground forest trees, river & bridge, city skyline silhouettes,
  sunset-to-twilight sky dome, and twinkling stars in the upper sky.

Saves:
  - /Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/Overlook_Boy_Girl_Stars.blend
  - /Users/arieljerickogacilo/mindscape-3d/Assets/Models/Overlook/Overlook_Boy_Girl_Stars.glb
  - /Users/arieljerickogacilo/mindscape-3d/Assets/Models/Overlook/Overlook_Boy_Girl_Stars.fbx
"""

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

# ---------------------------------------------------------------------------
# 1. Clean Scene Setup
# ---------------------------------------------------------------------------
base_scene = bpy.context.scene
for sc in list(bpy.data.scenes):
    if sc != base_scene:
        bpy.data.scenes.remove(sc)
base_scene.name = "Overlook_Stars"

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for c in list(bpy.data.curves):
    bpy.data.curves.remove(c)
for arm in list(bpy.data.armatures):
    bpy.data.armatures.remove(arm)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
for lt in list(bpy.data.lights):
    bpy.data.lights.remove(lt)
for cm in list(bpy.data.cameras):
    bpy.data.cameras.remove(cm)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

scene = base_scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
FPS = 30
PERIOD = 180  # 6.0 seconds seamless loop at 30 fps
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = PERIOD

def make_col(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

col_chars   = make_col("Overlook | Boy & Girl")
col_foliage = make_col("Overlook | Bushes & Leaves")
col_env     = make_col("Overlook | Path, Sky & Stars")
col_stage   = make_col("Overlook | Camera & Lights")

scene_root = bpy.data.objects.new("Overlook_Scene_Root", None)
col_env.objects.link(scene_root)
scene_root.location = (0, 0, 0)

# ---------------------------------------------------------------------------
# 2. Materials (Warm Golden Sunset Rim + Starry Twilight Palette)
# ---------------------------------------------------------------------------
def create_mat(name, color, roughness=0.65, metallic=0.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m

# Character Materials matching the uploaded illustration
mat_skin       = create_mat("OV | Warm Skin", (0.76, 0.48, 0.34), roughness=0.55, emission=(0.35, 0.16, 0.06), emission_strength=0.10)
mat_boy_hoodie = create_mat("OV | Boy Dark Hoodie", (0.045, 0.065, 0.105), roughness=0.65, emission=(0.12, 0.07, 0.03), emission_strength=0.05)
mat_boy_trim   = create_mat("OV | Boy Hoodie Rim", (0.08, 0.10, 0.15), roughness=0.60)
mat_boy_pants  = create_mat("OV | Boy Dark Pants", (0.04, 0.05, 0.07), roughness=0.72)
mat_boy_hair   = create_mat("OV | Boy Charcoal Hair", (0.025, 0.02, 0.02), roughness=0.48)

mat_girl_top   = create_mat("OV | Girl Rose Sweater", (0.52, 0.32, 0.38), roughness=0.60, emission=(0.30, 0.14, 0.12), emission_strength=0.10)
mat_girl_trim  = create_mat("OV | Girl Sweater Cuff", (0.42, 0.24, 0.30), roughness=0.60)
mat_girl_jeans = create_mat("OV | Girl Denim Jeans", (0.06, 0.12, 0.22), roughness=0.68)
mat_girl_hair  = create_mat("OV | Girl Dark Wavy Hair", (0.04, 0.022, 0.018), roughness=0.42, emission=(0.18, 0.07, 0.03), emission_strength=0.06)
mat_shoes      = create_mat("OV | Sneakers", (0.12, 0.11, 0.14), roughness=0.60)
mat_eye        = create_mat("OV | Dark Eye", (0.015, 0.01, 0.01), roughness=0.25)

# Environment & Foliage Materials
mat_stone_base = create_mat("OV | Path Earth", (0.10, 0.07, 0.06), roughness=0.88)
mat_cobble_1   = create_mat("OV | Cobblestone Warm", (0.34, 0.22, 0.15), roughness=0.55, emission=(0.45, 0.22, 0.08), emission_strength=0.18)
mat_cobble_2   = create_mat("OV | Cobblestone Slate", (0.22, 0.16, 0.15), roughness=0.62, emission=(0.25, 0.12, 0.05), emission_strength=0.10)

mat_bush_dark  = create_mat("OV | Bush Deep Green", (0.035, 0.10, 0.055), roughness=0.58)
mat_bush_lit   = create_mat("OV | Bush Sunlit Leaf", (0.14, 0.22, 0.065), roughness=0.50, emission=(0.35, 0.22, 0.04), emission_strength=0.20)
mat_tree_bark  = create_mat("OV | Tree Bark", (0.07, 0.045, 0.035), roughness=0.82)
mat_tree_leaf  = create_mat("OV | Canopy Leaf", (0.055, 0.13, 0.045), roughness=0.52, emission=(0.20, 0.14, 0.03), emission_strength=0.14)

mat_fl_purple  = create_mat("OV | Flower Lavender", (0.58, 0.44, 0.94), roughness=0.38, emission=(0.58, 0.44, 0.94), emission_strength=0.75)
mat_fl_blue    = create_mat("OV | Flower Sky Blue", (0.38, 0.62, 0.96), roughness=0.38, emission=(0.38, 0.62, 0.96), emission_strength=0.70)
mat_fl_pink    = create_mat("OV | Flower Rose Pink", (0.94, 0.48, 0.72), roughness=0.38, emission=(0.94, 0.48, 0.72), emission_strength=0.75)
mat_fl_gold    = create_mat("OV | Flower Golden", (1.00, 0.85, 0.35), roughness=0.32, emission=(1.00, 0.82, 0.28), emission_strength=0.95)

mat_star_glow  = create_mat("OV | Starlight Twinkle", (1.0, 0.97, 0.86), roughness=0.10, emission=(1.0, 0.94, 0.72), emission_strength=8.5)
mat_sun_glow   = create_mat("OV | Sunset Sun", (1.0, 0.88, 0.52), roughness=0.10, emission=(1.0, 0.76, 0.28), emission_strength=4.5)
mat_city_sil   = create_mat("OV | City Silhouette", (0.14, 0.10, 0.15), roughness=0.75, emission=(0.28, 0.15, 0.12), emission_strength=0.18)
mat_river_gold = create_mat("OV | River Sunset Reflection", (0.85, 0.48, 0.24), roughness=0.16, metallic=0.45, emission=(0.95, 0.52, 0.20), emission_strength=0.65)
mat_cloud_gold = create_mat("OV | Sunset Cloud Glow", (0.96, 0.56, 0.34), roughness=0.80, emission=(0.98, 0.52, 0.26), emission_strength=1.15)
mat_cloud_rose = create_mat("OV | Twilight Cloud Rose", (0.72, 0.38, 0.48), roughness=0.80, emission=(0.75, 0.36, 0.45), emission_strength=0.75)

# ---------------------------------------------------------------------------
# 3. Geometry Helpers
# ---------------------------------------------------------------------------
def make_uv_sphere(name, radius=1.0, scale=(1, 1, 1), mat=None, u_seg=18, v_seg=12):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u_seg, v_segments=v_seg, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    mesh.update()
    return mesh

def make_tapered_limb_mesh(name, p_start, p_end, r_start, r_end, mat, segs=16, rings=10):
    a = Vector(p_start)
    b = Vector(p_end)
    direction = b - a
    q = direction.to_track_quat('Z', 'Y')
    verts, faces = [], []
    for i in range(rings + 1):
        t = i / rings
        bulge = 1.0 + 0.07 * math.sin(math.pi * t)
        r = (r_start * (1.0 - t) + r_end * t) * bulge
        for j in range(segs):
            ang = 2.0 * math.pi * j / segs
            pt = a + direction * t + q @ Vector((r * math.cos(ang), r * math.sin(ang), 0.0))
            verts.append(pt)
    faces.append(tuple(reversed(range(segs))))
    for i in range(rings):
        for j in range(segs):
            k = i * segs + j
            faces.append((k, i * segs + (j + 1) % segs, (i + 1) * segs + (j + 1) % segs, k + segs))
    faces.append(tuple(range(rings * segs, (rings + 1) * segs)))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    for p in mesh.polygons:
        p.use_smooth = True
    if mat:
        mesh.materials.append(mat)
    mesh.update()
    return mesh

# ---------------------------------------------------------------------------
# 4. Build Rigged Character (Boy & Girl)
# ---------------------------------------------------------------------------
def build_character(name, is_boy, location, rotation_z_deg, char_scale=0.50):
    parts = []
    cloth_mat = mat_boy_hoodie if is_boy else mat_girl_top
    trim_mat  = mat_boy_trim if is_boy else mat_girl_trim
    pants_mat = mat_boy_pants if is_boy else mat_girl_jeans
    hair_mat  = mat_boy_hair if is_boy else mat_girl_hair

    def add_part(part_name, mesh, pos=(0, 0, 0), rot=(0, 0, 0), bind_bone="Chest"):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        rot_mat = Euler(rot, 'XYZ').to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=Matrix.Translation(pos) @ rot_mat, verts=bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        ob = bpy.data.objects.new(f"{name}_{part_name}", mesh)
        col_chars.objects.link(ob)
        ob["bind"] = bind_bone
        parts.append(ob)
        return ob

    # Torso & Hips
    torso_w = 0.34 if is_boy else 0.29
    add_part("Torso_Upper", make_uv_sphere("TorsoU", 1.0, (torso_w, 0.22, 0.35), cloth_mat), (0, 0, 2.04), bind_bone="Chest")
    add_part("Torso_Lower", make_uv_sphere("TorsoL", 1.0, (torso_w * 0.94, 0.21, 0.28), cloth_mat), (0, 0.01, 1.74), bind_bone="Spine")
    add_part("Waist_Hem",   make_uv_sphere("Waist",  1.0, (torso_w * 0.96, 0.22, 0.12), trim_mat),  (0, 0.01, 1.56), bind_bone="Hips")
    add_part("Hips_Pelvis", make_uv_sphere("HipsP",  1.0, (0.31, 0.22, 0.20), pants_mat), (0, 0.02, 1.44), bind_bone="Hips")

    if is_boy:
        # Sculpted hoodie hood resting on upper back & collar
        add_part("Hoodie_Hood", make_uv_sphere("Hood", 1.0, (0.31, 0.23, 0.17), cloth_mat), (0, 0.15, 2.30), rot=(-0.22, 0, 0), bind_bone="Chest")
        add_part("Hoodie_Rim",  make_uv_sphere("HoodRim", 1.0, (0.33, 0.19, 0.10), trim_mat), (0, 0.13, 2.34), rot=(-0.18, 0, 0), bind_bone="Chest")
    else:
        add_part("Sweater_Collar", make_uv_sphere("Collar", 1.0, (0.21, 0.17, 0.08), trim_mat), (0, 0.0, 2.33), bind_bone="Chest")

    # Neck & Head
    add_part("Neck", make_uv_sphere("Neck", 1.0, (0.11, 0.11, 0.16), mat_skin), (0, 0, 2.42), bind_bone="Neck")
    add_part("Head", make_uv_sphere("Head", 1.0, (0.28, 0.27, 0.32), mat_skin), (0, -0.02, 2.76), bind_bone="Head")
    add_part("Nose", make_uv_sphere("Nose", 1.0, (0.032, 0.045, 0.042), mat_skin), (0, -0.28, 2.74), bind_bone="Head")

    for s in (-1, 1):
        add_part(f"Ear_{s}", make_uv_sphere(f"Ear_{s}", 1.0, (0.055, 0.045, 0.085), mat_skin), (s * 0.27, -0.01, 2.75), bind_bone="Head")
        add_part(f"Eye_{s}", make_uv_sphere(f"Eye_{s}", 1.0, (0.028, 0.018, 0.042), mat_eye), (s * 0.11, -0.25, 2.78), bind_bone="Head")

    # Hair
    add_part("Hair_Crown", make_uv_sphere("HairCrown", 1.0, (0.30, 0.29, 0.28), hair_mat), (0, 0.02, 2.84), bind_bone="Head")
    add_part("Hair_Back",  make_uv_sphere("HairBack",  1.0, (0.29, 0.24, 0.27), hair_mat), (0, 0.09, 2.75), bind_bone="Head")

    if is_boy:
        random.seed(17)
        for i in range(12):
            ang = (i / 12.0) * 2.0 * math.pi
            hx = 0.23 * math.sin(ang)
            hy = 0.21 * math.cos(ang) + 0.02
            hz = 2.86 + 0.07 * math.cos(i * 1.7)
            add_part(
                f"Boy_Tuft_{i}",
                make_uv_sphere(f"Tuft_{i}", 1.0, (0.10, 0.13, 0.15), hair_mat),
                (hx, hy, hz),
                rot=(0.25 * math.cos(ang), 0.25 * math.sin(ang), ang * 0.3),
                bind_bone="Head"
            )
    else:
        for s in (-1, 1):
            add_part(f"Girl_SideLock_{s}", make_uv_sphere(f"SideLock_{s}", 1.0, (0.10, 0.13, 0.26), hair_mat), (s * 0.23, 0.02, 2.62), rot=(0.1, s * 0.12, 0), bind_bone="Head")
        for i in range(7):
            hx = (i - 3) * 0.072
            hy = 0.17 + 0.02 * abs(i - 3)
            add_part(
                f"Girl_LongHair_Upper_{i}",
                make_uv_sphere(f"LongHairU_{i}", 1.0, (0.095, 0.085, 0.28), hair_mat),
                (hx, hy, 2.46),
                rot=(0.18, 0, (i - 3) * 0.04),
                bind_bone="Head"
            )
            add_part(
                f"Girl_LongHair_Flow_{i}",
                make_uv_sphere(f"LongHairL_{i}", 1.0, (0.09, 0.075, 0.30), hair_mat),
                (hx * 1.06, hy + 0.04, 2.14),
                rot=(0.12, 0, (i - 3) * 0.06),
                bind_bone="HairBack"
            )

    # Arms, Hands & Pointing Index Fingers, plus Legs & Shoes
    for s, side in ((1, 'L'), (-1, 'R')):
        add_part(
            f"Sleeve_{side}",
            make_tapered_limb_mesh(f"Sleeve_{side}", (s * 0.28, 0, 2.22), (s * 1.12, 0, 2.22), 0.13, 0.088, cloth_mat),
            bind_bone=f"ARM.{side}"
        )
        add_part(
            f"Cuff_{side}",
            make_tapered_limb_mesh(f"Cuff_{side}", (s * 1.08, 0, 2.22), (s * 1.16, 0, 2.22), 0.092, 0.090, trim_mat),
            bind_bone=f"Forearm.{side}"
        )
        add_part(
            f"Hand_{side}",
            make_uv_sphere(f"Hand_{side}", 1.0, (0.09, 0.062, 0.052), mat_skin),
            (s * 1.23, -0.01, 2.22),
            bind_bone=f"Hand.{side}"
        )
        add_part(
            f"PointFinger_{side}",
            make_tapered_limb_mesh(f"Finger_{side}", (s * 1.28, -0.02, 2.23), (s * 1.42, -0.02, 2.23), 0.022, 0.014, mat_skin),
            bind_bone=f"Hand.{side}"
        )

        add_part(
            f"PantLeg_{side}",
            make_tapered_limb_mesh(f"PantLeg_{side}", (s * 0.16, 0, 1.42), (s * 0.17, 0, 0.22), 0.145, 0.095, pants_mat),
            bind_bone=f"LEG.{side}"
        )
        add_part(
            f"Shoe_{side}",
            make_uv_sphere(f"Shoe_{side}", 1.0, (0.10, 0.19, 0.075), mat_shoes),
            (s * 0.17, -0.06, 0.12),
            bind_bone=f"Foot.{side}"
        )

    # Create Armature
    arm = bpy.data.armatures.new(f"{name}_Armature")
    rig = bpy.data.objects.new(f"{name}_Rig", arm)
    col_chars.objects.link(rig)
    rig.parent = scene_root

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')

    def add_bone(bname, head, tail, parent_name=None):
        b = arm.edit_bones.new(bname)
        b.head = head
        b.tail = tail
        if parent_name:
            b.parent = arm.edit_bones[parent_name]
        return b

    add_bone("Root",     (0, 0, 0.0),  (0, 0, 0.25))
    add_bone("Hips",     (0, 0, 1.40), (0, 0, 1.62), "Root")
    add_bone("Spine",    (0, 0, 1.62), (0, 0, 1.92), "Hips")
    add_bone("Chest",    (0, 0, 1.92), (0, 0, 2.28), "Spine")
    add_bone("Neck",     (0, 0, 2.28), (0, 0, 2.50), "Chest")
    add_bone("Head",     (0, 0, 2.50), (0, 0, 3.05), "Neck")
    add_bone("HairBack", (0, 0.18, 2.42), (0, 0.22, 1.90), "Head")

    for s, side in ((1, 'L'), (-1, 'R')):
        add_bone(f"UpperArm.{side}", (s * 0.30, 0, 2.22), (s * 0.74, 0, 2.22), "Chest")
        add_bone(f"Forearm.{side}",  (s * 0.74, 0, 2.22), (s * 1.16, 0, 2.22), f"UpperArm.{side}")
        add_bone(f"Hand.{side}",     (s * 1.16, 0, 2.22), (s * 1.42, 0, 2.22), f"Forearm.{side}")
        add_bone(f"Thigh.{side}",    (s * 0.16, 0, 1.42), (s * 0.17, 0, 0.80), "Hips")
        add_bone(f"Shin.{side}",     (s * 0.17, 0, 0.80), (s * 0.17, 0, 0.20), f"Thigh.{side}")
        add_bone(f"Foot.{side}",     (s * 0.17, 0, 0.20), (s * 0.17, -0.24, 0.10), f"Shin.{side}")

    bpy.ops.object.mode_set(mode='OBJECT')

    for ob in parts:
        bind = ob["bind"]
        for v in ob.data.vertices:
            if bind.startswith("ARM."):
                side = bind[-1]
                w = max(0.0, min(1.0, (0.82 - abs(v.co.x)) / 0.22))
                weights = [(f"UpperArm.{side}", w), (f"Forearm.{side}", 1.0 - w)]
            elif bind.startswith("LEG."):
                side = bind[-1]
                w = max(0.0, min(1.0, (v.co.z - 0.70) / 0.24))
                weights = [(f"Thigh.{side}", w), (f"Shin.{side}", 1.0 - w)]
            else:
                weights = [(bind, 1.0)]
            for bname, wval in weights:
                if wval > 0.0:
                    vg = ob.vertex_groups.get(bname) or ob.vertex_groups.new(name=bname)
                    vg.add([v.index], wval, 'REPLACE')
        ob.parent = rig

    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = f"{name}_Mesh"

    mod = body.modifiers.new("Armature", 'ARMATURE')
    mod.object = rig
    mod.use_deform_preserve_volume = True

    rig.location = location
    rig.rotation_euler = (0.0, 0.0, math.radians(rotation_z_deg))
    rig.scale = (char_scale, char_scale, char_scale)

    for pbone in rig.pose.bones:
        pbone.rotation_mode = 'QUATERNION'

    return rig, body

# Position Boy & Girl in the exact foreground overlook composition of the reference artwork:
# Seated on the cobblestone path (hips resting right on the stones at z ~ 0.12),
# facing the sunset horizon & stars (+Y) and angled slightly toward each other.
boy_rig, boy_mesh   = build_character("Boy",  is_boy=True,  location=(-1.05, -2.05, 0.06), rotation_z_deg=156.0,  char_scale=0.52)
girl_rig, girl_mesh = build_character("Girl", is_boy=False, location=( 1.05, -2.05, 0.05), rotation_z_deg=-156.0, char_scale=0.49)

# ---------------------------------------------------------------------------
# 5. Build Foreground Cobblestone Overlook Path, Bushes, Leaves, Trees & Sky
# ---------------------------------------------------------------------------
path_base_mesh = make_uv_sphere("Overlook_Ground", 1.0, (5.2, 3.4, 0.32), mat_stone_base, u_seg=28, v_seg=16)
path_base = bpy.data.objects.new("Overlook_Ground", path_base_mesh)
col_env.objects.link(path_base)
path_base.parent = scene_root
path_base.location = (0.0, -2.1, -0.26)

random.seed(42)
cobble_positions = [
    (0.0, -3.1, 0.01, 0.42, 0.30), (-0.54, -3.0, 0.01, 0.38, 0.28), (0.52, -3.05, 0.01, 0.38, 0.28),
    (-0.26, -2.55, 0.03, 0.44, 0.32), (0.30, -2.58, 0.03, 0.42, 0.32), (-0.78, -2.50, 0.02, 0.36, 0.28),
    (0.80, -2.52, 0.02, 0.36, 0.28), (0.02, -2.05, 0.04, 0.46, 0.34), (-0.50, -2.00, 0.04, 0.40, 0.30),
    (0.54, -2.02, 0.04, 0.40, 0.30), (-0.20, -1.55, 0.04, 0.42, 0.30), (0.32, -1.58, 0.04, 0.40, 0.28),
    (-0.72, -1.50, 0.03, 0.35, 0.26), (0.74, -1.52, 0.03, 0.35, 0.26), (0.0, -1.08, 0.03, 0.46, 0.28),
    (-0.48, -1.05, 0.02, 0.36, 0.25), (0.48, -1.05, 0.02, 0.36, 0.25),
]
for idx, (cx, cy, cz, sx, sy) in enumerate(cobble_positions):
    cmat = mat_cobble_1 if idx % 2 == 0 else mat_cobble_2
    cmesh = make_uv_sphere(f"Cobble_{idx}", 1.0, (sx, sy, 0.055), cmat, u_seg=14, v_seg=8)
    cob = bpy.data.objects.new(f"Cobble_{idx}", cmesh)
    col_env.objects.link(cob)
    cob.parent = scene_root
    cob.location = (cx, cy, cz)
    cob.rotation_euler = (0.0, 0.0, random.uniform(-0.4, 0.4))

# Animated Bushes & Wildflower Clusters (Left & Right banks around the Boy & Girl)
animated_bushes = []

def create_bush_cluster(name, loc, base_scale=1.0, phase_offset=0.0):
    pivot = bpy.data.objects.new(name, None)
    col_foliage.objects.link(pivot)
    pivot.parent = scene_root
    pivot.location = loc

    puff_offsets = [
        (0.0, 0.0, 0.16, 0.40, 0.34, 0.26, mat_bush_dark),
        (-0.20, -0.08, 0.22, 0.30, 0.26, 0.22, mat_bush_lit),
        ( 0.20, -0.06, 0.20, 0.32, 0.26, 0.22, mat_bush_lit),
        ( 0.03,  0.12, 0.28, 0.28, 0.24, 0.20, mat_bush_lit),
    ]
    for i, (ox, oy, oz, sx, sy, sz, bmat) in enumerate(puff_offsets):
        pmesh = make_uv_sphere(f"{name}_Puff_{i}", 1.0, (sx * base_scale, sy * base_scale, sz * base_scale), bmat, u_seg=14, v_seg=10)
        pob = bpy.data.objects.new(f"{name}_Puff_{i}", pmesh)
        col_foliage.objects.link(pob)
        pob.parent = pivot
        pob.location = (ox * base_scale, oy * base_scale, oz * base_scale)

    flower_mats = [mat_fl_purple, mat_fl_blue, mat_fl_pink, mat_fl_gold]
    for f_idx in range(8):
        ang = f_idx * 0.82 + phase_offset
        fx = 0.28 * math.cos(ang) * base_scale
        fy = (-0.22 + 0.14 * math.sin(ang)) * base_scale
        fz = (0.20 + 0.11 * math.cos(f_idx * 1.5)) * base_scale
        fmat = flower_mats[(f_idx + int(phase_offset * 3)) % len(flower_mats)]
        fmesh = make_uv_sphere(f"{name}_Flower_{f_idx}", 1.0, (0.048, 0.032, 0.048), fmat, u_seg=10, v_seg=8)
        fob = bpy.data.objects.new(f"{name}_Flower_{f_idx}", fmesh)
        col_foliage.objects.link(fob)
        fob.parent = pivot
        fob.location = (fx, fy, fz)

    animated_bushes.append((pivot, phase_offset, 1.0))
    return pivot

bush_specs = [
    # Left bank (around & beside the Boy)
    ("Bush_L_Front_1", (-1.85, -3.15, -0.02), 1.05, 0.0),
    ("Bush_L_Front_2", (-1.25, -3.30, -0.05), 0.85, 0.7),
    ("Bush_L_Mid_1",   (-2.25, -2.35,  0.10), 1.20, 1.4),
    ("Bush_L_Mid_2",   (-1.75, -1.65,  0.06), 0.98, 2.1),
    ("Bush_L_Back_1",  (-2.55, -1.05,  0.22), 1.35, 2.8),
    ("Bush_L_Back_2",  (-1.60, -0.85,  0.02), 0.95, 3.5),
    # Right bank (around & beside the Girl)
    ("Bush_R_Front_1", ( 1.85, -3.15, -0.02), 1.05, 0.4),
    ("Bush_R_Front_2", ( 1.25, -3.30, -0.05), 0.85, 1.1),
    ("Bush_R_Mid_1",   ( 2.25, -2.35,  0.10), 1.20, 1.8),
    ("Bush_R_Mid_2",   ( 1.75, -1.65,  0.06), 0.98, 2.5),
    ("Bush_R_Back_1",  ( 2.55, -1.05,  0.22), 1.35, 3.2),
    ("Bush_R_Back_2",  ( 1.60, -0.85,  0.02), 0.95, 3.9),
]
for bname, bloc, bscale, bphase in bush_specs:
    create_bush_cluster(bname, bloc, bscale, bphase)

# Overarching Left & Right Framing Trees with Animated Leaf Clusters
animated_leaves = []

def create_framing_tree(side_sign, name_prefix):
    tree_root = bpy.data.objects.new(f"{name_prefix}_Tree", None)
    col_foliage.objects.link(tree_root)
    tree_root.parent = scene_root
    tree_root.location = (side_sign * 1.76, -2.25, -0.05)

    trunk_mesh = make_tapered_limb_mesh(
        f"{name_prefix}_Trunk",
        (0.0, 0.0, -0.15),
        (-side_sign * 0.22, 0.05, 1.85),
        0.18, 0.095, mat_tree_bark
    )
    trunk_ob = bpy.data.objects.new(f"{name_prefix}_Trunk", trunk_mesh)
    col_foliage.objects.link(trunk_ob)
    trunk_ob.parent = tree_root

    branch_mesh = make_tapered_limb_mesh(
        f"{name_prefix}_ArchBranch",
        (-side_sign * 0.16, 0.04, 1.52),
        (-side_sign * 1.10, 0.08, 1.88),
        0.085, 0.032, mat_tree_bark
    )
    branch_ob = bpy.data.objects.new(f"{name_prefix}_ArchBranch", branch_mesh)
    col_foliage.objects.link(branch_ob)
    branch_ob.parent = tree_root

    leaf_positions = [
        (-side_sign * 0.10, -0.06, 1.32, 0.34, 0.0),
        (-side_sign * 0.28, -0.08, 1.52, 0.38, 0.8),
        (-side_sign * 0.52, -0.08, 1.66, 0.36, 1.6),
        (-side_sign * 0.78, -0.06, 1.75, 0.32, 2.4),
        (-side_sign * 1.02, -0.04, 1.82, 0.28, 3.2),
        (-side_sign * 0.05, -0.10, 1.05, 0.30, 4.0),
    ]
    for idx, (lx, ly, lz, lsc, lph) in enumerate(leaf_positions):
        lpivot = bpy.data.objects.new(f"{name_prefix}_LeafCluster_{idx}", None)
        col_foliage.objects.link(lpivot)
        lpivot.parent = tree_root
        lpivot.location = (lx, ly, lz)

        for sub in range(3):
            ang = sub * 2.1 + lph
            smesh = make_uv_sphere(
                f"{name_prefix}_LeafSub_{idx}_{sub}",
                1.0,
                (lsc * 0.72, lsc * 0.42, lsc * 0.34),
                mat_bush_lit if sub == 0 else mat_tree_leaf,
                u_seg=12, v_seg=8
            )
            sob = bpy.data.objects.new(f"{name_prefix}_LeafSub_{idx}_{sub}", smesh)
            col_foliage.objects.link(sob)
            sob.parent = lpivot
            sob.location = (0.11 * math.cos(ang), 0.05 * math.sin(ang), -0.06 * sub)
            sob.rotation_euler = (0.15, side_sign * 0.22, ang * 0.2)

        animated_leaves.append((lpivot, lph + (0.0 if side_sign < 0 else 1.2)))

create_framing_tree(-1, "FrameLeft")
create_framing_tree( 1, "FrameRight")

# Midground Valley Treetops, Sunset River, Bridge & Distant City Skyline
for m_idx, (mx, my, mz, msc) in enumerate([
    (-3.2, 1.5, -0.35, 1.2), (-2.1, 1.8, -0.45, 1.0), (-1.1, 2.0, -0.55, 0.9),
    ( 1.1, 2.0, -0.55, 0.9), ( 2.1, 1.8, -0.45, 1.0), ( 3.2, 1.5, -0.35, 1.2),
]):
    mmesh = make_uv_sphere(f"MidValley_Trees_{m_idx}", 1.0, (0.95 * msc, 0.75 * msc, 0.55 * msc), mat_bush_lit if m_idx % 2 == 0 else mat_tree_leaf)
    mob = bpy.data.objects.new(f"MidValley_Trees_{m_idx}", mmesh)
    col_env.objects.link(mob)
    mob.parent = scene_root
    mob.location = (mx, my, mz)

river_mesh = bpy.data.meshes.new("Sunset_River_Mesh")
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=14.0)
bmesh.ops.scale(bm, vec=(1.4, 0.55, 1.0), verts=bm.verts)
bm.to_mesh(river_mesh)
bm.free()
river_mesh.materials.append(mat_river_gold)
river_ob = bpy.data.objects.new("Sunset_River", river_mesh)
col_env.objects.link(river_ob)
river_ob.parent = scene_root
river_ob.location = (0.0, 6.2, -0.75)

# Distant City Skyline Horizon Silhouette (grounded at z = -0.75)
building_specs = [
    (-5.2, 9.8, 0.55, 1.5), (-4.4, 9.9, 0.48, 1.1), (-3.6, 9.7, 0.52, 1.8), (-2.8, 9.8, 0.46, 1.3),
    (-2.0, 9.9, 0.50, 1.6), (-1.2, 9.9, 0.44, 1.0), (-0.5, 9.9, 0.42, 0.8), ( 0.6, 9.9, 0.42, 0.9),
    ( 1.3, 9.8, 0.40, 1.7), ( 2.1, 9.9, 0.48, 1.4), ( 2.9, 9.7, 0.54, 1.9), ( 3.7, 9.6, 0.58, 2.4),
    ( 4.5, 9.4, 0.62, 3.4), ( 5.3, 9.7, 0.52, 1.8),
]
for idx, (bx, by, bw, bh) in enumerate(building_specs):
    bmesh_data = bpy.data.meshes.new(f"Skyline_Tower_{idx}")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(bw, bw, bh), verts=bm.verts)
    bm.to_mesh(bmesh_data)
    bm.free()
    bmesh_data.materials.append(mat_city_sil)
    bob = bpy.data.objects.new(f"Skyline_Tower_{idx}", bmesh_data)
    col_env.objects.link(bob)
    bob.parent = scene_root
    bob.location = (bx, by, -0.75 + bh * 0.5)

# Glowing Sunset Sun & Soft Sunset Clouds on the Horizon
sun_mesh = make_uv_sphere("Horizon_Sun", 0.55, (1.0, 0.25, 1.0), mat_sun_glow, u_seg=24, v_seg=16)
sun_ob = bpy.data.objects.new("Horizon_Sun", sun_mesh)
col_env.objects.link(sun_ob)
sun_ob.parent = scene_root
sun_ob.location = (0.0, 10.2, 0.95)

cloud_specs = [
    (-2.8, 10.4, 1.45, 1.4, 0.22, mat_cloud_gold),
    ( 2.6, 10.4, 1.40, 1.5, 0.22, mat_cloud_gold),
    (-1.4, 10.3, 1.85, 1.2, 0.18, mat_cloud_rose),
    ( 1.5, 10.3, 1.80, 1.2, 0.18, mat_cloud_rose),
]
for c_idx, (cx, cy, cz, csc_x, csc_z, cmat) in enumerate(cloud_specs):
    cmesh = make_uv_sphere(f"Sunset_Cloud_{c_idx}", 1.0, (csc_x, 0.2, csc_z), cmat, u_seg=16, v_seg=10)
    cob = bpy.data.objects.new(f"Sunset_Cloud_{c_idx}", cmesh)
    col_env.objects.link(cob)
    cob.parent = scene_root
    cob.location = (cx, cy, cz)

# Twinkling 3D Stars in the Upper Twilight Sky (where the Boy and Girl point!)
star_positions = [
    (-2.5, 8.8, 2.35, 0.055, 0.0), (-1.6, 8.8, 2.65, 0.072, 0.8), (-0.7, 8.8, 2.85, 0.068, 1.6),
    ( 0.2, 8.8, 2.90, 0.075, 2.4), ( 1.1, 8.8, 2.70, 0.072, 3.2), ( 2.1, 8.8, 2.45, 0.060, 4.0),
    (-2.0, 8.8, 2.05, 0.050, 1.2), (-1.1, 8.8, 2.30, 0.062, 2.0), (-0.2, 8.8, 2.50, 0.080, 0.4),
    ( 0.7, 8.8, 2.35, 0.065, 2.8), ( 1.6, 8.8, 2.15, 0.055, 3.6), (-0.4, 8.8, 3.10, 0.065, 4.4),
    ( 0.5, 8.8, 3.12, 0.065, 1.9), (-1.4, 8.8, 3.02, 0.058, 2.7), ( 1.4, 8.8, 2.98, 0.058, 3.5),
]
star_objects = []
for idx, (sx, sy, sz, srad, sphase) in enumerate(star_positions):
    smesh = make_uv_sphere(f"Star_{idx}", srad, (1.0, 0.35, 1.0), mat_star_glow, u_seg=10, v_seg=8)
    sob = bpy.data.objects.new(f"Star_{idx}", smesh)
    col_env.objects.link(sob)
    sob.parent = scene_root
    sob.location = (sx, sy, sz)
    star_objects.append((sob, sphase))

# ---------------------------------------------------------------------------
# 6. Armature-Space Rotation Helper & Keyframe Animation (Frames 1..180)
# ---------------------------------------------------------------------------
rx = lambda a: Matrix.Rotation(a, 3, 'X')
ry = lambda a: Matrix.Rotation(a, 3, 'Y')
rz = lambda a: Matrix.Rotation(a, 3, 'Z')

def rotate_bone_armature_space(rig, bone_name, rot_mat3):
    """Apply a 3x3 rotation matrix defined in Character Armature Space
    (+X = Left, -X = Right, -Y = Front/Forward, +Z = Up) to a PoseBone."""
    pb = rig.pose.bones[bone_name]
    basis = rig.data.bones[bone_name].matrix_local.to_3x3()
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = (basis.inverted() @ rot_mat3 @ basis).to_quaternion()

def smooth_window(phase_norm, start_n, peak1_n, peak2_n, end_n):
    if phase_norm <= start_n or phase_norm >= end_n:
        return 0.0
    if phase_norm < peak1_n:
        u = (phase_norm - start_n) / (peak1_n - start_n)
        return 0.5 - 0.5 * math.cos(math.pi * u)
    if phase_norm <= peak2_n:
        return 1.0
    u = (phase_norm - peak2_n) / (end_n - peak2_n)
    return 0.5 + 0.5 * math.cos(math.pi * u)

def pose_and_keyframe_character(rig, is_boy, frame, u_norm):
    theta = u_norm * 2.0 * math.pi
    sway_phase = theta if is_boy else (theta + 0.90)

    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)

    # 1. Lower Root in Armature space so Hips (z=1.40 in rest) sit right on the cobblestones (z ~ 0.15)
    basis_root = rig.data.bones["Root"].matrix_local.to_3x3()
    breath_z = 0.015 * math.sin(2.0 * sway_phase)
    rig.pose.bones["Root"].location = basis_root.inverted() @ Vector((0.0, 0.0, -1.24 + breath_z))

    # 2. Seated Legs:
    # In Armature space, leg hangs along -Z (0, 0, -1).
    # rx(-1.42) swings (0, 0, -1) forward to (0, -0.99, -0.15) (-Y is front of character!).
    # Shin bends down/back relative to thigh by rx(+1.15).
    for s, side in ((1, 'L'), (-1, 'R')):
        thigh_m = rz(-s * 0.22) @ rx(-1.45 + 0.02 * math.sin(sway_phase + s))
        shin_m  = rx(1.18 + 0.02 * math.cos(sway_phase + s))
        foot_m  = rx(-0.20)
        rotate_bone_armature_space(rig, f"Thigh.{side}", thigh_m)
        rotate_bone_armature_space(rig, f"Shin.{side}",  shin_m)
        rotate_bone_armature_space(rig, f"Foot.{side}",  foot_m)

    # 3. Gentle Continuous Upper Body Swaying (Hips, Spine, Chest)
    # ry(a) tilts torso left/right in front/back view; rx(a) leans forward/back; rz(a) turns left/right.
    sway_tilt = math.radians(6.5 * math.sin(sway_phase))
    sway_lean = math.radians(-4.0 + 2.5 * math.cos(sway_phase * 2.0))
    sway_yaw  = math.radians(5.0 * math.sin(sway_phase))

    rotate_bone_armature_space(rig, "Hips",  rx(sway_lean * 0.3) @ ry(sway_tilt * 0.3))
    rotate_bone_armature_space(rig, "Spine", rx(sway_lean * 0.5) @ ry(sway_tilt * 0.55) @ rz(sway_yaw * 0.4))
    rotate_bone_armature_space(rig, "Chest", rx(sway_lean * 0.6) @ ry(sway_tilt * 0.65) @ rz(sway_yaw * 0.6))

    # 4. Star-Pointing Gesture Envelopes:
    # - Boy points up at the stars with his Right Arm during u_norm in [0.05 .. 0.54]
    # - Girl points up at the stars with her Left Arm during u_norm in [0.46 .. 0.95]
    boy_point  = smooth_window(u_norm, 0.05, 0.17, 0.41, 0.54)
    girl_point = smooth_window(u_norm, 0.46, 0.58, 0.82, 0.95)
    star_sweep = math.sin(theta * 2.0)

    if is_boy:
        w_pt = boy_point
        w_watch = girl_point

        # Boy's Left Arm (+X rest): lowered & resting forward on his left knee
        # ry(+1.15) lowers (+1,0,0) to (+0.41, 0, -0.91); rx(-0.55) pitches it forward (-Y)
        ua_L_m = rx(-0.55 + 0.03 * math.sin(sway_phase)) @ rz(-0.25) @ ry(1.15)
        fa_L_m = rx(-0.45) @ rz(-0.35)
        rotate_bone_armature_space(rig, "UpperArm.L", ua_L_m)
        rotate_bone_armature_space(rig, "Forearm.L",  fa_L_m)

        # Boy's Right Arm (-X rest):
        # At rest (w_pt=0): ry(-1.15) lowers (-1,0,0) to (-0.41, 0, -0.91), rx(-0.55) pitches forward to knee.
        # When pointing at stars (w_pt=1):
        #   rz(+1.28) swings (-1,0,0) forward to (-0.28, -0.96, 0) (in front of Boy),
        #   rx(-0.78) pitches (0, -0.96, 0) UP by +45 deg to (-0.28, -0.68, +0.68) pointing straight up at the stars!
        ry_r = -1.15 * (1.0 - w_pt) + (0.35 + 0.12 * star_sweep) * w_pt
        rz_r =  0.25 * (1.0 - w_pt) + (1.22 + 0.15 * star_sweep) * w_pt
        rx_r = -0.55 * (1.0 - w_pt) + (-0.65 - 0.10 * star_sweep) * w_pt
        ua_R_m = rx(rx_r) @ rz(rz_r) @ ry(ry_r)

        fa_ry_r = -0.35 * (1.0 - w_pt) + (0.18 + 0.06 * star_sweep) * w_pt
        fa_rz_r =  0.35 * (1.0 - w_pt) + (0.15 + 0.05 * star_sweep) * w_pt
        fa_R_m = rz(fa_rz_r) @ ry(fa_ry_r)

        rotate_bone_armature_space(rig, "UpperArm.R", ua_R_m)
        rotate_bone_armature_space(rig, "Forearm.R",  fa_R_m)
        rotate_bone_armature_space(rig, "Hand.R",     ry(0.15 * w_pt))

        # Head & Neck: pitches up (+rx tilts +Z head back so -Y face looks up at the stars!)
        head_pitch = math.radians(10.0 + 24.0 * w_pt + 18.0 * w_watch)
        head_yaw   = math.radians(-10.0 * w_pt + 16.0 * w_watch + 5.0 * math.sin(sway_phase))
        rotate_bone_armature_space(rig, "Neck", rx(head_pitch * 0.35) @ ry(sway_tilt * 0.3) @ rz(head_yaw * 0.35))
        rotate_bone_armature_space(rig, "Head", rx(head_pitch * 0.65) @ ry(sway_tilt * 0.4) @ rz(head_yaw * 0.65))
    else:
        w_pt = girl_point
        w_watch = boy_point

        # Girl's Right Arm (-X rest): lowered & resting forward on her right knee
        ua_R_m = rx(-0.55 + 0.03 * math.cos(sway_phase)) @ rz(0.25) @ ry(-1.15)
        fa_R_m = rx(-0.45) @ rz(0.35)
        rotate_bone_armature_space(rig, "UpperArm.R", ua_R_m)
        rotate_bone_armature_space(rig, "Forearm.R",  fa_R_m)

        # Girl's Left Arm (+X rest):
        # At rest (w_pt=0): ry(+1.15) lowers (+1,0,0) to (+0.41, 0, -0.91), rx(-0.55) pitches forward.
        # When pointing at stars (w_pt=1):
        #   rz(-1.22) swings (+1,0,0) forward to (+0.34, -0.94, 0) (in front of Girl),
        #   ry(-0.38) + rx(-0.65) pitches arm UP +45 deg toward the stars!
        ry_l =  1.15 * (1.0 - w_pt) + (-0.35 - 0.12 * star_sweep) * w_pt
        rz_l = -0.25 * (1.0 - w_pt) + (-1.22 - 0.15 * star_sweep) * w_pt
        rx_l = -0.55 * (1.0 - w_pt) + (-0.65 - 0.10 * star_sweep) * w_pt
        ua_L_m = rx(rx_l) @ rz(rz_l) @ ry(ry_l)

        fa_ry_l =  0.35 * (1.0 - w_pt) + (-0.18 - 0.06 * star_sweep) * w_pt
        fa_rz_l = -0.35 * (1.0 - w_pt) + (-0.15 - 0.05 * star_sweep) * w_pt
        fa_L_m = rz(fa_rz_l) @ ry(fa_ry_l)

        rotate_bone_armature_space(rig, "UpperArm.L", ua_L_m)
        rotate_bone_armature_space(rig, "Forearm.L",  fa_L_m)
        rotate_bone_armature_space(rig, "Hand.L",     ry(-0.15 * w_pt))

        # Head, Neck & Flowing Long Hair sway
        head_pitch = math.radians(10.0 + 24.0 * w_pt + 18.0 * w_watch)
        head_yaw   = math.radians(10.0 * w_pt - 16.0 * w_watch + 5.0 * math.sin(sway_phase))
        rotate_bone_armature_space(rig, "Neck", rx(head_pitch * 0.35) @ ry(sway_tilt * 0.3) @ rz(head_yaw * 0.35))
        rotate_bone_armature_space(rig, "Head", rx(head_pitch * 0.65) @ ry(sway_tilt * 0.4) @ rz(head_yaw * 0.65))
        rotate_bone_armature_space(rig, "HairBack", rx(-head_pitch * 0.45) @ ry(-sway_tilt * 0.75))

    for pb in rig.pose.bones:
        if pb.name == "Root":
            pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)

anim_frames = sorted(set(list(range(1, PERIOD + 1, 3)) + [1, PERIOD]))
for f in anim_frames:
    u = (f - 1) / float(PERIOD - 1)
    theta = u * 2.0 * math.pi

    pose_and_keyframe_character(boy_rig,  is_boy=True,  frame=f, u_norm=u)
    pose_and_keyframe_character(girl_rig, is_boy=False, frame=f, u_norm=u)

    # Slightly animate all foreground bushes & wildflowers (soft evening breeze wave)
    for bush_obj, bphase, amp in animated_bushes:
        breeze_x = math.radians(2.8 * amp * math.sin(theta * 2.0 + bphase))
        breeze_y = math.radians(3.6 * amp * math.cos(theta * 2.0 + bphase * 1.3))
        breeze_z = math.radians(2.2 * amp * math.sin(theta * 1.0 + bphase * 0.7))
        bush_obj.rotation_euler = (breeze_x, breeze_y, breeze_z)
        bush_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Slightly animate all overarching tree leaf clusters (gentle rustling & sway)
    for leaf_obj, lphase in animated_leaves:
        flutter_x = math.radians(3.5 * math.sin(theta * 3.0 + lphase))
        flutter_y = math.radians(4.8 * math.cos(theta * 2.0 + lphase))
        flutter_z = math.radians(3.0 * math.sin(theta * 2.0 + lphase * 0.8))
        leaf_obj.rotation_euler = (flutter_x, flutter_y, flutter_z)
        leaf_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Twinkling stars in the upper sky
    for star_obj, sphase in star_objects:
        twinkle = 0.72 + 0.45 * (0.5 + 0.5 * math.sin(theta * 3.0 + sphase))
        star_obj.scale = (twinkle, twinkle, twinkle)
        star_obj.keyframe_insert(data_path="scale", frame=f)

# ---------------------------------------------------------------------------
# 7. Camera & Sunset Rim / Twilight Sky Lighting Setup
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new("Overlook_Sunset_World")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.16, 0.14, 0.28, 1.0)
    bg.inputs[1].default_value = 0.75
scene.world = world

def add_scene_light(name, ltype, loc, rot_deg, energy, color, size=3.0):
    ld = bpy.data.lights.new(name, type=ltype)
    ld.energy = energy
    ld.color = color
    if ltype == 'AREA':
        ld.size = size
    ob = bpy.data.objects.new(name, ld)
    col_stage.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    return ob

add_scene_light("Sunset_Horizon_Rim", 'AREA', (0.0, 3.5, 2.2), (-110, 0, 0), 750.0, (1.0, 0.65, 0.25), size=6.0)
add_scene_light("Twilight_Sky_Fill",  'AREA', (0.0, -5.5, 3.5), (58, 0, 0),  190.0, (0.62, 0.70, 1.0), size=5.5)
add_scene_light("Boy_Gold_Rim",       'POINT', (-0.35, -1.2, 1.2), (0, 0, 0), 120.0, (1.0, 0.62, 0.22))
add_scene_light("Girl_Gold_Rim",      'POINT', ( 0.35, -1.2, 1.2), (0, 0, 0), 120.0, (1.0, 0.62, 0.22))

cam_data = bpy.data.cameras.new("Overlook_Camera")
cam_data.lens = 34.0
cam_obj = bpy.data.objects.new("Overlook_Camera", cam_data)
col_stage.objects.link(cam_obj)
cam_obj.location = (0.0, -5.65, 1.05)
cam_obj.rotation_euler = (math.radians(85.5), 0.0, 0.0)
scene.camera = cam_obj

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'AgX'
scene.frame_set(45)

# ---------------------------------------------------------------------------
# 8. Save Blend File & Export Unity-Ready GLB + FBX to Assets/Models/Overlook
# ---------------------------------------------------------------------------
blend_out = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/Overlook_Boy_Girl_Stars.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print("Saved Blend file:", blend_out)

unity_out_dir = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Overlook"
os.makedirs(unity_out_dir, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'ARMATURE', 'MESH', 'EMPTY'}:
        obj.select_set(True)
bpy.context.view_layer.objects.active = scene_root

glb_out = os.path.join(unity_out_dir, "Overlook_Boy_Girl_Stars.glb")
bpy.ops.export_scene.gltf(
    filepath=glb_out,
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
print("Exported GLB:", glb_out)

fbx_out = os.path.join(unity_out_dir, "Overlook_Boy_Girl_Stars.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_out,
    use_selection=True,
    object_types={'ARMATURE', 'EMPTY', 'MESH'},
    add_leaf_bones=False,
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    path_mode='AUTO'
)
print("Exported FBX:", fbx_out)
