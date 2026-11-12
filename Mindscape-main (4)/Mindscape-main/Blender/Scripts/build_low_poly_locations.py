"""Build small, box-based game locations in Blender via the Blender MCP.

In Blender's Python context, call build_location("home"),
build_location("dormitory"), or build_location("cafeteria"), followed by
save_location(kind). Export the selected meshes as GLB after saving.
"""

import bpy
from mathutils import Vector


ROOT = "/Users/arieljerickogacilo/mindscape-3d"
KINDS = {"home": "Home", "dormitory": "Dormitory", "cafeteria": "Cafeteria"}
COLLECTION = None

COLORS = {
    "Floor": (0.43, 0.46, 0.46, 1),
    "Wall": (0.80, 0.78, 0.69, 1),
    "Wood": (0.52, 0.35, 0.20, 1),
    "Dark": (0.18, 0.21, 0.22, 1),
    "Glass": (0.39, 0.62, 0.72, 1),
    "Linen": (0.75, 0.72, 0.63, 1),
    "Green": (0.12, 0.28, 0.22, 1),
    "Ceramic": (0.87, 0.86, 0.78, 1),
}


def material(name):
    full_name = "LP_" + name
    mat = bpy.data.materials.get(full_name) or bpy.data.materials.new(full_name)
    mat.diffuse_color = COLORS[name]
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = COLORS[name]
    shader.inputs["Roughness"].default_value = 1.0
    return mat


def block(name, location, size, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(color))
    for old_collection in tuple(obj.users_collection):
        old_collection.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    return obj


def wall_x(name, x, y0, y1, z0=0, z1=3.0, color="Wall"):
    return block(name, (x, (y0 + y1) / 2, (z0 + z1) / 2),
                 (0.14, y1 - y0, z1 - z0), color)


def wall_y(name, x0, x1, y, z0=0, z1=3.0, color="Wall"):
    return block(name, ((x0 + x1) / 2, y, (z0 + z1) / 2),
                 (x1 - x0, 0.14, z1 - z0), color)


