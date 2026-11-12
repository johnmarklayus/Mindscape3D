"""Small low-poly dorm room with one bunk bed, cabinet, and computer desk.

Call build() and then save() through the Blender MCP. Export the selected
meshes as Dormitory_LowPoly_SmallRoom.glb afterward.
"""

import bpy
from mathutils import Vector

import build_low_poly_locations as base


ROOT = "/Users/arieljerickogacilo/mindscape-3d"


def build():
    base.reset("Dormitory_SmallRoom")
    for col in tuple(bpy.data.collections):
        if col.name.startswith("Furnished_") and not col.objects:
            bpy.data.collections.remove(col)
    base.shell(5, 4.4, back_windows=False, left_windows=False)

    # Replace the solid back wall with one real, rectangular window opening.
    bpy.data.objects.remove(bpy.data.objects["Back_Wall"], do_unlink=True)
    back_y = 2.13
    base.wall_y("Back_Wall_Lower", -2.5, 2.5, back_y, 0, 1.1)
    base.wall_y("Back_Wall_Upper", -2.5, 2.5, back_y, 2.3, 3.0)
    base.wall_y("Back_Wall_Left", -2.5, -0.6, back_y, 1.1, 2.3)
    base.wall_y("Back_Wall_Right", 0.6, 2.5, back_y, 1.1, 2.3)
    base.block("Back_Window", (0, back_y, 1.7), (1.2, 0.04, 1.2), "Glass")

    # One bunk bed, built from cuboids. The upper bunk has a simple guardrail
    # and a short ladder; both bunks have a flat mattress and pillow.
    # The frame's left edge meets the interior face of the left wall.
    x, y = -1.71, -0.10
    for index, (frame_z, mattress_z, pillow_z) in enumerate(
            ((0.30, 0.46, 0.56), (1.53, 1.68, 1.78)), 1):
        base.block("Bunk_%d_Frame" % index, (x, y, frame_z),
                   (1.30, 2.05, 0.20), "Wood")
        base.block("Bunk_%d_Mattress" % index, (x, y, mattress_z),
                   (1.20, 1.90, 0.12), "Linen")
        base.block("Bunk_%d_Pillow" % index, (x, y + 0.70, pillow_z),
                   (0.72, 0.35, 0.08), "Ceramic")
    for side_x in (x - 0.57, x + 0.57):
        for end_y in (y - 0.93, y + 0.93):
            base.block("Bunk_Post_%.2f_%.2f" % (side_x, end_y),
                       (side_x, end_y, 1.05), (0.10, 0.10, 2.10), "Wood")
    base.block("Upper_Bunk_Guardrail", (x + 0.60, y + 0.21, 1.94),
               (0.08, 1.60, 0.22), "Wood")
    for index, ladder_x in enumerate((x - 0.30, x + 0.30), 1):
        base.block("Ladder_Upright_%d" % index,
                   (ladder_x, y - 1.10, 0.95), (0.07, 0.07, 1.72), "Dark")
    for index, rung_z in enumerate((0.47, 0.92, 1.37), 1):
        base.block("Ladder_Rung_%d" % index,
                   (x, y - 1.10, rung_z), (0.67, 0.08, 0.08), "Dark")

    # Cabinet meets the rear and right walls.
    base.block("Cabinet", (1.86, 1.77, 0.93),
               (1.00, 0.58, 1.86), "Wood")
    base.block("Cabinet_Door_Seam", (1.86, 1.46, 0.96),
               (0.035, 0.025, 1.75), "Dark")
    for index, handle_x in enumerate((1.75, 1.97), 1):
        base.block("Cabinet_Handle_%d" % index,
                   (handle_x, 1.44, 1.05), (0.04, 0.04, 0.20), "Dark")

    # Desk is turned so its long back edge meets the right wall.
    base.block("Computer_Desk_Top", (2.03, -0.55, 0.74),
               (0.66, 1.25, 0.10), "Wood")
    for index, leg_y in enumerate((-1.08, -0.02), 1):
        base.block("Computer_Desk_Leg_%d" % index,
                   (2.04, leg_y, 0.35), (0.54, 0.10, 0.68), "Wood")
    base.block("Computer_Monitor", (2.24, -0.55, 1.10),
               (0.08, 0.70, 0.48), "Dark")
    base.block("Computer_Screen", (2.19, -0.55, 1.11),
               (0.015, 0.61, 0.39), "Glass")
    base.block("Computer_Monitor_Stand", (2.24, -0.55, 0.83),
               (0.16, 0.10, 0.13), "Dark")
    base.block("Computer_Keyboard", (1.85, -0.55, 0.82),
               (0.18, 0.52, 0.04), "Dark")
    base.block("Computer_Tower", (2.05, 0.37, 0.43),
               (0.33, 0.40, 0.86), "Dark")
    base.block("Desk_Chair_Seat", (1.12, -0.55, 0.45),
               (0.50, 0.55, 0.09), "Wood")
    base.block("Desk_Chair_Back", (0.87, -0.55, 0.77),
               (0.08, 0.55, 0.68), "Wood")
    for index, leg_y in enumerate((-0.77, -0.33), 1):
        base.block("Desk_Chair_Leg_%d" % index,
                   (1.12, leg_y, 0.22), (0.42, 0.07, 0.40), "Dark")

    base.set_preview(5, 4.4)
    camera = bpy.context.scene.camera
    camera.location = (-4.20, -5.0, 9.5)
    camera.rotation_euler = (Vector((0, 0, 0.6)) - camera.location).to_track_quat(
        "-Z", "Y").to_euler()
    meshes = [obj for obj in base.COLLECTION.objects if obj.type == "MESH"]
    triangles = sum(len(face.vertices) - 2
                    for obj in meshes for face in obj.data.polygons)
    return {"meshes": len(meshes), "triangles": triangles}


def save():
    scene = bpy.context.scene
    preview = ROOT + "Documents/Concepts/low-poly-dormitory-small-room-preview.png"
    scene.render.filepath = preview
    hidden = [obj for obj in base.COLLECTION.objects
              if obj.name.startswith("Front_") or obj.name == "Left_Wall"]
    for obj in hidden:
        obj.hide_render = True
    bpy.ops.render.render(write_still=True)
    for obj in hidden:
        obj.hide_render = False
    blend = ROOT + "/Blender/Blend Files/low-poly-dormitory-small-room.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in base.COLLECTION.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["Floor"]
    return {"blend": blend, "preview": preview,
            "selected": len(bpy.context.selected_objects)}
