"""Build a new Blender file with the 3D MindScape3D logo and 2 animations:
1. IntroScreen Animation (3D reveal + floating motion)
2. MainMenu_GlowOnly Animation (100% stationary logo where ONLY the golden brain,
   letter rims, leaf veins, and berries pulse with a radial golden glow).

Creates two scenes in 'Blender/Blend Files/MindScape3D_Logo.blend':
- Scene 'IntroScreen':
    - Frames 1-120: Animation 1 (Intro Screen 3D reveal + living float, settling at 120)
    - Frames 121-240: Animation 2 (Main Menu Glow-Only loop, marked with timeline markers)
- Scene 'MainMenu_GlowOnly':
    - Frames 1-120: Dedicated Main Menu Glow-Only loop (100% static geometry, pulsing glow only).
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

# ---------------------------------------------------------------------------
# 1. Reset to a Clean Blender File State
# ---------------------------------------------------------------------------
base_scene = bpy.context.scene

# Remove any extra scenes first so "IntroScreen" name is never taken
for sc in list(bpy.data.scenes):
    if sc != base_scene:
        bpy.data.scenes.remove(sc)

base_scene.name = "IntroScreen"

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for c in list(bpy.data.curves):
    bpy.data.curves.remove(c)
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
scene.frame_start = 1
scene.frame_end = 240
scene.render.fps = 24

# Clear existing timeline markers and add clear markers for the 2 animations
scene.timeline_markers.clear()
m1 = scene.timeline_markers.new("1_IntroScreen (1-120)", frame=1)
m2 = scene.timeline_markers.new("2_MainMenu_GlowOnly (121-240)", frame=121)

def make_col(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

col_root = make_col("Logo | Root")
col_text = make_col("Logo | Typography")
col_brain = make_col("Logo | Brain & Tree")
col_flora = make_col("Logo | Botanical Leaves")
col_stage = make_col("Logo | Lighting & Camera")

logo_root = bpy.data.objects.new("MindScape3D_Root", None)
col_root.objects.link(logo_root)
logo_root.location = (0, 0, 0)

# ---------------------------------------------------------------------------
# 2. PBR & Emissive Materials
# ---------------------------------------------------------------------------
def create_mat(name, base_color, metallic=0.0, roughness=0.4,
               emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*base_color, 1.0)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission_color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

# Deep midnight obsidian-navy for main letter front faces & brain outer contour
mat_navy = create_mat(
    "MS | Midnight Navy",
    base_color=(0.010, 0.025, 0.065),
    metallic=0.45,
    roughness=0.18,
    emission_color=(0.008, 0.020, 0.050),
    emission_strength=0.08
)

# Deep obsidian shadow backing for maximum silhouette contrast against bright sunset skies
mat_shadow = create_mat(
    "MS | Obsidian Shadow Backing",
    base_color=(0.005, 0.010, 0.025),
    metallic=0.15,
    roughness=0.50,
    emission_color=(0.003, 0.006, 0.015),
    emission_strength=0.04
)

# Radiant Imperial Champagne Gold for letter bevels/outlines, leaf rims, and accents (high specular pop)
mat_gold = create_mat(
    "MS | Metallic Gold Rim",
    base_color=(1.00, 0.82, 0.28),
    metallic=0.92,
    roughness=0.14,
    emission_color=(1.00, 0.85, 0.35),
    emission_strength=0.75
)

# Bright warm gold for berries
mat_berry_gold = create_mat(
    "MS | Golden Berry",
    base_color=(1.00, 0.84, 0.22),
    metallic=0.60,
    roughness=0.15,
    emission_color=(1.00, 0.88, 0.28),
    emission_strength=1.60
)

# Rich dark forest charcoal for subtitle text
mat_subtitle = create_mat(
    "MS | Forest Charcoal",
    base_color=(0.012, 0.038, 0.022),
    metallic=0.25,
    roughness=0.30
)

# Tree trunk & neural branches (warm dark bronze-mahogany wood with crisp specular)
mat_trunk = create_mat(
    "MS | Tree Trunk Bronze",
    base_color=(0.14, 0.050, 0.018),
    metallic=0.20,
    roughness=0.32,
    emission_color=(0.32, 0.12, 0.03),
    emission_strength=0.20
)

# Dark espresso-bronze for brain sulcus creases
mat_sulcus = create_mat(
    "MS | Brain Sulcus Crease",
    base_color=(0.08, 0.030, 0.012),
    roughness=0.40,
    emission_color=(0.18, 0.065, 0.020),
    emission_strength=0.10
)

# Brain Glowing Tiers: High-contrast palette designed specifically against sunset peach/sky colors
# Sun Core -> Warm Saturated Amber-Gold Mid -> Rich Sunset Coral-Amber Outer (NOT pale peach!)
mat_brain_core = create_mat(
    "MS | Brain Core Glow",
    base_color=(1.00, 0.96, 0.62),
    roughness=0.16,
    emission_color=(1.00, 0.94, 0.55),
    emission_strength=3.8
)

mat_brain_mid = create_mat(
    "MS | Brain Mid Amber",
    base_color=(1.00, 0.65, 0.16),
    roughness=0.22,
    emission_color=(1.00, 0.62, 0.18),
    emission_strength=2.2
)

mat_brain_outer = create_mat(
    "MS | Brain Outer Sunset Amber",
    base_color=(0.88, 0.38, 0.16),
    roughness=0.26,
    emission_color=(0.92, 0.42, 0.18),
    emission_strength=1.4
)

# Botanical Olive Leaf Materials (Deep Emerald with Golden Accents)
mat_leaf_blade = create_mat(
    "MS | Olive Leaf",
    base_color=(0.06, 0.18, 0.04),
    metallic=0.08,
    roughness=0.28,
    emission_color=(0.08, 0.20, 0.05),
    emission_strength=0.22
)

mat_leaf_stem = create_mat(
    "MS | Leaf Stem",
    base_color=(0.22, 0.16, 0.05),
    metallic=0.25,
    roughness=0.35
)

# ---------------------------------------------------------------------------
# 3. Font Loading Helper
# ---------------------------------------------------------------------------
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
if not os.path.exists(FONT_BOLD_PATH):
    FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"

font_bold = bpy.data.fonts.load(FONT_BOLD_PATH) if os.path.exists(FONT_BOLD_PATH) else None

# ---------------------------------------------------------------------------
# 4. Single-Mesh Beveled 3D Text Builder (Front Face vs Gold Bevel/Side Rim)
# ---------------------------------------------------------------------------
def create_3d_text_mesh(name, body, size, extrude=0.11, bevel_depth=0.028,
                        font=font_bold, front_mat=mat_navy, rim_mat=mat_gold,
                        space_character=0.98, strip_i_dot=False, front_z_thresh=0.88):
    cu = bpy.data.curves.new(name + "_Curve", type='FONT')
    cu.body = body
    if font:
        cu.font = font
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel_depth
    cu.bevel_resolution = 4
    cu.align_x = 'LEFT'
    cu.align_y = 'BOTTOM_BASELINE'
    cu.space_character = space_character

    tmp_obj = bpy.data.objects.new(name + "_tmp", cu)
    col_text.objects.link(tmp_obj)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = tmp_obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj)
    mesh.name = name + "_Mesh"
    bpy.data.objects.remove(tmp_obj, do_unlink=True)
    bpy.data.curves.remove(cu)

    dot_center = None
    if strip_i_dot:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        to_del = [v for v in bm.verts if v.co.y > size * 0.39 and v.co.x < size * 0.25]
        if to_del:
            avg_x = sum(v.co.x for v in to_del) / len(to_del)
            avg_y = sum(v.co.y for v in to_del) / len(to_del)
            dot_center = (avg_x, avg_y)
            bmesh.ops.delete(bm, geom=to_del, context='VERTS')
            bm.to_mesh(mesh)
            mesh.update()
        bm.free()

    mesh.materials.clear()
    mesh.materials.append(front_mat)  # slot 0: Front/Back face (Midnight Navy)
    mesh.materials.append(rim_mat)    # slot 1: Bevel & Side Rim (Metallic Gold)

    for poly in mesh.polygons:
        if poly.normal.z > front_z_thresh:
            poly.material_index = 0
        else:
            poly.material_index = 1

    xs = [v.co.x for v in mesh.vertices]
    min_x = min(xs) if xs else 0.0
    max_x = max(xs) if xs else 0.0
    return mesh, min_x, max_x, dot_center

title_anchor = bpy.data.objects.new("Title_MindScape3D", None)
col_text.objects.link(title_anchor)
title_anchor.parent = logo_root
title_anchor.location = (0, 0, 0)

raw_segments = [
    ("Char_M",      "M",      1.85, 0.04, False, 0),
    ("Char_ind",    "ind",    1.62, 0.05, True,  3),
    ("Char_S",      "S",      1.82, 0.04, False, 6),
    ("Char_cape3D", "cape3D", 1.62, 0.00, False, 9),
]

built_segments = []
for sname, sbody, ssize, kern, strip_dot, delay in raw_segments:
    mesh, min_x, max_x, dot_c = create_3d_text_mesh(
        sname, sbody, size=ssize, extrude=0.11, bevel_depth=0.028,
        font=font_bold, front_mat=mat_navy, rim_mat=mat_gold,
        space_character=0.97, strip_i_dot=strip_dot, front_z_thresh=0.88
    )
    built_segments.append({
        "name": sname, "body": sbody, "size": ssize, "strip_dot": strip_dot,
        "mesh": mesh, "min_x": min_x, "max_x": max_x,
        "width": max_x - min_x, "kern": kern, "dot_c": dot_c, "delay": delay
    })

total_title_w = sum(s["width"] + s["kern"] for s in built_segments)
cursor_x = -total_title_w / 2.0

title_groups = []
i_dot_world_xz = (-2.68, 0.86)
s_center_x = 0.0
m_left_x = cursor_x
right_end_x = total_title_w / 2.0

for s in built_segments:
    grp = bpy.data.objects.new(s["name"] + "_Anchor", None)
    col_text.objects.link(grp)
    grp.parent = title_anchor
    seg_center_x = cursor_x + s["width"] / 2.0
    grp.location = (seg_center_x, 0.0, 0.0)

    obj = bpy.data.objects.new(s["name"], s["mesh"])
    col_text.objects.link(obj)
    obj.parent = grp
    local_shift_x = -(s["min_x"] + s["max_x"]) / 2.0
    obj.location = (local_shift_x, 0.0, 0.0)
    obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

    # Dark silhouette backing mesh to sharply frame the letters against bright sunset background
    sh_mesh, _, _, _ = create_3d_text_mesh(
        s["name"] + "_Shadow", s["body"], size=s["size"], extrude=0.14, bevel_depth=0.040,
        font=font_bold, front_mat=mat_shadow, rim_mat=mat_shadow,
        space_character=0.97, strip_i_dot=s["strip_dot"], front_z_thresh=0.5
    )
    sh_obj = bpy.data.objects.new(s["name"] + "_Shadow", sh_mesh)
    col_text.objects.link(sh_obj)
    sh_obj.parent = grp
    sh_obj.location = (local_shift_x, 0.032, 0.0)
    sh_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

    if s["dot_c"] is not None:
        i_dot_world_xz = (seg_center_x + local_shift_x + s["dot_c"][0], s["dot_c"][1])
    if s["name"] == "Char_S":
        s_center_x = seg_center_x

    cursor_x += s["width"] + s["kern"]
    title_groups.append((grp, s["delay"]))

# Subtitle: "Face Your Fear, Find Your Strength."
sub_mesh_L, smin_L, smax_L, _ = create_3d_text_mesh(
    "Subtitle_Left", "Face Your Fear, Find", size=0.48, extrude=0.05, bevel_depth=0.006,
    font=font_bold, front_mat=mat_subtitle, rim_mat=mat_subtitle, space_character=0.97, front_z_thresh=0.5
)
sub_mesh_R, smin_R, smax_R, _ = create_3d_text_mesh(
    "Subtitle_Right", "Your Strength.", size=0.48, extrude=0.05, bevel_depth=0.006,
    font=font_bold, front_mat=mat_subtitle, rim_mat=mat_subtitle, space_character=0.97, front_z_thresh=0.5
)

sub_left = bpy.data.objects.new("Subtitle_Left_Anchor", None)
col_text.objects.link(sub_left)
sub_left.parent = logo_root
sub_left.location = (0.58 - smax_L, 0.0, -0.60)
sub_left_obj = bpy.data.objects.new("Subtitle_Left", sub_mesh_L)
col_text.objects.link(sub_left_obj)
sub_left_obj.parent = sub_left
sub_left_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

sub_right = bpy.data.objects.new("Subtitle_Right_Anchor", None)
col_text.objects.link(sub_right)
sub_right.parent = logo_root
sub_right.location = (1.02 - smin_R, 0.0, -0.60)
sub_right_obj = bpy.data.objects.new("Subtitle_Right", sub_mesh_R)
col_text.objects.link(sub_right_obj)
sub_right_obj.parent = sub_right
sub_right_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

# ---------------------------------------------------------------------------
# 5. Custom 3D Botanical Leaf & Berry Builders (Broad Blade Facing Camera -Y)
# ---------------------------------------------------------------------------
def build_leaf_mesh_data(name="LeafMesh"):
    mesh = bpy.data.meshes.new(name)
    mesh.materials.append(mat_leaf_blade)  # slot 0: green leaf blade
    mesh.materials.append(mat_gold)        # slot 1: golden rim & central midrib vein

    bm = bmesh.new()
    stations = [
        (0.00, 0.022,  0.000),
        (0.15, 0.145, -0.015),
        (0.35, 0.250, -0.026),
        (0.55, 0.265, -0.028),
        (0.75, 0.195, -0.018),
        (0.90, 0.090, -0.006),
        (1.00, 0.008,  0.008),
    ]
    rows_top = []
    rows_bot = []
    thick = 0.028
    for z, hw, ya in stations:
        xs = [-hw, -hw * 0.86, -hw * 0.45, 0.0, hw * 0.45, hw * 0.86, hw]
        ys_offset = [0.012, 0.008, 0.0, -0.010, 0.0, 0.008, 0.012]
        row_t = []
        row_b = []
        for x, yo in zip(xs, ys_offset):
            vt = bm.verts.new((x, ya + yo - thick * 0.5, z))
            vb = bm.verts.new((x, ya + yo + thick * 0.5, z))
            row_t.append(vt)
            row_b.append(vb)
        rows_top.append(row_t)
        rows_bot.append(row_b)

    for i in range(len(stations) - 1):
        for j in range(6):
            f_top = bm.faces.new((rows_top[i][j], rows_top[i][j+1], rows_top[i+1][j+1], rows_top[i+1][j]))
            f_bot = bm.faces.new((rows_bot[i+1][j], rows_bot[i+1][j+1], rows_bot[i][j+1], rows_bot[i][j]))
            f_top.smooth = True
            f_bot.smooth = True
            mat_idx = 1 if j in (0, 5) else 0
            f_top.material_index = mat_idx
            f_bot.material_index = mat_idx

        f_rim_l = bm.faces.new((rows_bot[i][0], rows_top[i][0], rows_top[i+1][0], rows_bot[i+1][0]))
        f_rim_r = bm.faces.new((rows_top[i][6], rows_bot[i][6], rows_bot[i+1][6], rows_top[i+1][6]))
        f_rim_l.material_index = 1
        f_rim_r.material_index = 1
        f_rim_l.smooth = True
        f_rim_r.smooth = True

    for i in range(len(stations) - 1):
        z0, _, ya0 = stations[i]
        z1, _, ya1 = stations[i+1]
        vw = 0.018 * (1.0 - 0.60 * (i / len(stations)))
        v0 = bm.verts.new((-vw, ya0 - 0.028, z0))
        v1 = bm.verts.new(( vw, ya0 - 0.028, z0))
        v2 = bm.verts.new(( vw, ya1 - 0.028, z1))
        v3 = bm.verts.new((-vw, ya1 - 0.028, z1))
        fv = bm.faces.new((v0, v1, v2, v3))
        fv.material_index = 1
        fv.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh

SHARED_LEAF_MESH = build_leaf_mesh_data("MS_Shared_Leaf")

def spawn_leaf_2d(name, loc, angle_deg_in_xz, scale, parent, tilt_y_deg=8.0, col=col_flora):
    leaf_mesh = SHARED_LEAF_MESH.copy()
    leaf_mesh.name = name + "_Mesh"
    obj = bpy.data.objects.new(name, leaf_mesh)
    col.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = Euler((
        math.radians(tilt_y_deg),
        math.radians(-angle_deg_in_xz),
        0.0
    ), 'XYZ')
    if isinstance(scale, (int, float)):
        obj.scale = (scale, scale, scale)
    else:
        obj.scale = scale
    return obj

def spawn_sphere(name, loc, radius, mat, parent, col=col_flora, scale=(1, 1, 1)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=radius)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.scale = scale
    return obj

def create_curve_branch(name, points_with_radii, mat, parent, col=col_flora, resolution=8):
    cu = bpy.data.curves.new(name + "_Curve", type='CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 5
    cu.resolution_u = resolution
    cu.use_fill_caps = True

    spline = cu.splines.new('BEZIER')
    spline.bezier_points.add(len(points_with_radii) - 1)
    for idx, (x, y, z, r) in enumerate(points_with_radii):
        bp = spline.bezier_points[idx]
        bp.co = (x, y, z)
        bp.radius = r
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    tmp_obj = bpy.data.objects.new(name + "_tmp", cu)
    col.objects.link(tmp_obj)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = tmp_obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj)
    mesh.name = name + "_Mesh"
    bpy.data.objects.remove(tmp_obj, do_unlink=True)
    bpy.data.curves.remove(cu)

    mesh.materials.clear()
    mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.parent = parent
    return obj

# ---------------------------------------------------------------------------
# 6. Dot of 'i' + Sprouting Leaves (Directly Over the 'i' Stem)
# ---------------------------------------------------------------------------
i_dot_anchor = bpy.data.objects.new("I_Dot_Sprout", None)
col_flora.objects.link(i_dot_anchor)
i_dot_anchor.parent = logo_root
i_dot_anchor.location = (i_dot_world_xz[0], -0.05, i_dot_world_xz[1] + 0.04)

spawn_sphere("I_Dot_Navy", (0, -0.02, 0), 0.145, mat_navy, i_dot_anchor, scale=(1.0, 0.65, 1.0))
spawn_sphere("I_Dot_GoldRim", (0, 0.01, 0), 0.168, mat_gold, i_dot_anchor, scale=(1.0, 0.55, 1.0))

spawn_leaf_2d("I_Leaf_Main", (0.04, -0.02, 0.08), angle_deg_in_xz=-38, scale=0.68, parent=i_dot_anchor)
spawn_leaf_2d("I_Leaf_Side", (-0.04, -0.03, 0.09), angle_deg_in_xz=10,  scale=0.42, parent=i_dot_anchor)

# ---------------------------------------------------------------------------
# 7. The Glowing 3D Brain Canopy & Tree Growing Seamlessly from 'S'
# ---------------------------------------------------------------------------
brain_tree_anchor = bpy.data.objects.new("Brain_Tree_Assembly", None)
col_brain.objects.link(brain_tree_anchor)
brain_tree_anchor.parent = logo_root
BRAIN_X = s_center_x + 0.06
BRAIN_Z = 1.84
brain_tree_anchor.location = (BRAIN_X, 0.0, BRAIN_Z)

brain_canopy = bpy.data.objects.new("Brain_Canopy_Lobes", None)
col_brain.objects.link(brain_canopy)
brain_canopy.parent = brain_tree_anchor
brain_canopy.location = (0, 0, 0)

# Dedicated static radiant gold material for Unity-native 3D Glow Wave domes
mat_unity_glow_core = create_mat(
    "MS | Radiant Sun Glow Core",
    base_color=(1.00, 0.96, 0.68),
    metallic=0.05,
    roughness=0.15,
    emission_color=(1.00, 0.90, 0.48),
    emission_strength=5.5
)
mat_unity_glow_mid = create_mat(
    "MS | Radiant Sun Glow Mid",
    base_color=(1.00, 0.88, 0.52),
    metallic=0.05,
    roughness=0.18,
    emission_color=(1.00, 0.82, 0.38),
    emission_strength=3.8
)
mat_unity_glow_outer = create_mat(
    "MS | Radiant Sun Glow Outer",
    base_color=(1.00, 0.82, 0.56),
    metallic=0.05,
    roughness=0.22,
    emission_color=(1.00, 0.76, 0.42),
    emission_strength=2.6
)

glow_wave_core_pivot = bpy.data.objects.new("Glow_Wave_Core", None)
col_brain.objects.link(glow_wave_core_pivot)
glow_wave_core_pivot.parent = brain_canopy

glow_wave_mid_pivot = bpy.data.objects.new("Glow_Wave_Mid", None)
col_brain.objects.link(glow_wave_mid_pivot)
glow_wave_mid_pivot.parent = brain_canopy

glow_wave_outer_pivot = bpy.data.objects.new("Glow_Wave_Outer", None)
col_brain.objects.link(glow_wave_outer_pivot)
glow_wave_outer_pivot.parent = brain_canopy

spawn_sphere(
    "Brain_Interior_Backing", (0.0, 0.03, 0.14),
    1.0, mat_brain_mid, brain_canopy, col=col_brain,
    scale=(1.05, 0.16, 0.66)
)

outer_lobe_ring = [
    (-1.02, -0.34, 0.28, 0.20, 0.23),
    ( 1.02, -0.34, 0.28, 0.20, 0.23),
    (-1.14, -0.08, 0.29, 0.22, 0.25),
    ( 1.14, -0.08, 0.29, 0.22, 0.25),
    (-1.10,  0.22, 0.30, 0.23, 0.26),
    ( 1.10,  0.22, 0.30, 0.23, 0.26),
    (-0.90,  0.50, 0.30, 0.24, 0.27),
    ( 0.90,  0.50, 0.30, 0.24, 0.27),
    (-0.60,  0.72, 0.31, 0.24, 0.27),
    ( 0.60,  0.72, 0.31, 0.24, 0.27),
    (-0.24,  0.82, 0.30, 0.24, 0.27),
    ( 0.24,  0.82, 0.30, 0.24, 0.27),
    (-0.68, -0.46, 0.27, 0.18, 0.20),
    ( 0.68, -0.46, 0.27, 0.18, 0.20),
]

for idx, (dx, dz, rx, ry, rz) in enumerate(outer_lobe_ring):
    # Deep obsidian silhouette shell (frames the entire outer contour against bright sunset skies)
    spawn_sphere(
        f"Brain_Shell_Shadow_{idx}", (dx * 1.06, 0.09, dz * 1.05),
        1.0, mat_shadow, brain_canopy, col=col_brain,
        scale=(rx + 0.110, ry * 0.72, rz + 0.110)
    )
    # Gleaming metallic gold contour rim
    spawn_sphere(
        f"Brain_Shell_Gold_{idx}", (dx * 1.04, 0.05, dz * 1.03),
        1.0, mat_gold, brain_canopy, col=col_brain,
        scale=(rx + 0.075, ry * 0.75, rz + 0.075)
    )
    # Rich sunset coral-amber outer lobes (high contrast against pale peach sky)
    spawn_sphere(
        f"Brain_Lobe_Outer_{idx}", (dx, -0.01, dz),
        1.0, mat_brain_outer, brain_canopy, col=col_brain,
        scale=(rx, ry, rz)
    )
    spawn_sphere(
        f"Brain_GlowDome_Outer_{idx}", (dx, -0.01, dz),
        1.0, mat_unity_glow_outer, glow_wave_outer_pivot, col=col_brain,
        scale=(rx * 0.95, ry * 1.12, rz * 0.95)
    )

mid_lobe_ring = [
    (-0.74, -0.18, 0.28, 0.22, 0.22),
    ( 0.74, -0.18, 0.28, 0.22, 0.22),
    (-0.78,  0.14, 0.29, 0.23, 0.24),
    ( 0.78,  0.14, 0.29, 0.23, 0.24),
    (-0.56,  0.42, 0.29, 0.23, 0.24),
    ( 0.56,  0.42, 0.29, 0.23, 0.24),
    (-0.26,  0.56, 0.27, 0.23, 0.23),
    ( 0.26,  0.56, 0.27, 0.23, 0.23),
    (-0.44, -0.22, 0.26, 0.21, 0.21),
    ( 0.44, -0.22, 0.26, 0.21, 0.21),
    (-0.48,  0.12, 0.28, 0.22, 0.24),
    ( 0.48,  0.12, 0.28, 0.22, 0.24),
]
for idx, (dx, dz, rx, ry, rz) in enumerate(mid_lobe_ring):
    spawn_sphere(
        f"Brain_Sulcus_Mid_{idx}", (dx, -0.02, dz),
        1.0, mat_sulcus, brain_canopy, col=col_brain,
        scale=(rx + 0.025, ry * 0.90, rz + 0.025)
    )
    spawn_sphere(
        f"Brain_Lobe_Mid_{idx}", (dx, -0.06, dz),
        1.0, mat_brain_mid, brain_canopy, col=col_brain,
        scale=(rx, ry, rz)
    )
    spawn_sphere(
        f"Brain_GlowDome_Mid_{idx}", (dx, -0.06, dz),
        1.0, mat_unity_glow_mid, glow_wave_mid_pivot, col=col_brain,
        scale=(rx * 0.95, ry * 1.12, rz * 0.95)
    )

core_lobes = [
    ( 0.00,  0.14, 0.40, 0.28, 0.36),
    (-0.24,  0.22, 0.30, 0.26, 0.28),
    ( 0.24,  0.22, 0.30, 0.26, 0.28),
    ( 0.00, -0.10, 0.30, 0.24, 0.26),
]
for idx, (dx, dz, rx, ry, rz) in enumerate(core_lobes):
    spawn_sphere(
        f"Brain_Lobe_Core_{idx}", (dx, -0.09, dz),
        1.0, mat_brain_core, brain_canopy, col=col_brain,
        scale=(rx, ry, rz)
    )
    spawn_sphere(
        f"Brain_GlowDome_Core_{idx}", (dx, -0.09, dz),
        1.0, mat_unity_glow_core, glow_wave_core_pivot, col=col_brain,
        scale=(rx * 0.96, ry * 1.12, rz * 0.96)
    )

core_light_data = bpy.data.lights.new("Brain_Core_Light", type='POINT')
core_light_data.color = (1.0, 0.80, 0.32)
core_light_data.energy = 90.0
core_light_data.shadow_soft_size = 0.5
core_light = bpy.data.objects.new("Brain_Core_Light", core_light_data)
col_brain.objects.link(core_light)
core_light.parent = brain_tree_anchor
core_light.location = (0.0, -0.35, 0.08)

tree_branches_anchor = bpy.data.objects.new("Tree_Neural_Branches", None)
col_brain.objects.link(tree_branches_anchor)
tree_branches_anchor.parent = brain_tree_anchor
tree_branches_anchor.location = (0, 0, 0)

branch_definitions = [
    ("Trunk_Main_L", [
        (-0.02, -0.16, -0.94, 0.095),
        (-0.01, -0.24, -0.56, 0.078),
        (-0.06, -0.28, -0.18, 0.056),
        (-0.16, -0.29,  0.24, 0.036),
        (-0.24, -0.27,  0.68, 0.016),
    ]),
    ("Trunk_Main_R", [
        ( 0.02, -0.16, -0.94, 0.095),
        ( 0.03, -0.24, -0.54, 0.078),
        ( 0.08, -0.28, -0.16, 0.054),
        ( 0.18, -0.29,  0.26, 0.035),
        ( 0.26, -0.27,  0.68, 0.016),
    ]),
    ("Branch_L_Upper", [
        (-0.03, -0.25, -0.44, 0.062),
        (-0.26, -0.28, -0.12, 0.045),
        (-0.52, -0.28,  0.24, 0.028),
        (-0.68, -0.25,  0.58, 0.014),
    ]),
    ("Branch_L_Mid", [
        (-0.26, -0.28, -0.12, 0.042),
        (-0.64, -0.27,  0.04, 0.028),
        (-0.98, -0.24,  0.20, 0.014),
    ]),
    ("Branch_L_Lower", [
        (-0.04, -0.23, -0.54, 0.056),
        (-0.40, -0.26, -0.36, 0.040),
        (-0.78, -0.25, -0.24, 0.024),
        (-1.04, -0.22, -0.10, 0.013),
    ]),
    ("Twig_L_1", [
        (-0.52, -0.28,  0.24, 0.024),
        (-0.84, -0.25,  0.42, 0.013),
    ]),
    ("Twig_L_2", [
        (-0.40, -0.26, -0.36, 0.026),
        (-0.68, -0.23, -0.42, 0.013),
    ]),
    ("Twig_L_3", [
        (-0.16, -0.29,  0.24, 0.024),
        (-0.42, -0.26,  0.52, 0.013),
    ]),
    ("Branch_R_Upper", [
        ( 0.04, -0.25, -0.44, 0.062),
        ( 0.28, -0.28, -0.10, 0.045),
        ( 0.54, -0.28,  0.24, 0.028),
        ( 0.70, -0.25,  0.58, 0.014),
    ]),
    ("Branch_R_Mid", [
        ( 0.28, -0.28, -0.10, 0.042),
        ( 0.66, -0.27,  0.04, 0.028),
        ( 1.00, -0.24,  0.20, 0.014),
    ]),
    ("Branch_R_Lower", [
        ( 0.05, -0.23, -0.54, 0.056),
        ( 0.42, -0.26, -0.34, 0.040),
        ( 0.80, -0.25, -0.22, 0.024),
        ( 1.06, -0.22, -0.08, 0.013),
    ]),
    ("Twig_R_1", [
        ( 0.54, -0.28,  0.24, 0.024),
        ( 0.86, -0.25,  0.42, 0.013),
    ]),
    ("Twig_R_2", [
        ( 0.42, -0.26, -0.34, 0.026),
        ( 0.70, -0.23, -0.40, 0.013),
    ]),
    ("Twig_R_3", [
        ( 0.18, -0.29,  0.26, 0.024),
        ( 0.44, -0.26,  0.52, 0.013),
    ]),
]

for bname, bpts in branch_definitions:
    create_curve_branch(bname, bpts, mat_trunk, tree_branches_anchor, col=col_brain)

# ---------------------------------------------------------------------------
# 8. Botanical Sprigs: Brain Flanks & Bottom-Left / Bottom-Right Laurel Branches
# ---------------------------------------------------------------------------
sprig_brain_L = bpy.data.objects.new("Sprig_Brain_Left", None)
col_flora.objects.link(sprig_brain_L)
sprig_brain_L.parent = brain_tree_anchor
sprig_brain_L.location = (-1.08, -0.04, -0.40)

create_curve_branch("Stem_Brain_L", [
    ( 0.18, 0.0, -0.06, 0.025),
    (-0.22, 0.0,  0.05, 0.020),
    (-0.56, 0.0,  0.32, 0.014),
], mat_leaf_stem, sprig_brain_L)

spawn_leaf_2d("Brain_L_Leaf1", (-0.28, -0.02,  0.10), angle_deg_in_xz=38,  scale=0.78, parent=sprig_brain_L)
spawn_leaf_2d("Brain_L_Leaf2", (-0.20, -0.01, -0.02), angle_deg_in_xz=76,  scale=0.62, parent=sprig_brain_L)
spawn_leaf_2d("Brain_L_Leaf3", (-0.02, -0.02, -0.08), angle_deg_in_xz=115, scale=0.46, parent=sprig_brain_L)
spawn_sphere("Brain_L_Berry1", (-0.36, -0.03, -0.10), 0.065, mat_berry_gold, sprig_brain_L)
spawn_sphere("Brain_L_Berry2", (-0.14, -0.03, -0.18), 0.052, mat_berry_gold, sprig_brain_L)

sprig_brain_R = bpy.data.objects.new("Sprig_Brain_Right", None)
col_flora.objects.link(sprig_brain_R)
sprig_brain_R.parent = brain_tree_anchor
sprig_brain_R.location = (1.08, -0.04, -0.40)

create_curve_branch("Stem_Brain_R", [
    (-0.18, 0.0, -0.06, 0.025),
    ( 0.22, 0.0,  0.05, 0.020),
    ( 0.56, 0.0,  0.32, 0.014),
], mat_leaf_stem, sprig_brain_R)

spawn_leaf_2d("Brain_R_Leaf1", ( 0.28, -0.02,  0.10), angle_deg_in_xz=-38,  scale=0.78, parent=sprig_brain_R)
spawn_leaf_2d("Brain_R_Leaf2", ( 0.20, -0.01, -0.02), angle_deg_in_xz=-76,  scale=0.62, parent=sprig_brain_R)
spawn_leaf_2d("Brain_R_Leaf3", ( 0.02, -0.02, -0.08), angle_deg_in_xz=-115, scale=0.46, parent=sprig_brain_R)
spawn_sphere("Brain_R_Berry1", ( 0.20, -0.03, -0.18), 0.065, mat_berry_gold, sprig_brain_R)
spawn_sphere("Brain_R_Berry2", ( 0.36, -0.03, -0.10), 0.052, mat_berry_gold, sprig_brain_R)

sprig_bot_L = bpy.data.objects.new("Sprig_Bottom_Left", None)
col_flora.objects.link(sprig_bot_L)
sprig_bot_L.parent = logo_root
sprig_bot_L.location = (m_left_x - 0.05, -0.04, -0.22)

create_curve_branch("Stem_Bottom_L", [
    ( 0.88, 0.0, -0.60, 0.030),
    ( 0.36, 0.0, -0.26, 0.025),
    (-0.18, 0.0,  0.12, 0.020),
    (-0.65, 0.0,  0.56, 0.015),
    (-0.96, 0.0,  0.94, 0.010),
], mat_leaf_stem, sprig_bot_L)

bot_L_leaves = [
    ((-0.68, -0.02,  0.56), 34, 0.72),
    ((-0.52, -0.02,  0.34), 68, 0.60),
    ((-0.26, -0.01,  0.20), 12, 0.54),
    ((-0.24, -0.02,  0.04), 78, 0.58),
    (( 0.08, -0.01, -0.06),  5, 0.52),
    (( 0.10, -0.02, -0.22), 82, 0.54),
    (( 0.42, -0.01, -0.24), -8, 0.52),
    (( 0.40, -0.02, -0.44), 72, 0.48),
]
for idx, (lloc, lang, lsc) in enumerate(bot_L_leaves):
    spawn_leaf_2d(f"Bot_L_Leaf_{idx}", lloc, angle_deg_in_xz=lang, scale=lsc, parent=sprig_bot_L)

for idx, bloc in enumerate([
    (0.02, -0.03, -0.14),
    (0.20, -0.03, -0.36),
    (0.36, -0.03, -0.50),
]):
    spawn_sphere(f"Bot_L_Berry_{idx}", bloc, 0.058, mat_berry_gold, sprig_bot_L)

sprig_bot_R = bpy.data.objects.new("Sprig_Bottom_Right", None)
col_flora.objects.link(sprig_bot_R)
sprig_bot_R.parent = logo_root
sprig_bot_R.location = (right_end_x - 0.15, -0.04, -0.54)

create_curve_branch("Stem_Bottom_R", [
    (-0.46, 0.0, -0.28, 0.028),
    (-0.10, 0.0, -0.04, 0.022),
    ( 0.28, 0.0,  0.18, 0.016),
    ( 0.62, 0.0,  0.34, 0.010),
], mat_leaf_stem, sprig_bot_R)

bot_R_leaves = [
    ((-0.18, -0.01, -0.06),  -12, 0.52),
    (( 0.05, -0.01,  0.08),  -28, 0.54),
    (( 0.30, -0.02,  0.16),  -64, 0.64),
    (( 0.16, -0.02, -0.06),  -98, 0.52),
    ((-0.05, -0.02, -0.18), -125, 0.54),
]
for idx, (lloc, lang, lsc) in enumerate(bot_R_leaves):
    spawn_leaf_2d(f"Bot_R_Leaf_{idx}", lloc, angle_deg_in_xz=lang, scale=lsc, parent=sprig_bot_R)

for idx, bloc in enumerate([
    (0.06, -0.03, 0.14),
    (0.26, -0.03, -0.10),
]):
    spawn_sphere(f"Bot_R_Berry_{idx}", bloc, 0.056, mat_berry_gold, sprig_bot_R)

# ---------------------------------------------------------------------------
# 9. Studio Lighting, World Backdrop & Camera Setup
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new("MS_Studio_World")
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.97, 0.96, 0.94, 1.0)
    bg_node.inputs[1].default_value = 0.95
scene.world = world

def add_light(name, ltype, loc, rot_deg, energy, color=(1.0, 1.0, 1.0), size=2.0):
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

add_light("Key_Light", 'AREA', (-4.5, -7.5, 4.5), (58, 0, -28), 320.0, (1.0, 0.96, 0.88), size=4.0)
add_light("Fill_Light", 'AREA', (5.5, -6.5, 2.0), (72, 0, 35), 180.0, (0.85, 0.92, 1.0), size=4.5)
add_light("Rim_Light", 'AREA', (0.0, 3.5, 5.0), (-135, 0, 0), 260.0, (1.0, 0.88, 0.65), size=5.0)

cam_data = bpy.data.cameras.new("Logo_Camera")
cam_data.lens = 42.0
cam_data.show_background_images = True
bg_menu_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Resources/MenuArt/Background3D.png"
if os.path.exists(bg_menu_path):
    bg_slot = cam_data.background_images.new()
    bg_slot.image = bpy.data.images.load(bg_menu_path)
    bg_slot.display_depth = 'BACK'
    bg_slot.frame_method = 'CROP'
    bg_slot.alpha = 1.0
cam_obj = bpy.data.objects.new("Logo_Camera", cam_data)
col_stage.objects.link(cam_obj)
cam_obj.location = (0.0, -12.4, 0.82)
cam_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
scene.camera = cam_obj

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# ---------------------------------------------------------------------------
# 10. ANIMATION 1: IntroScreen (Frames 1-120)
# ---------------------------------------------------------------------------
def keyframe_pop_in(obj, start_frame, end_frame, start_z_offset=-0.45, start_rot_x=0.35):
    final_loc = obj.location.copy()
    final_rot = obj.rotation_euler.copy()
    final_scale = obj.scale.copy()

    scene.frame_set(1)
    obj.scale = (0.001, 0.001, 0.001)
    obj.location = (final_loc.x, final_loc.y, final_loc.z + start_z_offset)
    obj.rotation_euler = (final_rot.x + start_rot_x, final_rot.y, final_rot.z)
    obj.keyframe_insert(data_path="scale", frame=max(1, start_frame))
    obj.keyframe_insert(data_path="location", frame=max(1, start_frame))
    obj.keyframe_insert(data_path="rotation_euler", frame=max(1, start_frame))

    mid_f = int(start_frame + (end_frame - start_frame) * 0.72)
    obj.scale = (final_scale.x * 1.06, final_scale.y * 1.06, final_scale.z * 1.06)
    obj.location = (final_loc.x, final_loc.y, final_loc.z + 0.04)
    obj.rotation_euler = final_rot
    obj.keyframe_insert(data_path="scale", frame=mid_f)
    obj.keyframe_insert(data_path="location", frame=mid_f)
    obj.keyframe_insert(data_path="rotation_euler", frame=mid_f)

    obj.scale = final_scale
    obj.location = final_loc
    obj.rotation_euler = final_rot
    obj.keyframe_insert(data_path="scale", frame=end_frame)
    obj.keyframe_insert(data_path="location", frame=end_frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    # Also lock stationary pose across Frames 120-240 for Animation 2 (Main Menu Glow-Only)
    obj.keyframe_insert(data_path="scale", frame=120)
    obj.keyframe_insert(data_path="location", frame=120)
    obj.keyframe_insert(data_path="rotation_euler", frame=120)
    obj.keyframe_insert(data_path="scale", frame=240)
    obj.keyframe_insert(data_path="location", frame=240)
    obj.keyframe_insert(data_path="rotation_euler", frame=240)

for grp, delay in title_groups:
    keyframe_pop_in(grp, 1 + delay, 18 + delay, start_z_offset=-0.5, start_rot_x=0.45)

keyframe_pop_in(i_dot_anchor, 14, 32, start_z_offset=-0.25, start_rot_x=0.3)
keyframe_pop_in(tree_branches_anchor, 12, 36, start_z_offset=-0.4, start_rot_x=0.2)
keyframe_pop_in(brain_canopy, 16, 40, start_z_offset=-0.3, start_rot_x=0.15)

keyframe_pop_in(sprig_brain_L, 22, 42, start_z_offset=-0.15, start_rot_x=0.2)
keyframe_pop_in(sprig_brain_R, 24, 44, start_z_offset=-0.15, start_rot_x=0.2)
keyframe_pop_in(sprig_bot_L,   20, 42, start_z_offset=-0.20, start_rot_x=0.25)
keyframe_pop_in(sprig_bot_R,   24, 46, start_z_offset=-0.20, start_rot_x=0.25)

keyframe_pop_in(sub_left,  26, 44, start_z_offset=-0.25, start_rot_x=0.2)
keyframe_pop_in(sub_right, 28, 46, start_z_offset=-0.25, start_rot_x=0.2)

# IntroScreen motion (Frames 1-120), settling smoothly to 0 at Frame 116-120
for f in range(1, 121, 4):
    t = (f - 1) / 116.0 * 2.0 * math.pi
    envelope = 1.0 if f < 96 else max(0.0, (116 - f) / 20.0)

    logo_root.location = (0.0, 0.0, 0.05 * math.sin(t) * envelope)
    logo_root.rotation_euler = (
        math.radians(2.0 * math.cos(t) * envelope),
        math.radians(1.2 * math.sin(t) * envelope),
        math.radians(7.0 * math.sin(t) * envelope)
    )
    logo_root.keyframe_insert(data_path="location", frame=f)
    logo_root.keyframe_insert(data_path="rotation_euler", frame=f)

    if f >= 44:
        sway = math.radians(4.0 * math.sin(t * 2.0) * envelope)
        for sp, sign in [(sprig_brain_L, 1), (sprig_brain_R, -1), (sprig_bot_L, 1), (sprig_bot_R, -1), (i_dot_anchor, 1)]:
            sp.rotation_euler = (0.0, sign * sway, 0.0)
            sp.keyframe_insert(data_path="rotation_euler", frame=f)

        b_pulse = 1.0 + 0.025 * math.sin(t * 2.0) * envelope
        brain_canopy.scale = (b_pulse, b_pulse, b_pulse)
        brain_canopy.keyframe_insert(data_path="scale", frame=f)

# Ensure 100% stationary pose from Frame 120 to 240 for Animation 2
for f_static in [120, 121, 240]:
    logo_root.location = (0.0, 0.0, 0.0)
    logo_root.rotation_euler = (0.0, 0.0, 0.0)
    logo_root.keyframe_insert(data_path="location", frame=f_static)
    logo_root.keyframe_insert(data_path="rotation_euler", frame=f_static)
    brain_canopy.scale = (1.0, 1.0, 1.0)
    brain_canopy.keyframe_insert(data_path="scale", frame=f_static)
    for sp in [sprig_brain_L, sprig_brain_R, sprig_bot_L, sprig_bot_R, i_dot_anchor]:
        sp.rotation_euler = (0.0, 0.0, 0.0)
        sp.keyframe_insert(data_path="rotation_euler", frame=f_static)

cam_obj.location = (0.0, -13.6, 0.82)
cam_obj.keyframe_insert(data_path="location", frame=1)
cam_obj.location = (0.0, -12.4, 0.82)
cam_obj.keyframe_insert(data_path="location", frame=48)
cam_obj.location = (0.0, -12.4, 0.82)
cam_obj.keyframe_insert(data_path="location", frame=120)
cam_obj.location = (0.0, -12.4, 0.82)
cam_obj.keyframe_insert(data_path="location", frame=240)

# ---------------------------------------------------------------------------
# 11. ANIMATION 2: MainMenu_GlowOnly (Radial Golden Glow Pulse, Zero Movement)
#     Keyframed across both 1-120 and 121-240 so it works in both scenes!
# ---------------------------------------------------------------------------
def set_mat_glow_keyframe(mat, frame, strength, base_rgb=None, emit_rgb=None):
    if base_rgb is not None:
        mat.diffuse_color = (*base_rgb, 1.0)
        mat.keyframe_insert(data_path="diffuse_color", frame=frame)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=frame)
    if base_rgb is not None and "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (*base_rgb, 1.0)
        bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=frame)
    if emit_rgb is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emit_rgb, 1.0)
        bsdf.inputs["Emission Color"].keyframe_insert(data_path="default_value", frame=frame)

# Animate 1 slow, atmospheric breathing glow cycle per 120 frames (period = 120 frames = 5.0s at 24fps)
# Slowed down for a serene, majestic, living main menu ambient pulse
glow_frames = sorted(set(list(range(1, 241, 3)) + [120, 121, 240]))
for f in glow_frames:
    # Phase angle (1 slow, majestic cycle per 120 frames: smooth seamless loop)
    phase = ((f - 1) % 120) / 120.0 * (2.0 * math.pi)

    # Radial wave propagating from Core -> Mid -> Outer -> Gold Rims & Berries
    w_core  = 0.5 + 0.5 * math.sin(phase - math.pi / 2.0)               # [0.0 .. 1.0]
    w_mid   = 0.5 + 0.5 * math.sin(phase - math.pi / 2.0 - 0.45)        # lags core
    w_outer = 0.5 + 0.5 * math.sin(phase - math.pi / 2.0 - 0.90)        # lags mid
    w_gold  = 0.5 + 0.5 * math.sin(phase - math.pi / 2.0 - 0.35)

    # Unity-native 3D Glow Wave Domes (depth shift along Y creates radial bloom across curved 3D lobes)
    glow_wave_core_pivot.location = (0.0, 0.036 * (1.0 - w_core) - 0.010 * w_core, 0.0)
    glow_wave_core_pivot.keyframe_insert(data_path="location", frame=f)

    glow_wave_mid_pivot.location = (0.0, 0.032 * (1.0 - w_mid) - 0.008 * w_mid, 0.0)
    glow_wave_mid_pivot.keyframe_insert(data_path="location", frame=f)

    glow_wave_outer_pivot.location = (0.0, 0.030 * (1.0 - w_outer) - 0.006 * w_outer, 0.0)
    glow_wave_outer_pivot.keyframe_insert(data_path="location", frame=f)

    # 1. Brain Core Glow (pulses from warm amber-gold to brilliant radiant sun-gold)
    set_mat_glow_keyframe(
        mat_brain_core, f,
        strength=0.25 + 5.5 * w_core,
        base_rgb=(0.88 + 0.12 * w_core, 0.72 + 0.24 * w_core, 0.28 + 0.34 * w_core),
        emit_rgb=(1.00, 0.90 + 0.08 * w_core, 0.35 + 0.35 * w_core)
    )

    # 2. Brain Mid Hemispheres Glow (ripples outward from core, rich honey amber)
    set_mat_glow_keyframe(
        mat_brain_mid, f,
        strength=0.15 + 3.2 * w_mid,
        base_rgb=(0.80 + 0.20 * w_mid, 0.44 + 0.26 * w_mid, 0.12 + 0.10 * w_mid),
        emit_rgb=(1.00, 0.58 + 0.22 * w_mid, 0.14 + 0.18 * w_mid)
    )

    # 3. Brain Outer Cerebral Lobes Glow (rich sunset coral-amber, contrasting sharply with pale peach sky)
    set_mat_glow_keyframe(
        mat_brain_outer, f,
        strength=0.10 + 1.8 * w_outer,
        base_rgb=(0.78 + 0.14 * w_outer, 0.32 + 0.16 * w_outer, 0.12 + 0.08 * w_outer),
        emit_rgb=(0.92, 0.38 + 0.18 * w_outer, 0.14 + 0.14 * w_outer)
    )

    # 4. Metallic Imperial Gold Letter Bevels & Leaf Veins/Rims Shimmer
    set_mat_glow_keyframe(
        mat_gold, f,
        strength=0.10 + 2.2 * w_gold,
        base_rgb=(0.82 + 0.18 * w_gold, 0.64 + 0.24 * w_gold, 0.18 + 0.16 * w_gold),
        emit_rgb=(1.00, 0.82 + 0.12 * w_gold, 0.25 + 0.20 * w_gold)
    )

    # 5. Golden Berries Glow
    set_mat_glow_keyframe(
        mat_berry_gold, f,
        strength=0.20 + 4.2 * w_gold,
        base_rgb=(0.82 + 0.18 * w_gold, 0.66 + 0.22 * w_gold, 0.15 + 0.15 * w_gold),
        emit_rgb=(1.00, 0.84 + 0.12 * w_gold, 0.22 + 0.22 * w_gold)
    )

    # 6. Tree Trunk inner neural energy pulse
    set_mat_glow_keyframe(
        mat_trunk, f,
        strength=0.04 + 0.95 * w_core,
        base_rgb=(0.12 + 0.14 * w_core, 0.04 + 0.06 * w_core, 0.015 + 0.02 * w_core),
        emit_rgb=(0.40 + 0.45 * w_core, 0.16 + 0.24 * w_core, 0.03 + 0.06 * w_core)
    )

    # 7. Brain Core Point Light intensity
    core_light_data.energy = 10.0 + 320.0 * w_core
    core_light_data.keyframe_insert(data_path="energy", frame=f)

# ---------------------------------------------------------------------------
# 12. Create Dedicated Second Scene: 'MainMenu_GlowOnly' (Frames 1-120, Static Pose + Glow)
# ---------------------------------------------------------------------------
# Set IntroScreen frame range to 1-120 for clean playback of Animation 1
base_scene.frame_start = 1
base_scene.frame_end = 120
base_scene.frame_set(120)

# Create 'MainMenu_GlowOnly' scene sharing the collections, locked to the glow-only range (121-240)
menu_scene = bpy.data.scenes.new("MainMenu_GlowOnly")
menu_scene.unit_settings.system = 'METRIC'
menu_scene.unit_settings.scale_length = 1.0
menu_scene.render.fps = 24
menu_scene.render.resolution_x = 1920
menu_scene.render.resolution_y = 1080
menu_scene.world = world
menu_scene.camera = cam_obj

for c in [col_root, col_text, col_brain, col_flora, col_stage]:
    menu_scene.collection.children.link(c)

# Frame range 121-240 in MainMenu_GlowOnly has 100% static objects and 2 full seamless glow loops
menu_scene.frame_start = 121
menu_scene.frame_end = 240
menu_scene.frame_set(121)

# Switch active window to 'MainMenu_GlowOnly' so the user can immediately press Spacebar to preview it
bpy.context.window.scene = menu_scene
bpy.context.view_layer.update()

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        space.shading.type = 'MATERIAL'
        space.shading.use_scene_lights = True
        space.shading.use_scene_world = True
        r3d = space.region_3d
        r3d.view_location = (0.0, 0.0, 0.90)
        r3d.view_distance = 10.5
        r3d.view_rotation = Euler((math.radians(90), 0.0, 0.0), 'XYZ').to_quaternion()
        r3d.view_perspective = 'CAMERA'

out_blend = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/MindScape3D_Logo.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
print("Saved new Blender file with 2 animations (IntroScreen & MainMenu_GlowOnly) to:", out_blend)