def reset(name):
    global COLLECTION
    for obj in tuple(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for existing in tuple(bpy.data.collections):
        if existing.name.startswith("LowPoly_"):
            bpy.data.collections.remove(existing)
    COLLECTION = bpy.data.collections.new("LowPoly_" + name)
    bpy.context.scene.collection.children.link(COLLECTION)


def shell(width, depth, front_door=True, back_windows=False, left_windows=True,
          front_door_width=1.0, open_front=False):
    x = width / 2
    y = depth / 2
    block("Floor", (0, 0, -0.1), (width, depth, 0.2), "Floor")
    if front_door:
        half_door = front_door_width / 2
        wall_y("Front_Wall_Left", -x, -half_door, -y)
        wall_y("Front_Wall_Right", half_door, x, -y)
        wall_y("Front_Door_Header", -half_door, half_door, -y, 2.2, 3.0)
        if not open_front:
            block("Front_Door", (0, -y + 0.01, 1.1),
                  (front_door_width - 0.08, 0.08, 2.2), "Wood")
    else:
        wall_y("Front_Wall", -x, x, -y)
    wall_x("Right_Wall", x - 0.07, -y, y)

    if back_windows:
        wall_y("Back_Wall_Lower", -x, x, y - 0.07, 0, 1.1)
        wall_y("Back_Wall_Upper", -x, x, y - 0.07, 2.3, 3.0)
        for index, (a, b) in enumerate(((-x, -x + 1.0), (-x + 2.4, x - 2.4), (x - 1.0, x))):
            wall_y("Back_Wall_Pier_%d" % index, a, b, y - 0.07, 1.1, 2.3)
        for index, center in enumerate((-x + 1.7, x - 1.7)):
            block("Back_Window_%d" % index, (center, y - 0.07, 1.7),
                  (1.4, 0.04, 1.2), "Glass")
    else:
        wall_y("Back_Wall", -x, x, y - 0.07)

    if left_windows:
        wall_x("Left_Wall_Lower", -x + 0.07, -y, y, 0, 1.1)
        wall_x("Left_Wall_Upper", -x + 0.07, -y, y, 2.3, 3.0)
        # Two equal openings with simple opaque blue game-style panes.
        first = -y + 1.2
        second = y - 2.6
        sections = ((-y, first), (first + 1.4, second), (second + 1.4, y))
        for index, (a, b) in enumerate(sections):
            wall_x("Left_Wall_Pier_%d" % index, -x + 0.07, a, b, 1.1, 2.3)
        for index, opening_start in enumerate((first, second)):
            block("Left_Window_%d" % index,
                  (-x + 0.07, opening_start + 0.7, 1.7),
                  (0.04, 1.4, 1.2), "Glass")
    else:
        wall_x("Left_Wall", -x + 0.07, -y, y)


def bed(name, x, y):
    block(name + "_Frame", (x, y, 0.28), (1.35, 2.05, 0.25), "Wood")
    block(name + "_Mattress", (x, y, 0.48), (1.2, 1.88, 0.17), "Linen")


def open_room_door(name, left, right, hinge_on_left=True):
    """A full-height room opening with its low-poly door swung into the room."""
    wall_y(name + "_Header", left, right, 0.8, 2.2, 3.0)
    hinge_x = left + 0.04 if hinge_on_left else right - 0.04
    block(name + "_Leaf", (hinge_x, 1.48, 1.1), (0.08, 1.3, 2.2), "Wood")
    handle_x = hinge_x + 0.05 if hinge_on_left else hinge_x - 0.05
    block(name + "_Handle", (handle_x, 1.98, 1.02),
          (0.06, 0.11, 0.05), "Dark")


def home():
    shell(16, 12, back_windows=True, left_windows=True,
          front_door_width=1.6, open_front=True)
    # The rear bedrooms and bathroom have 1.4-unit door openings onto a
    # wide shared room. Both beds have clear space on their doorway side.
    for index, (a, b) in enumerate(((-8, -4), (-2.6, -0.7),
                                   (0.7, 2.6), (4, 8))):
        wall_y("Rear_Rooms_Front_%d" % index, a, b, 0.8)
    open_room_door("Bedroom_1_Door", -4, -2.6)
    open_room_door("Bathroom_Door", -0.7, 0.7)
    open_room_door("Bedroom_2_Door", 2.6, 4, hinge_on_left=False)
    wall_x("Bedroom_1_Bath_Partition", -2.1, 0.8, 6)
    wall_x("Bath_Bedroom_2_Partition", 2.1, 0.8, 6)
    bed("Bedroom_1_Bed", -7.18, 4.83)
    bed("Bedroom_2_Bed", 7.18, 4.83)
    block("Bedroom_1_Wardrobe", (-7.3, 2.1, 0.9), (0.8, 0.7, 1.8), "Wood")
    block("Bedroom_2_Wardrobe", (7.3, 2.1, 0.9), (0.8, 0.7, 1.8), "Wood")
    # A simple bathtub/shower lines the bathroom's left wall.
    block("Bathroom_Toilet_Base", (1.3, 2.6, 0.25), (0.45, 0.6, 0.5), "Ceramic")
    block("Bathroom_Toilet_Tank", (1.3, 2.95, 0.55), (0.45, 0.18, 0.75), "Ceramic")
    block("Bathroom_Washbasin", (1.22, 4.75, 0.8), (0.65, 0.45, 0.2), "Ceramic")
    block("Bathroom_Washbasin_Pedestal", (1.22, 4.75, 0.35),
          (0.28, 0.25, 0.7), "Ceramic")
    block("Bathroom_Bathtub_Base", (-1.48, 4.68, 0.24),
          (0.95, 1.95, 0.48), "Ceramic")
    block("Bathroom_Bathtub_Water", (-1.48, 4.68, 0.485),
          (0.70, 1.70, 0.02), "Glass")
    for side, x in (("Left", -1.92), ("Right", -1.04)):
        block("Bathroom_Bathtub_Rim_" + side, (x, 4.68, 0.53),
              (0.07, 1.95, 0.12), "Ceramic")
    for end, y in (("Front", 3.74), ("Back", 5.62)):
        block("Bathroom_Bathtub_Rim_" + end, (-1.48, y, 0.53),
              (0.95, 0.07, 0.12), "Ceramic")
    block("Bathroom_Shower_Pipe", (-1.99, 5.28, 1.28),
          (0.05, 0.05, 1.3), "Dark")
    block("Bathroom_Shower_Arm", (-1.79, 5.28, 1.94),
          (0.42, 0.05, 0.05), "Dark")
    block("Bathroom_Shower_Head", (-1.58, 5.28, 1.89),
          (0.16, 0.16, 0.07), "Dark")
    # Shared living, cooking, and dining area.
    block("Living_Sofa_Seat", (-6.3, -3.6, 0.43), (1.8, 0.7, 0.42), "Linen")
    block("Living_Sofa_Back", (-6.3, -3.93, 0.76), (1.8, 0.14, 0.72), "Linen")
    block("Living_Coffee_Table", (-6.3, -1.8, 0.42), (0.85, 0.55, 0.22), "Wood")
    block("Kitchen_Counter", (5.3, -5.25, 0.48), (3.0, 0.65, 0.96), "Wood")
    block("Dining_Table", (5.3, -2.0, 0.72), (1.55, 1.0, 0.13), "Wood")
    for index, x in enumerate((4.0, 6.6)):
        block("Dining_Stool_%d" % index, (x, -2.0, 0.45),
              (0.42, 0.42, 0.9), "Wood")


def dormitory():
    shell(10, 8, back_windows=True, left_windows=True)
    for side, x in (("Left", -3.25), ("Right", 3.25)):
        for row, y in enumerate((-1.65, 1.05), 1):
            bed("%s_Bed_%d" % (side, row), x, y)
    for index, x in enumerate((-1.8, -0.6, 0.6, 1.8), 1):
        block("Locker_%d" % index, (x, 3.28, 0.95),
              (0.78, 0.7, 1.9), "Wood")


def cafeteria():
    shell(12, 9, back_windows=False, left_windows=True)
    wall_y("Serving_Back_Panel", -3.6, 3.6, 4.35, 1.2, 2.5, "Green")
    block("Serving_Counter_Base", (0, 3.12, 0.45), (5.3, 0.85, 0.9), "Wood")
    block("Serving_Counter_Top", (0, 3.12, 0.94), (5.55, 1.0, 0.12), "Dark")
    for row, y in enumerate((-1.95, 0.15), 1):
        for column, x in enumerate((-2.5, 2.5), 1):
            tag = "Dining_%d_%d" % (row, column)
            block(tag + "_Table", (x, y, 0.72), (1.55, 0.78, 0.13), "Wood")
            block(tag + "_Support", (x, y, 0.35), (0.15, 0.5, 0.68), "Dark")
            for index, bench_y in enumerate((y - 0.73, y + 0.73), 1):
                block(tag + "_Bench_%d" % index, (x, bench_y, 0.43),
                      (1.35, 0.32, 0.16), "Wood")


def set_preview(width, depth):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("Preview_Camera")
    cam = bpy.data.objects.new("Preview_Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (width * 0.75, -depth * 1.08, max(width, depth) * 1.9)
    cam.rotation_euler = (Vector((0, 0, 0.6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(width, depth) * 1.38
    scene.camera = cam
    light_data = bpy.data.lights.new("Preview_Light", type="AREA")
    light = bpy.data.objects.new("Preview_Light", light_data)
    scene.collection.objects.link(light)
    light.location = (0, -1, 8)
    light_data.energy = 1800
    light_data.shape = "DISK"
    light_data.size = 8
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.72, 0.76, 0.8, 1)
    bg.inputs["Strength"].default_value = 0.8


def build_location(kind):
    if kind not in KINDS:
        raise ValueError("Unknown location: " + kind)
    reset(KINDS[kind])
    {"home": home, "dormitory": dormitory, "cafeteria": cafeteria}[kind]()
    width, depth = {"home": (16, 12), "dormitory": (10, 8),
                    "cafeteria": (12, 9)}[kind]
    set_preview(width, depth)
    meshes = [obj for obj in COLLECTION.objects if obj.type == "MESH"]
    triangles = sum(len(obj.data.polygons) * 2 for obj in meshes)
    return {"kind": kind, "meshes": len(meshes), "triangles": triangles}


def save_location(kind):
    if kind not in KINDS:
        raise ValueError("Unknown location: " + kind)
    stem = KINDS[kind]
    scene = bpy.context.scene
    preview_path = ROOT + "Documents/Concepts/low-poly-" + kind + "-preview.png"
    scene.render.filepath = preview_path
    # Cutaway preview reveals the layout. Complete walls remain in the saved model.
    hidden = [obj for obj in COLLECTION.objects
              if obj.name.startswith("Front_") or obj.name == "Right_Wall"]
    for obj in hidden:
        obj.hide_render = True
    bpy.ops.render.render(write_still=True)
    for obj in hidden:
        obj.hide_render = False
    blend_path = ROOT + "/Blender/Blend Files/low-poly-" + kind + ".blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in COLLECTION.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["Floor"]
    return {"blend": blend_path, "preview": preview_path,
            "selected_meshes": len(COLLECTION.objects)}
