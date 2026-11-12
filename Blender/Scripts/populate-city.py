"""Populate the 7 empty blocks of world_new with hollow houses, hollow buildings, streetlights and trees.

Follows the mindscape-3d architectural and visual style:
- Metrics: Units in meters, Z up.
- Hollow houses & buildings: actual wall thickness, walk-in doorway openings, interior rooms/floors, open ceilings/hollow interiors.
- Materials: Reuses existing cozy low-poly materials (vanilla plaster, sage green, powder blue, apricot, graphite roof, timber).
- Streetlights: Slender dark poles with curved/angled arm and warm emissive lantern heads along all road sidewalks.
- Trees: Low-poly stylized trees (deciduous, boulevard, and evergreen) with faceted canopies in sidewalk verges and yards.
"""

import bpy
import math
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------------------
# Setup & Scene References
# ---------------------------------------------------------------------------
scene = bpy.data.scenes.get("world_new")
assert scene is not None, "Scene 'world_new' must be loaded before running."
bpy.context.window.scene = scene

root = bpy.data.objects.get("world_new")
assert root is not None, "Root empty 'world_new' must exist."

def get_or_create_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    return col

col_houses = get_or_create_col("World | Hollow Houses")
col_buildings = get_or_create_col("World | Hollow Buildings")
col_lights = get_or_create_col("World | Streetlights")
col_trees = get_or_create_col("World | Trees")

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def get_or_create_mat(name, color, roughness=0.85, emission=None, emission_strength=0.0):
    full_name = "World | " + name
    mat = bpy.data.materials.get(full_name) or bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(full_name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1.0)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

# Material definitions
mat_vanilla = bpy.data.materials.get("Cozy | vanilla plaster") or get_or_create_mat("Vanilla Plaster", (0.86, 0.80, 0.65))
mat_sage = bpy.data.materials.get("Cozy | sage green") or get_or_create_mat("Sage Green", (0.43, 0.62, 0.43))
mat_blue = bpy.data.materials.get("Cozy | powder blue") or get_or_create_mat("Powder Blue", (0.40, 0.63, 0.72))
mat_apricot = bpy.data.materials.get("Cozy | apricot") or get_or_create_mat("Apricot Plaster", (0.90, 0.53, 0.32))
mat_white = get_or_create_mat("Civic Ivory", (0.92, 0.90, 0.84))
mat_brick = get_or_create_mat("Warm Brick", (0.68, 0.38, 0.28))
mat_roof_graphite = bpy.data.materials.get("House - graphite standing seam roof") or get_or_create_mat("Roof Graphite", (0.25, 0.43, 0.40))
mat_roof_terracotta = get_or_create_mat("Roof Terracotta", (0.75, 0.38, 0.22))
mat_timber = bpy.data.materials.get("House - warm timber entrance") or get_or_create_mat("Timber", (0.34, 0.16, 0.06))
mat_oak = bpy.data.materials.get("Cozy | honey oak") or get_or_create_mat("Honey Oak", (0.56, 0.32, 0.14))
mat_charcoal = get_or_create_mat("Street Charcoal", (0.15, 0.16, 0.17), roughness=0.35)
mat_lamp_glow = get_or_create_mat("Streetlight Glow", (1.0, 0.94, 0.72), emission=(1.0, 0.94, 0.72), emission_strength=8.0)
mat_floor = get_or_create_mat("Interior Floor", (0.55, 0.50, 0.44))
mat_glass = get_or_create_mat("Window Glass", (0.38, 0.60, 0.72), roughness=0.1)
mat_leaf1 = bpy.data.materials.get("Cozy | leaf green") or get_or_create_mat("Foliage Leaf", (0.28, 0.47, 0.21))
mat_leaf2 = get_or_create_mat("Foliage Forest", (0.18, 0.36, 0.16))
mat_leaf3 = get_or_create_mat("Foliage Golden", (0.46, 0.52, 0.22))
mat_trunk = get_or_create_mat("Tree Trunk", (0.32, 0.20, 0.12))
mat_concrete = bpy.data.materials.get("World | Sidewalk") or get_or_create_mat("Sidewalk", (0.59, 0.61, 0.58))
mat_awning_red = get_or_create_mat("Awning Crimson", (0.78, 0.22, 0.18))

