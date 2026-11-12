import bpy
import bmesh
import math

# Clean scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# Create body
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.6))
body = bpy.context.active_object
body.name = "Body"
body.scale = (2.2, 1.0, 0.3)
bpy.ops.object.transform_apply(scale=True)

# Add bevel modifier to body
bev = body.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.05
bev.segments = 2
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create cutter cylinders for wheel wells
cutters = []
for wx, wy in [(1.35, 1.0), (1.35, -1.0), (-1.35, 1.0), (-1.35, -1.0)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=0.45, location=(wx, wy, 0.42), rotation=(math.radians(90), 0, 0))
    c = bpy.context.active_object
    cutters.append(c)

# Join cutters
bpy.ops.object.select_all(action='DESELECT')
for c in cutters:
    c.select_set(True)
bpy.context.view_layer.objects.active = cutters[0]
bpy.ops.object.join()
cutter_union = bpy.context.active_object

# Boolean difference
bool_mod = body.modifiers.new("WheelWells", 'BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cutter_union
bool_mod.solver = 'EXACT'
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="WheelWells")

bpy.data.objects.remove(cutter_union, do_unlink=True)
print("Wheel arches cut successfully! Verts:", len(body.data.vertices))
