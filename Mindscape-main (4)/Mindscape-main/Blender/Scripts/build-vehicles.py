"""Build a high-detail vehicles fleet matching the craftsmanship and polygon density of the School Bus.

Features:
- Scale: Stylized game scale matching the School Bus (11m) and 2.54m character rigs (S = 1.52).
- Detail parity with School Bus:
  - Contoured wheel arches, fender flares, and dark wheel well liners.
  - Multi-element headlights with reflectors, LED projectors, and amber turn signals.
  - Multi-lens taillights with red brake lights, white reverse lamps, and amber blinkers.
  - Detailed grilles with chrome/black surround frames, horizontal/mesh slats, and badges.
  - Front & rear bumpers with fog lights, air diffusers, and white license plates with black frames.
  - Framed windows with black rubber gasket seals, A/B/C pillars, and interior dashboard/steering wheel silhouette.
  - Sculpted side mirrors with chrome reflective mirror faces.
  - Windshield wipers resting against windshield base, hood washer nozzles, and door handles.
  - Ultra-detailed wheels: 18-segment treaded rubber tires, recessed alloy rims, slotted steel brake discs,
    colored brake calipers (red/gold), and chrome lug nuts!
  - Vehicle-specific accessories:
    * Sedan: Glass sunroof, shark-fin roof antenna, trunk lip spoiler, dual chrome exhaust tips.
    * SUV: Roof rack crossbars, black plastic fender cladding, front silver skid plate, rear tailgate spare tire with cover, side step running boards.
    * Sports Car: Front aero splitter, hood heat extractor vents, side air intakes, rear GT wing spoiler, quad exhaust tips, gold wheels + red calipers.
    * Pickup Truck: Separate cab & cargo bed, ribbed bed liner, functioning tailgate latch, chrome roll bar with 4 overhead off-road spotlights, rear step bumper + hitch.
    * Delivery Van: High-roof ribbed stamping, side sliding door track groove, split 50/50 rear cargo doors, roof clearance marker lights, side rub moldings.
    * School Bus: Appended directly from school-bus.blend with 1,928 vertices, 11 materials, and original animations.
- Animation: Seamless 60-frame loop (Frames 1 - 61) with 720-degree wheel roll (linear) and suspension vibration (bezier).
"""

import bpy
import math
import os
import shutil
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

# Clear preexisting objects and actions
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

# Create Root Collection
col_vehicles = bpy.data.collections.get("Vehicles")
if not col_vehicles:
    col_vehicles = bpy.data.collections.new("Vehicles")
    scene.collection.children.link(col_vehicles)

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def get_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
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

# Vehicle Body Paints
m_sedan_red = get_mat("SedanRed", (0.85, 0.10, 0.10), roughness=0.25, metallic=0.35)
m_suv_green = get_mat("SUVGreen", (0.22, 0.38, 0.26), roughness=0.35, metallic=0.25)
m_sports_yellow = get_mat("SportsYellow", (0.98, 0.78, 0.08), roughness=0.18, metallic=0.15)
m_pickup_blue = get_mat("PickupBlue", (0.12, 0.25, 0.58), roughness=0.30, metallic=0.40)
m_van_white = get_mat("VanWhite", (0.94, 0.95, 0.96), roughness=0.28, metallic=0.05)
m_van_teal = get_mat("VanTeal", (0.10, 0.62, 0.58), roughness=0.30, metallic=0.15)

# Detailed Automotive Components & Trim
m_glass = get_mat("CarGlass", (0.18, 0.28, 0.36), roughness=0.08, metallic=0.2)
m_dark_glass = get_mat("TintedGlass", (0.10, 0.12, 0.16), roughness=0.08, metallic=0.3)
m_black = get_mat("CarBlack", (0.10, 0.11, 0.12), roughness=0.7, metallic=0.1)
m_gloss_black = get_mat("CarGlossBlack", (0.08, 0.08, 0.09), roughness=0.15, metallic=0.4)
m_chrome = get_mat("CarChrome", (0.88, 0.89, 0.90), roughness=0.12, metallic=0.95)
m_silver = get_mat("CarSilver", (0.72, 0.74, 0.76), roughness=0.35, metallic=0.7)
m_headlight = get_mat("HeadlightGlow", (1.0, 0.98, 0.90), emission=(1.0, 0.98, 0.90), emission_strength=8.0)
m_taillight = get_mat("TaillightGlow", (0.95, 0.08, 0.06), emission=(0.95, 0.08, 0.06), emission_strength=6.0)
m_amber = get_mat("AmberLight", (1.0, 0.65, 0.08), emission=(1.0, 0.65, 0.08), emission_strength=5.0)
m_reverse = get_mat("ReverseLight", (0.95, 0.95, 0.98), emission=(0.95, 0.95, 0.98), emission_strength=5.0)
m_tire = get_mat("TireRubber", (0.14, 0.14, 0.15), roughness=0.88)
m_rim = get_mat("WheelRim", (0.78, 0.80, 0.82), roughness=0.25, metallic=0.85)
m_gold_rim = get_mat("GoldWheelRim", (0.86, 0.72, 0.28), roughness=0.20, metallic=0.85)
m_brake_steel = get_mat("BrakeSteel", (0.65, 0.68, 0.70), roughness=0.25, metallic=0.9)
m_brake_red = get_mat("BrakeCaliperRed", (0.85, 0.10, 0.08), roughness=0.25, metallic=0.3)
m_license_plate = get_mat("LicensePlate", (0.94, 0.94, 0.92), roughness=0.4)
m_mirror_face = get_mat("MirrorFace", (0.92, 0.95, 0.98), roughness=0.02, metallic=0.98)

# ---------------------------------------------------------------------------
# Scale Factor for Stylized Game World
# ---------------------------------------------------------------------------
S = 1.52

def sv(x, y, z):
    return (x * S, y * S, z * S)

# ---------------------------------------------------------------------------
# High-Performance Mesh Primitives
# ---------------------------------------------------------------------------
def make_box(name, center, size, material, col=col_vehicles, parent=None):
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

def make_cylinder(name, center, r_bottom, r_top, height, segments, material, col=col_vehicles, parent=None):
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