# ---------------------------------------------------------------------------
# Mesh Helpers
# ---------------------------------------------------------------------------
def make_box(name, center, size, mat, col, parent=None):
    mesh = bpy.data.meshes.new(name)
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    verts = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_cylinder(name, center, r_bottom, r_top, height, segments, mat, col, parent=None):
    mesh = bpy.data.meshes.new(name)
    verts = []
    hz = height / 2
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        verts.append((r_bottom * math.cos(a), r_bottom * math.sin(a), -hz))
    for i in range(segments):
        a = (2 * math.pi * i) / segments
        verts.append((r_top * math.cos(a), r_top * math.sin(a), hz))
    faces = []
    # side faces
    for i in range(segments):
        i_next = (i + 1) % segments
        faces.append((i, i_next, segments + i_next, segments + i))
    # bottom face
    faces.append(list(reversed(range(segments))))
    # top face
    faces.append(list(range(segments, 2 * segments)))
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_gable_roof(name, center, width, depth, roof_height, overhang, thickness, mat, col, parent=None):
    mesh = bpy.data.meshes.new(name)
    w = width + 2 * overhang
    d = depth + 2 * overhang
    hx = w / 2
    hd = d / 2
    rh = roof_height
    th = thickness
    verts = [
        # Top surfaces
        (-hx, -hd, 0), (hx, -hd, 0), (hx, 0, rh), (-hx, 0, rh),
        (-hx, 0, rh), (hx, 0, rh), (hx, hd, 0), (-hx, hd, 0),
        # Bottom surfaces
        (-hx, -hd, -th), (hx, -hd, -th), (hx, 0, rh - th), (-hx, 0, rh - th),
        (-hx, 0, rh - th), (hx, 0, rh - th), (hx, hd, -th), (-hx, hd, -th),
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7),
        (11, 10, 9, 8), (15, 14, 13, 12),
        (0, 8, 9, 1), (7, 6, 14, 15),
        (0, 3, 11, 8), (1, 2, 10, 9),
        (4, 7, 15, 12), (5, 6, 14, 13),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_gable_end(name, center, width, depth, rh, th, mat, col, is_left=True, parent=None):
    mesh = bpy.data.meshes.new(name)
    x0 = -width/2 if is_left else width/2 - th
    x1 = -width/2 + th if is_left else width/2
    d2 = depth/2
    verts = [
        (x0, -d2, 0), (x1, -d2, 0), (x1, d2, 0), (x0, d2, 0),
        (x0, 0, rh), (x1, 0, rh)
    ]
    if is_left:
        faces = [
            (3, 2, 1, 0), (0, 4, 3), (1, 2, 5), (0, 1, 5, 4), (3, 4, 5, 2)
        ]
    else:
        faces = [
            (0, 1, 2, 3), (1, 5, 2), (0, 3, 4), (0, 4, 5, 1), (3, 2, 5, 4)
        ]
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

