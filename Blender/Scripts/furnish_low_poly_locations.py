"""Add lightweight furniture to the four existing low-poly GLB locations.

Run start_furnished(kind) and save_furnished(kind) in Blender through the MCP,
then export the selected collection as a GLB. The sparse originals stay intact.
"""

import bpy
from mathutils import Vector


ROOT = "/Users/arieljerickogacilo/mindscape-3d"
KINDS = {
    "classroom": ("Classroom", 10, 8),
    "home": ("Home", 16, 12),
    "dormitory": ("Dormitory", 10, 8),
    "cafeteria": ("Cafeteria", 14, 11),
}
COLLECTION = None

COLORS = {
    "Wood": (0.53, 0.35, 0.20, 1),
    "Linen": (0.75, 0.72, 0.63, 1),
    "Dark": (0.18, 0.22, 0.23, 1),
    "Green": (0.10, 0.26, 0.21, 1),
    "Ceramic": (0.87, 0.86, 0.78, 1),
    "MutedBlue": (0.39, 0.61, 0.70, 1),
    "TabletWood": (0.40, 0.22, 0.09, 1),
    "TabletFrame": (0.035, 0.04, 0.045, 1),
}


def material(name):
    full_name = "LP_Detail_" + name
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
    for previous in tuple(obj.users_collection):
        previous.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    return obj