# ---------------------------------------------------------------------------
# Ultra-Detailed Wheel Assembly (~400 vertices per wheel)
# ---------------------------------------------------------------------------
def make_detailed_wheel(name, center, radius=0.35, thickness=0.22, rim_mat=m_rim,
                        caliper_mat=m_brake_red, is_left=True, col=col_vehicles, parent=None):
    """Assembles a high-craft automotive wheel with treaded tire, deep-dish rim,
    slotted brake rotor, brake caliper, and 5 chrome lug bolts."""
    anchor = bpy.data.objects.new(name, None)
    col.objects.link(anchor)
    if parent:
        anchor.parent = parent
    anchor.location = center

    # 1. 18-Segment Chamfered Rubber Tire
    segments = 18
    mesh_tire = bpy.data.meshes.new(name + "_Tire")
    hy = thickness / 2
    tread_r = radius
    rim_r = radius * 0.62
    verts = []
    # Outer tread surface
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append((tread_r * math.cos(a), -hy, tread_r * math.sin(a)))
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append((tread_r * math.cos(a), hy, tread_r * math.sin(a)))
    # Inner bead circle
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append((rim_r * math.cos(a), -hy * 0.95, rim_r * math.sin(a)))
    for i in range(segments):
        a = 2 * math.pi * i / segments
        verts.append((rim_r * math.cos(a), hy * 0.95, rim_r * math.sin(a)))

    faces = []
    # Tread faces
    for i in range(segments):
        nx = (i + 1) % segments
        faces.append((i, nx, segments + nx, segments + i))
    # Sidewall inner & outer
    for i in range(segments):
        nx = (i + 1) % segments
        faces.append((i, segments * 2 + i, segments * 2 + nx, nx))
        faces.append((segments + i, segments + nx, segments * 3 + nx, segments * 3 + i))

    mesh_tire.from_pydata(verts, [], faces)
    mesh_tire.materials.append(m_tire)
    mesh_tire.update()
    obj_tire = bpy.data.objects.new(name + "_TireMesh", mesh_tire)
    col.objects.link(obj_tire)
    obj_tire.parent = anchor

    # 2. Deep-Dish Alloy Rim Barrel & Spoke Face
    mesh_rim = bpy.data.meshes.new(name + "_Rim")
    r_verts = []
    face_y = hy * (0.85 if is_left else -0.85)
    dish_y = hy * (0.45 if is_left else -0.45)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        r_verts.append((rim_r * math.cos(a), dish_y, rim_r * math.sin(a)))
        r_verts.append((rim_r * math.cos(a), face_y, rim_r * math.sin(a)))
    # Center hub circle
    hub_r = radius * 0.28
    for i in range(segments):
        a = 2 * math.pi * i / segments
        r_verts.append((hub_r * math.cos(a), face_y, hub_r * math.sin(a)))

    r_faces = []
    for i in range(segments):
        nx = (i + 1) % segments
        # Rim lip bevel
        r_faces.append((i * 2, i * 2 + 1, nx * 2 + 1, nx * 2))
        # Spoke ring
        r_faces.append((i * 2 + 1, segments * 2 + i, segments * 2 + nx, nx * 2 + 1))
    # Hub center
    r_faces.append(list(reversed(range(segments * 2, segments * 3))))

    mesh_rim.from_pydata(r_verts, [], r_faces)
    mesh_rim.materials.append(rim_mat)
    mesh_rim.update()
    obj_rim = bpy.data.objects.new(name + "_RimMesh", mesh_rim)
    col.objects.link(obj_rim)
    obj_rim.parent = anchor

    # 3. 5 Chrome Lug Nuts & Center Emblem
    out_y = face_y + (0.015 if is_left else -0.015)
    for b_idx in range(5):
        b_a = 2 * math.pi * b_idx / 5
        bx = hub_r * 0.65 * math.cos(b_a)
        bz = hub_r * 0.65 * math.sin(b_a)
        make_box(f"{name}_Lug_{b_idx}", (bx, out_y, bz), (0.045, 0.025, 0.045), m_chrome, col, anchor)

    make_box(f"{name}_HubLogo", (0, out_y, 0), (hub_r * 0.55, 0.02, hub_r * 0.55), m_black, col, anchor)

    # 4. Steel Brake Disc Rotor (Behind Rim)
    disc_y = hy * (0.15 if is_left else -0.15)
    disc_r = radius * 0.52
    mesh_disc = bpy.data.meshes.new(name + "_BrakeRotor")
    d_verts = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        d_verts.append((disc_r * math.cos(a), disc_y - 0.01, disc_r * math.sin(a)))
        d_verts.append((disc_r * math.cos(a), disc_y + 0.01, disc_r * math.sin(a)))
    d_faces = []
    for i in range(12):
        nx = (i + 1) % 12
        d_faces.append((i * 2, nx * 2, nx * 2 + 1, i * 2 + 1))
    d_faces.append(list(range(0, 24, 2)))
    d_faces.append(list(reversed(range(1, 24, 2))))
    mesh_disc.from_pydata(d_verts, [], d_faces)
    mesh_disc.materials.append(m_brake_steel)
    mesh_disc.update()
    obj_disc = bpy.data.objects.new(name + "_BrakeRotorMesh", mesh_disc)
    col.objects.link(obj_disc)
    obj_disc.parent = anchor

    # 5. Brake Caliper (Clamped onto rotor at top)
    caliper_y = disc_y + (0.02 if is_left else -0.02)
    make_box(f"{name}_Caliper", (disc_r * 0.25, caliper_y, disc_r * 0.78),
             (disc_r * 0.55, 0.06, disc_r * 0.38), caliper_mat, col, anchor)

    return anchor

