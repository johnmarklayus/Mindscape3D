import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# Clear scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)

# Materials
def get_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=5.0):
    m = bpy.data.materials.new("Mat_" + name)
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

m_paint = get_mat("SedanRed", (0.85, 0.10, 0.10), roughness=0.25, metallic=0.35)
m_glass = get_mat("CarGlass", (0.15, 0.22, 0.30), roughness=0.08, metallic=0.2)
m_dark_glass = get_mat("SunroofGlass", (0.05, 0.08, 0.12), roughness=0.05, metallic=0.3)
m_black = get_mat("TrimBlack", (0.10, 0.11, 0.12), roughness=0.7)
m_chrome = get_mat("Chrome", (0.88, 0.89, 0.90), roughness=0.12, metallic=0.95)
m_silver = get_mat("Silver", (0.72, 0.74, 0.76), roughness=0.35, metallic=0.7)
m_headlight = get_mat("HeadlightGlow", (1.0, 0.98, 0.90), emission=(1.0, 0.98, 0.90), emission_strength=8.0)
m_taillight = get_mat("TaillightGlow", (0.95, 0.08, 0.06), emission=(0.95, 0.08, 0.06), emission_strength=6.0)
m_amber = get_mat("AmberLight", (1.0, 0.65, 0.08), emission=(1.0, 0.65, 0.08), emission_strength=5.0)
m_reverse = get_mat("ReverseLight", (0.95, 0.95, 0.98), emission=(0.95, 0.95, 0.98), emission_strength=5.0)
m_tire = get_mat("TireRubber", (0.14, 0.14, 0.15), roughness=0.88)
m_rim = get_mat("WheelRim", (0.78, 0.80, 0.82), roughness=0.25, metallic=0.85)
m_brake = get_mat("BrakeSteel", (0.65, 0.68, 0.70), roughness=0.25, metallic=0.9)
m_caliper = get_mat("BrakeCaliper", (0.85, 0.10, 0.10), roughness=0.3, metallic=0.2)
m_plate = get_mat("LicensePlate", (0.95, 0.95, 0.92), roughness=0.6)

def create_beveled_box(name, loc, size, bevel_width=0.04, segments=1, mat=None):
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if bevel_width > 0.001:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel_width, offset_type='OFFSET', segments=segments, profile=0.5, affect='EDGES')
    bm.to_mesh(me)
    bm.free()
    ob.location = loc
    if mat:
        ob.data.materials.append(mat)
    return ob

def create_tapered_box(name, loc, length, width_bottom, width_top, height, front_rake, rear_rake, bevel=0.04, mat=None):
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
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
    bm.to_mesh(me)
    bm.free()
    ob.location = loc
    if mat:
        ob.data.materials.append(mat)
    return ob

# Build Prototype Sedan
body_parts = []

# 1. Main lower body with carved wheel wells
body_base = create_beveled_box("Sedan_Base", (0, 0, 0.58), (4.7, 2.02, 0.46), bevel_width=0.06, segments=2, mat=m_paint)

cutters = []
for wx, wy in [(1.35, 1.05), (1.35, -1.05), (-1.35, 1.05), (-1.35, -1.05)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.45, location=(wx, wy, 0.42), rotation=(math.radians(90), 0, 0))
    cutters.append(bpy.context.active_object)

bpy.ops.object.select_all(action='DESELECT')
for c in cutters:
    c.select_set(True)
bpy.context.view_layer.objects.active = cutters[0]
bpy.ops.object.join()
cutter_union = bpy.context.active_object

