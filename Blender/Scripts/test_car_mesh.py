import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# Clean test scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

def create_beveled_cube(name, loc, size, bevel_width=0.04, segments=1, mat=None):
    """Creates a cube with beveled edges and applies scale."""
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale to size
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    
    # Bevel all edges
    if bevel_width > 0.001:
        bmesh.ops.bevel(
            bm,
            geom=bm.edges[:] + bm.verts[:],
            offset=bevel_width,
            offset_type='OFFSET',
            segments=segments,
            profile=0.5,
            affect='EDGES'
        )
    
    bm.to_mesh(me)
    bm.free()
    ob.location = loc
    if mat:
        ob.data.materials.append(mat)
    return ob

def create_tapered_cabin(name, loc, length, width_bottom, width_top, height, front_rake, rear_rake, bevel=0.04, mat=None):
    """Creates a realistic tapered car cabin with slanted windshield and rear glass."""
    me = bpy.data.meshes.new(name + "_Mesh")
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    
    bm = bmesh.new()
    # 8 vertices for a frustum/tapered prism
    # Bottom vertices (z = 0)
    x_f_b = length / 2.0
    x_r_b = -length / 2.0
    y_b = width_bottom / 2.0
    
    # Top vertices (z = height) with rake (front_rake pulls front edge back, rear_rake pushes rear edge forward)
    x_f_t = x_f_b - front_rake
    x_r_t = x_r_b + rear_rake
    y_t = width_top / 2.0
    z_t = height
    
    v0 = bm.verts.new((x_f_b, -y_b, 0)) # front-right bottom
    v1 = bm.verts.new((x_f_b,  y_b, 0)) # front-left bottom
    v2 = bm.verts.new((x_r_b,  y_b, 0)) # rear-left bottom
    v3 = bm.verts.new((x_r_b, -y_b, 0)) # rear-right bottom
    
    v4 = bm.verts.new((x_f_t, -y_t, z_t)) # front-right top
    v5 = bm.verts.new((x_f_t,  y_t, z_t)) # front-left top
    v6 = bm.verts.new((x_r_t,  y_t, z_t)) # rear-left top
    v7 = bm.verts.new((x_r_t, -y_t, z_t)) # rear-right top
    
    bm.faces.new((v0, v1, v2, v3)) # Bottom
    bm.faces.new((v7, v6, v5, v4)) # Top
    bm.faces.new((v0, v4, v5, v1)) # Front (Windshield)
    bm.faces.new((v2, v6, v7, v3)) # Rear (Rear Window)
    bm.faces.new((v1, v5, v6, v2)) # Left side
    bm.faces.new((v3, v7, v4, v0)) # Right side
    
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    if bevel > 0.001:
        bmesh.ops.bevel(
            bm,
            geom=bm.edges[:] + bm.verts[:],
            offset=bevel,
            offset_type='OFFSET',
            segments=1,
            profile=0.5,
            affect='EDGES'
        )
        
    bm.to_mesh(me)
    bm.free()
    ob.location = loc
    if mat:
        ob.data.materials.append(mat)
    return ob

print("Test car mesh helpers defined successfully.")

# Create materials
def get_mat(name, color, roughness=0.5, metallic=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 5.0
    return m

m_red = get_mat("PaintRed", (0.85, 0.1, 0.1), roughness=0.2, metallic=0.3)
m_glass = get_mat("Glass", (0.1, 0.2, 0.3), roughness=0.1, metallic=0.2)
m_black = get_mat("Black", (0.1, 0.1, 0.1), roughness=0.8)
m_chrome = get_mat("Chrome", (0.85, 0.85, 0.85), roughness=0.15, metallic=0.95)
m_glow = get_mat("Glow", (1, 1, 0.9), emission=(1, 1, 0.9))

# Lower Body / Beltline
body = create_beveled_cube("Test_Body", (0, 0, 0.7), (4.4, 2.0, 0.55), bevel_width=0.06, mat=m_red)

# Hood (slanted down at front)
hood = create_tapered_cabin("Test_Hood", (1.45, 0, 0.7), length=1.5, width_bottom=1.96, width_top=1.85, height=0.45, front_rake=0.2, rear_rake=0.0, bevel=0.04, mat=m_red)

# Cabin (tapered greenhouse with windshield rake)
cabin = create_tapered_cabin("Test_Cabin", (-0.1, 0, 0.97), length=2.2, width_bottom=1.88, width_top=1.52, height=0.68, front_rake=0.65, rear_rake=0.5, bevel=0.05, mat=m_glass)

# Roof panel
roof = create_beveled_cube("Test_Roof", (-0.02, 0, 1.66), (1.15, 1.54, 0.05), bevel_width=0.03, mat=m_red)

# Front Bumper
bumper_f = create_beveled_cube("Test_Bumper_F", (2.25, 0, 0.5), (0.25, 2.02, 0.35), bevel_width=0.05, mat=m_black)

# Headlights
hl_l = create_beveled_cube("Test_HL_L", (2.22, 0.65, 0.72), (0.15, 0.45, 0.18), bevel_width=0.02, mat=m_glow)
hl_r = create_beveled_cube("Test_HL_R", (2.22, -0.65, 0.72), (0.15, 0.45, 0.18), bevel_width=0.02, mat=m_glow)

# Grille
grille = create_beveled_cube("Test_Grille", (2.24, 0, 0.55), (0.08, 0.85, 0.22), bevel_width=0.02, mat=m_chrome)

# Wheels
for wx, wy in [(1.35, 1.05), (1.35, -1.05), (-1.35, 1.05), (-1.35, -1.05)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.32, location=(wx, wy, 0.42), rotation=(math.radians(90), 0, 0))
    wh = bpy.context.active_object
    wh.data.materials.append(m_black)

print("Test car constructed successfully.")