# ---------------------------------------------------------------------------
# Hollow House Builder
# ---------------------------------------------------------------------------
def create_hollow_house(name, pos, width, depth, wall_h=3.2, roof_h=2.2,
                        wall_mat=mat_vanilla, roof_mat=mat_roof_graphite,
                        door_x=0.0, col=col_houses, parent=root):
    anchor = bpy.data.objects.new(name + " | anchor", None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    th = 0.16
    hw, hd = width / 2, depth / 2
    # 1. Floor slab
    make_box(name + " | floor", (0, 0, 0.05), (width, depth, 0.1), mat_floor, col, anchor)

    # 2. Side walls (Left & Right)
    make_box(name + " | wall_left", (-hw + th/2, 0, wall_h/2), (th, depth, wall_h), wall_mat, col, anchor)
    make_box(name + " | wall_right", (hw - th/2, 0, wall_h/2), (th, depth, wall_h), wall_mat, col, anchor)

    # 3. Back wall (with rear window opening)
    # Window width 1.8m, height 1.2m, sill 1.0m
    win_w, win_h, sill_h = 2.0, 1.2, 1.0
    make_box(name + " | wall_back_low", (0, hd - th/2, sill_h/2), (width, th, sill_h), wall_mat, col, anchor)
    make_box(name + " | wall_back_high", (0, hd - th/2, (wall_h + sill_h + win_h)/2), (width, th, wall_h - (sill_h + win_h)), wall_mat, col, anchor)
    make_box(name + " | wall_back_left", (-(width + win_w)/4, hd - th/2, (sill_h + win_h/2)), ((width - win_w)/2, th, win_h), wall_mat, col, anchor)
    make_box(name + " | wall_back_right", ((width + win_w)/4, hd - th/2, (sill_h + win_h/2)), ((width - win_w)/2, th, win_h), wall_mat, col, anchor)
    make_box(name + " | win_back_glass", (0, hd - th/2, sill_h + win_h/2), (win_w - 0.05, 0.04, win_h - 0.05), mat_glass, col, anchor)

    # 4. Front wall (Door opening: width 1.3m, height 2.2m at door_x)
    dw, dh = 1.3, 2.2
    x_left_w = (door_x - dw/2) - (-hw)
    x_right_w = hw - (door_x + dw/2)
    # Left front segment
    make_box(name + " | wall_front_left", (-hw + x_left_w/2, -hd + th/2, wall_h/2), (x_left_w, th, wall_h), wall_mat, col, anchor)
    # Right front segment
    make_box(name + " | wall_front_right", (hw - x_right_w/2, -hd + th/2, wall_h/2), (x_right_w, th, wall_h), wall_mat, col, anchor)
    # Door header above door
    make_box(name + " | wall_front_header", (door_x, -hd + th/2, (wall_h + dh)/2), (dw, th, wall_h - dh), wall_mat, col, anchor)
    # Front window in the wider segment
    if x_left_w > 3.0:
        fwin_x = -hw + x_left_w/2
        make_box(name + " | win_front_glass", (fwin_x, -hd + th/2, 1.6), (1.5, 0.04, 1.2), mat_glass, col, anchor)
        make_box(name + " | win_front_frame", (fwin_x, -hd - 0.02, 1.0), (1.7, 0.08, 0.08), mat_timber, col, anchor)

    # 5. Front Porch
    porch_w, porch_d = dw + 1.2, 1.8
    make_box(name + " | porch_slab", (door_x, -hd - porch_d/2, 0.06), (porch_w, porch_d, 0.12), mat_concrete, col, anchor)
    make_box(name + " | porch_pillar_L", (door_x - porch_w/2 + 0.1, -hd - porch_d + 0.1, 1.4), (0.16, 0.16, 2.6), mat_timber, col, anchor)
    make_box(name + " | porch_pillar_R", (door_x + porch_w/2 - 0.1, -hd - porch_d + 0.1, 1.4), (0.16, 0.16, 2.6), mat_timber, col, anchor)
    make_box(name + " | porch_roof", (door_x, -hd - porch_d/2, 2.75), (porch_w + 0.3, porch_d + 0.2, 0.14), roof_mat, col, anchor)

    # 6. Interior Partition (Separates living & bedroom, HOLLOW with open interior doorway)
    part_x = -hw * 0.15
    part_door_y = 0.5
    p_dw, p_dh = 1.1, 2.1
    # Lower front partition
    p_front_len = (part_door_y - p_dw/2) - (-hd + th)
    make_box(name + " | interior_part_front", (part_x, -hd + th + p_front_len/2, wall_h/2), (th, p_front_len, wall_h), wall_mat, col, anchor)
    # Upper back partition
    p_back_len = (hd - th) - (part_door_y + p_dw/2)
    make_box(name + " | interior_part_back", (part_x, hd - th - p_back_len/2, wall_h/2), (th, p_back_len, wall_h), wall_mat, col, anchor)
    # Header above interior door
    make_box(name + " | interior_part_header", (part_x, part_door_y, (wall_h + p_dh)/2), (th, p_dw, wall_h - p_dh), wall_mat, col, anchor)

    # 7. Roof (Gabled, Hollow inside)
    make_gable_roof(name + " | roof", (0, 0, wall_h), width, depth, roof_h, 0.45, 0.14, roof_mat, col, anchor)
    make_gable_end(name + " | gable_left", (0, 0, wall_h), width, depth, roof_h, th, wall_mat, col, is_left=True, parent=anchor)
    make_gable_end(name + " | gable_right", (0, 0, wall_h), width, depth, roof_h, th, wall_mat, col, is_left=False, parent=anchor)

    # Chimney on roof
    make_box(name + " | chimney", (hw - 1.2, hd * 0.3, wall_h + roof_h * 0.65), (0.7, 0.7, 1.6), mat_brick, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# Hollow Multi-Story Building Builder
# ---------------------------------------------------------------------------
def create_hollow_building(name, pos, width, depth, stories=2, story_h=3.6,
                           wall_mat=mat_white, trim_mat=mat_timber,
                           col=col_buildings, parent=root):
    anchor = bpy.data.objects.new(name + " | anchor", None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    total_h = stories * story_h
    th = 0.22
    hw, hd = width / 2, depth / 2

    # 1. Foundation & Ground Floor Slab
    make_box(name + " | ground_slab", (0, 0, 0.08), (width, depth, 0.16), mat_concrete, col, anchor)

    # 2. Side & Back Walls (continuous with windows)
    make_box(name + " | wall_left", (-hw + th/2, 0, total_h/2), (th, depth, total_h), wall_mat, col, anchor)
    make_box(name + " | wall_right", (hw - th/2, 0, total_h/2), (th, depth, total_h), wall_mat, col, anchor)
    make_box(name + " | wall_back", (0, hd - th/2, total_h/2), (width, th, total_h), wall_mat, col, anchor)

    # Rear service windows
    for s in range(stories):
        w_z = s * story_h + story_h * 0.55
        make_box(name + f" | rear_win_{s}_1", (-width*0.25, hd - th/2, w_z), (2.4, 0.06, 1.4), mat_glass, col, anchor)
        make_box(name + f" | rear_win_{s}_2", (width*0.25, hd - th/2, w_z), (2.4, 0.06, 1.4), mat_glass, col, anchor)

    # 3. Front Facade
    # Ground floor: Wide commercial entrance (dw=2.6m, dh=2.6m) and display windows
    dw, dh = 2.6, 2.6
    left_w = (width - dw) / 2
    make_box(name + " | front_GF_left_pier", (-hw + left_w/2, -hd + th/2, story_h/2), (left_w, th, story_h), wall_mat, col, anchor)
    make_box(name + " | front_GF_right_pier", (hw - left_w/2, -hd + th/2, story_h/2), (left_w, th, story_h), wall_mat, col, anchor)
    make_box(name + " | front_GF_header", (0, -hd + th/2, (story_h + dh)/2), (dw, th, story_h - dh), wall_mat, col, anchor)

    # Storefront display windows inset into piers
    disp_w = left_w * 0.75
    make_box(name + " | storefront_glass_L", (-hw + left_w/2, -hd - 0.02, 1.5), (disp_w, 0.05, 1.9), mat_glass, col, anchor)
    make_box(name + " | storefront_glass_R", (hw - left_w/2, -hd - 0.02, 1.5), (disp_w, 0.05, 1.9), mat_glass, col, anchor)

    # Front Entrance Marquee / Awning
    make_box(name + " | marquee_awning", (0, -hd - 1.2, dh + 0.15), (dw + 1.2, 2.4, 0.18), trim_mat, col, anchor)
    make_box(name + " | marquee_signboard", (0, -hd - 0.1, dh + 0.5), (dw + 2.0, 0.22, 0.6), mat_charcoal, col, anchor)

    # Upper floor front walls & ribbon windows
    for s in range(1, stories):
        base_z = s * story_h
        # Sill & header
        make_box(name + f" | front_F{s}_sill", (0, -hd + th/2, base_z + 0.5), (width, th, 1.0), wall_mat, col, anchor)
        make_box(name + f" | front_F{s}_header", (0, -hd + th/2, base_z + story_h - 0.4), (width, th, 0.8), wall_mat, col, anchor)
        # Piers & inset window bands
        win_h_s = story_h - 1.8
        wz = base_z + 1.0 + win_h_s/2
        make_box(name + f" | front_F{s}_pier_L", (-width*0.475, -hd + th/2, wz), (width*0.05, th, win_h_s), wall_mat, col, anchor)
        make_box(name + f" | front_F{s}_pier_C", (0, -hd + th/2, wz), (width*0.10, th, win_h_s), wall_mat, col, anchor)
        make_box(name + f" | front_F{s}_pier_R", (width*0.475, -hd + th/2, wz), (width*0.05, th, win_h_s), wall_mat, col, anchor)
        make_box(name + f" | front_F{s}_glass_L", (-width*0.25, -hd + th/2, wz), (width*0.4, 0.06, win_h_s), mat_glass, col, anchor)
        make_box(name + f" | front_F{s}_glass_R", (width*0.25, -hd + th/2, wz), (width*0.4, 0.06, win_h_s), mat_glass, col, anchor)

    # 4. Hollow Upper Floor Slabs (with stairwell cut-out so vertical interior is open)
    stair_w, stair_d = 3.2, 4.0
    for s in range(1, stories):
        floor_z = s * story_h
        # Left half floor
        make_box(name + f" | slab_F{s}_left", (-hw + (width - stair_w)/4, 0, floor_z), ((width - stair_w)/2, depth - 2*th, 0.18), mat_floor, col, anchor)
        # Right half floor
        make_box(name + f" | slab_F{s}_right", (hw - (width - stair_w)/4, 0, floor_z), ((width - stair_w)/2, depth - 2*th, 0.18), mat_floor, col, anchor)
        # Rear connecting walkway behind stair opening
        make_box(name + f" | slab_F{s}_rear_walk", (0, (hd - th + (stair_d/2))/2, floor_z), (stair_w, (depth - 2*th - stair_d)/2, 0.18), mat_floor, col, anchor)

    # 5. Hollow Interior Columns (Ground Floor Lobby / Exhibition Space)
    col_x = hw * 0.45
    col_y = hd * 0.35
    for cx in [-col_x, col_x]:
        for cy in [-col_y, col_y]:
            make_box(name + f" | lobby_pillar_{cx:.0f}_{cy:.0f}", (cx, cy, story_h/2), (0.45, 0.45, story_h), trim_mat, col, anchor)

    # 6. Roof Slab & Parapet Wall
    make_box(name + " | roof_slab", (0, 0, total_h), (width, depth, 0.22), mat_floor, col, anchor)
    # Parapet around roof
    para_h = 0.75
    make_box(name + " | parapet_front", (0, -hd + th/2, total_h + para_h/2), (width, th, para_h), wall_mat, col, anchor)
    make_box(name + " | parapet_back", (0, hd - th/2, total_h + para_h/2), (width, th, para_h), wall_mat, col, anchor)
    make_box(name + " | parapet_left", (-hw + th/2, 0, total_h + para_h/2), (th, depth - 2*th, para_h), wall_mat, col, anchor)
    make_box(name + " | parapet_right", (hw - th/2, 0, total_h + para_h/2), (th, depth - 2*th, para_h), wall_mat, col, anchor)

    # Rooftop Stair Bulkhead / AC Unit
    make_box(name + " | rooftop_penthouse", (0, hd * 0.3, total_h + 1.2), (3.4, 3.8, 2.2), wall_mat, col, anchor)
    make_box(name + " | rooftop_ac_chiller", (-hw * 0.4, -hd * 0.2, total_h + 0.65), (2.0, 1.4, 1.1), mat_charcoal, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# Streetlight Builder
# ---------------------------------------------------------------------------
def create_streetlight(name, pos, yaw=0.0, col=col_lights, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    anchor.rotation_euler.z = yaw

    # Base Pedestal
    make_cylinder(name + "_base", (0, 0, 0.12), 0.22, 0.18, 0.24, 8, mat_charcoal, col, anchor)
    # Pole Column (4.2m tall)
    make_cylinder(name + "_pole", (0, 0, 2.15), 0.10, 0.07, 4.1, 8, mat_charcoal, col, anchor)
    # Collar ring
    make_cylinder(name + "_collar", (0, 0, 4.15), 0.12, 0.10, 0.12, 8, mat_charcoal, col, anchor)
    # Curved / Angled Outreach Arm (reaching out +Y direction by 1.1m)
    make_box(name + "_arm", (0, 0.55, 4.3), (0.08, 1.1, 0.08), mat_charcoal, col, anchor)
    # Lantern Hood / Cowl
    make_box(name + "_hood", (0, 1.1, 4.25), (0.35, 0.45, 0.14), mat_charcoal, col, anchor)
    # Emissive Warm Lamp Core (Glowing)
    make_box(name + "_bulb", (0, 1.1, 4.14), (0.24, 0.32, 0.10), mat_lamp_glow, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# Tree Builder (Low-Poly Stylized)
# ---------------------------------------------------------------------------
def create_tree(name, pos, scale=1.0, tree_type="round", foliage_mat=mat_leaf1,
                col=col_trees, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    if tree_type == "round":
        # Deciduous rounded tree with multi-tiered faceted canopy
        trunk_h = 2.4 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.22 * scale, 0.14 * scale, trunk_h, 7, mat_trunk, col, anchor)
        # Foliage cloud layers
        make_cylinder(name + "_foliage_base", (0, 0, trunk_h + 0.8 * scale), 1.9 * scale, 1.6 * scale, 1.4 * scale, 8, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_mid", (0.2 * scale, -0.1 * scale, trunk_h + 1.8 * scale), 1.5 * scale, 1.0 * scale, 1.3 * scale, 8, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_top", (-0.1 * scale, 0.1 * scale, trunk_h + 2.6 * scale), 0.9 * scale, 0.3 * scale, 1.0 * scale, 7, foliage_mat, col, anchor)

    elif tree_type == "boulevard":
        # Taller slender street tree with pedestrian clearance
        trunk_h = 2.9 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.16 * scale, 0.10 * scale, trunk_h, 6, mat_trunk, col, anchor)
        # Compact canopy
        make_cylinder(name + "_foliage_1", (0, 0, trunk_h + 0.7 * scale), 1.3 * scale, 1.1 * scale, 1.2 * scale, 7, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_2", (0, 0, trunk_h + 1.6 * scale), 1.0 * scale, 0.4 * scale, 1.1 * scale, 7, foliage_mat, col, anchor)
        # Tree well planter grate on sidewalk
        make_box(name + "_grate", (0, 0, 0.02), (1.4 * scale, 1.4 * scale, 0.04), mat_charcoal, col, anchor)

    elif tree_type == "pine":
        # Conical evergreen tree with 3 tiered cones
        trunk_h = 1.6 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.20 * scale, 0.12 * scale, trunk_h, 6, mat_trunk, col, anchor)
        make_cylinder(name + "_tier_1", (0, 0, trunk_h + 0.7 * scale), 1.8 * scale, 0.8 * scale, 1.3 * scale, 7, mat_leaf2, col, anchor)
        make_cylinder(name + "_tier_2", (0, 0, trunk_h + 1.7 * scale), 1.3 * scale, 0.5 * scale, 1.2 * scale, 7, mat_leaf2, col, anchor)
        make_cylinder(name + "_tier_3", (0, 0, trunk_h + 2.5 * scale), 0.8 * scale, 0.1 * scale, 1.1 * scale, 6, mat_leaf2, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# City Population Execution
# ---------------------------------------------------------------------------
print("Starting population of world_new...")

# Clean existing objects in our new collections if rerunning
for c in [col_houses, col_buildings, col_lights, col_trees]:
    for obj in list(c.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

# ---------------------------------------------------------------------------
# 1. HOLLOW HOUSES
# ---------------------------------------------------------------------------
houses_data = [
    # Block 32 (South Center, adjacent to Player's House)
    ("House 32A | Craftsman", (-24, -50, 0.10), 13, 10, 3.2, 2.3, mat_sage, mat_roof_graphite, 0.0),
    ("House 32B | Farmhouse", (0, -50, 0.10), 14, 9.5, 3.4, 2.4, mat_vanilla, mat_roof_terracotta, 0.5),
    ("House 32C | Villa", (24, -50, 0.10), 12, 10, 3.2, 2.2, mat_blue, mat_roof_graphite, -0.5),

    # Block 21 (West Center, residential street)
    ("House 21A | Bungalow", (-124, 0, 0.10), 13, 10, 3.2, 2.2, mat_blue, mat_sage, 0.0),
    ("House 21B | FamilyHome", (-102, 0, 0.10), 14, 10, 3.4, 2.5, mat_apricot, mat_roof_graphite, 1.0),
    ("House 21C | TownCottage", (-80, 0, 0.10), 12, 9, 3.0, 2.1, mat_vanilla, mat_roof_terracotta, -0.4),

    # Block 11 (Northwest Neighborhood)
    ("House 11A | CountryHome", (-126, 52, 0.10), 14, 10, 3.2, 2.2, mat_vanilla, mat_roof_graphite, 0.0),
    ("House 11B | GardenHouse", (-102, 52, 0.10), 12, 9, 3.2, 2.1, mat_sage, mat_roof_terracotta, 0.6),

    # Block 23 (East Center)
    ("House 23C | EastResidence", (128, 0, 0.10), 12, 9.5, 3.2, 2.2, mat_vanilla, mat_roof_graphite, 0.0),

    # Block 33 (Southeast Park)
    ("House 33B | CaretakerCottage", (124, -52, 0.10), 12, 9, 3.0, 2.0, mat_apricot, mat_roof_graphite, -0.5),
]

for name, pos, w, d, wh, rh, wmat, rmat, dx in houses_data:
    create_hollow_house(name, pos, w, d, wh, rh, wmat, rmat, dx)
print(f"Created {len(houses_data)} hollow houses.")

# ---------------------------------------------------------------------------
# 2. HOLLOW BUILDINGS
# ---------------------------------------------------------------------------
buildings_data = [
    # Block 22 (Central Downtown - Hub of the city)
    ("Building 22A | Department Store & Cafe", (-22, 0, 0.10), 22, 15, 2, 4.0, mat_vanilla, mat_timber),
    ("Building 22B | Town Hall & Civic Hub", (22, 0, 0.10), 22, 15, 3, 3.6, mat_white, mat_charcoal),

    # Block 12 (North Center - Civic & Library district near school)
    ("Building 12A | Community Library", (-22, 52, 0.10), 20, 14, 2, 3.8, mat_blue, mat_white),
    ("Building 12B | Innovation & Arts Studio", (22, 52, 0.10), 18, 14, 2, 3.6, mat_sage, mat_timber),

    # Block 23 (East Center - Mixed Commercial & Townhomes)
    ("Building 23A | Bakery & Bookstore", (78, 0, 0.10), 18, 12, 2, 3.6, mat_apricot, mat_awning_red),
    ("Building 23B | Metro Apartments", (104, 0, 0.10), 16, 12, 2, 3.8, mat_white, mat_timber),

    # Block 11 (Northwest - Corner Grocery Market)
    ("Building 11C | Neighborhood Market", (-76, 52, 0.10), 14, 11, 2, 3.4, mat_white, mat_timber),

    # Block 33 (Southeast - Community Pavilion)
    ("Building 33A | Community Pavilion", (80, -52, 0.10), 18, 13, 2, 3.4, mat_sage, mat_timber),
]

for name, pos, w, d, st, sh, wmat, tmat in buildings_data:
    create_hollow_building(name, pos, w, d, st, sh, wmat, tmat)
print(f"Created {len(buildings_data)} hollow multi-story buildings.")

# ---------------------------------------------------------------------------
# 3. STREETLIGHTS
# ---------------------------------------------------------------------------
# Sidewalks:
# NS roads at X = -153, -51, 51, 153 -> sidewalk edges at:
# X = -149 (west road, east sidewalk), X = -55 (mid-west road, west sidewalk), X = -47 (mid-west road, east sidewalk),
# X = 47 (mid-east road, west sidewalk), X = 55 (mid-east road, east sidewalk), X = 149 (east road, west sidewalk)
# EW roads at Y = -78, -26, 26, 78 -> sidewalk edges at:
# Y = -74, Y = -30, Y = -22, Y = 22, Y = 30, Y = 74

light_count = 0
# Intersection Streetlights (4 at each of the 4 inner junctions)
for ix in [-51, 51]:
    for iy in [-26, 26]:
        # Corners:
        # SW corner: sidewalk at (ix - 4, iy - 4)
        create_streetlight(f"Light | junction ({ix},{iy}) SW", (ix - 4.5, iy - 4.5, 0.06), yaw=math.radians(45))
        create_streetlight(f"Light | junction ({ix},{iy}) SE", (ix + 4.5, iy - 4.5, 0.06), yaw=math.radians(135))
        create_streetlight(f"Light | junction ({ix},{iy}) NW", (ix - 4.5, iy + 4.5, 0.06), yaw=math.radians(-45))
        create_streetlight(f"Light | junction ({ix},{iy}) NE", (ix + 4.5, iy + 4.5, 0.06), yaw=math.radians(-135))
        light_count += 4

# Mid-Block Sidewalk Streetlights
# Along NS road X = -51 (facing road towards X = -51)
for y_pos in [-64, -40, -12, 12, 40, 64]:
    create_streetlight(f"Light | NS -51 W {y_pos}", (-54.8, y_pos, 0.06), yaw=math.radians(90))
    create_streetlight(f"Light | NS -51 E {y_pos}", (-47.2, y_pos, 0.06), yaw=math.radians(-90))
    light_count += 2

# Along NS road X = 51 (facing road towards X = 51)
for y_pos in [-64, -40, -12, 12, 40, 64]:
    create_streetlight(f"Light | NS 51 W {y_pos}", (47.2, y_pos, 0.06), yaw=math.radians(90))
    create_streetlight(f"Light | NS 51 E {y_pos}", (54.8, y_pos, 0.06), yaw=math.radians(-90))
    light_count += 2

# Along EW road Y = -26 (facing road towards Y = -26)
for x_pos in [-120, -84, -20, 20, 84, 120]:
    create_streetlight(f"Light | EW -26 S {x_pos}", (x_pos, -29.8, 0.06), yaw=math.radians(0))
    create_streetlight(f"Light | EW -26 N {x_pos}", (x_pos, -22.2, 0.06), yaw=math.radians(180))
    light_count += 2

# Along EW road Y = 26 (facing road towards Y = 26)
for x_pos in [-120, -84, -20, 20, 84, 120]:
    create_streetlight(f"Light | EW 26 S {x_pos}", (x_pos, 22.2, 0.06), yaw=math.radians(0))
    create_streetlight(f"Light | EW 26 N {x_pos}", (x_pos, 29.8, 0.06), yaw=math.radians(180))
    light_count += 2

print(f"Created {light_count} streetlights along all roads and intersections.")

# ---------------------------------------------------------------------------
# 4. TREES (Boulevard, Yard, and Park)
# ---------------------------------------------------------------------------
tree_count = 0

# A. Boulevard Street Trees along Sidewalks
boulevard_spots = [
    # Along X = -55 sidewalk (Block 11, 21, 31 eastern edge)
    (-55.0, -52), (-55.0, -1), (-55.0, 52),
    # Along X = -47 sidewalk (Block 12, 22, 32 western edge)
    (-47.0, -52), (-47.0, -1), (-47.0, 52),
    # Along X = 47 sidewalk (Block 12, 22, 32 eastern edge)
    (47.0, -52), (47.0, -1), (47.0, 52),
    # Along X = 55 sidewalk (Block 13, 23, 33 western edge)
    (55.0, -52), (55.0, -1), (55.0, 52),
    # Along Y = -22 sidewalk (Block 21, 22, 23 southern edge)
    (-102, -22.0), (0, -22.0), (102, -22.0),
    # Along Y = 22 sidewalk (Block 21, 22, 23 northern edge)
    (-102, 22.0), (0, 22.0), (102, 22.0),
]
for spot in boulevard_spots:
    create_tree(f"Tree | boulevard ({spot[0]},{spot[1]})", (spot[0], spot[1], 0.06), scale=1.1, tree_type="boulevard", foliage_mat=mat_leaf1)
    tree_count += 1

# B. Yard Trees Around Houses
yard_spots = [
    # Block 32 yards
    (-34, -42, 1.2, "round", mat_leaf1), (-14, -62, 1.3, "pine", mat_leaf2),
    (12, -42, 1.1, "round", mat_leaf3), (34, -60, 1.2, "round", mat_leaf1),
    # Block 21 yards
    (-136, 12, 1.3, "round", mat_leaf1), (-114, -12, 1.1, "pine", mat_leaf2),
    (-90, 12, 1.2, "round", mat_leaf3), (-68, -10, 1.1, "round", mat_leaf1),
    # Block 11 yards & park
    (-138, 62, 1.3, "round", mat_leaf1), (-114, 40, 1.1, "pine", mat_leaf2),
    (-90, 62, 1.2, "round", mat_leaf3), (-62, 40, 1.0, "round", mat_leaf1),
    # Block 23 yards
    (66, 12, 1.2, "round", mat_leaf1), (116, 12, 1.1, "round", mat_leaf3),
    (138, -10, 1.2, "pine", mat_leaf2), (138, 12, 1.1, "round", mat_leaf1),
]
for spot in yard_spots:
    create_tree(f"Tree | yard ({spot[0]},{spot[1]})", (spot[0], spot[1], 0.10), scale=spot[2], tree_type=spot[3], foliage_mat=spot[4])
    tree_count += 1

# C. Plaza & Park Trees
plaza_park_spots = [
    # Block 22 Central Town Plaza (between Buildings 22A and 22B)
    (-8, -6, 1.2, "round", mat_leaf3), (-8, 6, 1.2, "round", mat_leaf3),
    (8, -6, 1.2, "round", mat_leaf3), (8, 6, 1.2, "round", mat_leaf3),
    (0, -10, 1.1, "boulevard", mat_leaf1), (0, 10, 1.1, "boulevard", mat_leaf1),

    # Block 12 Civic Plaza (between Library and Arts Studio)
    (-6, 44, 1.2, "round", mat_leaf1), (6, 44, 1.2, "round", mat_leaf1),
    (0, 60, 1.3, "pine", mat_leaf2),

    # Block 33 Community Park Meadow (lush grove of trees & greenery)
    (98, -42, 1.4, "round", mat_leaf1), (106, -60, 1.3, "round", mat_leaf3),
    (102, -50, 1.5, "pine", mat_leaf2), (112, -40, 1.2, "round", mat_leaf1),
    (92, -62, 1.1, "pine", mat_leaf2), (114, -62, 1.2, "round", mat_leaf3),
]
for spot in plaza_park_spots:
    create_tree(f"Tree | plaza_park ({spot[0]},{spot[1]})", (spot[0], spot[1], 0.10), scale=spot[2], tree_type=spot[3], foliage_mat=spot[4])
    tree_count += 1

print(f"Created {tree_count} stylized trees.")

# Update viewport and view layer
bpy.context.view_layer.update()
print("Populated world_new successfully!")