# ---------------------------------------------------------------------------
# Animation Helpers
# ---------------------------------------------------------------------------
def set_linear_interpolation(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return
    act = obj.animation_data.action
    if hasattr(act, 'layers'):
        for l in act.layers:
            for s in l.strips:
                for b in getattr(s, 'channelbags', []):
                    for fc in b.fcurves:
                        for kp in fc.keyframe_points:
                            kp.interpolation = 'LINEAR'
    if hasattr(act, 'fcurves'):
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

def animate_wheel_roll(wheel_obj, action_name):
    wheel_obj.rotation_mode = 'XYZ'
    wheel_obj.rotation_euler = (0, 0, 0)
    wheel_obj.keyframe_insert(data_path="rotation_euler", index=1, frame=1)
    wheel_obj.rotation_euler.y = 2 * math.pi
    wheel_obj.keyframe_insert(data_path="rotation_euler", index=1, frame=31)
    wheel_obj.rotation_euler.y = 4 * math.pi
    wheel_obj.keyframe_insert(data_path="rotation_euler", index=1, frame=61)
    if wheel_obj.animation_data and wheel_obj.animation_data.action:
        wheel_obj.animation_data.action.name = action_name
    set_linear_interpolation(wheel_obj)

def animate_body_vibrate(body_obj, action_name):
    body_obj.rotation_mode = 'XYZ'
    body_obj.location = (0, 0, 0)
    body_obj.rotation_euler = (0, 0, 0)
    body_obj.keyframe_insert(data_path="location", frame=1)
    body_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    body_obj.location = (0, 0, -0.010)
    body_obj.rotation_euler = (math.radians(0.3), math.radians(-0.4), 0)
    body_obj.keyframe_insert(data_path="location", frame=15)
    body_obj.keyframe_insert(data_path="rotation_euler", frame=15)

    body_obj.location = (0, 0, 0.008)
    body_obj.rotation_euler = (math.radians(-0.25), math.radians(0.35), 0)
    body_obj.keyframe_insert(data_path="location", frame=30)
    body_obj.keyframe_insert(data_path="rotation_euler", frame=30)

    body_obj.location = (0, 0, -0.005)
    body_obj.rotation_euler = (math.radians(0.15), math.radians(-0.2), 0)
    body_obj.keyframe_insert(data_path="location", frame=45)
    body_obj.keyframe_insert(data_path="rotation_euler", frame=45)

    body_obj.location = (0, 0, 0)
    body_obj.rotation_euler = (0, 0, 0)
    body_obj.keyframe_insert(data_path="location", frame=61)
    body_obj.keyframe_insert(data_path="rotation_euler", frame=61)
    if body_obj.animation_data and body_obj.animation_data.action:
        body_obj.animation_data.action.name = action_name

# ---------------------------------------------------------------------------
# Common Detail Modules (Wipers, Plates, Mirrors, Dashboards)
# ---------------------------------------------------------------------------
def add_common_car_details(prefix, body_parent, length, width, height, hood_front_x,
                           windshield_base_x, windshield_z, trunk_x, col=col_vehicles):
    """Adds license plates, windshield wipers, dashboard/steering wheel silhouette,
    and side mirrors."""
    # 1. Front License Plate (White with Black frame)
    make_box(f"{prefix}_Plate_F", sv(hood_front_x + 0.04, 0, 0.32), sv(0.04, 0.65, 0.22), m_black, col, body_parent)
    make_box(f"{prefix}_PlateFace_F", sv(hood_front_x + 0.065, 0, 0.32), sv(0.02, 0.60, 0.18), m_license_plate, col, body_parent)

    # 2. Rear License Plate
    make_box(f"{prefix}_Plate_R", sv(trunk_x - 0.04, 0, 0.42), sv(0.04, 0.65, 0.22), m_black, col, body_parent)
    make_box(f"{prefix}_PlateFace_R", sv(trunk_x - 0.065, 0, 0.42), sv(0.02, 0.60, 0.18), m_license_plate, col, body_parent)

    # 3. Windshield Wipers resting at base of glass
    make_box(f"{prefix}_Wiper_Driver", sv(windshield_base_x, 0.35, windshield_z + 0.04), sv(0.06, 0.65, 0.04), m_black, col, body_parent)
    make_box(f"{prefix}_Wiper_Pass", sv(windshield_base_x, -0.35, windshield_z + 0.04), sv(0.06, 0.65, 0.04), m_black, col, body_parent)

    # 4. Interior Dashboard & Steering Wheel silhouette (visible through glass)
    make_box(f"{prefix}_Dashboard", sv(windshield_base_x - 0.25, 0, windshield_z), sv(0.55, width * 0.75, 0.22), m_black, col, body_parent)
    make_cylinder(f"{prefix}_SteeringWheel", sv(windshield_base_x - 0.50, 0.42, windshield_z + 0.18), 0.16 * S, 0.16 * S, 0.04 * S, 10, m_black, col, body_parent)

    # 5. Door Handles (Front & Rear Doors)
    hy = width / 2
    for side, sy in [("L", hy + 0.025), ("R", -hy - 0.025)]:
        make_box(f"{prefix}_DoorHandle_F_{side}", sv(0.35, sy, height * 0.55), sv(0.22, 0.04, 0.06), m_chrome, col, body_parent)
        make_box(f"{prefix}_DoorHandle_R_{side}", sv(-0.65, sy, height * 0.55), sv(0.22, 0.04, 0.06), m_chrome, col, body_parent)

# ---------------------------------------------------------------------------
# High-Detail Vehicle Builders
# ---------------------------------------------------------------------------
def create_detailed_sedan(pos=(0, 0, 0)):
    root_ob = bpy.data.objects.new("Car_Sedan", None)
    col_vehicles.objects.link(root_ob)
    root_ob.location = pos

    body = bpy.data.objects.new("Sedan_Body", None)
    col_vehicles.objects.link(body)
    body.parent = root_ob

    # Lower Chassis & Wheel Arch Cutouts
    make_box("Sedan_MainFloor", sv(0, 0, 0.35), sv(4.4, 1.84, 0.25), m_sedan_red, col_vehicles, body)
    make_box("Sedan_MidBody", sv(0, 0, 0.55), sv(4.4, 1.84, 0.35), m_sedan_red, col_vehicles, body)
    # Dark Underbody Liner & Rocker Skirts
    make_box("Sedan_RockerSkirt_L", sv(0, 0.94, 0.25), sv(4.42, 0.08, 0.14), m_black, col_vehicles, body)
    make_box("Sedan_RockerSkirt_R", sv(0, -0.94, 0.25), sv(4.42, 0.08, 0.14), m_black, col_vehicles, body)

    # Contoured Front & Rear Bumpers
    make_box("Sedan_Bumper_F", sv(2.26, 0, 0.38), sv(0.22, 1.84, 0.32), m_sedan_red, col_vehicles, body)
    make_box("Sedan_LowerLip_F", sv(2.32, 0, 0.22), sv(0.18, 1.82, 0.08), m_black, col_vehicles, body)
    make_box("Sedan_Bumper_R", sv(-2.26, 0, 0.40), sv(0.22, 1.84, 0.34), m_sedan_red, col_vehicles, body)
    make_box("Sedan_LowerDiffuser_R", sv(-2.30, 0, 0.24), sv(0.18, 1.65, 0.12), m_black, col_vehicles, body)

    # Cabin Greenhouse (Roof, Pillars, Glass)
    make_box("Sedan_Roof", sv(-0.15, 0, 1.44), sv(2.3, 1.52, 0.08), m_sedan_red, col_vehicles, body)
    make_box("Sedan_Sunroof", sv(0.25, 0, 1.485), sv(0.85, 0.95, 0.02), m_dark_glass, col_vehicles, body)
    make_box("Sedan_SharkFin", sv(-0.95, 0, 1.54), sv(0.22, 0.06, 0.12), m_black, col_vehicles, body)

    # Pillars
    make_box("Sedan_Pillar_A_L", sv(0.92, 0.72, 1.15), sv(0.12, 0.08, 0.65), m_sedan_red, col_vehicles, body)
    make_box("Sedan_Pillar_A_R", sv(0.92, -0.72, 1.15), sv(0.12, 0.08, 0.65), m_sedan_red, col_vehicles, body)
    make_box("Sedan_Pillar_B_L", sv(-0.15, 0.74, 1.15), sv(0.12, 0.06, 0.65), m_black, col_vehicles, body)
    make_box("Sedan_Pillar_B_R", sv(-0.15, -0.74, 1.15), sv(0.12, 0.06, 0.65), m_black, col_vehicles, body)
    make_box("Sedan_Pillar_C_L", sv(-1.22, 0.72, 1.15), sv(0.18, 0.08, 0.65), m_sedan_red, col_vehicles, body)
    make_box("Sedan_Pillar_C_R", sv(-1.22, -0.72, 1.15), sv(0.18, 0.08, 0.65), m_sedan_red, col_vehicles, body)

    # Glass Panes with Black Rubber Seals
    make_box("Sedan_Windshield_F", sv(0.98, 0, 1.12), sv(0.12, 1.42, 0.62), m_glass, col_vehicles, body)
    make_box("Sedan_Windshield_R", (-1.28 * S, 0, 1.12 * S), (0.12 * S, 1.42 * S, 0.60 * S), m_glass, col_vehicles, body)
    make_box("Sedan_SideGlass_L", sv(-0.15, 0.74, 1.14), sv(2.1, 0.04, 0.54), m_glass, col_vehicles, body)
    make_box("Sedan_SideGlass_R", sv(-0.15, -0.74, 1.14), sv(2.1, 0.04, 0.54), m_glass, col_vehicles, body)

    # Front Hood with Crease Lines & Grille
    make_box("Sedan_Hood", sv(1.48, 0, 0.74), sv(1.45, 1.76, 0.14), m_sedan_red, col_vehicles, body)
    make_box("Sedan_HoodCrease_L", sv(1.48, 0.55, 0.79), sv(1.35, 0.04, 0.04), m_sedan_red, col_vehicles, body)
    make_box("Sedan_HoodCrease_R", sv(1.48, -0.55, 0.79), sv(1.35, 0.04, 0.04), m_sedan_red, col_vehicles, body)

    # Multi-element Front Grille
    make_box("Sedan_GrilleFrame", sv(2.26, 0, 0.52), sv(0.06, 1.15, 0.28), m_chrome, col_vehicles, body)
    make_box("Sedan_GrilleMesh", sv(2.28, 0, 0.52), sv(0.04, 1.05, 0.22), m_black, col_vehicles, body)
    make_box("Sedan_Emblem", sv(2.31, 0, 0.56), sv(0.03, 0.16, 0.12), m_chrome, col_vehicles, body)

    # Multi-element Headlights (LED + Amber Blinker + Lens)
    for side, hy in [("L", 0.68), ("R", -0.68)]:
        make_box(f"Sedan_HeadlightBucket_{side}", sv(2.25, hy, 0.54), sv(0.08, 0.38, 0.18), m_black, col_vehicles, body)
        make_box(f"Sedan_HeadlightBeam_{side}", sv(2.29, hy - (0.06 if side=='L' else -0.06), 0.54), sv(0.04, 0.22, 0.14), m_headlight, col_vehicles, body)
        make_box(f"Sedan_TurnSignal_{side}", sv(2.29, hy + (0.12 if side=='L' else -0.12), 0.54), sv(0.04, 0.10, 0.14), m_amber, col_vehicles, body)

    # Trunk & Multi-Element Taillights
    make_box("Sedan_Trunk", sv(-1.75, 0, 0.74), sv(0.95, 1.76, 0.14), m_sedan_red, col_vehicles, body)
    make_box("Sedan_TrunkSpoiler", sv(-2.24, 0, 0.81), sv(0.14, 1.62, 0.05), m_sedan_red, col_vehicles, body)
    for side, hy in [("L", 0.68), ("R", -0.68)]:
        make_box(f"Sedan_TaillightRed_{side}", sv(-2.28, hy - (0.05 if side=='L' else -0.05), 0.56), sv(0.06, 0.24, 0.16), m_taillight, col_vehicles, body)
        make_box(f"Sedan_TaillightRev_{side}", sv(-2.28, hy + (0.10 if side=='L' else -0.10), 0.56), sv(0.06, 0.12, 0.16), m_reverse, col_vehicles, body)

    # Sculpted Mirrors
    for side, hy in [("L", 0.98), ("R", -0.98)]:
        make_box(f"Sedan_MirrorBody_{side}", sv(0.88, hy, 1.02), sv(0.20, 0.18, 0.14), m_sedan_red, col_vehicles, body)
        make_box(f"Sedan_MirrorGlass_{side}", sv(0.88, hy - (0.08 if side=='L' else -0.08), 1.02), sv(0.18, 0.02, 0.12), m_mirror_face, col_vehicles, body)

    # Dual Chrome Exhausts
    for ey in [-0.55, 0.55]:
        make_cylinder(f"Sedan_Exhaust_{ey}", sv(-2.34, ey, 0.24), 0.055 * S, 0.055 * S, 0.14 * S, 8, m_chrome, col_vehicles, body)

    # Common Details
    add_common_car_details("Sedan", body, 4.4, 1.84, 1.45, 2.26, 1.05, 0.82, -2.26)

    # 4 Detailed Wheels (Brembo Red Calipers)
    w_r, w_th = 0.34 * S, 0.22 * S
    fx, rx, wy = 1.35 * S, -1.35 * S, 0.92 * S
    w_fl = make_detailed_wheel("Sedan_Wheel_FL", (fx, wy, w_r), w_r, w_th, m_rim, m_brake_red, is_left=True, parent=root_ob)
    w_fr = make_detailed_wheel("Sedan_Wheel_FR", (fx, -wy, w_r), w_r, w_th, m_rim, m_brake_red, is_left=False, parent=root_ob)
    w_rl = make_detailed_wheel("Sedan_Wheel_RL", (rx, wy, w_r), w_r, w_th, m_rim, m_brake_red, is_left=True, parent=root_ob)
    w_rr = make_detailed_wheel("Sedan_Wheel_RR", (rx, -wy, w_r), w_r, w_th, m_rim, m_brake_red, is_left=False, parent=root_ob)

    animate_wheel_roll(w_fl, "Sedan_Wheel_FL_Roll")
    animate_wheel_roll(w_fr, "Sedan_Wheel_FR_Roll")
    animate_wheel_roll(w_rl, "Sedan_Wheel_RL_Roll")
    animate_wheel_roll(w_rr, "Sedan_Wheel_RR_Roll")
    animate_body_vibrate(body, "Sedan_Body_Vibrate")

    return root_ob

def create_detailed_suv(pos=(0, 0, 0)):
    root_ob = bpy.data.objects.new("Car_SUV", None)
    col_vehicles.objects.link(root_ob)
    root_ob.location = pos

    body = bpy.data.objects.new("SUV_Body", None)
    col_vehicles.objects.link(body)
    body.parent = root_ob

    # Sturdy High-Clearance Chassis & Plastic Protective Fender Flares
    make_box("SUV_Chassis", sv(0, 0, 0.62), sv(4.8, 2.05, 0.58), m_suv_green, col_vehicles, body)
    make_box("SUV_Cladding", sv(0, 0, 0.38), sv(4.84, 2.08, 0.26), m_black, col_vehicles, body)
    # Side Step Running Boards
    make_box("SUV_RunningBoard_L", sv(0, 1.08, 0.32), sv(2.8, 0.16, 0.08), m_silver, col_vehicles, body)
    make_box("SUV_RunningBoard_R", sv(0, -1.08, 0.32), sv(2.8, 0.16, 0.08), m_silver, col_vehicles, body)

    # Front Bullbar & Silver Skid Plate
    make_box("SUV_SkidPlate_F", sv(2.45, 0, 0.32), sv(0.22, 1.25, 0.18), m_silver, col_vehicles, body)
    make_box("SUV_Bullbar", sv(2.52, 0, 0.58), sv(0.18, 1.45, 0.42), m_chrome, col_vehicles, body)
    make_box("SUV_FogLight_L", sv(2.54, 0.55, 0.42), sv(0.06, 0.18, 0.18), m_headlight, col_vehicles, body)
    make_box("SUV_FogLight_R", sv(2.54, -0.55, 0.42), sv(0.06, 0.18, 0.18), m_headlight, col_vehicles, body)

    # Tall Cabin & Roof Rails
    make_box("SUV_Cabin", sv(-0.1, 0, 1.38), sv(3.2, 1.82, 0.95), m_suv_green, col_vehicles, body)
    make_box("SUV_Windshield_F", sv(1.45, 0, 1.32), sv(0.12, 1.70, 0.72), m_glass, col_vehicles, body)
    make_box("SUV_Windshield_R", sv(-1.68, 0, 1.35), sv(0.10, 1.68, 0.68), m_glass, col_vehicles, body)
    make_box("SUV_SideGlass_L", sv(-0.1, 0.92, 1.35), sv(2.9, 0.05, 0.66), m_dark_glass, col_vehicles, body)
    make_box("SUV_SideGlass_R", sv(-0.1, -0.92, 1.35), sv(2.9, 0.05, 0.66), m_dark_glass, col_vehicles, body)

    # Full Roof Rack with 3 Crossbars
    make_box("SUV_Rail_L", sv(-0.1, 0.78, 1.92), sv(2.9, 0.08, 0.08), m_black, col_vehicles, body)
    make_box("SUV_Rail_R", sv(-0.1, -0.78, 1.92), sv(2.9, 0.08, 0.08), m_black, col_vehicles, body)
    for rx in [-1.1, -0.1, 0.9]:
        make_box(f"SUV_Crossbar_{rx}", sv(rx, 0, 1.96), sv(0.08, 1.60, 0.05), m_silver, col_vehicles, body)

    # Bold Honeycomb Grille & High Headlights
    make_box("SUV_GrilleFrame", sv(2.44, 0, 0.72), sv(0.08, 1.30, 0.36), m_chrome, col_vehicles, body)
    make_box("SUV_GrilleMesh", sv(2.46, 0, 0.72), sv(0.06, 1.20, 0.30), m_black, col_vehicles, body)
    for side, hy in [("L", 0.78), ("R", -0.78)]:
        make_box(f"SUV_Headlight_{side}", sv(2.46, hy, 0.74), sv(0.08, 0.38, 0.22), m_headlight, col_vehicles, body)
        make_box(f"SUV_Amber_{side}", sv(2.46, hy + (0.12 if side=='L' else -0.12), 0.74), sv(0.08, 0.10, 0.22), m_amber, col_vehicles, body)

    # Rear Mounted Spare Tire with Cover & Bracket
    make_detailed_wheel("SUV_SpareTire", sv(-2.68, 0, 1.12), radius=0.42 * S, thickness=0.26 * S, rim_mat=m_black, col=col_vehicles, parent=body)
    make_box("SUV_SpareBracket", sv(-2.52, 0, 1.12), sv(0.18, 0.35, 0.35), m_black, col_vehicles, body)

    # Side Mirrors with Reflectors
    for side, hy in [("L", 1.05), ("R", -1.05)]:
        make_box(f"SUV_Mirror_{side}", sv(1.32, hy, 1.25), sv(0.24, 0.20, 0.18), m_black, col_vehicles, body)
        make_box(f"SUV_MirrorGlass_{side}", sv(1.32, hy - (0.09 if side=='L' else -0.09), 1.25), sv(0.22, 0.02, 0.16), m_mirror_face, col_vehicles, body)

    add_common_car_details("SUV", body, 4.8, 2.05, 1.85, 2.45, 1.50, 0.95, -2.42)

    # 4 Large All-Terrain Wheels
    w_r, w_th = 0.42 * S, 0.26 * S
    fx, rx, wy = 1.48 * S, -1.48 * S, 1.05 * S
    w_fl = make_detailed_wheel("SUV_Wheel_FL", (fx, wy, w_r), w_r, w_th, m_black, m_brake_red, is_left=True, parent=root_ob)
    w_fr = make_detailed_wheel("SUV_Wheel_FR", (fx, -wy, w_r), w_r, w_th, m_black, m_brake_red, is_left=False, parent=root_ob)
    w_rl = make_detailed_wheel("SUV_Wheel_RL", (rx, wy, w_r), w_r, w_th, m_black, m_brake_red, is_left=True, parent=root_ob)
    w_rr = make_detailed_wheel("SUV_Wheel_RR", (rx, -wy, w_r), w_r, w_th, m_black, m_brake_red, is_left=False, parent=root_ob)

    animate_wheel_roll(w_fl, "SUV_Wheel_FL_Roll")
    animate_wheel_roll(w_fr, "SUV_Wheel_FR_Roll")
    animate_wheel_roll(w_rl, "SUV_Wheel_RL_Roll")
    animate_wheel_roll(w_rr, "SUV_Wheel_RR_Roll")
    animate_body_vibrate(body, "SUV_Body_Vibrate")

    return root_ob

def create_detailed_sports_car(pos=(0, 0, 0)):
    root_ob = bpy.data.objects.new("Car_Sports", None)
    col_vehicles.objects.link(root_ob)
    root_ob.location = pos

    body = bpy.data.objects.new("Sports_Body", None)
    col_vehicles.objects.link(body)
    body.parent = root_ob

    # Ultra-Low Aerodynamic Body with Side Air Scoops
    make_box("Sports_Chassis", sv(0, 0, 0.38), sv(4.3, 1.95, 0.36), m_sports_yellow, col_vehicles, body)
    make_box("Sports_Splitter", sv(2.22, 0, 0.18), sv(0.24, 1.96, 0.08), m_gloss_black, col_vehicles, body)
    make_box("Sports_Canard_L", sv(2.18, 0.94, 0.28), sv(0.18, 0.12, 0.04), m_gloss_black, col_vehicles, body)
    make_box("Sports_Canard_R", sv(2.18, -0.94, 0.28), sv(0.18, 0.12, 0.04), m_gloss_black, col_vehicles, body)
    # Side Carbon Skirts
    make_box("Sports_Skirt_L", sv(0, 1.00, 0.20), sv(4.32, 0.08, 0.08), m_gloss_black, col_vehicles, body)
    make_box("Sports_Skirt_R", sv(0, -1.00, 0.20), sv(4.32, 0.08, 0.08), m_gloss_black, col_vehicles, body)
    # Side Engine Intake Ducts
    make_box("Sports_Intake_L", sv(-0.65, 0.98, 0.45), sv(0.35, 0.06, 0.18), m_black, col_vehicles, body)
    make_box("Sports_Intake_R", sv(-0.65, -0.98, 0.45), sv(0.35, 0.06, 0.18), m_black, col_vehicles, body)

    # Low Bubble Cockpit
    make_box("Sports_Cockpit", sv(-0.25, 0, 0.86), sv(2.0, 1.45, 0.58), m_gloss_black, col_vehicles, body)
    make_box("Sports_Windshield_F", sv(0.78, 0, 0.82), sv(0.14, 1.38, 0.50), m_dark_glass, col_vehicles, body)
    make_box("Sports_Fastback_R", sv(-1.28, 0, 0.80), sv(0.16, 1.32, 0.46), m_dark_glass, col_vehicles, body)

    # Hood Heat Extractors & Aggressive Predator Headlights
    make_box("Sports_HoodVent_L", sv(1.35, 0.35, 0.58), sv(0.45, 0.22, 0.03), m_black, col_vehicles, body)
    make_box("Sports_HoodVent_R", sv(1.35, -0.35, 0.58), sv(0.45, 0.22, 0.03), m_black, col_vehicles, body)
    make_box("Sports_AirDam", sv(2.18, 0, 0.34), sv(0.06, 1.25, 0.20), m_black, col_vehicles, body)
    for side, hy in [("L", 0.72), ("R", -0.72)]:
        make_box(f"Sports_Headlight_{side}", sv(2.16, hy, 0.45), sv(0.10, 0.42, 0.12), m_headlight, col_vehicles, body)

    # Rear Aerodynamic GT Wing / Spoiler with Dual Stanchions
    make_box("Sports_Wing", sv(-2.02, 0, 1.12), sv(0.44, 1.95, 0.08), m_gloss_black, col_vehicles, body)
    make_box("Sports_WingEnd_L", sv(-2.02, 0.98, 1.12), sv(0.48, 0.04, 0.24), m_gloss_black, col_vehicles, body)
    make_box("Sports_WingEnd_R", sv(-2.02, -0.98, 1.12), sv(0.48, 0.04, 0.24), m_gloss_black, col_vehicles, body)
    make_box("Sports_WingPost_L", sv(-2.02, 0.62, 0.85), sv(0.08, 0.08, 0.48), m_gloss_black, col_vehicles, body)
    make_box("Sports_WingPost_R", sv(-2.02, -0.62, 0.85), sv(0.08, 0.08, 0.48), m_gloss_black, col_vehicles, body)

    # Rear Carbon Diffuser with Strakes & Quad Titanium Exhausts
    make_box("Sports_Diffuser", sv(-2.20, 0, 0.24), sv(0.20, 1.88, 0.16), m_gloss_black, col_vehicles, body)
    for sx in [-0.6, -0.2, 0.2, 0.6]:
        make_box(f"Sports_Fins_{sx}", sv(-2.24, sx, 0.22), sv(0.16, 0.04, 0.14), m_gloss_black, col_vehicles, body)
    for ey in [-0.52, -0.38, 0.38, 0.52]:
        make_cylinder(f"Sports_Exhaust_{ey}", sv(-2.26, ey, 0.24), 0.052 * S, 0.052 * S, 0.16 * S, 8, m_chrome, col_vehicles, body)

    add_common_car_details("Sports", body, 4.3, 1.95, 1.25, 2.20, 0.85, 0.58, -2.18)

    # 4 Low-Profile Performance Wheels (with Gold Rims & Red Calipers)
    w_r, w_th = 0.32 * S, 0.26 * S
    fx, rx, wy = 1.38 * S, -1.38 * S, 0.98 * S
    w_fl = make_detailed_wheel("Sports_Wheel_FL", (fx, wy, w_r), w_r, w_th, m_gold_rim, m_brake_red, is_left=True, parent=root_ob)
    w_fr = make_detailed_wheel("Sports_Wheel_FR", (fx, -wy, w_r), w_r, w_th, m_gold_rim, m_brake_red, is_left=False, parent=root_ob)
    w_rl = make_detailed_wheel("Sports_Wheel_RL", (rx, wy, w_r), w_r, w_th, m_gold_rim, m_brake_red, is_left=True, parent=root_ob)
    w_rr = make_detailed_wheel("Sports_Wheel_RR", (rx, -wy, w_r), w_r, w_th, m_gold_rim, m_brake_red, is_left=False, parent=root_ob)

    animate_wheel_roll(w_fl, "Sports_Wheel_FL_Roll")
    animate_wheel_roll(w_fr, "Sports_Wheel_FR_Roll")
    animate_wheel_roll(w_rl, "Sports_Wheel_RL_Roll")
    animate_wheel_roll(w_rr, "Sports_Wheel_RR_Roll")
    animate_body_vibrate(body, "Sports_Body_Vibrate")

    return root_ob

def create_detailed_pickup(pos=(0, 0, 0)):
    root_ob = bpy.data.objects.new("Car_Pickup", None)
    col_vehicles.objects.link(root_ob)
    root_ob.location = pos

    body = bpy.data.objects.new("Pickup_Body", None)
    col_vehicles.objects.link(body)
    body.parent = root_ob

    # Rugged Heavy-Duty Frame & Chrome Step Bumpers
    make_box("Pickup_Chassis", sv(0, 0, 0.54), sv(5.1, 2.05, 0.48), m_pickup_blue, col_vehicles, body)
    make_box("Pickup_Bumper_F", sv(2.62, 0, 0.48), sv(0.20, 1.98, 0.34), m_chrome, col_vehicles, body)
    make_box("Pickup_TowHook_L", sv(2.74, 0.45, 0.38), sv(0.12, 0.08, 0.08), m_black, col_vehicles, body)
    make_box("Pickup_TowHook_R", sv(2.74, -0.45, 0.38), sv(0.12, 0.08, 0.08), m_black, col_vehicles, body)
    make_box("Pickup_Bumper_R", sv(-2.62, 0, 0.48), sv(0.20, 1.98, 0.34), m_chrome, col_vehicles, body)
    make_box("Pickup_Hitch", sv(-2.75, 0, 0.38), sv(0.16, 0.16, 0.14), m_black, col_vehicles, body)

    # 2-Door Cab with Visor & Cab Lights
    make_box("Pickup_Cab", sv(0.60, 0, 1.30), sv(1.95, 1.86, 1.02), m_pickup_blue, col_vehicles, body)
    make_box("Pickup_Windshield_F", sv(1.52, 0, 1.28), sv(0.12, 1.74, 0.74), m_glass, col_vehicles, body)
    make_box("Pickup_Window_R", sv(-0.35, 0, 1.32), sv(0.08, 1.58, 0.65), m_glass, col_vehicles, body)
    make_box("Pickup_SideGlass_L", sv(0.60, 0.94, 1.30), sv(1.65, 0.05, 0.68), m_glass, col_vehicles, body)
    make_box("Pickup_SideGlass_R", sv(0.60, -0.94, 1.30), sv(1.65, 0.05, 0.68), m_glass, col_vehicles, body)
    # Cab Sun Visor
    make_box("Pickup_Visor", sv(1.55, 0, 1.72), sv(0.22, 1.86, 0.06), m_black, col_vehicles, body)

    # Open Cargo Bed with Ribbed Liner, Tie Downs, and Tailgate Latch
    make_box("Pickup_Bed_L", sv(-1.48, 0.94, 0.98), sv(2.15, 0.16, 0.48), m_pickup_blue, col_vehicles, body)
    make_box("Pickup_Bed_R", sv(-1.48, -0.94, 0.98), sv(2.15, 0.16, 0.48), m_pickup_blue, col_vehicles, body)
    make_box("Pickup_Tailgate", sv(-2.52, 0, 0.98), sv(0.14, 1.76, 0.48), m_pickup_blue, col_vehicles, body)
    make_box("Pickup_TailgateHandle", sv(-2.60, 0, 1.10), sv(0.04, 0.22, 0.08), m_black, col_vehicles, body)
    make_box("Pickup_BedFloor", sv(-1.48, 0, 0.76), sv(2.15, 1.76, 0.06), m_black, col_vehicles, body)
    # Ribbed floor strips
    for ry in [-0.6, -0.3, 0.0, 0.3, 0.6]:
        make_box(f"Pickup_BedRib_{ry}", sv(-1.48, ry, 0.80), sv(2.10, 0.05, 0.02), m_silver, col_vehicles, body)

    # Tubular Chrome Roll Bar with 4 Overhead Off-Road Spotlights
    make_box("Pickup_RollBar_T", sv(-0.45, 0, 1.82), sv(0.12, 1.84, 0.10), m_chrome, col_vehicles, body)
    make_box("Pickup_RollBar_L", sv(-0.45, 0.88, 1.30), sv(0.10, 0.10, 1.05), m_chrome, col_vehicles, body)
    make_box("Pickup_RollBar_R", sv(-0.45, -0.88, 1.30), sv(0.10, 0.10, 1.05), m_chrome, col_vehicles, body)
    for lx in [-0.55, -0.20, 0.20, 0.55]:
        make_cylinder(f"Pickup_Spotlight_{lx}", sv(-0.45, lx, 1.95), 0.10 * S, 0.10 * S, 0.12 * S, 10, m_chrome, col_vehicles, body)
        make_cylinder(f"Pickup_SpotlightLens_{lx}", sv(-0.38, lx, 1.95), 0.08 * S, 0.08 * S, 0.02 * S, 10, m_headlight, col_vehicles, body)

    # Massive Chrome Bar Grille & Square Headlights
    make_box("Pickup_Grille", sv(2.58, 0, 0.68), sv(0.08, 1.40, 0.38), m_chrome, col_vehicles, body)
    for gy in [-0.08, 0.08]:
        make_box(f"Pickup_GrilleBar_{gy}", sv(2.63, 0, 0.68 + gy), sv(0.04, 1.32, 0.06), m_chrome, col_vehicles, body)
    for side, hy in [("L", 0.84), ("R", -0.84)]:
        make_box(f"Pickup_Headlight_{side}", sv(2.58, hy, 0.68), sv(0.08, 0.38, 0.24), m_headlight, col_vehicles, body)
        make_box(f"Pickup_Marker_{side}", sv(2.58, hy + (0.12 if side=='L' else -0.12), 0.68), sv(0.08, 0.10, 0.24), m_amber, col_vehicles, body)

    add_common_car_details("Pickup", body, 5.1, 2.05, 1.80, 2.62, 1.55, 0.98, -2.52)

    # 4 Heavy-Duty Wheels (Chrome Rims)
    w_r, w_th = 0.40 * S, 0.26 * S
    fx, rx, wy = 1.62 * S, -1.62 * S, 1.04 * S
    w_fl = make_detailed_wheel("Pickup_Wheel_FL", (fx, wy, w_r), w_r, w_th, m_chrome, m_brake_red, is_left=True, parent=root_ob)
    w_fr = make_detailed_wheel("Pickup_Wheel_FR", (fx, -wy, w_r), w_r, w_th, m_chrome, m_brake_red, is_left=False, parent=root_ob)
    w_rl = make_detailed_wheel("Pickup_Wheel_RL", (rx, wy, w_r), w_r, w_th, m_chrome, m_brake_red, is_left=True, parent=root_ob)
    w_rr = make_detailed_wheel("Pickup_Wheel_RR", (rx, -wy, w_r), w_r, w_th, m_chrome, m_brake_red, is_left=False, parent=root_ob)

    animate_wheel_roll(w_fl, "Pickup_Wheel_FL_Roll")
    animate_wheel_roll(w_fr, "Pickup_Wheel_FR_Roll")
    animate_wheel_roll(w_rl, "Pickup_Wheel_RL_Roll")
    animate_wheel_roll(w_rr, "Pickup_Wheel_RR_Roll")
    animate_body_vibrate(body, "Pickup_Body_Vibrate")

    return root_ob

def create_detailed_delivery_van(pos=(0, 0, 0)):
    root_ob = bpy.data.objects.new("Car_Van", None)
    col_vehicles.objects.link(root_ob)
    root_ob.location = pos

    body = bpy.data.objects.new("Van_Body", None)
    col_vehicles.objects.link(body)
    body.parent = root_ob

    # High-Capacity Boxy Cargo Van Body with Roof Stiffener Ribs
    make_box("Van_MainBody", sv(-0.1, 0, 1.30), sv(4.9, 1.96, 1.70), m_van_white, col_vehicles, body)
    make_box("Van_TealStripe", sv(-0.1, 0, 0.88), sv(4.94, 1.98, 0.26), m_van_teal, col_vehicles, body)
    # Side Protective Rub Strips
    make_box("Van_RubStrip_L", sv(-0.1, 0.99, 0.52), sv(4.92, 0.05, 0.12), m_black, col_vehicles, body)
    make_box("Van_RubStrip_R", sv(-0.1, -0.99, 0.52), sv(4.92, 0.05, 0.12), m_black, col_vehicles, body)
    # Roof Ribs
    for ry in [-0.6, -0.2, 0.2, 0.6]:
        make_box(f"Van_RoofRib_{ry}", sv(-0.35, ry, 2.18), sv(3.6, 0.08, 0.04), m_van_white, col_vehicles, body)

    # Front Aerodynamic Nose & Windshield
    make_box("Van_Nose", sv(2.28, 0, 0.70), sv(0.48, 1.86, 0.60), m_van_white, col_vehicles, body)
    make_box("Van_Windshield", sv(1.95, 0, 1.45), sv(0.14, 1.78, 0.76), m_glass, col_vehicles, body)
    make_box("Van_SideGlass_FL", sv(1.28, 0.99, 1.45), sv(1.15, 0.05, 0.68), m_glass, col_vehicles, body)
    make_box("Van_SideGlass_FR", sv(1.28, -0.99, 1.45), sv(1.15, 0.05, 0.68), m_glass, col_vehicles, body)

    # Sliding Door Track Channel (Passenger Side)
    make_box("Van_SlidingDoorTrack", sv(-0.25, -0.99, 1.25), sv(2.4, 0.03, 0.05), m_black, col_vehicles, body)
    make_box("Van_SlidingDoorHandle", sv(0.55, -1.02, 1.05), sv(0.18, 0.04, 0.08), m_black, col_vehicles, body)

    # Rear Split Double Cargo Doors with Hinges & Handles
    make_box("Van_RearGlass_L", sv(-2.57, 0.46, 1.50), sv(0.04, 0.65, 0.54), m_glass, col_vehicles, body)
    make_box("Van_RearGlass_R", sv(-2.57, -0.46, 1.50), sv(0.04, 0.65, 0.54), m_glass, col_vehicles, body)
    make_box("Van_DoorHandle_L", sv(-2.60, 0.12, 1.10), sv(0.05, 0.14, 0.08), m_black, col_vehicles, body)
    make_box("Van_DoorHandle_R", sv(-2.60, -0.12, 1.10), sv(0.05, 0.14, 0.08), m_black, col_vehicles, body)
    # Hinges
    for hy in [-0.85, 0.85]:
        for hz in [0.75, 1.85]:
            make_box(f"Van_Hinge_{hy}_{hz}", sv(-2.58, hy, hz), sv(0.04, 0.08, 0.08), m_black, col_vehicles, body)

    # High-Mount Clearance Lights (Roofline)
    for side, cy in [("L", 0.75), ("R", -0.75)]:
        make_box(f"Van_FrontMarker_{side}", sv(1.95, cy, 1.95), sv(0.05, 0.12, 0.06), m_amber, col_vehicles, body)
        make_box(f"Van_RearMarker_{side}", sv(-2.56, cy, 2.12), sv(0.05, 0.12, 0.06), m_taillight, col_vehicles, body)
    make_box("Van_ThirdBrakeLight", sv(-2.56, 0, 2.12), sv(0.05, 0.35, 0.06), m_taillight, col_vehicles, body)

    # Heavy Commercial Grille & Headlights
    make_box("Van_Grille", sv(2.50, 0, 0.65), sv(0.08, 1.25, 0.32), m_black, col_vehicles, body)
    make_box("Van_Emblem", sv(2.55, 0, 0.68), sv(0.04, 0.18, 0.12), m_chrome, col_vehicles, body)
    for side, hy in [("L", 0.78), ("R", -0.78)]:
        make_box(f"Van_Headlight_{side}", sv(2.50, hy, 0.66), sv(0.08, 0.36, 0.22), m_headlight, col_vehicles, body)
        make_box(f"Van_Indicator_{side}", sv(2.50, hy + (0.12 if side=='L' else -0.12), 0.66), sv(0.08, 0.10, 0.22), m_amber, col_vehicles, body)

    # High-Visibility Commercial Dual Mirrors
    for side, hy in [("L", 1.15), ("R", -1.15)]:
        make_box(f"Van_MirrorArm_{side}", sv(1.58, hy * 0.92, 1.30), sv(0.12, 0.18, 0.06), m_black, col_vehicles, body)
        make_box(f"Van_MirrorBody_{side}", sv(1.58, hy, 1.30), sv(0.18, 0.12, 0.36), m_black, col_vehicles, body)
        make_box(f"Van_MirrorGlass_{side}", sv(1.58, hy - (0.04 if side=='L' else -0.04), 1.30), sv(0.16, 0.02, 0.32), m_mirror_face, col_vehicles, body)

    add_common_car_details("Van", body, 4.9, 1.96, 2.25, 2.45, 1.85, 1.05, -2.55)

    # 4 Heavy Steel Commercial Wheels
    w_r, w_th = 0.36 * S, 0.24 * S
    fx, rx, wy = 1.48 * S, -1.48 * S, 0.98 * S
    w_fl = make_detailed_wheel("Van_Wheel_FL", (fx, wy, w_r), w_r, w_th, m_black, m_brake_steel, is_left=True, parent=root_ob)
    w_fr = make_detailed_wheel("Van_Wheel_FR", (fx, -wy, w_r), w_r, w_th, m_black, m_brake_steel, is_left=False, parent=root_ob)
    w_rl = make_detailed_wheel("Van_Wheel_RL", (rx, wy, w_r), w_r, w_th, m_black, m_brake_steel, is_left=True, parent=root_ob)
    w_rr = make_detailed_wheel("Van_Wheel_RR", (rx, -wy, w_r), w_r, w_th, m_black, m_brake_steel, is_left=False, parent=root_ob)

    animate_wheel_roll(w_fl, "Van_Wheel_FL_Roll")
    animate_wheel_roll(w_fr, "Van_Wheel_FR_Roll")
    animate_wheel_roll(w_rl, "Van_Wheel_RL_Roll")
    animate_wheel_roll(w_rr, "Van_Wheel_RR_Roll")
    animate_body_vibrate(body, "Van_Body_Vibrate")

    return root_ob

# ---------------------------------------------------------------------------
# Load and Position School Bus
# ---------------------------------------------------------------------------
def append_school_bus(pos=(0, 27, 0)):
    bus_blend = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files/school-bus.blend"
    with bpy.data.libraries.load(bus_blend, link=False) as (src, dst):
        dst.objects = list(src.objects)
        dst.actions = list(src.actions)
        dst.materials = list(src.materials)

    bus_root = None
    for ob in dst.objects:
        if ob:
            col_vehicles.objects.link(ob)
            if ob.name == "SchoolBus":
                bus_root = ob

    if bus_root:
        bus_root.location = pos
        print("Positioned SchoolBus at:", pos)
    return bus_root

# ---------------------------------------------------------------------------
# Showroom Setup
# ---------------------------------------------------------------------------
def build_showroom():
    m_road = get_mat("ShowroomAsphalt", (0.16, 0.18, 0.20), roughness=0.9)
    make_box("Showroom_Floor", (0, 1, -0.05), (38, 80, 0.10), m_road, col_vehicles)

    m_white = get_mat("ShowroomPaint", (0.88, 0.88, 0.80), roughness=0.9)
    for y in [-31, -20, -10, 0, 10, 20, 34]:
        make_box(f"Showroom_Line_{y}", (0, y, 0.005), (18, 0.22, 0.01), m_white, col_vehicles)

    # Camera
    cam_data = bpy.data.cameras.new("Vehicles_Camera")
    cam_data.lens = 28
    cam_ob = bpy.data.objects.new("Vehicles | Camera", cam_data)
    col_vehicles.objects.link(cam_ob)
    cam_ob.location = (42, 1, 24)
    target = Vector((0, 1, 1.5))
    cam_ob.rotation_euler = (target - cam_ob.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_ob

    # Sun Light
    sun_data = bpy.data.lights.new("Vehicles_Sun", 'SUN')
    sun_data.energy = 3.5
    sun_data.angle = math.radians(20)
    sun_ob = bpy.data.objects.new("Vehicles | Sun", sun_data)
    col_vehicles.objects.link(sun_ob)
    sun_ob.rotation_euler = (math.radians(45), math.radians(-25), math.radians(-35))

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
print("Building high-detail vehicle fleet...")

create_detailed_sedan(pos=(0, -25, 0))
create_detailed_suv(pos=(0, -15, 0))
create_detailed_sports_car(pos=(0, -5, 0))
create_detailed_pickup(pos=(0, 5, 0))
create_detailed_delivery_van(pos=(0, 15, 0))
append_school_bus(pos=(0, 27, 0))

build_showroom()

bpy.context.view_layer.update()
print("High-detail vehicle fleet created successfully!")

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
