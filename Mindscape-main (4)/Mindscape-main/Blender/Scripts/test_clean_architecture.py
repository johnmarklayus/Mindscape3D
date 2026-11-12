import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# Clean scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)

def get_mat(name, color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.new("Mat_" + name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m

m_yellow = get_mat("Yellow", (0.98, 0.78, 0.08), roughness=0.2, metallic=0.2)
m_glass = get_mat("Glass", (0.15, 0.22, 0.30), roughness=0.08, metallic=0.2)
m_black = get_mat("Black", (0.1, 0.1, 0.1), roughness=0.7)
m_tire = get_mat("Tire", (0.14, 0.14, 0.15), roughness=0.88)
m_rim = get_mat("Rim", (0.86, 0.72, 0.28), roughness=0.25, metallic=0.85)

def create_beveled_box(name, loc, size, bevel_width=0.04, segments=1, mat=None, rot=(0,0,0)):
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
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

# Build Sports Car
parts = []
# Body Base (ground clearance 0.26, height 0.38)
body_base = create_beveled_box("Sports_Base", (0, 0, 0.45), (4.55, 2.16, 0.38), bevel_width=0.06, segments=2, mat=m_yellow)

# Cut wheel wells
cutters = []
for wx, wy in [(1.35, 1.05), (1.35, -1.05), (-1.35, 1.05), (-1.35, -1.05)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.44, depth=0.45, location=(wx, wy, 0.36), rotation=(math.radians(90), 0, 0))
    c = bpy.context.active_object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    cutters.append(c)
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
parts.append(body_base)

# Hood (sloping down from 0.82 to 0.65)
hood = create_tapered_box("Sports_Hood", (1.40, 0, 0.58), length=1.50, width_bottom=2.10, width_top=1.92, height=0.22, front_rake=0.30, rear_rake=0.0, bevel=0.03, mat=m_yellow)
parts.append(hood)

# Splitter
splitter = create_beveled_box("Sports_Splitter", (2.38, 0, 0.20), (0.35, 2.18, 0.05), bevel_width=0.015, mat=m_black)
parts.append(splitter)

# Cabin
cabin = create_tapered_box("Sports_Cabin", (-0.10, 0, 0.64), length=2.20, width_bottom=1.95, width_top=1.50, height=0.60, front_rake=0.75, rear_rake=0.70, bevel=0.03, mat=m_glass)
roof = create_beveled_box("Sports_Roof", (-0.15, 0, 1.25), (1.05, 1.50, 0.04), bevel_width=0.02, mat=m_yellow)
parts.extend([cabin, roof])

# GT Wing
pylon_l = create_beveled_box("Sports_Pylon_L", (-2.05, 0.55, 0.88), (0.12, 0.04, 0.36), bevel_width=0.01, mat=m_black)
pylon_r = create_beveled_box("Sports_Pylon_R", (-2.05, -0.55, 0.88), (0.12, 0.04, 0.36), bevel_width=0.01, mat=m_black)
wing = create_beveled_box("Sports_Wing", (-2.05, 0, 1.08), (0.30, 2.10, 0.04), bevel_width=0.015, mat=m_black)
parts.extend([pylon_l, pylon_r, wing])

# Join Body
bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = body_base
bpy.ops.object.join()
sports_body = bpy.context.active_object
sports_body.name = "SportsCar_Body"

# Wheel Generator
def make_wheel(name, loc, is_left=True):
    wparts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.36, depth=0.32, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    tire = bpy.context.active_object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    tire.data.materials.append(m_tire)
    wparts.append(tire)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.27, depth=0.325, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    rim = bpy.context.active_object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    rim.data.materials.append(m_rim)
    wparts.append(rim)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in wparts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = tire
    bpy.ops.object.join()
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.location = loc
    return wheel

w_fl = make_wheel("Wheel_FL", (1.35, 1.05, 0.36), is_left=True)
w_fr = make_wheel("Wheel_FR", (1.35, -1.05, 0.36), is_left=False)
w_rl = make_wheel("Wheel_RL", (-1.35, 1.05, 0.36), is_left=True)
w_rr = make_wheel("Wheel_RR", (-1.35, -1.05, 0.36), is_left=False)

root = bpy.data.objects.new("Car_Sports", None)
bpy.context.scene.collection.objects.link(root)
for ob in [sports_body, w_fl, w_fr, w_rl, w_rr]:
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)

print("Test clean architecture sports car built!")
