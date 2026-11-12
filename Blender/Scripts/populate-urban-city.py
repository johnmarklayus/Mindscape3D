"""Build a dense, fully urbanized 3D city across the 9-block grid in world_new.

Features:
- Master Urban Master Plan:
  - Block 22: High-density Central Downtown (4-6 story office towers, department stores, bank, cinema, hotel, central plaza).
  - Block 12: Civic & University District (Library, Tech Institute, Academic Halls, bookstore, campus quad).
  - Block 21: Urban Mixed-Use (Contiguous street walls of 3-4 story walkups, ground floor shops, rear service alley).
  - Block 23: Commercial Boulevard & Medical/Retail (Supermarket, clinic, lofts, urban diners).
  - Block 11: Historic Urban Quarter (Cobbled town square, gabled row houses, corner market).
  - Block 32: Brownstone Residential Row (Classic brownstones with elevated stoops, bay windows, rear yards).
  - Block 33: Civic Park & Waterfront Community Center (Modern recreation center, park residential tower, grand central park with gazebo, fountain, and mature groves).
  - Block 31: Residential Neighborhood embedding the original Player's House seamlessly with adjacent townhomes and cottages.
  - Block 13: School Campus Perimeter (Bus stops, bike racks, crossing signals, boulevard trees).
- Every building and house is 100% HOLLOW with walk-in entrances, interior floors, open stairwells/rooms, and roof structures.
- Urban ground treatment: Paved plazas, stone promenades, alleys, and structured green beds replace raw empty grass.
- Rich Street Furniture: Bus shelters, park benches, trash/recycle bins, fire hydrants, bike racks, water towers, AC chillers, antennas.
- Streetlights & Trees: Comprehensive network of 80+ streetlights and 90+ trees.
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

col_pavement = get_or_create_col("World | Urban Pavement")
col_buildings = get_or_create_col("World | Hollow Buildings")
col_houses = get_or_create_col("World | Hollow Houses")
col_props = get_or_create_col("World | Urban Props")
col_lights = get_or_create_col("World | Streetlights")
col_trees = get_or_create_col("World | Trees")

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def mat(name, color, roughness=0.85, emission=None, emission_strength=0.0):
    full_name = "World | " + name
    m = bpy.data.materials.get(full_name) or bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(full_name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m

# Urban Palette
m_pave_granite = mat("Plaza Granite", (0.64, 0.65, 0.63), roughness=0.8)
m_pave_cobble = mat("Cobblestone", (0.50, 0.49, 0.46), roughness=0.9)
m_pave_concrete = mat("Paved Concrete", (0.58, 0.60, 0.58), roughness=0.85)
m_alley_asphalt = mat("Alley Asphalt", (0.16, 0.18, 0.20), roughness=0.9)
m_park_grass = mat("Park Turf", (0.26, 0.42, 0.22), roughness=0.95)

# Building Facades
m_brick_red = mat("Brick Red", (0.65, 0.26, 0.20), roughness=0.9)
m_brownstone = mat("Brownstone Stone", (0.44, 0.28, 0.20), roughness=0.85)
m_stone_ivory = mat("Civic Stone Ivory", (0.90, 0.88, 0.82), roughness=0.75)
m_modern_slate = mat("Modern Slate", (0.24, 0.28, 0.32), roughness=0.5)
m_vanilla = mat("Vanilla Plaster", (0.86, 0.80, 0.65), roughness=0.8)
m_sage = mat("Sage Green", (0.43, 0.62, 0.43), roughness=0.8)
m_blue = mat("Powder Blue", (0.40, 0.63, 0.72), roughness=0.8)
m_apricot = mat("Apricot Plaster", (0.90, 0.53, 0.32), roughness=0.8)
m_ochre = mat("Warm Ochre", (0.82, 0.64, 0.38), roughness=0.8)

# Details & Trim
m_dark_metal = mat("Metal Charcoal", (0.14, 0.15, 0.16), roughness=0.35)
m_steel_silver = mat("Steel Silver", (0.75, 0.77, 0.80), roughness=0.3)
m_timber = mat("Timber Brown", (0.36, 0.22, 0.12), roughness=0.8)
m_oak = mat("Honey Oak", (0.56, 0.32, 0.14), roughness=0.75)
m_floor = mat("Interior Floor", (0.52, 0.48, 0.42), roughness=0.8)
m_glass = mat("Window Glass", (0.35, 0.58, 0.72), roughness=0.1)
m_glow_window = mat("Lit Window", (1.0, 0.96, 0.82), emission=(1.0, 0.94, 0.75), emission_strength=2.5)
m_lamp_glow = mat("Streetlight Glow", (1.0, 0.94, 0.72), emission=(1.0, 0.94, 0.72), emission_strength=8.0)
m_awning_red = mat("Awning Crimson", (0.78, 0.22, 0.18), roughness=0.8)
m_awning_blue = mat("Awning Royal Blue", (0.18, 0.32, 0.65), roughness=0.8)
m_awning_green = mat("Awning Forest Green", (0.16, 0.38, 0.22), roughness=0.8)
m_hydrant = mat("Hydrant Red", (0.88, 0.14, 0.10), roughness=0.4)

# Nature
m_leaf1 = mat("Foliage Leaf", (0.28, 0.47, 0.21), roughness=0.9)
m_leaf2 = mat("Foliage Forest", (0.18, 0.36, 0.16), roughness=0.9)
m_leaf3 = mat("Foliage Golden", (0.46, 0.52, 0.22), roughness=0.9)
m_trunk = mat("Tree Trunk", (0.32, 0.20, 0.12), roughness=0.9)

# ---------------------------------------------------------------------------
# Mesh Primitives (from_pydata for high performance)
# ---------------------------------------------------------------------------
def make_box(name, center, size, material, col, parent=None):
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
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_cylinder(name, center, r_bottom, r_top, height, segments, material, col, parent=None):
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
    for i in range(segments):
        i_next = (i + 1) % segments
        faces.append((i, i_next, segments + i_next, segments + i))
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, 2 * segments)))
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_gable_roof(name, center, width, depth, roof_height, overhang, thickness, material, col, parent=None):
    mesh = bpy.data.meshes.new(name)
    w = width + 2 * overhang
    d = depth + 2 * overhang
    hx = w / 2
    hd = d / 2
    rh = roof_height
    th = thickness
    verts = [
        (-hx, -hd, 0), (hx, -hd, 0), (hx, 0, rh), (-hx, 0, rh),
        (-hx, 0, rh), (hx, 0, rh), (hx, hd, 0), (-hx, hd, 0),
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
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

def make_gable_end(name, center, width, depth, rh, th, material, col, is_left=True, parent=None):
    mesh = bpy.data.meshes.new(name)
    x0 = -width/2 if is_left else width/2 - th
    x1 = -width/2 + th if is_left else width/2
    d2 = depth/2 - 0.02
    rh_in = rh - 0.04
    verts = [
        (x0, -d2, 0), (x1, -d2, 0), (x1, d2, 0), (x0, d2, 0),
        (x0, 0, rh_in), (x1, 0, rh_in)
    ]
    faces = [
        (3, 2, 1, 0),
        (0, 4, 3),
        (1, 2, 5),
        (0, 1, 5, 4),
        (3, 4, 5, 2)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if parent:
        obj.parent = parent
    return obj

# ---------------------------------------------------------------------------
# Complex Urban Building Archetypes (All 100% HOLLOW)
# ---------------------------------------------------------------------------
def create_urban_building(name, pos, width, depth, stories=4, story_h=3.5,
                          facade_mat=m_stone_ivory, trim_mat=m_dark_metal,
                          awning_mat=None, has_water_tower=False, has_antenna=False,
                          col=col_buildings, parent=root):
    """Multi-story urban building with walk-in commercial ground floor,
    upper ribbon/grid windows with full piers/mullions, cornice, rooftop parapet,
    AC units, and hollow interiors."""
    anchor = bpy.data.objects.new(name + " | anchor", None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    total_h = stories * story_h
    th = 0.22
    hw, hd = width / 2, depth / 2
    inner_w = width - 2 * th
    inner_d = depth - 2 * th

    # 1. Base Ground Floor Slab (inset to avoid coplanar z-fighting with walls)
    make_box(name + " | ground_slab", (0, 0, 0.08), (inner_w, inner_d, 0.16), m_pave_concrete, col, anchor)

    # 2. Side & Back Walls (Hollow perimeter enclosure without corner overlaps)
    make_box(name + " | wall_left", (-hw + th/2, 0, total_h/2), (th, depth, total_h), facade_mat, col, anchor)
    make_box(name + " | wall_right", (hw - th/2, 0, total_h/2), (th, depth, total_h), facade_mat, col, anchor)
    make_box(name + " | wall_back", (0, hd - th/2, total_h/2), (inner_w, th, total_h), facade_mat, col, anchor)

    # 3. Ground Floor Commercial Entrance & Framed Storefront Windows
    dw, dh = 2.6, 2.6
    pier_w = (inner_w - dw) / 2
    make_box(name + " | GF_header", (0, -hd + th/2, (story_h + dh)/2), (dw, th, story_h - dh), facade_mat, col, anchor)

    # Open walk-in door frame (left/right jambs + top lintel so doorway is unobstructed)
    make_box(name + " | door_jamb_L", (-dw/2 - 0.04, -hd - 0.02, dh/2), (0.08, 0.08, dh), trim_mat, col, anchor)
    make_box(name + " | door_jamb_R", (dw/2 + 0.04, -hd - 0.02, dh/2), (0.08, 0.08, dh), trim_mat, col, anchor)
    make_box(name + " | door_lintel", (0, -hd - 0.02, dh + 0.04), (dw + 0.24, 0.08, 0.08), trim_mat, col, anchor)

    # Storefront display window openings on Left and Right sides of entrance
    disp_w = pier_w * 0.72
    side_m = (pier_w - disp_w) / 2
    disp_sill, disp_h = 0.5, 2.0
    disp_top = disp_sill + disp_h
    for side_tag, cx in [("L", -dw/2 - pier_w/2), ("R", dw/2 + pier_w/2)]:
        make_box(name + f" | GF_sill_{side_tag}", (cx, -hd + th/2, disp_sill/2), (pier_w, th, disp_sill), facade_mat, col, anchor)
        make_box(name + f" | GF_spandrel_{side_tag}", (cx, -hd + th/2, (story_h + disp_top)/2), (pier_w, th, story_h - disp_top), facade_mat, col, anchor)
        make_box(name + f" | GF_pier_out_{side_tag}", (cx - disp_w/2 - side_m/2, -hd + th/2, disp_sill + disp_h/2), (side_m, th, disp_h), facade_mat, col, anchor)
        make_box(name + f" | GF_pier_in_{side_tag}", (cx + disp_w/2 + side_m/2, -hd + th/2, disp_sill + disp_h/2), (side_m, th, disp_h), facade_mat, col, anchor)
        make_box(name + f" | glass_display_{side_tag}", (cx, -hd + th/2, disp_sill + disp_h/2), (disp_w, 0.06, disp_h), m_glass, col, anchor)

    # Optional Canvas Awning / Marquee
    if awning_mat:
        make_box(name + " | awning", (0, -hd - 1.2, dh + 0.1), (width * 0.85, 2.2, 0.16), awning_mat, col, anchor)
    else:
        make_box(name + " | canopy", (0, -hd - 1.0, dh + 0.2), (dw + 1.2, 2.0, 0.15), trim_mat, col, anchor)
    make_box(name + " | signboard", (0, -hd - 0.1, dh + 0.55), (width * 0.6, 0.18, 0.55), trim_mat, col, anchor)

    # 4. Upper Floors Facade (Complete sills, headers, side piers, center mullion pier, and windows)
    win_w = inner_w * 0.38
    center_pier_w = inner_w * 0.10
    edge_pier_w = (inner_w - 2 * win_w - center_pier_w) / 2
    for s in range(1, stories):
        base_z = s * story_h
        sill_h, head_h = 0.9, 0.7
        win_h = story_h - sill_h - head_h
        win_z = base_z + sill_h + win_h / 2
        make_box(name + f" | front_F{s}_sill", (0, -hd + th/2, base_z + sill_h/2), (inner_w, th, sill_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_header", (0, -hd + th/2, base_z + story_h - head_h/2), (inner_w, th, head_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_pier_L", (-inner_w/2 + edge_pier_w/2, -hd + th/2, win_z), (edge_pier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_pier_C", (0, -hd + th/2, win_z), (center_pier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_pier_R", (inner_w/2 - edge_pier_w/2, -hd + th/2, win_z), (edge_pier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_win_L", (-center_pier_w/2 - win_w/2, -hd + th/2, win_z), (win_w, 0.06, win_h), m_glass, col, anchor)
        make_box(name + f" | front_F{s}_win_R", (center_pier_w/2 + win_w/2, -hd + th/2, win_z), (win_w, 0.06, win_h), m_glass, col, anchor)

    # 5. Hollow Interior Upper Floors (with central stair opening and rear connecting landing)
    stair_w, stair_d = 3.5, 4.2
    side_slab_w = (inner_w - stair_w) / 2
    rear_walk_d = (inner_d - stair_d) / 2
    for s in range(1, stories):
        fz = s * story_h
        make_box(name + f" | slab_F{s}_L", (-inner_w/2 + side_slab_w/2, 0, fz), (side_slab_w, inner_d, 0.16), m_floor, col, anchor)
        make_box(name + f" | slab_F{s}_R", (inner_w/2 - side_slab_w/2, 0, fz), (side_slab_w, inner_d, 0.16), m_floor, col, anchor)
        make_box(name + f" | slab_F{s}_rear", (0, inner_d/2 - rear_walk_d/2, fz), (stair_w, rear_walk_d, 0.16), m_floor, col, anchor)

    # Hollow lobby columns (Ground floor)
    cx, cy = hw * 0.45, hd * 0.35
    for px in [-cx, cx]:
        for py in [-cy, cy]:
            make_box(name + f" | pillar_{px:.0f}_{py:.0f}", (px, py, story_h/2), (0.45, 0.45, story_h), trim_mat, col, anchor)

    # 6. Roof & Parapet
    make_box(name + " | roof_slab", (0, 0, total_h), (inner_w, inner_d, 0.22), m_floor, col, anchor)
    make_box(name + " | cornice", (0, -hd - 0.15, total_h + 0.15), (width + 0.4, 0.35, 0.35), trim_mat, col, anchor)
    # Parapets
    para_h = 0.85
    make_box(name + " | parapet_F", (0, -hd + th/2, total_h + para_h/2), (inner_w, th, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_B", (0, hd - th/2, total_h + para_h/2), (inner_w, th, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_L", (-hw + th/2, 0, total_h + para_h/2), (th, depth, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_R", (hw - th/2, 0, total_h + para_h/2), (th, depth, para_h), facade_mat, col, anchor)

    # Rooftop Structures
    make_box(name + " | penthouse", (0, hd * 0.25, total_h + 1.25), (3.2, 3.8, 2.5), facade_mat, col, anchor)
    make_box(name + " | ac_unit_1", (-hw * 0.35, -hd * 0.2, total_h + 0.6), (1.8, 1.4, 1.2), m_dark_metal, col, anchor)
    make_box(name + " | ac_unit_2", (hw * 0.35, -hd * 0.2, total_h + 0.6), (1.8, 1.4, 1.2), m_dark_metal, col, anchor)

    if has_water_tower:
        create_water_tower(name + " | water_tower", (hw * 0.45, hd * 0.35, total_h + 0.2), col, anchor)

    if has_antenna:
        create_antenna_mast(name + " | antenna", (-hw * 0.45, hd * 0.35, total_h + 0.2), col, anchor)

    return anchor

def create_urban_townhome(name, pos, width=11.0, depth=10.0, stories=3,
                          facade_mat=m_brownstone, trim_mat=m_dark_metal,
                          col=col_buildings, parent=root):
    """Classic Brownstone / Rowhouse with elevated stoop stairs, 2-story hollow bay window,
    complete upper-floor front walls, walk-in doorway, hollow floors, and decorative cornice."""
    anchor = bpy.data.objects.new(name + " | anchor", None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    stoop_h = 0.8
    sh = 3.0
    wall_total_h = stories * sh
    total_h = stoop_h + wall_total_h
    th = 0.20
    hw, hd = width / 2, depth / 2
    inner_w = width - 2 * th
    inner_d = depth - 2 * th
    half_w = inner_w / 2
    cx_L = -half_w / 2
    cx_R = half_w / 2

    # 1. Foundation Plinth (z = 0 to stoop_h) & Inset Ground Floor Slab (zero z-fighting)
    make_box(name + " | base_plinth_L", (-hw + th/2, 0, stoop_h/2), (th, depth, stoop_h), m_stone_ivory, col, anchor)
    make_box(name + " | base_plinth_R", (hw - th/2, 0, stoop_h/2), (th, depth, stoop_h), m_stone_ivory, col, anchor)
    make_box(name + " | base_plinth_B", (0, hd - th/2, stoop_h/2), (inner_w, th, stoop_h), m_stone_ivory, col, anchor)
    make_box(name + " | base_plinth_F", (0, -hd + th/2, stoop_h/2), (inner_w, th, stoop_h), m_stone_ivory, col, anchor)
    make_box(name + " | floor_elevated", (0, 0, stoop_h - 0.08), (inner_w, inner_d, 0.16), m_floor, col, anchor)

    # 2. Exterior Hollow Perimeter Walls (z = stoop_h to total_h)
    make_box(name + " | wall_left", (-hw + th/2, 0, stoop_h + wall_total_h/2), (th, depth, wall_total_h), facade_mat, col, anchor)
    make_box(name + " | wall_right", (hw - th/2, 0, stoop_h + wall_total_h/2), (th, depth, wall_total_h), facade_mat, col, anchor)
    make_box(name + " | wall_back", (0, hd - th/2, stoop_h + wall_total_h/2), (inner_w, th, wall_total_h), facade_mat, col, anchor)

    # 3. Front Facade - Left Bay (Walk-in Entrance on GF + Framed Windows on Upper Floors)
    door_x = cx_L
    dw, dh = 1.4, 2.2
    gf_pier_w = (half_w - dw) / 2
    make_box(name + " | front_GF_L_pier1", (door_x - dw/2 - gf_pier_w/2, -hd + th/2, stoop_h + sh/2), (gf_pier_w, th, sh), facade_mat, col, anchor)
    make_box(name + " | front_GF_L_pier2", (door_x + dw/2 + gf_pier_w/2, -hd + th/2, stoop_h + sh/2), (gf_pier_w, th, sh), facade_mat, col, anchor)
    make_box(name + " | front_GF_L_header", (door_x, -hd + th/2, stoop_h + dh + (sh - dh)/2), (dw, th, sh - dh), facade_mat, col, anchor)

    # Open doorframe around doorway
    make_box(name + " | door_jamb_L", (door_x - dw/2 - 0.04, -hd - 0.02, stoop_h + dh/2), (0.08, 0.08, dh), trim_mat, col, anchor)
    make_box(name + " | door_jamb_R", (door_x + dw/2 + 0.04, -hd - 0.02, stoop_h + dh/2), (0.08, 0.08, dh), trim_mat, col, anchor)
    make_box(name + " | door_lintel", (door_x, -hd - 0.02, stoop_h + dh + 0.04), (dw + 0.24, 0.08, 0.08), trim_mat, col, anchor)

    # Front Stoop Stairs & Railings leading up to doorway
    stoop_len = 2.4
    for step in range(5):
        s_z = (step + 1) * (stoop_h / 5)
        s_y = -hd - stoop_len + (step + 0.5) * (stoop_len / 5)
        make_box(name + f" | step_{step}", (door_x, s_y, s_z/2), (dw + 0.6, stoop_len / 5 + 0.02, s_z), m_stone_ivory, col, anchor)
    make_box(name + " | stoop_rail_L", (door_x - dw/2 - 0.25, -hd - stoop_len/2, stoop_h + 0.45), (0.06, stoop_len, 0.9), trim_mat, col, anchor)
    make_box(name + " | stoop_rail_R", (door_x + dw/2 + 0.25, -hd - stoop_len/2, stoop_h + 0.45), (0.06, stoop_len, 0.9), trim_mat, col, anchor)

    # Upper Story Front Walls & Windows on Left Bay
    sill_h, win_h = 0.85, 1.4
    head_h = sh - sill_h - win_h
    win_w_L = 1.6
    wpier_L = (half_w - win_w_L) / 2
    for s in range(1, stories):
        base_z = stoop_h + s * sh
        wz = base_z + sill_h + win_h / 2
        make_box(name + f" | front_F{s}_L_sill", (cx_L, -hd + th/2, base_z + sill_h/2), (half_w, th, sill_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_L_header", (cx_L, -hd + th/2, base_z + sill_h + win_h + head_h/2), (half_w, th, head_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_L_pier1", (door_x - win_w_L/2 - wpier_L/2, -hd + th/2, wz), (wpier_L, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_L_pier2", (door_x + win_w_L/2 + wpier_L/2, -hd + th/2, wz), (wpier_L, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | win_F{s}_L", (door_x, -hd + th/2, wz), (win_w_L, 0.06, win_h), m_glass, col, anchor)
        make_box(name + f" | win_sill_F{s}_L", (door_x, -hd - 0.04, base_z + sill_h - 0.05), (win_w_L + 0.2, 0.10, 0.10), m_stone_ivory, col, anchor)

    # 4. Front Facade - Right Bay (2-Story Hollow Bay Projection + Top Floor Front Wall)
    bay_x = cx_R
    bay_w = half_w * 0.76
    bay_d = 0.75
    flank_w = (half_w - bay_w) / 2
    bay_stories = min(2, stories)
    bay_h = bay_stories * sh

    # Flank walls flush with main front facade beside the bay window
    make_box(name + " | bay_flank_L", (bay_x - bay_w/2 - flank_w/2, -hd + th/2, stoop_h + bay_h/2), (flank_w, th, bay_h), facade_mat, col, anchor)
    make_box(name + " | bay_flank_R", (bay_x + bay_w/2 + flank_w/2, -hd + th/2, stoop_h + bay_h/2), (flank_w, th, bay_h), facade_mat, col, anchor)

    # Projecting bay side walls, foundation plinth, and top cornice cap
    make_box(name + " | bay_base", (bay_x, -hd - bay_d/2, stoop_h/2), (bay_w, bay_d, stoop_h), m_stone_ivory, col, anchor)
    make_box(name + " | bay_wall_L", (bay_x - bay_w/2 + th/2, -hd - bay_d/2, stoop_h + bay_h/2), (th, bay_d, bay_h), facade_mat, col, anchor)
    make_box(name + " | bay_wall_R", (bay_x + bay_w/2 - th/2, -hd - bay_d/2, stoop_h + bay_h/2), (th, bay_d, bay_h), facade_mat, col, anchor)
    make_box(name + " | bay_roof_cap", (bay_x, -hd - bay_d/2, stoop_h + bay_h - 0.08), (bay_w + 0.16, bay_d + 0.12, 0.16), m_stone_ivory, col, anchor)

    # Bay front wall & windows on stories 0 and 1
    bay_in_w = bay_w - 2 * th
    bwin_w = bay_in_w * 0.80
    bpier_w = (bay_in_w - bwin_w) / 2
    for s in range(bay_stories):
        base_z = stoop_h + s * sh
        wz = base_z + sill_h + win_h / 2
        make_box(name + f" | bay_F{s}_sill", (bay_x, -hd - bay_d + th/2, base_z + sill_h/2), (bay_in_w, th, sill_h), facade_mat, col, anchor)
        make_box(name + f" | bay_F{s}_header", (bay_x, -hd - bay_d + th/2, base_z + sill_h + win_h + head_h/2), (bay_in_w, th, head_h), facade_mat, col, anchor)
        make_box(name + f" | bay_F{s}_pier_L", (bay_x - bwin_w/2 - bpier_w/2, -hd - bay_d + th/2, wz), (bpier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | bay_F{s}_pier_R", (bay_x + bwin_w/2 + bpier_w/2, -hd - bay_d + th/2, wz), (bpier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | bay_glass_F{s}", (bay_x, -hd - bay_d + th/2, wz), (bwin_w, 0.06, win_h), m_glass, col, anchor)

    # Right Bay Top Story Front Wall (above the 2-story bay window)
    rwin_w = bay_in_w * 0.80
    rpier_w = (half_w - rwin_w) / 2
    for s in range(bay_stories, stories):
        base_z = stoop_h + s * sh
        wz = base_z + sill_h + win_h / 2
        make_box(name + f" | front_F{s}_R_sill", (cx_R, -hd + th/2, base_z + sill_h/2), (half_w, th, sill_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_R_header", (cx_R, -hd + th/2, base_z + sill_h + win_h + head_h/2), (half_w, th, head_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_R_pier1", (cx_R - rwin_w/2 - rpier_w/2, -hd + th/2, wz), (rpier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | front_F{s}_R_pier2", (cx_R + rwin_w/2 + rpier_w/2, -hd + th/2, wz), (rpier_w, th, win_h), facade_mat, col, anchor)
        make_box(name + f" | win_F{s}_R", (cx_R, -hd + th/2, wz), (rwin_w, 0.06, win_h), m_glass, col, anchor)
        make_box(name + f" | win_sill_F{s}_R", (cx_R, -hd - 0.04, base_z + sill_h - 0.05), (rwin_w + 0.2, 0.10, 0.10), m_stone_ivory, col, anchor)

    # 5. Interior Partition Wall (with connecting doorways) & Upper Floor Slabs
    idw, idh = 1.2, 2.1
    ipier_d = (inner_d - idw) / 2
    for s in range(stories):
        base_z = stoop_h + s * sh
        make_box(name + f" | interior_part_F{s}_1", (0, -inner_d/2 + ipier_d/2, base_z + sh/2), (th, ipier_d, sh), facade_mat, col, anchor)
        make_box(name + f" | interior_part_F{s}_2", (0, inner_d/2 - ipier_d/2, base_z + sh/2), (th, ipier_d, sh), facade_mat, col, anchor)
        make_box(name + f" | interior_part_F{s}_hdr", (0, 0, base_z + idh + (sh - idh)/2), (th, idw, sh - idh), facade_mat, col, anchor)

    stair_w = 2.6
    for s in range(1, stories):
        fz = stoop_h + s * sh
        make_box(name + f" | slab_F{s}_L", (cx_L, 0, fz), (half_w - th/2, inner_d, 0.16), m_floor, col, anchor)
        make_box(name + f" | slab_F{s}_R", (cx_R + stair_w/2, 0, fz), (half_w - th/2 - stair_w, inner_d, 0.16), m_floor, col, anchor)

    # 6. Roof Slab, Parapet & Cornice
    make_box(name + " | roof_slab", (0, 0, total_h), (inner_w, inner_d, 0.20), m_floor, col, anchor)
    para_h = 0.45
    make_box(name + " | parapet_F", (0, -hd + th/2, total_h + para_h/2), (inner_w, th, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_B", (0, hd - th/2, total_h + para_h/2), (inner_w, th, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_L", (-hw + th/2, 0, total_h + para_h/2), (th, depth, para_h), facade_mat, col, anchor)
    make_box(name + " | parapet_R", (hw - th/2, 0, total_h + para_h/2), (th, depth, para_h), facade_mat, col, anchor)
    make_box(name + " | cornice", (0, -hd - 0.15, total_h + 0.22), (width + 0.4, 0.35, 0.45), m_stone_ivory, col, anchor)
    make_box(name + " | chimney", (hw - 1.2, hd * 0.3, total_h + 1.2), (0.7, 0.7, 2.0), m_brick_red, col, anchor)

    return anchor

def create_urban_cottage(name, pos, width=12.0, depth=9.5, wall_h=3.2, roof_h=2.2,
                         wall_mat=m_vanilla, roof_mat=m_dark_metal, col=col_houses, parent=root):
    """Hollow single-story or 1.5-story cottage/house with porch, framed windows, and interior doorway."""
    anchor = bpy.data.objects.new(name + " | anchor", None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos

    th = 0.16
    hw, hd = width / 2, depth / 2
    inner_w = width - 2 * th
    inner_d = depth - 2 * th
    half_w = inner_w / 2
    cx_L = -half_w / 2

    make_box(name + " | floor", (0, 0, 0.05), (inner_w, inner_d, 0.10), m_floor, col, anchor)
    make_box(name + " | wall_L", (-hw + th/2, 0, wall_h/2), (th, depth, wall_h), wall_mat, col, anchor)
    make_box(name + " | wall_R", (hw - th/2, 0, wall_h/2), (th, depth, wall_h), wall_mat, col, anchor)
    make_box(name + " | wall_B", (0, hd - th/2, wall_h/2), (inner_w, th, wall_h), wall_mat, col, anchor)

    # Front door on right side of center (x from 0 to dw) & framed window opening on left half
    dw, dh = 1.3, 2.2
    right_pier_w = half_w - dw
    make_box(name + " | front_wall_R", (dw + right_pier_w/2, -hd + th/2, wall_h/2), (right_pier_w, th, wall_h), wall_mat, col, anchor)
    make_box(name + " | front_header", (dw/2, -hd + th/2, (wall_h + dh)/2), (dw, th, wall_h - dh), wall_mat, col, anchor)
    make_box(name + " | door_jamb_L", (0.03, -hd - 0.02, dh/2), (0.06, 0.06, dh), m_timber, col, anchor)
    make_box(name + " | door_jamb_R", (dw - 0.03, -hd - 0.02, dh/2), (0.06, 0.06, dh), m_timber, col, anchor)

    # Left half front wall with framed window opening
    win_w, sill_h, win_h = 1.8, 0.9, 1.2
    head_h = wall_h - sill_h - win_h
    wpier_w = (half_w - win_w) / 2
    make_box(name + " | front_L_sill", (cx_L, -hd + th/2, sill_h/2), (half_w, th, sill_h), wall_mat, col, anchor)
    make_box(name + " | front_L_header", (cx_L, -hd + th/2, sill_h + win_h + head_h/2), (half_w, th, head_h), wall_mat, col, anchor)
    make_box(name + " | front_L_pier1", (cx_L - win_w/2 - wpier_w/2, -hd + th/2, sill_h + win_h/2), (wpier_w, th, win_h), wall_mat, col, anchor)
    make_box(name + " | front_L_pier2", (cx_L + win_w/2 + wpier_w/2, -hd + th/2, sill_h + win_h/2), (wpier_w, th, win_h), wall_mat, col, anchor)
    make_box(name + " | front_win", (cx_L, -hd + th/2, sill_h + win_h/2), (win_w, 0.05, win_h), m_glass, col, anchor)
    make_box(name + " | front_win_sill", (cx_L, -hd - 0.03, sill_h - 0.04), (win_w + 0.16, 0.08, 0.08), m_timber, col, anchor)

    # Porch
    make_box(name + " | porch_slab", (dw/2, -hd - 0.9, 0.06), (2.4, 1.8, 0.12), m_pave_concrete, col, anchor)
    make_box(name + " | porch_roof", (dw/2, -hd - 0.9, 2.7), (2.6, 2.0, 0.12), roof_mat, col, anchor)
    make_box(name + " | porch_post_L", (dw/2 - 1.0, -hd - 1.6, 1.35), (0.14, 0.14, 2.6), m_timber, col, anchor)
    make_box(name + " | porch_post_R", (dw/2 + 1.0, -hd - 1.6, 1.35), (0.14, 0.14, 2.6), m_timber, col, anchor)

    # Interior partition with doorway opening (centered at y=0 so it never pokes through wall_B)
    idw, idh = 1.1, 2.1
    ipier_d = (inner_d - idw) / 2
    make_box(name + " | interior_wall_1", (0, -inner_d/2 + ipier_d/2, wall_h/2), (th, ipier_d, wall_h), wall_mat, col, anchor)
    make_box(name + " | interior_wall_2", (0, inner_d/2 - ipier_d/2, wall_h/2), (th, ipier_d, wall_h), wall_mat, col, anchor)
    make_box(name + " | interior_wall_hdr", (0, 0, idh + (wall_h - idh)/2), (th, idw, wall_h - idh), wall_mat, col, anchor)

    # Roof & Chimney
    make_gable_roof(name + " | roof", (0, 0, wall_h), width, depth, roof_h, 0.45, 0.14, roof_mat, col, anchor)
    make_gable_end(name + " | gable_L", (0, 0, wall_h), width, depth, roof_h, th, wall_mat, col, is_left=True, parent=anchor)
    make_gable_end(name + " | gable_R", (0, 0, wall_h), width, depth, roof_h, th, wall_mat, col, is_left=False, parent=anchor)
    make_box(name + " | chimney", (hw - 1.2, hd * 0.3, wall_h + roof_h * 0.65), (0.7, 0.7, 1.8), m_brick_red, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# Urban Props (Street Furniture, Roof Details, Infrastructure)
# ---------------------------------------------------------------------------
def create_water_tower(name, pos, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    # 4 Steel lattice legs
    for lx in [-0.85, 0.85]:
        for ly in [-0.85, 0.85]:
            make_cylinder(name + f"_leg_{lx}_{ly}", (lx, ly, 1.4), 0.07, 0.06, 2.8, 6, m_dark_metal, col, anchor)
    # Cross braces
    make_box(name + "_brace_X", (0, 0, 1.4), (1.7, 0.06, 0.06), m_dark_metal, col, anchor)
    make_box(name + "_brace_Y", (0, 0, 1.4), (0.06, 1.7, 0.06), m_dark_metal, col, anchor)
    make_box(name + "_platform", (0, 0, 2.8), (2.4, 2.4, 0.14), m_dark_metal, col, anchor)
    # Timber Water Tank
    make_cylinder(name + "_tank", (0, 0, 4.0), 1.1, 1.1, 2.2, 12, m_timber, col, anchor)
    # Conical Roof
    make_cylinder(name + "_cap", (0, 0, 5.35), 1.25, 0.05, 0.6, 12, m_dark_metal, col, anchor)
    return anchor

def create_antenna_mast(name, pos, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    make_cylinder(name + "_base", (0, 0, 0.4), 0.35, 0.25, 0.8, 6, m_dark_metal, col, anchor)
    make_cylinder(name + "_mast", (0, 0, 3.5), 0.12, 0.04, 6.2, 6, m_steel_silver, col, anchor)
    make_cylinder(name + "_beacon", (0, 0, 6.7), 0.08, 0.08, 0.18, 6, m_hydrant, col, anchor)
    return anchor

def create_bus_shelter(name, pos, yaw=0.0, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    anchor.rotation_euler.z = yaw
    # Concrete platform
    make_box(name + "_slab", (0, 0, 0.04), (3.6, 1.8, 0.08), m_pave_concrete, col, anchor)
    # Steel frame posts
    for px in [-1.6, 1.6]:
        make_box(name + f"_post_{px}", (px, 0.7, 1.25), (0.08, 0.08, 2.4), m_dark_metal, col, anchor)
    # Glass rear wall
    make_box(name + "_rear_glass", (0, 0.7, 1.3), (3.1, 0.04, 2.0), m_glass, col, anchor)
    # Cantilevered Roof
    make_box(name + "_roof", (0, 0.1, 2.5), (3.8, 2.2, 0.12), m_dark_metal, col, anchor)
    # Bench inside
    make_box(name + "_bench", (0, 0.4, 0.45), (2.4, 0.4, 0.08), m_timber, col, anchor)
    # Ad display panel
    make_box(name + "_ad_panel", (1.6, 0.1, 1.3), (0.10, 0.8, 1.8), m_glow_window, col, anchor)
    return anchor

def create_bench(name, pos, yaw=0.0, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    anchor.rotation_euler.z = yaw
    # Cast iron legs
    for lx in [-0.8, 0.8]:
        make_box(name + f"_leg_{lx}", (lx, 0, 0.22), (0.08, 0.45, 0.45), m_dark_metal, col, anchor)
        make_box(name + f"_backpost_{lx}", (lx, 0.2, 0.55), (0.08, 0.08, 0.7), m_dark_metal, col, anchor)
    # Timber seat & back slats
    make_box(name + "_seat", (0, 0, 0.45), (1.9, 0.45, 0.06), m_timber, col, anchor)
    make_box(name + "_back", (0, 0.2, 0.75), (1.9, 0.06, 0.35), m_timber, col, anchor)
    return anchor

def create_trash_bin(name, pos, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    make_cylinder(name + "_body", (0, 0, 0.45), 0.26, 0.26, 0.9, 10, m_dark_metal, col, anchor)
    make_cylinder(name + "_lid", (0, 0, 0.95), 0.28, 0.24, 0.12, 10, m_modern_slate, col, anchor)
    return anchor

def create_fire_hydrant(name, pos, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    make_cylinder(name + "_base", (0, 0, 0.15), 0.18, 0.16, 0.3, 8, m_hydrant, col, anchor)
    make_cylinder(name + "_body", (0, 0, 0.45), 0.14, 0.14, 0.35, 8, m_hydrant, col, anchor)
    make_cylinder(name + "_bonnet", (0, 0, 0.68), 0.15, 0.06, 0.15, 8, m_hydrant, col, anchor)
    make_box(name + "_caps", (0, 0, 0.45), (0.42, 0.10, 0.10), m_hydrant, col, anchor)
    return anchor

def create_bike_rack(name, pos, yaw=0.0, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    anchor.rotation_euler.z = yaw
    for rx in [-0.6, 0.0, 0.6]:
        make_box(name + f"_hoop_{rx}", (rx, 0, 0.45), (0.06, 0.75, 0.9), m_steel_silver, col, anchor)
    return anchor

def create_fountain(name, pos, col=col_props, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    make_cylinder(name + "_basin", (0, 0, 0.25), 3.2, 3.0, 0.5, 16, m_stone_ivory, col, anchor)
    make_cylinder(name + "_water", (0, 0, 0.35), 2.8, 2.8, 0.04, 16, m_glass, col, anchor)
    make_cylinder(name + "_pillar", (0, 0, 0.85), 0.5, 0.4, 0.8, 8, m_stone_ivory, col, anchor)
    make_cylinder(name + "_tier2", (0, 0, 1.25), 1.5, 1.4, 0.25, 12, m_stone_ivory, col, anchor)
    make_cylinder(name + "_finial", (0, 0, 1.7), 0.2, 0.05, 0.6, 8, m_stone_ivory, col, anchor)
    return anchor

# ---------------------------------------------------------------------------
# Streetlights & Trees
# ---------------------------------------------------------------------------
def create_streetlight(name, pos, yaw=0.0, col=col_lights, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    anchor.rotation_euler.z = yaw
    make_cylinder(name + "_base", (0, 0, 0.12), 0.22, 0.18, 0.24, 8, m_dark_metal, col, anchor)
    make_cylinder(name + "_pole", (0, 0, 2.15), 0.10, 0.07, 4.1, 8, m_dark_metal, col, anchor)
    make_cylinder(name + "_collar", (0, 0, 4.15), 0.12, 0.10, 0.12, 8, m_dark_metal, col, anchor)
    make_box(name + "_arm", (0, 0.55, 4.3), (0.08, 1.1, 0.08), m_dark_metal, col, anchor)
    make_box(name + "_hood", (0, 1.1, 4.25), (0.35, 0.45, 0.14), m_dark_metal, col, anchor)
    make_box(name + "_bulb", (0, 1.1, 4.14), (0.24, 0.32, 0.10), m_lamp_glow, col, anchor)
    return anchor

def create_tree(name, pos, scale=1.0, tree_type="round", foliage_mat=m_leaf1, col=col_trees, parent=root):
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    anchor.parent = parent
    anchor.location = pos
    if tree_type == "round":
        trunk_h = 2.4 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.22 * scale, 0.14 * scale, trunk_h, 7, m_trunk, col, anchor)
        make_cylinder(name + "_foliage_base", (0, 0, trunk_h + 0.8 * scale), 1.9 * scale, 1.6 * scale, 1.4 * scale, 8, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_mid", (0.2 * scale, -0.1 * scale, trunk_h + 1.8 * scale), 1.5 * scale, 1.0 * scale, 1.3 * scale, 8, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_top", (-0.1 * scale, 0.1 * scale, trunk_h + 2.6 * scale), 0.9 * scale, 0.3 * scale, 1.0 * scale, 7, foliage_mat, col, anchor)
    elif tree_type == "boulevard":
        trunk_h = 2.9 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.16 * scale, 0.10 * scale, trunk_h, 6, m_trunk, col, anchor)
        make_cylinder(name + "_foliage_1", (0, 0, trunk_h + 0.7 * scale), 1.3 * scale, 1.1 * scale, 1.2 * scale, 7, foliage_mat, col, anchor)
        make_cylinder(name + "_foliage_2", (0, 0, trunk_h + 1.6 * scale), 1.0 * scale, 0.4 * scale, 1.1 * scale, 7, foliage_mat, col, anchor)
        make_box(name + "_grate", (0, 0, 0.02), (1.4 * scale, 1.4 * scale, 0.04), m_dark_metal, col, anchor)
    elif tree_type == "pine":
        trunk_h = 1.6 * scale
        make_cylinder(name + "_trunk", (0, 0, trunk_h / 2), 0.20 * scale, 0.12 * scale, trunk_h, 6, m_trunk, col, anchor)
        make_cylinder(name + "_tier_1", (0, 0, trunk_h + 0.7 * scale), 1.8 * scale, 0.8 * scale, 1.3 * scale, 7, m_leaf2, col, anchor)
        make_cylinder(name + "_tier_2", (0, 0, trunk_h + 1.7 * scale), 1.3 * scale, 0.5 * scale, 1.2 * scale, 7, m_leaf2, col, anchor)
        make_cylinder(name + "_tier_3", (0, 0, trunk_h + 2.5 * scale), 0.8 * scale, 0.1 * scale, 1.1 * scale, 6, m_leaf2, col, anchor)
    return anchor

# ---------------------------------------------------------------------------
# City Clean & Clear for Regenerating
# ---------------------------------------------------------------------------
print("Rebuilding dense urban city...")
for c in [col_pavement, col_buildings, col_houses, col_props, col_lights, col_trees]:
    for obj in list(c.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

# ---------------------------------------------------------------------------
# 1. URBAN GROUND PAVEMENT & INTERNAL ALLEYS
# ---------------------------------------------------------------------------
# Block 22: Downtown Central Plaza Ground
make_box("Pavement | Block 22 Plaza", (0, 0, 0.105), (89.6, 39.6, 0.02), m_pave_granite, col_pavement)
# Block 12: Civic & University Promenade Ground
make_box("Pavement | Block 12 Campus", (0, 52, 0.105), (89.6, 39.6, 0.02), m_pave_concrete, col_pavement)
# Block 21: Urban Mixed-Use Pavement with Central Asphalt Alley
make_box("Pavement | Block 21 Base", (-102, 0, 0.105), (89.6, 39.6, 0.02), m_pave_concrete, col_pavement)
make_box("Pavement | Block 21 Alley", (-102, 0, 0.11), (89.6, 6.0, 0.015), m_alley_asphalt, col_pavement)
# Block 23: Commercial Boulevard Ground
make_box("Pavement | Block 23 Base", (102, 0, 0.105), (89.6, 39.6, 0.02), m_pave_concrete, col_pavement)
make_box("Pavement | Block 23 Alley", (102, 0, 0.11), (89.6, 6.0, 0.015), m_alley_asphalt, col_pavement)
# Block 11: Historic Cobbled Square
make_box("Pavement | Block 11 Cobblestone", (-102, 52, 0.105), (89.6, 39.6, 0.02), m_pave_cobble, col_pavement)
# Block 32: Brownstone Residential Pavement
make_box("Pavement | Block 32 Base", (0, -52, 0.105), (89.6, 39.6, 0.02), m_pave_concrete, col_pavement)
# Block 33: Civic Park & Waterfront Plaza (West Paved, East Lush Park)
make_box("Pavement | Block 33 Civic Plaza", (72, -52, 0.105), (30.0, 39.6, 0.02), m_pave_granite, col_pavement)
make_box("Pavement | Block 33 Park Turf", (117, -52, 0.105), (59.6, 39.6, 0.02), m_park_grass, col_pavement)
# Diagonal Park Promenades
make_box("Pavement | Block 33 Park Walk 1", (117, -52, 0.11), (50.0, 3.2, 0.015), m_pave_cobble, col_pavement)

# ---------------------------------------------------------------------------
# 2. BLOCK 22: HIGH-DENSITY CENTRAL DOWNTOWN (8 Towers/Mid-Rises + Grand Plaza)
# ---------------------------------------------------------------------------
# North Row (Y = 11, facing Y = 26 avenue)
create_urban_building("B22-N1 | Financial Office Tower", (-33, 11, 0.10), 20, 14, stories=6, story_h=3.6,
                      facade_mat=m_modern_slate, trim_mat=m_dark_metal, has_water_tower=True, has_antenna=True)
create_urban_building("B22-N2 | Metropolitan Bank & Trust", (-11, 11, 0.10), 20, 14, stories=5, story_h=3.5,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, awning_mat=m_awning_blue)
create_urban_building("B22-N3 | Tech Innovation Hub", (11, 11, 0.10), 20, 14, stories=5, story_h=3.5,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, has_water_tower=True)
create_urban_building("B22-N4 | Grand Hotel & Suites", (33, 11, 0.10), 20, 14, stories=6, story_h=3.6,
                      facade_mat=m_ochre, trim_mat=m_dark_metal, awning_mat=m_awning_red, has_antenna=True)

# South Row (Y = -11, facing Y = -26 avenue)
create_urban_building("B22-S1 | Grand Department Store", (-33, -11, 0.10), 20, 14, stories=4, story_h=3.8,
                      facade_mat=m_vanilla, trim_mat=m_dark_metal, awning_mat=m_awning_green)
create_urban_building("B22-S2 | Downtown Cinema & Arts", (-11, -11, 0.10), 20, 14, stories=4, story_h=3.6,
                      facade_mat=m_modern_slate, trim_mat=m_steel_silver, awning_mat=m_awning_red)
create_urban_building("B22-S3 | City Medical & Pharmacy", (11, -11, 0.10), 20, 14, stories=4, story_h=3.5,
                      facade_mat=m_blue, trim_mat=m_dark_metal)
create_urban_building("B22-S4 | Central Plaza Bistro & Lofts", (33, -11, 0.10), 20, 14, stories=5, story_h=3.4,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, awning_mat=m_awning_blue, has_water_tower=True)

# Central Downtown Plaza Features
create_fountain("Downtown | Grand Fountain", (0, 0, 0.11))
for bx in [-8, 8]:
    for by in [-3, 3]:
        create_bench(f"Downtown | bench ({bx},{by})", (bx, by, 0.11), yaw=math.radians(90 if bx < 0 else -90))
        create_trash_bin(f"Downtown | bin ({bx},{by})", (bx, by + 1.2, 0.11))

# ---------------------------------------------------------------------------
# 3. BLOCK 12: CIVIC & UNIVERSITY DISTRICT (7 Buildings + Quad)
# ---------------------------------------------------------------------------
# North Row (Y = 63, facing Y = 78 avenue)
create_urban_building("B12-N1 | University Science Center", (-33, 63, 0.10), 20, 14, stories=5, story_h=3.4,
                      facade_mat=m_modern_slate, trim_mat=m_steel_silver, has_antenna=True)
create_urban_building("B12-N2 | Central Public Library", (0, 63, 0.10), 26, 14, stories=4, story_h=3.8,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal)
create_urban_building("B12-N3 | Student Housing & Union", (33, 63, 0.10), 20, 14, stories=5, story_h=3.4,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, has_water_tower=True)

# South Row (Y = 41, facing Y = 26 avenue)
create_urban_building("B12-S1 | University Bookstore", (-33, 41, 0.10), 20, 14, stories=3, story_h=3.5,
                      facade_mat=m_ochre, trim_mat=m_dark_metal, awning_mat=m_awning_green)
create_urban_building("B12-S2 | Fine Arts Gallery", (-11, 41, 0.10), 20, 14, stories=3, story_h=3.6,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal)
create_urban_building("B12-S3 | Campus Market & Deli", (11, 41, 0.10), 20, 14, stories=3, story_h=3.5,
                      facade_mat=m_sage, trim_mat=m_timber, awning_mat=m_awning_red)
create_urban_building("B12-S4 | Research Innovation Lab", (33, 41, 0.10), 20, 14, stories=4, story_h=3.5,
                      facade_mat=m_blue, trim_mat=m_dark_metal)

# ---------------------------------------------------------------------------
# 4. BLOCK 21: URBAN MIXED-USE RESIDENTIAL & SHOPS (8 Dense Buildings)
# ---------------------------------------------------------------------------
# North Row (Y = 11, facing Y = 26 avenue)
create_urban_building("B21-N1 | Urban Lofts & Bakery", (-136, 11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, awning_mat=m_awning_red)
create_urban_building("B21-N2 | Avenue Apartments & Florist", (-114, 11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_ochre, trim_mat=m_dark_metal, awning_mat=m_awning_green)
create_urban_building("B21-N3 | Metro Walkup & Tailor", (-90, 11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_vanilla, trim_mat=m_dark_metal)
create_urban_building("B21-N4 | Corner Trattoria & Flats", (-68, 11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_brownstone, trim_mat=m_dark_metal, awning_mat=m_awning_blue, has_water_tower=True)

# South Row (Y = -11, facing Y = -26 avenue)
create_urban_townhome("B21-S1 | Townhome A", (-136, -11, 0.10), width=18, depth=14, stories=3, facade_mat=m_brownstone)
create_urban_townhome("B21-S2 | Townhome B", (-114, -11, 0.10), width=18, depth=14, stories=3, facade_mat=m_brick_red)
create_urban_townhome("B21-S3 | Townhome C", (-90, -11, 0.10), width=18, depth=14, stories=3, facade_mat=m_ochre)
create_urban_townhome("B21-S4 | Townhome D", (-68, -11, 0.10), width=18, depth=14, stories=3, facade_mat=m_vanilla)

# ---------------------------------------------------------------------------
# 5. BLOCK 23: COMMERCIAL BOULEVARD & MEDICAL DISTRICT (8 Buildings)
# ---------------------------------------------------------------------------
# North Row (Y = 11, facing Y = 26 avenue)
create_urban_building("B23-N1 | Metro Health Clinic", (68, 11, 0.10), 20, 14, stories=4, story_h=3.6,
                      facade_mat=m_blue, trim_mat=m_dark_metal)
create_urban_building("B23-N2 | Supermarket & Gourmet Grocer", (90, 11, 0.10), 20, 14, stories=4, story_h=3.5,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, awning_mat=m_awning_green)
create_urban_building("B23-N3 | Eastside Apartments & Books", (114, 11, 0.10), 20, 14, stories=4, story_h=3.5,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, awning_mat=m_awning_blue)
create_urban_building("B23-N4 | Boulevard Hotel & Dining", (136, 11, 0.10), 20, 14, stories=5, story_h=3.5,
                      facade_mat=m_ochre, trim_mat=m_dark_metal, has_water_tower=True)

# South Row (Y = -11, facing Y = -26 avenue)
create_urban_building("B23-S1 | East Hardware & Supplies", (68, -11, 0.10), 20, 14, stories=3, story_h=3.6,
                      facade_mat=m_modern_slate, trim_mat=m_dark_metal)
create_urban_building("B23-S2 | Metro Radio & Media Studio", (90, -11, 0.10), 20, 14, stories=4, story_h=3.5,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, has_antenna=True)
create_urban_building("B23-S3 | Urban Pharmacy & Flats", (114, -11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_vanilla, trim_mat=m_dark_metal, awning_mat=m_awning_red)
create_urban_building("B23-S4 | Corner Bistro & Residences", (136, -11, 0.10), 20, 14, stories=4, story_h=3.4,
                      facade_mat=m_brownstone, trim_mat=m_dark_metal, has_water_tower=True)

# ---------------------------------------------------------------------------
# 6. BLOCK 11: HISTORIC URBAN QUARTER & MARKET SQUARE (8 Row Buildings)
# ---------------------------------------------------------------------------
# North Row (Y = 63, facing Y = 78 avenue)
create_urban_building("B11-N1 | Historic Clock Tower Hall", (-136, 63, 0.10), 20, 14, stories=4, story_h=3.8,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, has_antenna=True)
create_urban_building("B11-N2 | Old Quarter Guildhouse", (-114, 63, 0.10), 20, 14, stories=3, story_h=3.5,
                      facade_mat=m_brick_red, trim_mat=m_timber)
create_urban_building("B11-N3 | Artisan Workshop & Flats", (-90, 63, 0.10), 20, 14, stories=3, story_h=3.4,
                      facade_mat=m_sage, trim_mat=m_timber, awning_mat=m_awning_green)
create_urban_building("B11-N4 | Cobblestone Bakery & Cafe", (-68, 63, 0.10), 20, 14, stories=3, story_h=3.4,
                      facade_mat=m_vanilla, trim_mat=m_timber, awning_mat=m_awning_red)

# South Row (Y = 41, facing Y = 26 avenue)
create_urban_townhome("B11-S1 | Historic Rowhouse A", (-136, 41, 0.10), width=18, depth=14, stories=3, facade_mat=m_brick_red)
create_urban_townhome("B11-S2 | Historic Rowhouse B", (-114, 41, 0.10), width=18, depth=14, stories=3, facade_mat=m_ochre)
create_urban_townhome("B11-S3 | Historic Rowhouse C", (-90, 41, 0.10), width=18, depth=14, stories=3, facade_mat=m_vanilla)
create_urban_building("B11-S4 | Corner Market & General Store", (-68, 41, 0.10), 20, 14, stories=3, story_h=3.4,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, awning_mat=m_awning_blue)

# Central Cobbled Fountain in Block 11
create_fountain("Block 11 | Market Fountain", (-102, 52, 0.11))

# ---------------------------------------------------------------------------
# 7. BLOCK 32: BROWNSTONE RESIDENTIAL ROW (8 Classic Townhomes)
# ---------------------------------------------------------------------------
# North Row (Y = -41, facing Y = -26 avenue)
create_urban_townhome("B32-N1 | Brownstone 1", (-33, -41, 0.10), width=18, depth=14, stories=3, facade_mat=m_brownstone)
create_urban_townhome("B32-N2 | Brownstone 2", (-11, -41, 0.10), width=18, depth=14, stories=3, facade_mat=m_brick_red)
create_urban_townhome("B32-N3 | Brownstone 3", (11, -41, 0.10), width=18, depth=14, stories=3, facade_mat=m_ochre)
create_urban_townhome("B32-N4 | Brownstone 4", (33, -41, 0.10), width=18, depth=14, stories=3, facade_mat=m_brownstone)

# South Row (Y = -63, facing Y = -78 avenue)
create_urban_townhome("B32-S1 | Brownstone 5", (-33, -63, 0.10), width=18, depth=14, stories=3, facade_mat=m_brick_red)
create_urban_townhome("B32-S2 | Brownstone 6", (-11, -63, 0.10), width=18, depth=14, stories=3, facade_mat=m_vanilla)
create_urban_townhome("B32-S3 | Brownstone 7", (11, -63, 0.10), width=18, depth=14, stories=3, facade_mat=m_sage)
create_urban_townhome("B32-S4 | Brownstone 8", (33, -63, 0.10), width=18, depth=14, stories=3, facade_mat=m_brownstone)

# ---------------------------------------------------------------------------
# 8. BLOCK 33: CIVIC PARK & WATERFRONT PROMENADE (3 Buildings + Grand Park)
# ---------------------------------------------------------------------------
create_urban_building("B33-W1 | Community Sports Complex", (68, -41, 0.10), 18, 14, stories=3, story_h=3.8,
                      facade_mat=m_modern_slate, trim_mat=m_steel_silver)
create_urban_building("B33-W2 | Parkside Cultural Pavilion", (68, -63, 0.10), 18, 14, stories=3, story_h=3.6,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, awning_mat=m_awning_blue)
create_urban_building("B33-E1 | Parkview Residential Tower", (136, -63, 0.10), 18, 14, stories=5, story_h=3.5,
                      facade_mat=m_brick_red, trim_mat=m_dark_metal, has_water_tower=True)

# Park Bandstand / Gazebo & Fountain
create_fountain("Park | Grand Central Fountain", (117, -52, 0.11))
for ang in [0, 90, 180, 270]:
    rad = math.radians(ang)
    bx = 117 + 8 * math.cos(rad)
    by = -52 + 8 * math.sin(rad)
    create_bench(f"Park | bench {ang}", (bx, by, 0.11), yaw=rad + math.pi/2)

# ---------------------------------------------------------------------------
# 9. BLOCK 31: RESIDENTIAL NEIGHBORHOOD (Embedding Player's House)
# ---------------------------------------------------------------------------
# The player's house is at (-102, -43)
# Fill East and West frontages of Block 31
create_urban_cottage("B31-W1 | West Neighbor Home", (-134, -43, 0.10), width=13, depth=10, wall_h=3.4, wall_mat=m_vanilla, roof_mat=m_dark_metal)
create_urban_cottage("B31-W2 | West Neighbor Villa", (-119, -43, 0.10), width=12, depth=9.5, wall_h=3.2, wall_mat=m_sage, roof_mat=m_dark_metal)
create_urban_cottage("B31-E1 | East Neighbor Home", (-85, -43, 0.10), width=12, depth=9.5, wall_h=3.2, wall_mat=m_blue, roof_mat=m_dark_metal)
create_urban_building("B31-E2 | Neighborhood Corner Store", (-68, -43, 0.10), 16, 11, stories=2, story_h=3.4,
                      facade_mat=m_stone_ivory, trim_mat=m_dark_metal, awning_mat=m_awning_red)

# South Residential Mews Lane in Block 31 (Y = -63)
create_urban_cottage("B31-S1 | Mews Cottage 1", (-132, -63, 0.10), width=13, depth=9, wall_h=3.0, wall_mat=m_apricot)
create_urban_cottage("B31-S2 | Mews Cottage 2", (-102, -63, 0.10), width=13, depth=9, wall_h=3.0, wall_mat=m_vanilla)
create_urban_cottage("B31-S3 | Mews Cottage 3", (-72, -63, 0.10), width=13, depth=9, wall_h=3.0, wall_mat=m_sage)

# ---------------------------------------------------------------------------
# 10. STREET FURNITURE & URBAN INFRASTRUCTURE (City-Wide)
# ---------------------------------------------------------------------------
# Bus Stops / Transit Shelters
bus_shelters = [
    ("Bus Stop | Downtown North", (0, 23.0, 0.06), 0),
    ("Bus Stop | Downtown South", (0, -23.0, 0.06), math.pi),
    ("Bus Stop | School Gate", (94, 30.5, 0.06), 0),
    ("Bus Stop | House Block", (-102, -29.8, 0.06), math.pi),
    ("Bus Stop | West Avenue", (-53.5, 0, 0.06), -math.pi/2),
    ("Bus Stop | East Avenue", (53.5, 0, 0.06), math.pi/2),
]
for name, pos, yaw in bus_shelters:
    create_bus_shelter(name, pos, yaw)

# Fire Hydrants along Curbs
hydrant_positions = [
    # Inner junctions corners
    (-56, -23, 0.06), (-46, -23, 0.06), (-56, 23, 0.06), (-46, 23, 0.06),
    (46, -23, 0.06), (56, -23, 0.06), (46, 23, 0.06), (56, 23, 0.06),
    # Mid-avenue curbs
    (-102, 23, 0.06), (-102, -23, 0.06), (102, 23, 0.06), (102, -23, 0.06),
    (-46, 52, 0.06), (-46, -52, 0.06), (46, 52, 0.06), (46, -52, 0.06),
]
for idx, pos in enumerate(hydrant_positions):
    create_fire_hydrant(f"Hydrant | #{idx+1}", pos)

# Bike Racks outside Key Buildings
bike_rack_positions = [
    (-22, 23, 0), (22, 23, 0), (-22, -23, math.pi), (22, -23, math.pi),
    (0, 33, 0), (98, 33, 0), (-102, 33, 0), (90, -23, math.pi),
]
for idx, (x, y, yaw) in enumerate(bike_rack_positions):
    create_bike_rack(f"Bike Rack | #{idx+1}", (x, y, 0.06), yaw)

# Benches and Trash Bins along Main Sidewalks
for x_pos in [-120, -84, -20, 20, 84, 120]:
    create_bench(f"Sidewalk Bench | N {x_pos}", (x_pos, 23.2, 0.06), yaw=0)
    create_trash_bin(f"Sidewalk Bin | N {x_pos}", (x_pos + 1.6, 23.2, 0.06))
    create_bench(f"Sidewalk Bench | S {x_pos}", (x_pos, -23.2, 0.06), yaw=math.pi)
    create_trash_bin(f"Sidewalk Bin | S {x_pos}", (x_pos + 1.6, -23.2, 0.06))

# ---------------------------------------------------------------------------
# 11. STREETLIGHTS (Uniform Dense Grid: 80 Streetlights)
# ---------------------------------------------------------------------------
light_count = 0
# Junction Streetlights (4 at each of the 4 inner junctions)
for ix in [-51, 51]:
    for iy in [-26, 26]:
        create_streetlight(f"Light | junction ({ix},{iy}) SW", (ix - 4.5, iy - 4.5, 0.06), yaw=math.radians(45))
        create_streetlight(f"Light | junction ({ix},{iy}) SE", (ix + 4.5, iy - 4.5, 0.06), yaw=math.radians(135))
        create_streetlight(f"Light | junction ({ix},{iy}) NW", (ix - 4.5, iy + 4.5, 0.06), yaw=math.radians(-45))
        create_streetlight(f"Light | junction ({ix},{iy}) NE", (ix + 4.5, iy + 4.5, 0.06), yaw=math.radians(-135))
        light_count += 4

# NS Road Sidewalk Lights
for x_w, x_e in [(-54.8, -47.2), (47.2, 54.8)]:
    for y_pos in [-70, -56, -42, -14, 0, 14, 42, 56, 70]:
        create_streetlight(f"Light | NS ({x_w:.0f},{y_pos})", (x_w, y_pos, 0.06), yaw=math.radians(90))
        create_streetlight(f"Light | NS ({x_e:.0f},{y_pos})", (x_e, y_pos, 0.06), yaw=math.radians(-90))
        light_count += 2

# EW Road Sidewalk Lights
for y_s, y_n in [(-29.8, -22.2), (22.2, 29.8)]:
    for x_pos in [-136, -114, -90, -68, -34, -14, 14, 34, 68, 90, 114, 136]:
        create_streetlight(f"Light | EW ({x_pos},{y_s:.0f})", (x_pos, y_s, 0.06), yaw=math.radians(0))
        create_streetlight(f"Light | EW ({x_pos},{y_n:.0f})", (x_pos, y_n, 0.06), yaw=math.radians(180))
        light_count += 2

print(f"Created {light_count} streetlights.")

# ---------------------------------------------------------------------------
# 12. URBAN TREES (Boulevard Street Trees & Park Groves: 95 Trees)
# ---------------------------------------------------------------------------
tree_count = 0

# Boulevard Street Trees in Sidewalk Planters
for x in [-55.0, -47.0, 47.0, 55.0]:
    for y in [-65, -45, -7, 7, 45, 65]:
        create_tree(f"Tree | street ({x},{y})", (x, y, 0.06), scale=1.1, tree_type="boulevard", foliage_mat=m_leaf1)
        tree_count += 1

for y in [-22.0, 22.0]:
    for x in [-125, -102, -79, -24, 0, 24, 79, 102, 125]:
        create_tree(f"Tree | ave ({x},{y})", (x, y, 0.06), scale=1.1, tree_type="boulevard", foliage_mat=m_leaf1)
        tree_count += 1

# Central Downtown Plaza Trees
for px in [-16, -6, 6, 16]:
    for py in [-4, 4]:
        create_tree(f"Tree | plaza ({px},{py})", (px, py, 0.11), scale=1.15, tree_type="round", foliage_mat=m_leaf3)
        tree_count += 1

# Block 33 Grand Civic Park Mature Forest Grove
park_trees = [
    (100, -38, 1.4, "round", m_leaf1), (110, -36, 1.3, "pine", m_leaf2),
    (124, -38, 1.5, "round", m_leaf3), (134, -36, 1.2, "round", m_leaf1),
    (102, -48, 1.5, "pine", m_leaf2), (132, -48, 1.4, "round", m_leaf1),
    (98, -60, 1.3, "round", m_leaf3), (108, -64, 1.5, "pine", m_leaf2),
    (120, -64, 1.4, "round", m_leaf1), (132, -60, 1.3, "round", m_leaf3),
]
for x, y, sc, ttype, fmat in park_trees:
    create_tree(f"Tree | park ({x},{y})", (x, y, 0.11), scale=sc, tree_type=ttype, foliage_mat=fmat)
    tree_count += 1

# Block 11 Historic Square Trees
for sx, sy in [(-112, 46), (-92, 46), (-112, 58), (-92, 58)]:
    create_tree(f"Tree | square ({sx},{sy})", (sx, sy, 0.11), scale=1.2, tree_type="round", foliage_mat=m_leaf3)
    tree_count += 1

# Residential Yards (Block 31 & 32)
res_trees = [
    (-140, -43, 1.2, "round", m_leaf1), (-125, -66, 1.3, "pine", m_leaf2),
    (-88, -66, 1.2, "round", m_leaf3), (-62, -66, 1.1, "round", m_leaf1),
    (-22, -52, 1.1, "round", m_leaf1), (0, -52, 1.2, "round", m_leaf3), (22, -52, 1.1, "round", m_leaf1),
]
for x, y, sc, ttype, fmat in res_trees:
    create_tree(f"Tree | res ({x},{y})", (x, y, 0.11), scale=sc, tree_type=ttype, foliage_mat=fmat)
    tree_count += 1

print(f"Created {tree_count} trees.")

# Update viewport and view layer
bpy.context.view_layer.update()
print("Urbanized city generated successfully!")
