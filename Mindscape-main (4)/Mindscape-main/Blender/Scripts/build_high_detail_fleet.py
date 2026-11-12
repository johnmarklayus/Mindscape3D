"""
High-Detail Stylized Vehicles Fleet Generator
Clean Local-Space Asset Architecture with Unity Prefab Parity.

Hierarchy per vehicle:
Car_<Type> (Empty root at world position)
├── <Type>_Body (Local origin (0, 0, 0) with suspension idle animation)
├── <Type>_Wheel_FL (Local axle offset with continuous linear roll)
├── <Type>_Wheel_FR
├── <Type>_Wheel_RL
└── <Type>_Wheel_RR
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------------------
# Setup Clean Scene
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.name = "Vehicles_Scene"
scene.frame_start = 1
scene.frame_end = 61
scene.render.fps = 30
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

col_vehicles = bpy.data.collections.get("Vehicles")
if not col_vehicles:
    col_vehicles = bpy.data.collections.new("Vehicles")
    scene.collection.children.link(col_vehicles)

# ---------------------------------------------------------------------------
# Shared Materials
# ---------------------------------------------------------------------------
def get_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=5.0):
    mat_name = "Mat_" + name
    m = bpy.data.materials.get(mat_name)
    if not m:
        m = bpy.data.materials.new(mat_name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m

# Paints
m_sedan_red = get_mat("SedanRed", (0.85, 0.10, 0.10), roughness=0.25, metallic=0.35)
m_suv_green = get_mat("SUVGreen", (0.18, 0.38, 0.22), roughness=0.35, metallic=0.25)
m_sports_yellow = get_mat("SportsYellow", (0.98, 0.78, 0.08), roughness=0.18, metallic=0.15)
m_pickup_blue = get_mat("PickupBlue", (0.12, 0.25, 0.58), roughness=0.30, metallic=0.40)
m_van_white = get_mat("VanWhite", (0.94, 0.95, 0.96), roughness=0.28, metallic=0.05)
m_van_teal = get_mat("VanTeal", (0.10, 0.62, 0.58), roughness=0.30, metallic=0.15)

# Components & Trim
m_glass = get_mat("CarGlass", (0.15, 0.22, 0.30), roughness=0.08, metallic=0.2)
m_dark_glass = get_mat("TintedGlass", (0.06, 0.08, 0.12), roughness=0.05, metallic=0.3)
m_black = get_mat("TrimBlack", (0.10, 0.11, 0.12), roughness=0.7)
m_gloss_black = get_mat("GlossBlack", (0.05, 0.05, 0.06), roughness=0.15, metallic=0.3)
m_chrome = get_mat("CarChrome", (0.88, 0.89, 0.90), roughness=0.12, metallic=0.95)
m_silver = get_mat("CarSilver", (0.72, 0.74, 0.76), roughness=0.35, metallic=0.7)
m_headlight = get_mat("HeadlightGlow", (1.0, 0.98, 0.90), emission=(1.0, 0.98, 0.90), emission_strength=8.0)
m_taillight = get_mat("TaillightGlow", (0.95, 0.08, 0.06), emission=(0.95, 0.08, 0.06), emission_strength=6.0)
m_amber = get_mat("AmberLight", (1.0, 0.65, 0.08), emission=(1.0, 0.65, 0.08), emission_strength=5.0)
m_reverse = get_mat("ReverseLight", (0.95, 0.95, 0.98), emission=(0.95, 0.95, 0.98), emission_strength=5.0)
m_tire = get_mat("TireRubber", (0.14, 0.14, 0.15), roughness=0.88)
m_rim = get_mat("WheelRim", (0.78, 0.80, 0.82), roughness=0.25, metallic=0.85)
m_gold_rim = get_mat("GoldWheelRim", (0.86, 0.72, 0.28), roughness=0.20, metallic=0.85)
m_brake = get_mat("BrakeSteel", (0.65, 0.68, 0.70), roughness=0.25, metallic=0.9)
m_caliper_red = get_mat("CaliperRed", (0.85, 0.10, 0.10), roughness=0.3, metallic=0.2)
m_caliper_gold = get_mat("CaliperGold", (0.88, 0.68, 0.15), roughness=0.3, metallic=0.5)
m_plate = get_mat("LicensePlate", (0.95, 0.95, 0.92), roughness=0.6)

# ---------------------------------------------------------------------------
# Geometry Helpers (Translation Baked into BMesh Vertices)
# ---------------------------------------------------------------------------
def create_beveled_box(name, loc, size, bevel_width=0.04, segments=1, mat=None, rot=(0,0,0)):
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    col_vehicles.objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if bevel_width > 0.001:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel_width, offset_type='OFFSET', segments=segments, profile=0.5, affect='EDGES')
    if rot != (0, 0, 0):
        rot_mat = Euler(rot, 'XYZ').to_matrix()
        bmesh.ops.rotate(bm, matrix=rot_mat, verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob.location = (0, 0, 0)
    if mat:
        ob.data.materials.append(mat)
    return ob

def create_tapered_box(name, loc, length, width_bottom, width_top, height, front_rake, rear_rake, bevel=0.04, mat=None, rot=(0,0,0)):
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    col_vehicles.objects.link(ob)
    bm = bmesh.new()
    x_f_b, x_r_b = length / 2.0, -length / 2.0
    y_b = width_bottom / 2.0
    x_f_t, x_r_t = x_f_b - front_rake, x_r_b + rear_rake
    y_t = width_top / 2.0
    z_t = height
    v0 = bm.verts.new((x_f_b, -y_b, 0))
    v1 = bm.verts.new((x_f_b,  y_b, 0))
    v2 = bm.verts.new((x_r_b,  y_b, 0))
    v3 = bm.verts.new((x_r_b, -y_b, 0))
    v4 = bm.verts.new((x_f_t, -y_t, z_t))
    v5 = bm.verts.new((x_f_t,  y_t, z_t))
    v6 = bm.verts.new((x_r_t,  y_t, z_t))
    v7 = bm.verts.new((x_r_t, -y_t, z_t))
    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v7, v6, v5, v4))
    bm.faces.new((v0, v4, v5, v1))
    bm.faces.new((v2, v6, v7, v3))
    bm.faces.new((v1, v5, v6, v2))
    bm.faces.new((v3, v7, v4, v0))
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0.001:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, offset_type='OFFSET', segments=1, profile=0.5, affect='EDGES')
    if rot != (0, 0, 0):
        rot_mat = Euler(rot, 'XYZ').to_matrix()
        bmesh.ops.rotate(bm, matrix=rot_mat, verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob.location = (0, 0, 0)
    if mat:
        ob.data.materials.append(mat)
    return ob

def carve_wheel_wells(body_obj, wheel_positions, radius=0.48, depth=0.45):
    cutters = []
    for wx, wy, wz in wheel_positions:
        bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=radius, depth=depth, location=(wx, wy, wz), rotation=(math.radians(90), 0, 0))
        c = bpy.context.active_object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        cutters.append(c)
    bpy.ops.object.select_all(action='DESELECT')
    for c in cutters:
        c.select_set(True)
    bpy.context.view_layer.objects.active = cutters[0]
    bpy.ops.object.join()
    cutter_union = bpy.context.active_object
    bool_mod = body_obj.modifiers.new("WheelWells", 'BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter_union
    bool_mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.modifier_apply(modifier="WheelWells")
    bpy.data.objects.remove(cutter_union, do_unlink=True)

def build_wheel_mesh(name, loc, radius=0.40, width=0.30, is_left=True, rim_mat=m_rim, caliper_mat=m_caliper_red):
    parts = []
    # 1. Tire
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=width, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    tire = bpy.context.active_object
    if tire.name not in col_vehicles.objects:
        col_vehicles.objects.link(tire)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bev = tire.modifiers.new("Bevel", 'BEVEL')
    bev.width = radius * 0.1
    bev.segments = 1
    bpy.ops.object.modifier_apply(modifier="Bevel")
    tire.data.materials.append(m_tire)
    parts.append(tire)
    
    # 2. Rim
    rim_r = radius * 0.74
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=rim_r, depth=width + 0.005, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    rim = bpy.context.active_object
    if rim.name not in col_vehicles.objects:
        col_vehicles.objects.link(rim)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    rim.data.materials.append(rim_mat)
    parts.append(rim)
    
    # 3. Brake Rotor
    rotor_r = radius * 0.58
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=rotor_r, depth=0.03, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    rotor = bpy.context.active_object
    if rotor.name not in col_vehicles.objects:
        col_vehicles.objects.link(rotor)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    rotor.data.materials.append(m_brake)
    parts.append(rotor)
    
    # 4. Brake Caliper
    caliper = create_beveled_box(f"{name}_Caliper", (rotor_r * 0.65, 0, rotor_r * 0.65), (radius * 0.35, width * 0.3, radius * 0.35), bevel_width=0.015, mat=caliper_mat)
    parts.append(caliper)
    
    # 5. Hubcap & 5 Lug nuts
    outer_y = (width / 2.0) + 0.005 if is_left else -(width / 2.0) - 0.005
    cap = create_beveled_box(f"{name}_Cap", (0, outer_y, 0), (radius * 0.22, 0.015, radius * 0.22), bevel_width=0.008, mat=m_silver)
    parts.append(cap)
    
    lug_dist = radius * 0.28
    for i in range(5):
        ang = i * (2 * math.pi / 5.0)
        lx = lug_dist * math.cos(ang)
        lz = lug_dist * math.sin(ang)
        lug = create_beveled_box(f"{name}_Lug_{i}", (lx, outer_y, lz), (0.025, 0.02, 0.025), bevel_width=0.005, mat=m_chrome)
        parts.append(lug)
        
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = tire
    bpy.ops.object.join()
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.location = loc
    return wheel

def set_linear_interpolation(action):
    if hasattr(action, 'layers'):
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fcurve in cb.fcurves:
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = 'LINEAR'
    elif hasattr(action, 'fcurves'):
        for fcurve in action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'

def animate_wheel(wheel_obj, prefix):
    act = bpy.data.actions.new(f"{prefix}_WheelRoll")
    wheel_obj.animation_data_create()
    wheel_obj.animation_data.action = act
    wheel_obj.rotation_mode = 'XYZ'
    wheel_obj.rotation_euler = (0, 0, 0)
    wheel_obj.keyframe_insert("rotation_euler", index=1, frame=1)
    wheel_obj.rotation_euler = (0, math.radians(360), 0)
    wheel_obj.keyframe_insert("rotation_euler", index=1, frame=31)
    wheel_obj.rotation_euler = (0, math.radians(720), 0)
    wheel_obj.keyframe_insert("rotation_euler", index=1, frame=61)
    set_linear_interpolation(act)

def animate_body_vibration(body_obj, prefix):
    act = bpy.data.actions.new(f"{prefix}_BodyVibe")
    body_obj.animation_data_create()
    body_obj.animation_data.action = act
    for f, dz, roll in [(1, 0, 0), (15, 0.008, 0.003), (30, -0.006, -0.002), (45, 0.007, 0.002), (61, 0, 0)]:
        body_obj.location = (0, 0, dz)
        body_obj.rotation_euler = (0, 0, roll)
        body_obj.keyframe_insert("location", index=2, frame=f)
        body_obj.keyframe_insert("rotation_euler", index=2, frame=f)

def join_body_elements(parts, main_name):
    base = parts[0]
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    body = bpy.context.active_object
    body.name = main_name
    return body

# ===========================================================================
# 1. SEDAN BUILDER
# ===========================================================================
def build_sedan(world_pos=(0, -25.0, 0)):
    parts = []
    
    # Lower Body (ground clearance 0.32m, height 0.44m, covers Z=0.32 to 0.76)
    body_base = create_beveled_box("Sedan_Base", (0, 0, 0.54), (4.7, 2.02, 0.44), bevel_width=0.06, segments=2, mat=m_sedan_red)
    wheel_coords = [(1.35, 1.05, 0.40), (1.35, -1.05, 0.40),
                    (-1.35, 1.05, 0.40), (-1.35, -1.05, 0.40)]
    carve_wheel_wells(body_base, wheel_coords, radius=0.48, depth=0.45)
    parts.append(body_base)
    
    # Fender Arch Flares
    for wx, wy, wz in wheel_coords:
        y_side = 1 if wy > 0 else -1
        flare = create_beveled_box(f"Sedan_Fender_{wx}_{y_side}", (wx, wy + y_side*0.01, 0.64), (0.95, 0.04, 0.08), bevel_width=0.02, mat=m_sedan_red)
        parts.append(flare)

    # Sloped Hood
    hood = create_tapered_box("Sedan_Hood", (1.45, 0, 0.68), length=1.45, width_bottom=1.98, width_top=1.85, height=0.20, front_rake=0.18, rear_rake=0.0, bevel=0.03, mat=m_sedan_red)
    parts.append(hood)

    # Rear Trunk Deck & Spoiler
    trunk = create_tapered_box("Sedan_Trunk", (-1.65, 0, 0.68), length=1.05, width_bottom=1.98, width_top=1.86, height=0.18, front_rake=0.0, rear_rake=0.15, bevel=0.03, mat=m_sedan_red)
    trunk_spoiler = create_beveled_box("Sedan_TrunkSpoiler", (-2.18, 0, 0.86), (0.12, 1.70, 0.05), bevel_width=0.015, mat=m_black)
    parts.extend([trunk, trunk_spoiler])

    # Greenhouse / Cabin
    cabin_glass = create_tapered_box("Sedan_CabinGlass", (-0.10, 0, 0.76), length=2.25, width_bottom=1.88, width_top=1.54, height=0.68, front_rake=0.65, rear_rake=0.55, bevel=0.03, mat=m_glass)
    roof_panel = create_beveled_box("Sedan_Roof", (-0.05, 0, 1.44), (1.18, 1.56, 0.05), bevel_width=0.025, mat=m_sedan_red)
    sunroof = create_beveled_box("Sedan_Sunroof", (0.10, 0, 1.465), (0.55, 0.95, 0.01), bevel_width=0.01, mat=m_dark_glass)
    fin = create_beveled_box("Sedan_SharkFin", (-0.50, 0, 1.50), (0.16, 0.05, 0.08), bevel_width=0.015, mat=m_black)
    b_pillar_l = create_beveled_box("Sedan_BPillar_L", (-0.08, 0.86, 1.10), (0.08, 0.04, 0.65), bevel_width=0.01, mat=m_black)
    b_pillar_r = create_beveled_box("Sedan_BPillar_R", (-0.08, -0.86, 1.10), (0.08, 0.04, 0.65), bevel_width=0.01, mat=m_black)
    parts.extend([cabin_glass, roof_panel, sunroof, fin, b_pillar_l, b_pillar_r])

    # Front Bumper, Intake, Fogs, Grille
    bumper_f = create_beveled_box("Sedan_Bumper_F", (2.35, 0, 0.44), (0.28, 2.06, 0.34), bevel_width=0.06, segments=2, mat=m_sedan_red)
    intake_f = create_beveled_box("Sedan_Intake_F", (2.42, 0, 0.36), (0.16, 1.10, 0.14), bevel_width=0.02, mat=m_black)
    fog_l = create_beveled_box("Sedan_Fog_L", (2.42, 0.80, 0.36), (0.16, 0.22, 0.10), bevel_width=0.015, mat=m_headlight)
    fog_r = create_beveled_box("Sedan_Fog_R", (2.42, -0.80, 0.36), (0.16, 0.22, 0.10), bevel_width=0.015, mat=m_headlight)
    grille_frame = create_beveled_box("Sedan_GrilleFrame", (2.36, 0, 0.65), (0.12, 1.12, 0.26), bevel_width=0.03, mat=m_chrome)
    grille_mesh = create_beveled_box("Sedan_GrilleMesh", (2.38, 0, 0.65), (0.10, 1.04, 0.20), bevel_width=0.01, mat=m_black)
    grille_badge = create_beveled_box("Sedan_Badge_F", (2.44, 0, 0.65), (0.04, 0.14, 0.10), bevel_width=0.01, mat=m_silver)
    parts.extend([bumper_f, intake_f, fog_l, fog_r, grille_frame, grille_mesh, grille_badge])

    # Multi-Lens Headlights
    for side, y_sign in [("L", 1), ("R", -1)]:
        hl_housing = create_beveled_box(f"Sedan_HL_House_{side}", (2.32, y_sign * 0.78, 0.66), (0.18, 0.42, 0.18), bevel_width=0.02, mat=m_chrome)
        hl_proj = create_beveled_box(f"Sedan_HL_Proj_{side}", (2.36, y_sign * 0.72, 0.66), (0.12, 0.24, 0.12), bevel_width=0.01, mat=m_headlight)
        hl_turn = create_beveled_box(f"Sedan_HL_Turn_{side}", (2.34, y_sign * 0.90, 0.66), (0.12, 0.10, 0.12), bevel_width=0.01, mat=m_amber)
        parts.extend([hl_housing, hl_proj, hl_turn])

    # Rear Bumper, Diffuser, Dual Chrome Exhaust
    bumper_r = create_beveled_box("Sedan_Bumper_R", (-2.35, 0, 0.44), (0.28, 2.06, 0.34), bevel_width=0.06, segments=2, mat=m_sedan_red)
    diffuser_r = create_beveled_box("Sedan_Diffuser_R", (-2.42, 0, 0.34), (0.16, 1.30, 0.12), bevel_width=0.02, mat=m_black)
    exhaust_l = create_beveled_box("Sedan_Exhaust_L", (-2.48, 0.55, 0.32), (0.15, 0.12, 0.08), bevel_width=0.015, mat=m_chrome)
    exhaust_r = create_beveled_box("Sedan_Exhaust_R", (-2.48, -0.55, 0.32), (0.15, 0.12, 0.08), bevel_width=0.015, mat=m_chrome)
    parts.extend([bumper_r, diffuser_r, exhaust_l, exhaust_r])

    for side, y_sign in [("L", 1), ("R", -1)]:
        tl_house = create_beveled_box(f"Sedan_TL_House_{side}", (-2.32, y_sign * 0.78, 0.68), (0.16, 0.44, 0.16), bevel_width=0.02, mat=m_black)
        tl_brake = create_beveled_box(f"Sedan_TL_Brake_{side}", (-2.35, y_sign * 0.82, 0.68), (0.12, 0.26, 0.12), bevel_width=0.01, mat=m_taillight)
        tl_amber = create_beveled_box(f"Sedan_TL_Amber_{side}", (-2.35, y_sign * 0.66, 0.71), (0.12, 0.12, 0.06), bevel_width=0.01, mat=m_amber)
        tl_rev = create_beveled_box(f"Sedan_TL_Rev_{side}", (-2.35, y_sign * 0.66, 0.64), (0.12, 0.12, 0.06), bevel_width=0.01, mat=m_reverse)
        parts.extend([tl_house, tl_brake, tl_amber, tl_rev])

    # Plates, Mirrors, Handles, Wipers
    plate_f_frame = create_beveled_box("Sedan_Plate_F_Frame", (2.48, 0, 0.44), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
    plate_f_face = create_beveled_box("Sedan_Plate_F_Face", (2.50, 0, 0.44), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
    plate_r_frame = create_beveled_box("Sedan_Plate_R_Frame", (-2.48, 0, 0.52), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
    plate_r_face = create_beveled_box("Sedan_Plate_R_Face", (-2.50, 0, 0.52), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
    parts.extend([plate_f_frame, plate_f_face, plate_r_frame, plate_r_face])

    for side, y_sign in [("L", 1), ("R", -1)]:
        stalk = create_beveled_box(f"Sedan_Mirror_Stalk_{side}", (0.70, y_sign * 0.98, 0.84), (0.10, 0.14, 0.04), bevel_width=0.01, mat=m_black)
        house = create_beveled_box(f"Sedan_Mirror_House_{side}", (0.70, y_sign * 1.10, 0.88), (0.18, 0.14, 0.12), bevel_width=0.02, mat=m_sedan_red)
        face = create_beveled_box(f"Sedan_Mirror_Face_{side}", (0.64, y_sign * 1.10, 0.88), (0.02, 0.11, 0.09), bevel_width=0.005, mat=m_chrome)
        parts.extend([stalk, house, face])

    for x_pos, name_x in [(0.30, "F"), (-0.60, "R")]:
        for side, y_sign in [("L", 1), ("R", -1)]:
            handle = create_beveled_box(f"Sedan_Handle_{name_x}_{side}", (x_pos, y_sign * 1.02, 0.76), (0.14, 0.03, 0.04), bevel_width=0.008, mat=m_chrome)
            parts.append(handle)

    wiper_l = create_beveled_box("Sedan_Wiper_L", (0.75, 0.35, 0.84), (0.32, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-15), math.radians(18)))
    wiper_r = create_beveled_box("Sedan_Wiper_R", (0.75, -0.35, 0.84), (0.32, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-15), math.radians(18)))
    parts.extend([wiper_l, wiper_r])

    # Join Body
    sedan_body = join_body_elements(parts, "Sedan_Body")
    animate_body_vibration(sedan_body, "Sedan")

    # Wheels (R=0.40, W=0.30)
    w_fl = build_wheel_mesh("Sedan_Wheel_FL", (1.35, 1.05, 0.40), radius=0.40, width=0.30, is_left=True, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_fr = build_wheel_mesh("Sedan_Wheel_FR", (1.35, -1.05, 0.40), radius=0.40, width=0.30, is_left=False, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_rl = build_wheel_mesh("Sedan_Wheel_RL", (-1.35, 1.05, 0.40), radius=0.40, width=0.30, is_left=True, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_rr = build_wheel_mesh("Sedan_Wheel_RR", (-1.35, -1.05, 0.40), radius=0.40, width=0.30, is_left=False, rim_mat=m_rim, caliper_mat=m_caliper_red)

    for w, name in [(w_fl, "Sedan_FL"), (w_fr, "Sedan_FR"), (w_rl, "Sedan_RL"), (w_rr, "Sedan_RR")]:
        animate_wheel(w, name)

    root = bpy.data.objects.new("Car_Sedan", None)
    root.location = world_pos
    col_vehicles.objects.link(root)
    for ob in [sedan_body, w_fl, w_fr, w_rl, w_rr]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)

    print(f"Sedan built successfully at {world_pos} with {len(sedan_body.data.vertices)} body verts!")
    return root

# ===========================================================================
# 2. SUV BUILDER
# ===========================================================================
def build_suv(world_pos=(0, -15.0, 0)):
    parts = []
    
    # Lower Body with High Clearance (ground clearance 0.42m, height 0.54m, covers Z=0.42 to 0.96)
    body_base = create_beveled_box("SUV_Base", (0, 0, 0.69), (4.85, 2.12, 0.54), bevel_width=0.07, segments=2, mat=m_suv_green)
    wheel_coords = [(1.42, 1.10, 0.46), (1.42, -1.10, 0.46),
                    (-1.42, 1.10, 0.46), (-1.42, -1.10, 0.46)]
    carve_wheel_wells(body_base, wheel_coords, radius=0.54, depth=0.45)
    parts.append(body_base)

    # Black Plastic Rugged Fender Flares
    for wx, wy, wz in wheel_coords:
        y_side = 1 if wy > 0 else -1
        flare = create_beveled_box(f"SUV_Flare_{wx}_{y_side}", (wx, wy + y_side*0.02, 0.74), (1.10, 0.06, 0.12), bevel_width=0.03, mat=m_black)
        parts.append(flare)

    # Lower Rocker Panel Cladding & Side Steps
    for y_side in [1, -1]:
        cladding = create_beveled_box(f"SUV_Rocker_{y_side}", (0, y_side * 1.05, 0.46), (2.0, 0.05, 0.12), bevel_width=0.02, mat=m_black)
        step = create_beveled_box(f"SUV_Step_{y_side}", (0, y_side * 1.16, 0.36), (1.9, 0.14, 0.04), bevel_width=0.015, mat=m_black)
        parts.extend([cladding, step])

    # Muscular Hood
    hood = create_tapered_box("SUV_Hood", (1.50, 0, 0.84), length=1.55, width_bottom=2.08, width_top=1.95, height=0.28, front_rake=0.22, rear_rake=0.0, bevel=0.04, mat=m_suv_green)
    bulge = create_beveled_box("SUV_HoodBulge", (1.40, 0, 1.00), (0.90, 0.70, 0.05), bevel_width=0.02, mat=m_suv_green)
    parts.extend([hood, bulge])

    # Tall Greenhouse Cabin
    cabin_glass = create_tapered_box("SUV_CabinGlass", (-0.25, 0, 0.98), length=2.85, width_bottom=2.02, width_top=1.80, height=0.88, front_rake=0.45, rear_rake=0.20, bevel=0.04, mat=m_glass)
    roof_panel = create_beveled_box("SUV_Roof", (-0.28, 0, 1.86), (2.35, 1.82, 0.06), bevel_width=0.03, mat=m_suv_green)
    parts.extend([cabin_glass, roof_panel])

    # Pillars (B, C, D Pillars)
    for x_p, name_p in [(0.25, "B"), (-0.55, "C"), (-1.35, "D")]:
        for y_side in [1, -1]:
            pillar = create_beveled_box(f"SUV_Pillar_{name_p}_{y_side}", (x_p, y_side * 0.94, 1.40), (0.10, 0.04, 0.82), bevel_width=0.015, mat=m_black)
            parts.append(pillar)

    # Roof Rack
    for y_side in [1, -1]:
        rail = create_beveled_box(f"SUV_RoofRail_{y_side}", (-0.28, y_side * 0.75, 1.94), (2.10, 0.05, 0.05), bevel_width=0.015, mat=m_black)
        parts.append(rail)
    for rx in [0.60, -0.28, -1.15]:
        crossbar = create_beveled_box(f"SUV_Crossbar_{rx}", (rx, 0, 1.95), (0.05, 1.50, 0.04), bevel_width=0.01, mat=m_black)
        parts.append(crossbar)

    # Front Off-Road Bumper & Silver Skid Plate
    bumper_f = create_beveled_box("SUV_Bumper_F", (2.44, 0, 0.52), (0.32, 2.14, 0.40), bevel_width=0.07, segments=2, mat=m_black)
    skid_plate = create_beveled_box("SUV_SkidPlate", (2.48, 0, 0.36), (0.18, 0.85, 0.18), bevel_width=0.02, mat=m_silver)
    fog_l = create_beveled_box("SUV_Fog_L", (2.50, 0.82, 0.44), (0.12, 0.20, 0.12), bevel_width=0.015, mat=m_headlight)
    fog_r = create_beveled_box("SUV_Fog_R", (2.50, -0.82, 0.44), (0.12, 0.20, 0.12), bevel_width=0.015, mat=m_headlight)
    parts.extend([bumper_f, skid_plate, fog_l, fog_r])

    # Vertical 4x4 Radiator Grille
    grille_frame = create_beveled_box("SUV_GrilleFrame", (2.42, 0, 0.78), (0.14, 1.15, 0.32), bevel_width=0.03, mat=m_chrome)
    grille_mesh = create_beveled_box("SUV_GrilleMesh", (2.44, 0, 0.78), (0.10, 1.05, 0.26), bevel_width=0.01, mat=m_black)
    for s_i in range(-3, 4):
        slat = create_beveled_box(f"SUV_GrilleSlat_{s_i}", (2.47, s_i * 0.14, 0.78), (0.03, 0.04, 0.24), bevel_width=0.008, mat=m_chrome)
        parts.append(slat)
    parts.extend([grille_frame, grille_mesh])

    # Circular Headlights with Chrome Rings
    for side, y_sign in [("L", 1), ("R", -1)]:
        hl_ring = create_beveled_box(f"SUV_HL_Ring_{side}", (2.40, y_sign * 0.82, 0.78), (0.16, 0.28, 0.28), bevel_width=0.03, mat=m_chrome)
        hl_lens = create_beveled_box(f"SUV_HL_Lens_{side}", (2.44, y_sign * 0.82, 0.78), (0.12, 0.22, 0.22), bevel_width=0.02, mat=m_headlight)
        hl_turn = create_beveled_box(f"SUV_HL_Turn_{side}", (2.42, y_sign * 0.98, 0.78), (0.10, 0.08, 0.18), bevel_width=0.01, mat=m_amber)
        parts.extend([hl_ring, hl_lens, hl_turn])

    # Rear Bumper & Hitch
    bumper_r = create_beveled_box("SUV_Bumper_R", (-2.44, 0, 0.54), (0.32, 2.14, 0.40), bevel_width=0.07, segments=2, mat=m_black)
    hitch = create_beveled_box("SUV_Hitch", (-2.60, 0, 0.40), (0.18, 0.12, 0.12), bevel_width=0.015, mat=m_black)
    parts.extend([bumper_r, hitch])

    # Vertical Taillight Columns
    for side, y_sign in [("L", 1), ("R", -1)]:
        tl_house = create_beveled_box(f"SUV_TL_House_{side}", (-2.40, y_sign * 0.88, 1.25), (0.14, 0.18, 0.55), bevel_width=0.02, mat=m_black)
        tl_brake = create_beveled_box(f"SUV_TL_Brake_{side}", (-2.44, y_sign * 0.88, 1.40), (0.10, 0.14, 0.20), bevel_width=0.01, mat=m_taillight)
        tl_amber = create_beveled_box(f"SUV_TL_Amber_{side}", (-2.44, y_sign * 0.88, 1.22), (0.10, 0.14, 0.12), bevel_width=0.01, mat=m_amber)
        tl_rev = create_beveled_box(f"SUV_TL_Rev_{side}", (-2.44, y_sign * 0.88, 1.08), (0.10, 0.14, 0.10), bevel_width=0.01, mat=m_reverse)
        parts.extend([tl_house, tl_brake, tl_amber, tl_rev])

    # Tailgate Mounted Spare Wheel
    spare_bracket = create_beveled_box("SUV_SpareBracket", (-2.46, 0, 1.05), (0.12, 0.20, 0.20), bevel_width=0.01, mat=m_black)
    spare_cover = create_beveled_box("SUV_SpareCover", (-2.65, 0, 1.05), (0.30, 0.86, 0.86), bevel_width=0.08, segments=2, mat=m_suv_green)
    spare_cap = create_beveled_box("SUV_SpareCap", (-2.76, 0, 1.05), (0.05, 0.35, 0.35), bevel_width=0.02, mat=m_black)
    parts.extend([spare_bracket, spare_cover, spare_cap])

    # Plates, Mirrors, Handles, Wipers
    plate_f_frame = create_beveled_box("SUV_Plate_F_Frame", (2.58, 0, 0.46), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
    plate_f_face = create_beveled_box("SUV_Plate_F_Face", (2.60, 0, 0.46), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
    plate_r_frame = create_beveled_box("SUV_Plate_R_Frame", (-2.48, -0.45, 0.62), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
    plate_r_face = create_beveled_box("SUV_Plate_R_Face", (-2.50, -0.45, 0.62), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
    parts.extend([plate_f_frame, plate_f_face, plate_r_frame, plate_r_face])

    for side, y_sign in [("L", 1), ("R", -1)]:
        stalk = create_beveled_box(f"SUV_Mirror_Stalk_{side}", (0.72, y_sign * 1.04, 1.02), (0.12, 0.16, 0.05), bevel_width=0.01, mat=m_black)
        house = create_beveled_box(f"SUV_Mirror_House_{side}", (0.72, y_sign * 1.18, 1.08), (0.20, 0.16, 0.16), bevel_width=0.02, mat=m_black)
        face = create_beveled_box(f"SUV_Mirror_Face_{side}", (0.66, y_sign * 1.18, 1.08), (0.02, 0.13, 0.13), bevel_width=0.005, mat=m_chrome)
        parts.extend([stalk, house, face])

    for x_pos, name_x in [(0.25, "F"), (-0.65, "R")]:
        for side, y_sign in [("L", 1), ("R", -1)]:
            handle = create_beveled_box(f"SUV_Handle_{name_x}_{side}", (x_pos, y_sign * 1.07, 0.95), (0.15, 0.04, 0.04), bevel_width=0.008, mat=m_black)
            parts.append(handle)

    wiper_l = create_beveled_box("SUV_Wiper_L", (0.78, 0.38, 1.02), (0.34, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-12), math.radians(15)))
    wiper_r = create_beveled_box("SUV_Wiper_R", (0.78, -0.38, 1.02), (0.34, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-12), math.radians(15)))
    parts.extend([wiper_l, wiper_r])

    # Join Body
    suv_body = join_body_elements(parts, "SUV_Body")
    animate_body_vibration(suv_body, "SUV")

    # Wheels (R=0.46, W=0.36)
    w_fl = build_wheel_mesh("SUV_Wheel_FL", (1.42, 1.10, 0.46), radius=0.46, width=0.36, is_left=True, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_fr = build_wheel_mesh("SUV_Wheel_FR", (1.42, -1.10, 0.46), radius=0.46, width=0.36, is_left=False, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_rl = build_wheel_mesh("SUV_Wheel_RL", (-1.42, 1.10, 0.46), radius=0.46, width=0.36, is_left=True, rim_mat=m_rim, caliper_mat=m_caliper_red)
    w_rr = build_wheel_mesh("SUV_Wheel_RR", (-1.42, -1.10, 0.46), radius=0.46, width=0.36, is_left=False, rim_mat=m_rim, caliper_mat=m_caliper_red)

    for w, name in [(w_fl, "SUV_FL"), (w_fr, "SUV_FR"), (w_rl, "SUV_RL"), (w_rr, "SUV_RR")]:
        animate_wheel(w, name)

    root = bpy.data.objects.new("Car_SUV", None)
    root.location = world_pos
    col_vehicles.objects.link(root)
    for ob in [suv_body, w_fl, w_fr, w_rl, w_rr]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)

    print(f"SUV built successfully at {world_pos} with {len(suv_body.data.vertices)} body verts!")
    return root

# ===========================================================================
# 3. SPORTS CAR BUILDER
# ===========================================================================
def build_sports_car(world_pos=(0, -5.0, 0)):
    parts = []

    # Low-slung Wide Chassis (ground clearance 0.26m, height 0.38m, covers Z=0.26 to 0.64)
    body_base = create_beveled_box("Sports_Base", (0, 0, 0.45), (4.55, 2.16, 0.38), bevel_width=0.06, segments=2, mat=m_sports_yellow)
    wheel_coords = [(1.35, 1.05, 0.36), (1.35, -1.05, 0.36),
                    (-1.35, 1.05, 0.36), (-1.35, -1.05, 0.36)]
    carve_wheel_wells(body_base, wheel_coords, radius=0.44, depth=0.45)
    parts.append(body_base)

    # Front Carbon Aero Splitter Lip
    splitter = create_beveled_box("Sports_Splitter", (2.38, 0, 0.20), (0.35, 2.18, 0.05), bevel_width=0.015, mat=m_gloss_black)
    canard_l = create_beveled_box("Sports_Canard_L", (2.35, 1.05, 0.28), (0.15, 0.12, 0.08), bevel_width=0.01, mat=m_gloss_black, rot=(math.radians(20), 0, 0))
    canard_r = create_beveled_box("Sports_Canard_R", (2.35, -1.05, 0.28), (0.15, 0.12, 0.08), bevel_width=0.01, mat=m_gloss_black, rot=(math.radians(-20), 0, 0))
    parts.extend([splitter, canard_l, canard_r])

    # Side Skirt Extensions
    for y_side in [1, -1]:
        skirt = create_beveled_box(f"Sports_SideSkirt_{y_side}", (0, y_side * 1.10, 0.22), (1.80, 0.08, 0.05), bevel_width=0.015, mat=m_gloss_black)
        parts.append(skirt)

    # Low Aerodynamic Sloping Nose & Hood
    hood = create_tapered_box("Sports_Hood", (1.40, 0, 0.56), length=1.50, width_bottom=2.10, width_top=1.92, height=0.22, front_rake=0.30, rear_rake=0.0, bevel=0.03, mat=m_sports_yellow)
    parts.append(hood)

    # Hood Heat-Extractor Air Vents
    for y_side in [1, -1]:
        vent = create_beveled_box(f"Sports_HoodVent_{y_side}", (1.45, y_side * 0.45, 0.68), (0.35, 0.20, 0.02), bevel_width=0.008, mat=m_black)
        parts.append(vent)

    # Sleek Fastback Greenhouse Teardrop Canopy
    cabin_glass = create_tapered_box("Sports_CabinGlass", (-0.10, 0, 0.64), length=2.20, width_bottom=1.95, width_top=1.50, height=0.60, front_rake=0.75, rear_rake=0.70, bevel=0.03, mat=m_glass)
    roof_panel = create_beveled_box("Sports_Roof", (-0.15, 0, 1.24), (1.05, 1.50, 0.04), bevel_width=0.02, mat=m_sports_yellow)
    roof_channel = create_beveled_box("Sports_RoofChannel", (-0.15, 0, 1.25), (0.95, 0.35, 0.02), bevel_width=0.01, mat=m_gloss_black)
    parts.extend([cabin_glass, roof_panel, roof_channel])

    # Side Mid-Engine Air Intakes
    for y_side in [1, -1]:
        intake_scoop = create_beveled_box(f"Sports_SideScoop_{y_side}", (-0.55, y_side * 1.08, 0.54), (0.45, 0.06, 0.22), bevel_width=0.02, mat=m_black)
        parts.append(intake_scoop)

    # Elevated Rear GT Wing Spoiler on Twin Aerodynamic Pylons
    pylon_l = create_beveled_box("Sports_WingPylon_L", (-2.05, 0.55, 0.88), (0.12, 0.04, 0.36), bevel_width=0.01, mat=m_gloss_black)
    pylon_r = create_beveled_box("Sports_WingPylon_R", (-2.05, -0.55, 0.88), (0.12, 0.04, 0.36), bevel_width=0.01, mat=m_gloss_black)
    wing_blade = create_beveled_box("Sports_WingBlade", (-2.05, 0, 1.08), (0.30, 2.10, 0.04), bevel_width=0.015, mat=m_gloss_black)
    endplate_l = create_beveled_box("Sports_WingEnd_L", (-2.05, 1.06, 1.08), (0.36, 0.03, 0.18), bevel_width=0.01, mat=m_sports_yellow)
    endplate_r = create_beveled_box("Sports_WingEnd_R", (-2.05, -1.06, 1.08), (0.36, 0.03, 0.18), bevel_width=0.01, mat=m_sports_yellow)
    parts.extend([pylon_l, pylon_r, wing_blade, endplate_l, endplate_r])

    # Front Fascia & Wide-Mouth Radiator Intake
    bumper_f = create_beveled_box("Sports_Bumper_F", (2.28, 0, 0.38), (0.28, 2.16, 0.30), bevel_width=0.06, segments=2, mat=m_sports_yellow)
    intake_mouth = create_beveled_box("Sports_FrontIntake", (2.34, 0, 0.32), (0.14, 1.40, 0.18), bevel_width=0.02, mat=m_black)
    parts.extend([bumper_f, intake_mouth])

    # Swept-Back LED Headlights
    for side, y_sign in [("L", 1), ("R", -1)]:
        hl_housing = create_beveled_box(f"Sports_HL_House_{side}", (2.22, y_sign * 0.80, 0.54), (0.28, 0.38, 0.14), bevel_width=0.02, mat=m_black)
        hl_drl = create_beveled_box(f"Sports_HL_DRL_{side}", (2.26, y_sign * 0.80, 0.58), (0.20, 0.30, 0.03), bevel_width=0.008, mat=m_headlight)
        hl_lens = create_beveled_box(f"Sports_HL_Lens_{side}", (2.27, y_sign * 0.74, 0.52), (0.14, 0.16, 0.08), bevel_width=0.01, mat=m_headlight)
        parts.extend([hl_housing, hl_drl, hl_lens])

    # Rear Fascia, Diffuser with 4 Fins, Quad Chrome Exhaust
    bumper_r = create_beveled_box("Sports_Bumper_R", (-2.28, 0, 0.40), (0.28, 2.16, 0.32), bevel_width=0.06, segments=2, mat=m_sports_yellow)
    diffuser_tray = create_beveled_box("Sports_DiffuserTray", (-2.36, 0, 0.26), (0.20, 1.45, 0.14), bevel_width=0.02, mat=m_gloss_black)
    parts.extend([bumper_r, diffuser_tray])
    for f_i, f_y in enumerate([-0.45, -0.15, 0.15, 0.45]):
        fin = create_beveled_box(f"Sports_DiffuserFin_{f_i}", (-2.42, f_y, 0.24), (0.16, 0.03, 0.12), bevel_width=0.008, mat=m_gloss_black)
        parts.append(fin)

    # Quad Chrome Exhaust Pipes
    for ex_y in [0.72, 0.84, -0.72, -0.84]:
        pipe = create_beveled_box(f"Sports_Exhaust_{ex_y}", (-2.44, ex_y, 0.30), (0.14, 0.09, 0.09), bevel_width=0.015, mat=m_chrome)
        parts.append(pipe)

    # Slim LED Taillight Blade
    tl_blade = create_beveled_box("Sports_TL_Blade", (-2.32, 0, 0.58), (0.10, 1.90, 0.06), bevel_width=0.01, mat=m_taillight)
    parts.append(tl_blade)

    # Plates, Aerodynamic Mirrors, Door Handles, Single Center Wiper
    plate_f = create_beveled_box("Sports_Plate_F", (2.44, 0, 0.28), (0.02, 0.48, 0.12), bevel_width=0.005, mat=m_plate)
    plate_r = create_beveled_box("Sports_Plate_R", (-2.44, 0, 0.44), (0.02, 0.48, 0.12), bevel_width=0.005, mat=m_plate)
    parts.extend([plate_f, plate_r])

    for side, y_sign in [("L", 1), ("R", -1)]:
        stalk = create_beveled_box(f"Sports_Mirror_Stalk_{side}", (0.55, y_sign * 0.98, 0.68), (0.08, 0.14, 0.03), bevel_width=0.008, mat=m_gloss_black)
        house = create_beveled_box(f"Sports_Mirror_House_{side}", (0.55, y_sign * 1.10, 0.70), (0.16, 0.12, 0.08), bevel_width=0.015, mat=m_sports_yellow)
        face = create_beveled_box(f"Sports_Mirror_Face_{side}", (0.50, y_sign * 1.10, 0.70), (0.02, 0.10, 0.07), bevel_width=0.005, mat=m_chrome)
        handle = create_beveled_box(f"Sports_Handle_{side}", (-0.10, y_sign * 1.07, 0.60), (0.12, 0.02, 0.03), bevel_width=0.005, mat=m_black)
        parts.extend([stalk, house, face, handle])

    wiper = create_beveled_box("Sports_CenterWiper", (0.68, 0, 0.70), (0.36, 0.03, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-16), 0))
    parts.append(wiper)

    # Join Body
    sports_body = join_body_elements(parts, "SportsCar_Body")
    animate_body_vibration(sports_body, "SportsCar")

    # Wheels (R=0.36, W=0.34, Gold Rims, Red Calipers)
    w_fl = build_wheel_mesh("SportsCar_Wheel_FL", (1.35, 1.05, 0.36), radius=0.36, width=0.34, is_left=True, rim_mat=m_gold_rim, caliper_mat=m_caliper_red)
    w_fr = build_wheel_mesh("SportsCar_Wheel_FR", (1.35, -1.05, 0.36), radius=0.36, width=0.34, is_left=False, rim_mat=m_gold_rim, caliper_mat=m_caliper_red)
    w_rl = build_wheel_mesh("SportsCar_Wheel_RL", (-1.35, 1.05, 0.36), radius=0.36, width=0.34, is_left=True, rim_mat=m_gold_rim, caliper_mat=m_caliper_red)
    w_rr = build_wheel_mesh("SportsCar_Wheel_RR", (-1.35, -1.05, 0.36), radius=0.36, width=0.34, is_left=False, rim_mat=m_gold_rim, caliper_mat=m_caliper_red)

    for w, name in [(w_fl, "Sports_FL"), (w_fr, "Sports_FR"), (w_rl, "Sports_RL"), (w_rr, "Sports_RR")]:
        animate_wheel(w, name)

    root = bpy.data.objects.new("Car_Sports", None)
    root.location = world_pos
    col_vehicles.objects.link(root)
    for ob in [sports_body, w_fl, w_fr, w_rl, w_rr]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)

    print(f"Sports Car built successfully at {world_pos} with {len(sports_body.data.vertices)} body verts!")
    return root

# ===========================================================================
# 4. PICKUP TRUCK BUILDER
# ===========================================================================
def build_pickup(world_pos=(0, 5.0, 0)):
    parts = []

    # High Heavy-Duty Chassis (ground clearance 0.44m, height 0.56m, covers Z=0.44 to 1.00)
    body_base = create_beveled_box("Pickup_Base", (0, 0, 0.72), (5.50, 2.18, 0.56), bevel_width=0.07, segments=2, mat=m_pickup_blue)
    wheel_coords = [(1.65, 1.12, 0.48), (1.65, -1.12, 0.48),
                    (-1.65, 1.12, 0.48), (-1.65, -1.12, 0.48)]
    carve_wheel_wells(body_base, wheel_coords, radius=0.56, depth=0.48)
    parts.append(body_base)

    # Muscular Flared Wheel Arches
    for wx, wy, wz in wheel_coords:
        y_side = 1 if wy > 0 else -1
        flare = create_beveled_box(f"Pickup_Flare_{wx}_{y_side}", (wx, wy + y_side*0.02, 0.78), (1.15, 0.06, 0.12), bevel_width=0.025, mat=m_pickup_blue)
        parts.append(flare)

    # Tubular Black Rocker Steps
    for y_side in [1, -1]:
        step = create_beveled_box(f"Pickup_Step_{y_side}", (0.10, y_side * 1.18, 0.38), (2.10, 0.12, 0.05), bevel_width=0.015, mat=m_black)
        parts.append(step)

    # Muscular High Hood
    hood = create_tapered_box("Pickup_Hood", (1.70, 0, 0.86), length=1.55, width_bottom=2.14, width_top=2.00, height=0.32, front_rake=0.20, rear_rake=0.0, bevel=0.04, mat=m_pickup_blue)
    bulge = create_beveled_box("Pickup_HoodBulge", (1.65, 0, 1.04), (0.95, 0.85, 0.06), bevel_width=0.02, mat=m_pickup_blue)
    parts.extend([hood, bulge])

    # Crew Cab
    cab_glass = create_tapered_box("Pickup_CabGlass", (0.10, 0, 1.00), length=2.15, width_bottom=2.10, width_top=1.84, height=0.86, front_rake=0.50, rear_rake=0.15, bevel=0.04, mat=m_glass)
    cab_roof = create_beveled_box("Pickup_CabRoof", (0.06, 0, 1.86), (1.80, 1.86, 0.06), bevel_width=0.03, mat=m_pickup_blue)
    b_pillar_l = create_beveled_box("Pickup_BPillar_L", (0.12, 0.96, 1.43), (0.12, 0.04, 0.80), bevel_width=0.015, mat=m_black)
    b_pillar_r = create_beveled_box("Pickup_BPillar_R", (0.12, -0.96, 1.43), (0.12, 0.04, 0.80), bevel_width=0.015, mat=m_black)
    parts.extend([cab_glass, cab_roof, b_pillar_l, b_pillar_r])

    # Deep Cargo Bed Box
    bed_wall_l = create_beveled_box("Pickup_BedL", (-1.65, 1.02, 1.12), (2.20, 0.12, 0.60), bevel_width=0.03, mat=m_pickup_blue)
    bed_wall_r = create_beveled_box("Pickup_BedR", (-1.65, -1.02, 1.12), (2.20, 0.12, 0.60), bevel_width=0.03, mat=m_pickup_blue)
    bed_front = create_beveled_box("Pickup_BedF", (-0.95, 0, 1.12), (0.12, 2.00, 0.60), bevel_width=0.03, mat=m_pickup_blue)
    bed_tailgate = create_beveled_box("Pickup_Tailgate", (-2.70, 0, 1.12), (0.12, 2.00, 0.60), bevel_width=0.04, mat=m_pickup_blue)
    bed_floor = create_beveled_box("Pickup_BedFloor", (-1.65, 0, 0.86), (2.15, 1.94, 0.08), bevel_width=0.02, mat=m_black)
    parts.extend([bed_wall_l, bed_wall_r, bed_front, bed_tailgate, bed_floor])

    # Ribbed Bed Floor Rails
    for r_y in [-0.70, -0.35, 0.0, 0.35, 0.70]:
        rib = create_beveled_box(f"Pickup_BedRib_{r_y}", (-1.65, r_y, 0.92), (2.05, 0.06, 0.04), bevel_width=0.01, mat=m_black)
        parts.append(rib)

    # Polished Tubular Chrome Roll Bar
    rb_post_l = create_beveled_box("Pickup_RB_Post_L", (-1.10, 0.90, 1.62), (0.08, 0.08, 0.90), bevel_width=0.02, mat=m_chrome)
    rb_post_r = create_beveled_box("Pickup_RB_Post_R", (-1.10, -0.90, 1.62), (0.08, 0.08, 0.90), bevel_width=0.02, mat=m_chrome)
    rb_top = create_beveled_box("Pickup_RB_Top", (-1.10, 0, 2.07), (0.08, 1.84, 0.08), bevel_width=0.02, mat=m_chrome)
    rb_brace_l = create_beveled_box("Pickup_RB_Brace_L", (-1.45, 0.90, 1.52), (0.75, 0.06, 0.06), bevel_width=0.015, mat=m_chrome, rot=(0, math.radians(45), 0))
    rb_brace_r = create_beveled_box("Pickup_RB_Brace_R", (-1.45, -0.90, 1.52), (0.75, 0.06, 0.06), bevel_width=0.015, mat=m_chrome, rot=(0, math.radians(45), 0))
    parts.extend([rb_post_l, rb_post_r, rb_top, rb_brace_l, rb_brace_r])

    # 4 Overhead Off-Road Rally Spotlights
    for sp_y in [-0.54, -0.18, 0.18, 0.54]:
        sp_can = create_beveled_box(f"Pickup_SpotCan_{sp_y}", (-1.05, sp_y, 2.19), (0.16, 0.16, 0.16), bevel_width=0.03, mat=m_black)
        sp_lens = create_beveled_box(f"Pickup_SpotLens_{sp_y}", (-0.96, sp_y, 2.19), (0.04, 0.12, 0.12), bevel_width=0.01, mat=m_headlight)
        parts.extend([sp_can, sp_lens])

    # Front Fascia & Chrome Grille
    grille_frame = create_beveled_box("Pickup_GrilleFrame", (2.70, 0, 0.82), (0.16, 1.40, 0.42), bevel_width=0.04, mat=m_chrome)
    grille_bar1 = create_beveled_box("Pickup_GrilleBar1", (2.76, 0, 0.90), (0.08, 1.30, 0.08), bevel_width=0.015, mat=m_chrome)
    grille_bar2 = create_beveled_box("Pickup_GrilleBar2", (2.76, 0, 0.74), (0.08, 1.30, 0.08), bevel_width=0.015, mat=m_chrome)
    grille_mesh = create_beveled_box("Pickup_GrilleMesh", (2.72, 0, 0.82), (0.08, 1.32, 0.36), bevel_width=0.01, mat=m_black)
    grille_badge = create_beveled_box("Pickup_GrilleBadge", (2.82, 0, 0.82), (0.04, 0.20, 0.12), bevel_width=0.01, mat=m_silver)
    parts.extend([grille_frame, grille_bar1, grille_bar2, grille_mesh, grille_badge])

    # Stacked Rectangular Headlights
    for side, y_sign in [("L", 1), ("R", -1)]:
        hl_box = create_beveled_box(f"Pickup_HL_Box_{side}", (2.68, y_sign * 0.94, 0.82), (0.16, 0.32, 0.40), bevel_width=0.02, mat=m_chrome)
        hl_high = create_beveled_box(f"Pickup_HL_High_{side}", (2.74, y_sign * 0.92, 0.90), (0.08, 0.22, 0.14), bevel_width=0.01, mat=m_headlight)
        hl_low = create_beveled_box(f"Pickup_HL_Low_{side}", (2.74, y_sign * 0.92, 0.74), (0.08, 0.22, 0.14), bevel_width=0.01, mat=m_headlight)
        hl_turn = create_beveled_box(f"Pickup_HL_Turn_{side}", (2.72, y_sign * 1.06, 0.82), (0.08, 0.06, 0.36), bevel_width=0.01, mat=m_amber)
        parts.extend([hl_box, hl_high, hl_low, hl_turn])

    # Heavy-Duty Front Chrome Bumper
    bumper_f = create_beveled_box("Pickup_Bumper_F", (2.74, 0, 0.52), (0.34, 2.22, 0.42), bevel_width=0.07, segments=2, mat=m_chrome)
    hook_l = create_beveled_box("Pickup_TowHook_L", (2.92, 0.55, 0.42), (0.12, 0.06, 0.06), bevel_width=0.01, mat=m_black)
    hook_r = create_beveled_box("Pickup_TowHook_R", (2.92, -0.55, 0.42), (0.12, 0.06, 0.06), bevel_width=0.01, mat=m_black)
    fog_l = create_beveled_box("Pickup_Fog_L", (2.88, 0.85, 0.48), (0.08, 0.18, 0.12), bevel_width=0.01, mat=m_headlight)
    fog_r = create_beveled_box("Pickup_Fog_R", (2.88, -0.85, 0.48), (0.08, 0.18, 0.12), bevel_width=0.01, mat=m_headlight)
    parts.extend([bumper_f, hook_l, hook_r, fog_l, fog_r])

    # Heavy-Duty Rear Step Bumper & Tow Hitch
    bumper_r = create_beveled_box("Pickup_Bumper_R", (-2.82, 0, 0.52), (0.30, 2.22, 0.38), bevel_width=0.06, segments=2, mat=m_chrome)
    step_pad = create_beveled_box("Pickup_StepPad", (-2.82, 0, 0.72), (0.18, 1.40, 0.03), bevel_width=0.008, mat=m_black)
    hitch = create_beveled_box("Pickup_Hitch", (-2.98, 0, 0.40), (0.18, 0.14, 0.14), bevel_width=0.015, mat=m_black)
    parts.extend([bumper_r, step_pad, hitch])

    # Rear Taillights on Bed Corners
    for side, y_sign in [("L", 1), ("R", -1)]:
        tl_house = create_beveled_box(f"Pickup_TL_House_{side}", (-2.74, y_sign * 1.04, 1.15), (0.14, 0.14, 0.56), bevel_width=0.02, mat=m_black)
        tl_brake = create_beveled_box(f"Pickup_TL_Brake_{side}", (-2.78, y_sign * 1.04, 1.30), (0.08, 0.10, 0.22), bevel_width=0.01, mat=m_taillight)
        tl_rev = create_beveled_box(f"Pickup_TL_Rev_{side}", (-2.78, y_sign * 1.04, 1.15), (0.08, 0.10, 0.10), bevel_width=0.01, mat=m_reverse)
        tl_amber = create_beveled_box(f"Pickup_TL_Amber_{side}", (-2.78, y_sign * 1.04, 1.02), (0.08, 0.10, 0.12), bevel_width=0.01, mat=m_amber)
        parts.extend([tl_house, tl_brake, tl_rev, tl_amber])

    # Tailgate Handle & License Plates
    tg_handle = create_beveled_box("Pickup_TG_Handle", (-2.78, 0, 1.35), (0.04, 0.24, 0.08), bevel_width=0.01, mat=m_black)
    plate_f = create_beveled_box("Pickup_Plate_F", (2.92, 0, 0.42), (0.02, 0.50, 0.14), bevel_width=0.005, mat=m_plate)
    plate_r = create_beveled_box("Pickup_Plate_R", (-2.98, -0.45, 0.52), (0.02, 0.50, 0.14), bevel_width=0.005, mat=m_plate)
    parts.extend([tg_handle, plate_f, plate_r])

    # Large Towing Mirrors & 4 Door Handles
    for side, y_sign in [("L", 1), ("R", -1)]:
        arm_top = create_beveled_box(f"Pickup_MirrorArm1_{side}", (0.85, y_sign * 1.08, 1.14), (0.06, 0.18, 0.03), bevel_width=0.008, mat=m_black)
        arm_bot = create_beveled_box(f"Pickup_MirrorArm2_{side}", (0.85, y_sign * 1.08, 1.00), (0.06, 0.18, 0.03), bevel_width=0.008, mat=m_black)
        house = create_beveled_box(f"Pickup_MirrorHouse_{side}", (0.85, y_sign * 1.25, 1.08), (0.16, 0.14, 0.26), bevel_width=0.02, mat=m_black)
        face = create_beveled_box(f"Pickup_MirrorFace_{side}", (0.79, y_sign * 1.25, 1.08), (0.02, 0.11, 0.23), bevel_width=0.005, mat=m_chrome)
        parts.extend([arm_top, arm_bot, house, face])

    for x_pos, name_x in [(0.55, "F"), (-0.35, "R")]:
        for side, y_sign in [("L", 1), ("R", -1)]:
            handle = create_beveled_box(f"Pickup_Handle_{name_x}_{side}", (x_pos, y_sign * 1.10, 0.96), (0.16, 0.03, 0.04), bevel_width=0.008, mat=m_chrome)
            parts.append(handle)

    wiper_l = create_beveled_box("Pickup_Wiper_L", (0.95, 0.40, 1.04), (0.36, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-14), math.radians(16)))
    wiper_r = create_beveled_box("Pickup_Wiper_R", (0.95, -0.40, 1.04), (0.36, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-14), math.radians(16)))
    parts.extend([wiper_l, wiper_r])

    # Join Body
    pickup_body = join_body_elements(parts, "Pickup_Body")
    animate_body_vibration(pickup_body, "Pickup")

    # Wheels (R=0.48, W=0.38, Chrome Rim, Gold Calipers)
    w_fl = build_wheel_mesh("Pickup_Wheel_FL", (1.65, 1.12, 0.48), radius=0.48, width=0.38, is_left=True, rim_mat=m_chrome, caliper_mat=m_caliper_gold)
    w_fr = build_wheel_mesh("Pickup_Wheel_FR", (1.65, -1.12, 0.48), radius=0.48, width=0.38, is_left=False, rim_mat=m_chrome, caliper_mat=m_caliper_gold)
    w_rl = build_wheel_mesh("Pickup_Wheel_RL", (-1.65, 1.12, 0.48), radius=0.48, width=0.38, is_left=True, rim_mat=m_chrome, caliper_mat=m_caliper_gold)
    w_rr = build_wheel_mesh("Pickup_Wheel_RR", (-1.65, -1.12, 0.48), radius=0.48, width=0.38, is_left=False, rim_mat=m_chrome, caliper_mat=m_caliper_gold)

    for w, name in [(w_fl, "Pickup_FL"), (w_fr, "Pickup_FR"), (w_rl, "Pickup_RL"), (w_rr, "Pickup_RR")]:
        animate_wheel(w, name)

    root = bpy.data.objects.new("Car_Pickup", None)
    root.location = world_pos
    col_vehicles.objects.link(root)
    for ob in [pickup_body, w_fl, w_fr, w_rl, w_rr]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)

    print(f"Pickup built successfully at {world_pos} with {len(pickup_body.data.vertices)} body verts!")
    return root

# ===========================================================================
# 5. DELIVERY VAN BUILDER
# ===========================================================================
def build_delivery_van(world_pos=(0, 15.0, 0)):
    parts = []

    # Lower Chassis (ground clearance 0.36m, height 0.52m, covers Z=0.36 to 0.88)
    body_base = create_beveled_box("Van_Base", (0, 0, 0.62), (5.60, 2.14, 0.52), bevel_width=0.07, segments=2, mat=m_van_white)
    wheel_coords = [(1.60, 1.08, 0.44), (1.60, -1.08, 0.44),
                    (-1.60, 1.08, 0.44), (-1.60, -1.08, 0.44)]
    carve_wheel_wells(body_base, wheel_coords, radius=0.52, depth=0.45)
    parts.append(body_base)

    # Protective Side Rub Moldings
    for y_side in [1, -1]:
        molding = create_beveled_box(f"Van_RubMolding_{y_side}", (-0.20, y_side * 1.08, 0.54), (4.50, 0.04, 0.10), bevel_width=0.015, mat=m_black)
        parts.append(molding)

    # Turquoise Teal Commercial Livery Stripe
    for y_side in [1, -1]:
        stripe = create_beveled_box(f"Van_LiveryStripe_{y_side}", (-0.20, y_side * 1.075, 1.05), (4.50, 0.03, 0.16), bevel_width=0.01, mat=m_van_teal)
        parts.append(stripe)

    # Forward-Slanted Cab Nose & Hood
    hood = create_tapered_box("Van_Hood", (2.10, 0, 0.72), length=1.20, width_bottom=2.12, width_top=2.00, height=0.30, front_rake=0.35, rear_rake=0.0, bevel=0.04, mat=m_van_white)
    parts.append(hood)

    # Cab Greenhouse
    cab_glass = create_tapered_box("Van_CabGlass", (1.25, 0, 1.04), length=1.40, width_bottom=2.10, width_top=1.92, height=0.85, front_rake=0.65, rear_rake=0.05, bevel=0.04, mat=m_glass)
    cab_roof = create_beveled_box("Van_CabRoof", (1.00, 0, 1.89), (0.95, 1.94, 0.06), bevel_width=0.03, mat=m_van_white)
    a_pillar_l = create_beveled_box("Van_APillar_L", (1.45, 0.98, 1.38), (0.10, 0.04, 0.80), bevel_width=0.015, mat=m_van_white, rot=(0, math.radians(-30), 0))
    a_pillar_r = create_beveled_box("Van_APillar_R", (1.45, -0.98, 1.38), (0.10, 0.04, 0.80), bevel_width=0.015, mat=m_van_white, rot=(0, math.radians(-30), 0))
    parts.extend([cab_glass, cab_roof, a_pillar_l, a_pillar_r])

    # High Cargo Box Body (extends to Z=2.20)
    cargo_body = create_beveled_box("Van_CargoBox", (-0.85, 0, 1.44), (3.70, 2.10, 1.45), bevel_width=0.06, segments=2, mat=m_van_white)
    high_roof = create_beveled_box("Van_HighRoof", (-0.85, 0, 2.21), (3.70, 2.06, 0.12), bevel_width=0.04, mat=m_van_white)
    parts.extend([cargo_body, high_roof])

    # 3 Longitudinal Stamped Roof Stiffening Ribs
    for r_y in [-0.55, 0.0, 0.55]:
        rib = create_beveled_box(f"Van_RoofRib_{r_y}", (-0.85, r_y, 2.29), (3.40, 0.08, 0.05), bevel_width=0.015, mat=m_van_white)
        parts.append(rib)

    # 5 Front Roof Clearance Marker Lamps
    for m_y in [-0.60, -0.30, 0.0, 0.30, 0.60]:
        marker = create_beveled_box(f"Van_RoofMarker_{m_y}", (1.42, m_y, 1.94), (0.06, 0.08, 0.04), bevel_width=0.008, mat=m_amber)
        parts.append(marker)

    # Side Sliding Cargo Door Guide Track Groove
    slide_track = create_beveled_box("Van_SlideTrack", (-0.65, 1.06, 1.15), (2.10, 0.03, 0.05), bevel_width=0.01, mat=m_black)
    slide_handle = create_beveled_box("Van_SlideHandle", (0.35, 1.07, 1.05), (0.04, 0.03, 0.14), bevel_width=0.008, mat=m_black)
    parts.extend([slide_track, slide_handle])

    # Asymmetrical Split Rear Cargo Barn Doors
    door_seam = create_beveled_box("Van_RearDoorSeam", (-2.71, 0, 1.44), (0.02, 0.04, 1.40), bevel_width=0.005, mat=m_black)
    door_handle_r = create_beveled_box("Van_RearDoorHandle", (-2.73, 0.15, 1.15), (0.04, 0.12, 0.04), bevel_width=0.008, mat=m_black)
    rear_win_l = create_beveled_box("Van_RearWin_L", (-2.72, 0.50, 1.68), (0.02, 0.70, 0.50), bevel_width=0.02, mat=m_glass)
    rear_win_r = create_beveled_box("Van_RearWin_R", (-2.72, -0.50, 1.68), (0.02, 0.70, 0.50), bevel_width=0.02, mat=m_glass)
    parts.extend([door_seam, door_handle_r, rear_win_l, rear_win_r])

    # Commercial Radiator Grille & Bumper
    bumper_f = create_beveled_box("Van_Bumper_F", (2.74, 0, 0.46), (0.32, 2.18, 0.38), bevel_width=0.06, segments=2, mat=m_black)
    bumper_step = create_beveled_box("Van_BumperStep", (2.85, 0, 0.40), (0.16, 0.85, 0.10), bevel_width=0.015, mat=m_black)
    grille = create_beveled_box("Van_Grille", (2.72, 0, 0.68), (0.12, 1.20, 0.24), bevel_width=0.02, mat=m_black)
    badge = create_beveled_box("Van_Badge", (2.80, 0, 0.68), (0.04, 0.16, 0.12), bevel_width=0.01, mat=m_silver)
    parts.extend([bumper_f, bumper_step, grille, badge])

    # Wraparound Headlights
    for side, y_sign in [("L", 1), ("R", -1)]:
        hl_box = create_beveled_box(f"Van_HL_Box_{side}", (2.68, y_sign * 0.85, 0.70), (0.18, 0.36, 0.22), bevel_width=0.02, mat=m_black)
        hl_glow = create_beveled_box(f"Van_HL_Glow_{side}", (2.74, y_sign * 0.80, 0.70), (0.10, 0.24, 0.16), bevel_width=0.01, mat=m_headlight)
        hl_turn = create_beveled_box(f"Van_HL_Turn_{side}", (2.70, y_sign * 0.98, 0.70), (0.10, 0.10, 0.16), bevel_width=0.01, mat=m_amber)
        parts.extend([hl_box, hl_glow, hl_turn])

    # Rear Bumper & Tall Vertical Taillight Columns
    bumper_r = create_beveled_box("Van_Bumper_R", (-2.74, 0, 0.42), (0.28, 2.18, 0.34), bevel_width=0.06, segments=2, mat=m_black)
    parts.append(bumper_r)

    for side, y_sign in [("L", 1), ("R", -1)]:
        tl_col = create_beveled_box(f"Van_TL_Col_{side}", (-2.70, y_sign * 1.04, 1.20), (0.12, 0.12, 0.85), bevel_width=0.02, mat=m_black)
        tl_red = create_beveled_box(f"Van_TL_Red_{side}", (-2.74, y_sign * 1.04, 1.40), (0.06, 0.08, 0.35), bevel_width=0.01, mat=m_taillight)
        tl_amb = create_beveled_box(f"Van_TL_Amb_{side}", (-2.74, y_sign * 1.04, 1.15), (0.06, 0.08, 0.12), bevel_width=0.01, mat=m_amber)
        tl_rev = create_beveled_box(f"Van_TL_Rev_{side}", (-2.74, y_sign * 1.04, 0.98), (0.06, 0.08, 0.12), bevel_width=0.01, mat=m_reverse)
        parts.extend([tl_col, tl_red, tl_amb, tl_rev])

    # Plates, Large Commercial Dual-Glass Mirrors, Front Wipers, Door Handles
    plate_f = create_beveled_box("Van_Plate_F", (2.92, 0, 0.40), (0.02, 0.50, 0.14), bevel_width=0.005, mat=m_plate)
    plate_r = create_beveled_box("Van_Plate_R", (-2.74, -0.45, 0.95), (0.02, 0.50, 0.14), bevel_width=0.005, mat=m_plate)
    parts.extend([plate_f, plate_r])

    for side, y_sign in [("L", 1), ("R", -1)]:
        arm = create_beveled_box(f"Van_MirrorArm_{side}", (1.40, y_sign * 1.06, 1.14), (0.10, 0.16, 0.04), bevel_width=0.01, mat=m_black)
        house = create_beveled_box(f"Van_MirrorHouse_{side}", (1.40, y_sign * 1.22, 1.18), (0.16, 0.14, 0.32), bevel_width=0.02, mat=m_black)
        face1 = create_beveled_box(f"Van_MirrorFace1_{side}", (1.34, y_sign * 1.22, 1.24), (0.02, 0.11, 0.16), bevel_width=0.005, mat=m_chrome)
        face2 = create_beveled_box(f"Van_MirrorFace2_{side}", (1.34, y_sign * 1.22, 1.08), (0.02, 0.11, 0.08), bevel_width=0.005, mat=m_chrome)
        handle = create_beveled_box(f"Van_CabHandle_{side}", (0.85, y_sign * 1.08, 0.95), (0.14, 0.03, 0.04), bevel_width=0.008, mat=m_black)
        parts.extend([arm, house, face1, face2, handle])

    wiper_l = create_beveled_box("Van_Wiper_L", (1.62, 0.42, 1.04), (0.38, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-15), math.radians(18)))
    wiper_r = create_beveled_box("Van_Wiper_R", (1.62, -0.42, 1.04), (0.38, 0.04, 0.02), bevel_width=0.005, mat=m_black, rot=(0, math.radians(-15), math.radians(18)))
    parts.extend([wiper_l, wiper_r])

    # Join Body
    van_body = join_body_elements(parts, "Van_Body")
    animate_body_vibration(van_body, "Van")

    # Wheels (R=0.44, W=0.32, Steel Rims)
    w_fl = build_wheel_mesh("Van_Wheel_FL", (1.60, 1.08, 0.44), radius=0.44, width=0.32, is_left=True, rim_mat=m_silver, caliper_mat=m_caliper_red)
    w_fr = build_wheel_mesh("Van_Wheel_FR", (1.60, -1.08, 0.44), radius=0.44, width=0.32, is_left=False, rim_mat=m_silver, caliper_mat=m_caliper_red)
    w_rl = build_wheel_mesh("Van_Wheel_RL", (-1.60, 1.08, 0.44), radius=0.44, width=0.32, is_left=True, rim_mat=m_silver, caliper_mat=m_caliper_red)
    w_rr = build_wheel_mesh("Van_Wheel_RR", (-1.60, -1.08, 0.44), radius=0.44, width=0.32, is_left=False, rim_mat=m_silver, caliper_mat=m_caliper_red)

    for w, name in [(w_fl, "Van_FL"), (w_fr, "Van_FR"), (w_rl, "Van_RL"), (w_rr, "Van_RR")]:
        animate_wheel(w, name)

    root = bpy.data.objects.new("Car_Van", None)
    root.location = world_pos
    col_vehicles.objects.link(root)
    for ob in [van_body, w_fl, w_fr, w_rl, w_rr]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)

    print(f"Van built successfully at {world_pos} with {len(van_body.data.vertices)} body verts!")
    return root

# ===========================================================================
# 6. SCHOOL BUS APPENDER
# ===========================================================================
def append_school_bus(world_pos=(0, 27.0, 0)):
    bus_blend = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/school-bus.blend"
    if not os.path.exists(bus_blend):
        print("Warning: school-bus.blend not found at", bus_blend)
        return None
    
    with bpy.data.libraries.load(bus_blend, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name in ["SchoolBus", "Bus_Body", "Wheel_FL", "Wheel_FR", "Wheel_RL", "Wheel_RR"]]

    bus_root = None
    for ob in data_to.objects:
        if ob:
            if ob.name not in col_vehicles.objects:
                col_vehicles.objects.link(ob)
            if ob.name == "SchoolBus":
                bus_root = ob

    if bus_root:
        bus_root.location = world_pos
        print(f"School Bus appended and positioned at {world_pos}")
    return bus_root

# ===========================================================================
# 7. SHOWROOM ENVIRONMENT & CAMERA
# ===========================================================================
def build_showroom():
    # Floor
    m_floor = get_mat("ShowroomFloor", (0.16, 0.17, 0.19), roughness=0.75, metallic=0.1)
    floor = create_beveled_box("Showroom_Floor", (0, 0, -0.05), (32.0, 75.0, 0.10), bevel_width=0.01, mat=m_floor)

    # White Parking Bay Lines
    m_stripe = get_mat("ShowroomStripe", (0.90, 0.90, 0.85), roughness=0.8)
    for y in [-30, -20, -10, 0, 10, 20, 34]:
        stripe = create_beveled_box(f"Showroom_Line_{y}", (0, y, 0.005), (16.0, 0.22, 0.01), bevel_width=0.002, mat=m_stripe)

    # Camera
    cam_data = bpy.data.cameras.new("Vehicles_Camera")
    cam_data.lens = 28
    cam_ob = bpy.data.objects.new("Vehicles | Camera", cam_data)
    col_vehicles.objects.link(cam_ob)
    cam_ob.location = (38, 1, 16)
    target = Vector((0, 1, 1.2))
    cam_ob.rotation_euler = (target - cam_ob.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_ob

    # Sun Light
    sun_data = bpy.data.lights.new("Vehicles_Sun", 'SUN')
    sun_data.energy = 3.5
    sun_data.angle = math.radians(20)
    sun_ob = bpy.data.objects.new("Vehicles | Sun", sun_data)
    col_vehicles.objects.link(sun_ob)
    sun_ob.rotation_euler = (math.radians(45), math.radians(-25), math.radians(-35))

# ===========================================================================
# MAIN RUNNER
# ===========================================================================
print("=" * 60)
print("BUILDING HIGH-DETAIL VEHICLES FLEET")
print("=" * 60)

build_sedan((0, -25.0, 0))
build_suv((0, -15.0, 0))
build_sports_car((0, -5.0, 0))
build_pickup((0, 5.0, 0))
build_delivery_van((0, 15.0, 0))
append_school_bus((0, 27.0, 0))

build_showroom()

bpy.context.view_layer.update()
print("All vehicles assembled and updated successfully!")

# Save to Blender/Blend Files/vehicles.blend
out_blend = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/vehicles.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
print("Saved blend file to:", out_blend)

# Export to Assets/Models/Vehicles/
out_models_dir = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Vehicles"
os.makedirs(out_models_dir, exist_ok=True)

glb_path = os.path.join(out_models_dir, "vehicles.glb")
print("Exporting GLB to:", glb_path)
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=False,
    export_apply=False,
    export_animations=True,
    export_yup=True
)
print("Exported GLB successfully!")

fbx_path = os.path.join(out_models_dir, "vehicles.fbx")
print("Exporting FBX to:", fbx_path)
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=False,
    object_types={'EMPTY', 'MESH'},
    bake_anim=True,
    bake_anim_use_all_actions=True,
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True
)
print("Exported FBX successfully!")
print("=" * 60)
print("VEHICLES FLEET GENERATION & EXPORT COMPLETE")
print("=" * 60)