def tablet_surface(name, x, y):
    """A thin L-shaped writing tablet with an open notch beside the seat."""
    outline = ((-0.20, 0.42), (0.28, 0.42), (0.28, -0.10),
               (0.80, -0.10), (0.80, 0.70), (-0.20, 0.70))
    count = len(outline)
    bottom, top = 0.76, 0.83
    vertices = [(x + px, y + py, bottom) for px, py in outline]
    vertices += [(x + px, y + py, top) for px, py in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    COLLECTION.objects.link(obj)
    mesh.materials.append(material("TabletWood"))
    return obj


def add_tablet_armchair(tag, x, y):
    """Low-poly black-frame classroom chair with a wood writing arm."""
    block(tag + "_Seat_Frame", (x, y, 0.43), (0.70, 0.58, 0.06), "TabletFrame")
    block(tag + "_Wood_Seat", (x, y, 0.51), (0.64, 0.53, 0.10), "TabletWood")
    for side, offset in (("Left", -0.33), ("Right", 0.33)):
        block(tag + "_Rear_Post_" + side, (x + offset, y - 0.29, 0.65),
              (0.07, 0.07, 1.30), "TabletFrame")
        block(tag + "_Front_Leg_" + side, (x + offset, y + 0.27, 0.25),
              (0.07, 0.07, 0.50), "TabletFrame")
        block(tag + "_Lower_Rail_" + side, (x + offset, y, 0.18),
              (0.06, 0.55, 0.06), "TabletFrame")
    block(tag + "_Lower_Front_Rail", (x, y + 0.27, 0.18),
          (0.68, 0.06, 0.06), "TabletFrame")
    block(tag + "_Wood_Back", (x, y - 0.29, 1.06),
          (0.64, 0.06, 0.32), "TabletWood")
    block(tag + "_Tablet_Support", (x + 0.74, y + 0.05, 0.40),
          (0.07, 0.07, 0.80), "TabletFrame")
    block(tag + "_Tablet_Connector", (x + 0.54, y - 0.10, 0.75),
          (0.48, 0.07, 0.07), "TabletFrame")
    tablet_surface(tag + "_Writing_Tablet", x, y)


def classroom_details():
    # A tablet chair already supplies its own desk surface, so remove the
    # separate student desks and chairs from the original classroom model.
    for obj in tuple(COLLECTION.objects):
        if obj.name.startswith("Student_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for row, y in enumerate((-2.10, 0.15), 1):
        for column, x in enumerate((-3.45, -1.15, 1.15, 3.45), 1):
            add_tablet_armchair("Tablet_Chair_%d_%d" % (row, column), x, y)
    block("Detail_Teacher_Chair_Seat", (0, 3.02, 0.46), (0.6, 0.52, 0.1), "Wood")
    block("Detail_Teacher_Chair_Back", (0, 3.28, 0.78), (0.6, 0.08, 0.68), "Wood")
    block("Detail_Teacher_Chair_Base", (0, 3.02, 0.22), (0.22, 0.3, 0.4), "Dark")
    for side, offset in (("Left", -0.32), ("Right", 0.32)):
        block("Detail_Teacher_Chair_Arm_" + side,
              (offset, 3.02, 0.62), (0.12, 0.48, 0.25), "Wood")
    block("Detail_Bookcase", (4.35, 2.45, 0.95), (0.65, 1.3, 1.9), "Wood")
    for index, z in enumerate((0.45, 1.05, 1.63), 1):
        block("Detail_Bookcase_Shelf_%d" % index,
              (3.98, 2.45, z), (0.04, 1.25, 0.08), "Dark")
    block("Detail_Noticeboard", (-3.45, 3.80, 1.82),
          (1.65, 0.06, 1.05), "MutedBlue")
    block("Detail_Teacher_Books_1", (-0.53, 2.31, 0.88),
          (0.28, 0.38, 0.12), "Linen")
    block("Detail_Teacher_Books_2", (-0.53, 2.31, 0.99),
          (0.30, 0.36, 0.10), "Green")


def home_details():
    for index, (x, table_x) in enumerate(((-7.18, -6.05), (7.18, 6.05)), 1):
        block("Detail_Bedroom_%d_Pillow" % index, (x, 5.58, 0.62),
              (0.76, 0.38, 0.11), "Ceramic")
        block("Detail_Bedroom_%d_Blanket" % index, (x, 4.46, 0.59),
              (1.20, 0.72, 0.06), "MutedBlue")
        block("Detail_Bedroom_%d_Bedside_Table" % index,
              (table_x, 5.15, 0.43), (0.42, 0.42, 0.86), "Wood")
    block("Detail_Sofa_Left_Arm", (-7.16, -3.6, 0.65),
          (0.16, 0.7, 0.5), "Linen")
    block("Detail_Sofa_Right_Arm", (-5.44, -3.6, 0.65),
          (0.16, 0.7, 0.5), "Linen")
    block("Detail_TV_Stand", (-6.3, 0.02, 0.4),
          (1.25, 0.35, 0.8), "Wood")
    block("Detail_TV", (-6.3, 0.15, 1.14),
          (0.95, 0.08, 0.65), "Dark")
    block("Detail_Kitchen_Sink", (4.4, -5.25, 0.99),
          (0.48, 0.38, 0.04), "Dark")
    block("Detail_Kitchen_Stove", (5.9, -5.25, 0.99),
          (0.50, 0.38, 0.04), "Dark")
    block("Detail_Kitchen_Fridge", (7.25, -4.55, 0.90),
          (0.75, 0.72, 1.8), "Ceramic")
    for index, x in enumerate((4.0, 6.6), 1):
        block("Detail_Dining_Chair_Back_%d" % index,
              (x, -1.73, 0.81), (0.36, 0.08, 0.75), "Wood")
    block("Detail_Toilet_Seat", (1.3, 2.55, 0.52),
          (0.43, 0.45, 0.05), "Ceramic")
    block("Detail_Washbasin_Rim", (1.22, 4.75, 0.92),
          (0.60, 0.40, 0.04), "Ceramic")


def dormitory_details():
    for side, x, table_x in (("Left", -3.25, -2.07),
                             ("Right", 3.25, 2.07)):
        for row, y in enumerate((-1.65, 1.05), 1):
            tag = "Detail_%s_Bed_%d" % (side, row)
            block(tag + "_Pillow", (x, y + 0.67, 0.63),
                  (0.74, 0.36, 0.11), "Ceramic")
            block(tag + "_Blanket", (x, y - 0.35, 0.59),
                  (1.15, 0.75, 0.06), "MutedBlue")
            block(tag + "_Bedside", (table_x, y + 0.45, 0.42),
                  (0.40, 0.42, 0.84), "Wood")
    for index, x in enumerate((-1.8, -0.6, 0.6, 1.8), 1):
        block("Detail_Locker_Handle_%d" % index,
              (x + 0.25, 2.91, 1.1), (0.05, 0.04, 0.25), "Dark")
    block("Detail_Study_Table_Top", (0, 1.35, 0.72),
          (1.30, 0.66, 0.12), "Wood")
    block("Detail_Study_Table_Base", (0, 1.35, 0.34),
          (0.16, 0.48, 0.68), "Dark")
    for index, x in enumerate((-0.95, 0.95), 1):
        block("Detail_Study_Stool_%d" % index, (x, 1.35, 0.42),
              (0.38, 0.38, 0.84), "Wood")


def enlarge_cafeteria_shell():
    """Expand the imported room shell while leaving its furniture unscaled."""
    scale_x, scale_y = 14 / 12, 11 / 9
    for obj in COLLECTION.objects:
        if (obj.name == "Floor" or obj.name.startswith(("Front_", "Back_Wall",
                                                         "Left_Wall", "Left_Window"))
                or obj.name == "Right_Wall"):
            obj.location.x *= scale_x
            obj.location.y *= scale_y
            obj.scale.x *= scale_x
            obj.scale.y *= scale_y
    bpy.context.view_layer.update()


def cafeteria_details():
    right_wall = bpy.data.objects["Right_Wall"]
    back_wall = bpy.data.objects["Back_Wall"]
    front_wall = bpy.data.objects["Front_Wall_Left"]
    right_inner = right_wall.location.x - right_wall.dimensions.x / 2
    back_inner = back_wall.location.y - back_wall.dimensions.y / 2
    front_inner = front_wall.location.y + front_wall.dimensions.y / 2
    counter_y = back_inner - 1.23

    # Move the serving furniture with the expanded rear wall.
    for name in ("Serving_Counter_Base", "Serving_Counter_Top"):
        bpy.data.objects[name].location.y = counter_y
    panel = bpy.data.objects["Serving_Back_Panel"]
    panel.location.y = back_inner - panel.dimensions.y / 2

    # Three columns and two rows, with clear routes between all table groups.
    for obj in COLLECTION.objects:
        parts = obj.name.split("_")
        if len(parts) >= 4 and parts[0] == "Dining" and parts[1] in ("1", "2"):
            obj.location.x += -1.5 if parts[2] == "1" else 1.5
            obj.location.y += -0.65 if parts[1] == "1" else 0.85
    for row, y in enumerate((-2.60, 1.00), 1):
        tag = "Detail_Center_Dining_%d" % row
        block(tag + "_Table", (0, y, 0.72), (1.55, 0.78, 0.13), "Wood")
        block(tag + "_Support", (0, y, 0.35), (0.15, 0.50, 0.68), "Dark")
        for index, bench_y in enumerate((y - 0.73, y + 0.73), 1):
            block(tag + "_Bench_%d" % index, (0, bench_y, 0.43),
                  (1.35, 0.32, 0.16), "Wood")
    cabinet_x = right_inner - 0.375
    cabinet_y = back_inner - 0.325
    for index, x in enumerate((-cabinet_x, cabinet_x), 1):
        block("Detail_Service_Cabinet_%d" % index,
              (x, cabinet_y, 0.95), (0.75, 0.65, 1.9), "Wood")
    block("Detail_Cash_Register", (2.15, counter_y, 1.10),
          (0.42, 0.38, 0.25), "Dark")
    for index, x in enumerate((-2.15, -1.45, -0.75, -0.05, 0.65, 1.35), 1):
        block("Detail_Serving_Tray_%d" % index,
              (x, counter_y, 1.04), (0.48, 0.32, 0.04), "Ceramic")
    bin_x = right_inner - 0.26
    bin_y = front_inner + 0.26
    for index, x in enumerate((-bin_x, bin_x), 1):
        block("Detail_Waste_Bin_%d" % index,
              (x, bin_y, 0.42), (0.52, 0.52, 0.84), "Dark")


def preview_setup(width, depth):
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new("Preview_Camera")
    camera = bpy.data.objects.new("Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (width * 0.75, -depth * 1.08,
                       max(width, depth) * 1.9)
    camera.rotation_euler = (Vector((0, 0, 0.6)) - camera.location).to_track_quat(
        "-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(width, depth) * 1.38
    scene.camera = camera
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
    bg.inputs["Color"].default_value = (0.72, 0.76, 0.80, 1)
    bg.inputs["Strength"].default_value = 0.8


def start_furnished(kind):
    global COLLECTION
    if kind not in KINDS:
        raise ValueError("Unknown location: " + kind)
    name, width, depth = KINDS[kind]
    for obj in tuple(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in tuple(bpy.data.collections):
        if col.name.startswith(("LowPoly_", "Furnished_")):
            bpy.data.collections.remove(col)
    source = ROOT + "/Assets/Models/" + name + "_LowPoly.glb"
    bpy.ops.import_scene.gltf(filepath=source)
    COLLECTION = bpy.data.collections.new("Furnished_" + name)
    bpy.context.scene.collection.children.link(COLLECTION)
    base_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    for obj in base_objects:
        for old_col in tuple(obj.users_collection):
            old_col.objects.unlink(obj)
        COLLECTION.objects.link(obj)
    if kind == "cafeteria":
        enlarge_cafeteria_shell()
    {"classroom": classroom_details, "home": home_details,
     "dormitory": dormitory_details, "cafeteria": cafeteria_details}[kind]()
    preview_setup(width, depth)
    meshes = [obj for obj in COLLECTION.objects if obj.type == "MESH"]
    triangles = sum(len(face.vertices) - 2
                    for obj in meshes for face in obj.data.polygons)
    return {"kind": kind, "base_meshes": len(base_objects),
            "meshes": len(meshes), "triangles": triangles}


def save_furnished(kind):
    if kind not in KINDS:
        raise ValueError("Unknown location: " + kind)
    name = KINDS[kind][0]
    preview = ROOT + "Documents/Concepts/low-poly-" + kind + "-furnished-preview.png"
    bpy.context.scene.render.filepath = preview
    hidden = [obj for obj in COLLECTION.objects
              if obj.name.startswith("Front_") or obj.name == "Right_Wall"
              or (kind == "classroom" and obj.name.startswith("Door"))]
    for obj in hidden:
        obj.hide_render = True
    bpy.ops.render.render(write_still=True)
    for obj in hidden:
        obj.hide_render = False
    blend = ROOT + "/Blender/Blend Files/low-poly-" + kind + "-furnished.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in COLLECTION.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["Floor"]
    return {"blend": blend, "preview": preview,
            "selected_meshes": len(COLLECTION.objects)}