bool_mod = body_base.modifiers.new("WheelWells", 'BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cutter_union
bool_mod.solver = 'EXACT'
bpy.context.view_layer.objects.active = body_base
bpy.ops.object.modifier_apply(modifier="WheelWells")
bpy.data.objects.remove(cutter_union, do_unlink=True)
body_parts.append(body_base)

# 2. Sloped Hood
hood = create_tapered_box("Sedan_Hood", (1.45, 0, 0.70), length=1.45, width_bottom=1.98, width_top=1.85, height=0.20, front_rake=0.18, rear_rake=0.0, bevel=0.03, mat=m_paint)
body_parts.append(hood)

# 3. Rear Trunk Deck
trunk = create_tapered_box("Sedan_Trunk", (-1.65, 0, 0.70), length=1.05, width_bottom=1.98, width_top=1.86, height=0.18, front_rake=0.0, rear_rake=0.15, bevel=0.03, mat=m_paint)
body_parts.append(trunk)

# Trunk Lip Spoiler
trunk_spoiler = create_beveled_box("Sedan_TrunkSpoiler", (-2.18, 0, 0.88), (0.12, 1.70, 0.05), bevel_width=0.015, mat=m_black)
body_parts.append(trunk_spoiler)

# 4. Greenhouse / Cabin (Slanted Windshield & Rear Window)
cabin_glass = create_tapered_box("Sedan_CabinGlass", (-0.10, 0, 0.81), length=2.25, width_bottom=1.88, width_top=1.54, height=0.68, front_rake=0.65, rear_rake=0.55, bevel=0.03, mat=m_glass)
body_parts.append(cabin_glass)

# Roof Panel with slight overhang
roof_panel = create_beveled_box("Sedan_Roof", (-0.05, 0, 1.49), (1.18, 1.56, 0.05), bevel_width=0.025, mat=m_paint)
body_parts.append(roof_panel)

# Sunroof Glass
sunroof = create_beveled_box("Sedan_Sunroof", (0.10, 0, 1.515), (0.55, 0.95, 0.01), bevel_width=0.01, mat=m_dark_glass)
body_parts.append(sunroof)

# Shark fin antenna
fin = create_beveled_box("Sedan_SharkFin", (-0.50, 0, 1.55), (0.16, 0.05, 0.08), bevel_width=0.015, mat=m_black)
body_parts.append(fin)

# Window Pillars (A, B, C pillars)
# B-Pillars (vertical center post)
b_pillar_l = create_beveled_box("Sedan_BPillar_L", (-0.08, 0.86, 1.15), (0.08, 0.04, 0.65), bevel_width=0.01, mat=m_black)
b_pillar_r = create_beveled_box("Sedan_BPillar_R", (-0.08, -0.86, 1.15), (0.08, 0.04, 0.65), bevel_width=0.01, mat=m_black)
body_parts.extend([b_pillar_l, b_pillar_r])

# 5. Front Bumper with wraparound corners & lower intake
bumper_f = create_beveled_box("Sedan_Bumper_F", (2.35, 0, 0.44), (0.28, 2.06, 0.34), bevel_width=0.06, segments=2, mat=m_paint)
intake_f = create_beveled_box("Sedan_Intake_F", (2.42, 0, 0.36), (0.16, 1.10, 0.14), bevel_width=0.02, mat=m_black)
fog_l = create_beveled_box("Sedan_Fog_L", (2.42, 0.80, 0.36), (0.16, 0.22, 0.10), bevel_width=0.015, mat=m_headlight)
fog_r = create_beveled_box("Sedan_Fog_R", (2.42, -0.80, 0.36), (0.16, 0.22, 0.10), bevel_width=0.015, mat=m_headlight)
body_parts.extend([bumper_f, intake_f, fog_l, fog_r])

# Front Grille with Chrome Frame & Horizontal Slats
grille_frame = create_beveled_box("Sedan_GrilleFrame", (2.36, 0, 0.65), (0.12, 1.12, 0.26), bevel_width=0.03, mat=m_chrome)
grille_mesh = create_beveled_box("Sedan_GrilleMesh", (2.38, 0, 0.65), (0.10, 1.04, 0.20), bevel_width=0.01, mat=m_black)
grille_badge = create_beveled_box("Sedan_Badge_F", (2.44, 0, 0.65), (0.04, 0.14, 0.10), bevel_width=0.01, mat=m_silver)
body_parts.extend([grille_frame, grille_mesh, grille_badge])

# Multi-Lens Headlights (Projectors + Amber Turn Signal)
for side, y_sign in [("L", 1), ("R", -1)]:
    hl_housing = create_beveled_box(f"Sedan_HL_House_{side}", (2.32, y_sign * 0.78, 0.66), (0.18, 0.42, 0.18), bevel_width=0.02, mat=m_chrome)
    hl_proj = create_beveled_box(f"Sedan_HL_Proj_{side}", (2.36, y_sign * 0.72, 0.66), (0.12, 0.24, 0.12), bevel_width=0.01, mat=m_headlight)
    hl_turn = create_beveled_box(f"Sedan_HL_Turn_{side}", (2.34, y_sign * 0.90, 0.66), (0.12, 0.10, 0.12), bevel_width=0.01, mat=m_amber)
    body_parts.extend([hl_housing, hl_proj, hl_turn])

# 6. Rear Bumper & Fascia
bumper_r = create_beveled_box("Sedan_Bumper_R", (-2.35, 0, 0.44), (0.28, 2.06, 0.34), bevel_width=0.06, segments=2, mat=m_paint)
diffuser_r = create_beveled_box("Sedan_Diffuser_R", (-2.42, 0, 0.34), (0.16, 1.30, 0.12), bevel_width=0.02, mat=m_black)
body_parts.extend([bumper_r, diffuser_r])

# Dual Chrome Exhaust Pipes
exhaust_l = create_beveled_box("Sedan_Exhaust_L", (-2.48, 0.55, 0.32), (0.15, 0.12, 0.08), bevel_width=0.015, mat=m_chrome)
exhaust_r = create_beveled_box("Sedan_Exhaust_R", (-2.48, -0.55, 0.32), (0.15, 0.12, 0.08), bevel_width=0.015, mat=m_chrome)
body_parts.extend([exhaust_l, exhaust_r])

# Multi-Lens Taillights
for side, y_sign in [("L", 1), ("R", -1)]:
    tl_house = create_beveled_box(f"Sedan_TL_House_{side}", (-2.32, y_sign * 0.78, 0.68), (0.16, 0.44, 0.16), bevel_width=0.02, mat=m_black)
    tl_brake = create_beveled_box(f"Sedan_TL_Brake_{side}", (-2.35, y_sign * 0.82, 0.68), (0.12, 0.26, 0.12), bevel_width=0.01, mat=m_taillight)
    tl_amber = create_beveled_box(f"Sedan_TL_Amber_{side}", (-2.35, y_sign * 0.66, 0.71), (0.12, 0.12, 0.06), bevel_width=0.01, mat=m_amber)
    tl_rev = create_beveled_box(f"Sedan_TL_Rev_{side}", (-2.35, y_sign * 0.66, 0.64), (0.12, 0.12, 0.06), bevel_width=0.01, mat=m_reverse)
    body_parts.extend([tl_house, tl_brake, tl_amber, tl_rev])

# License Plates (Front & Rear)
plate_f_frame = create_beveled_box("Sedan_Plate_F_Frame", (2.48, 0, 0.44), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
plate_f_face = create_beveled_box("Sedan_Plate_F_Face", (2.50, 0, 0.44), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
plate_r_frame = create_beveled_box("Sedan_Plate_R_Frame", (-2.48, 0, 0.52), (0.04, 0.54, 0.18), bevel_width=0.01, mat=m_black)
plate_r_face = create_beveled_box("Sedan_Plate_R_Face", (-2.50, 0, 0.52), (0.02, 0.48, 0.14), bevel_width=0.005, mat=m_plate)
body_parts.extend([plate_f_frame, plate_f_face, plate_r_frame, plate_r_face])

# Side Mirrors
for side, y_sign in [("L", 1), ("R", -1)]:
    stalk = create_beveled_box(f"Sedan_Mirror_Stalk_{side}", (0.70, y_sign * 0.98, 0.84), (0.10, 0.14, 0.04), bevel_width=0.01, mat=m_black)
    house = create_beveled_box(f"Sedan_Mirror_House_{side}", (0.70, y_sign * 1.10, 0.88), (0.18, 0.14, 0.12), bevel_width=0.02, mat=m_paint)
    face = create_beveled_box(f"Sedan_Mirror_Face_{side}", (0.64, y_sign * 1.10, 0.88), (0.02, 0.11, 0.09), bevel_width=0.005, mat=m_chrome)
    body_parts.extend([stalk, house, face])

# Door Handles (4 Doors)
for x_pos, name_x in [(0.30, "F"), (-0.60, "R")]:
    for side, y_sign in [("L", 1), ("R", -1)]:
        handle = create_beveled_box(f"Sedan_Handle_{name_x}_{side}", (x_pos, y_sign * 1.02, 0.76), (0.14, 0.03, 0.04), bevel_width=0.008, mat=m_chrome)
        body_parts.append(handle)

# Windshield Wipers
wiper_l = create_beveled_box("Sedan_Wiper_L", (0.75, 0.35, 0.84), (0.32, 0.04, 0.02), bevel_width=0.005, mat=m_black)
wiper_l.rotation_euler = (0, math.radians(-15), math.radians(18))
wiper_r = create_beveled_box("Sedan_Wiper_R", (0.75, -0.35, 0.84), (0.32, 0.04, 0.02), bevel_width=0.005, mat=m_black)
wiper_r.rotation_euler = (0, math.radians(-15), math.radians(18))
body_parts.extend([wiper_l, wiper_r])

# JOIN ALL BODY PARTS INTO ONE UNIFIED MESH: Sedan_Body!
bpy.ops.object.select_all(action='DESELECT')
for p in body_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = body_base
bpy.ops.object.join()
sedan_body = bpy.context.active_object
sedan_body.name = "Sedan_Body"
print("Joined Sedan_Body successfully! Vertices:", len(sedan_body.data.vertices), "Materials:", len(sedan_body.data.materials))

# WHEELS GENERATION (Each wheel joined into Sedan_Wheel_*)
def build_wheel(name, loc, is_left=True):
    parts = []
    # 1. Treaded rubber tire with beveled sidewall
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.42, depth=0.32, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    tire = bpy.context.active_object
    bev = tire.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.04
    bev.segments = 1
    bpy.ops.object.modifier_apply(modifier="Bevel")
    tire.data.materials.append(m_tire)
    parts.append(tire)
    
    # 2. Alloy Rim
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.32, depth=0.325, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    rim = bpy.context.active_object
    rim.data.materials.append(m_rim)
    parts.append(rim)
    
    # 3. Brake Rotor (steel disc inside)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.25, depth=0.03, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    rotor = bpy.context.active_object
    rotor.data.materials.append(m_brake)
    parts.append(rotor)
    
    # 4. Red Brake Caliper
    caliper = create_beveled_box(f"{name}_Caliper", (0.14, 0, 0.16), (0.12, 0.08, 0.14), bevel_width=0.015, mat=m_caliper)
    parts.append(caliper)
    
    # 5. Hubcap & 5 Lug nuts
    outer_y = 0.165 if is_left else -0.165
    cap = create_beveled_box(f"{name}_Cap", (0, outer_y, 0), (0.10, 0.02, 0.10), bevel_width=0.01, mat=m_silver)
    parts.append(cap)
    
    for i in range(5):
        ang = i * (2 * math.pi / 5.0)
        lx = 0.12 * math.cos(ang)
        lz = 0.12 * math.sin(ang)
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

w_fl = build_wheel("Sedan_Wheel_FL", (1.35, 1.05, 0.42), is_left=True)
w_fr = build_wheel("Sedan_Wheel_FR", (1.35, -1.05, 0.42), is_left=False)
w_rl = build_wheel("Sedan_Wheel_RL", (-1.35, 1.05, 0.42), is_left=True)
w_rr = build_wheel("Sedan_Wheel_RR", (-1.35, -1.05, 0.42), is_left=False)

# Root Empty
car_root = bpy.data.objects.new("Car_Sedan", None)
car_root.empty_display_type = 'ARROWS'
car_root.empty_display_size = 1.0
bpy.context.scene.collection.objects.link(car_root)

for ob in [sedan_body, w_fl, w_fr, w_rl, w_rr]:
    ob.parent = car_root

print("Prototype Sedan fully constructed with clean hierarchy!")
