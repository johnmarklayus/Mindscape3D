"""Build Door Varieties with Opening Animations for Mindscape 3D / Unity.

Creates 4 distinct architectural door varieties:
1. Door_Classic_Panel: 4-panel beveled wood door with brass lever handle and hinges.
2. Door_Modern_Glass: Contemporary dark minimalist door with frosted architectural glass pane, long tubular pull handle, and kick plate.
3. Door_Rustic_Barn: Heavy timber plank door with Z-brace ledgers, wrought-iron strap hinges, and forged iron latch.
4. Door_Double_French: Grand double swinging doors with 8-lite French glass grid panes and dual brass hardware.

Each door variety includes:
- Structural door frame/casing, sill, and jambs
- Properly placed hinge pivots for realistic rotation
- Hardware (handles, hinges, locks, plates)
- Detailed animated open/close motions (handle depression + smooth door swing with easing)
- Clean materials (Mahogany, Oak, Rustic Pine, Frosted Glass, Brass, Chrome, Iron, Anthracite)
- Individual and collection FBX & GLB exports for Unity
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def clear_scene():
    """Clear all mesh, light, camera, and armature objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.actions:
        if block.users == 0:
            bpy.data.actions.remove(block)

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, transmission=0.0, alpha=1.0, emission_color=(0,0,0,1)):
    """Create a Principled BSDF material safely looking up nodes by type."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission_color
    if transmission > 0.0 or alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat

def create_materials():
    """Build the palette of materials for all door varieties."""
    mats = {}
    # Classic wood (Rich warm mahogany)
    mats["Wood_Mahogany"] = create_pbr_material("Wood_Mahogany", (0.35, 0.16, 0.08, 1.0), roughness=0.38)
    # Natural warm oak
    mats["Wood_Oak"] = create_pbr_material("Wood_Oak", (0.62, 0.44, 0.28, 1.0), roughness=0.45)
    # Rustic weathered pine/timber
    mats["Wood_Rustic"] = create_pbr_material("Wood_Rustic", (0.42, 0.32, 0.22, 1.0), roughness=0.68)
    # Painted Ivory / off-white frame
    mats["Paint_Ivory"] = create_pbr_material("Paint_Ivory", (0.92, 0.90, 0.86, 1.0), roughness=0.4)
    # Modern Anthracite / Charcoal matte aluminum
    mats["Metal_Anthracite"] = create_pbr_material("Metal_Anthracite", (0.12, 0.13, 0.14, 1.0), metallic=0.7, roughness=0.32)
    # Polished Brass / Gold hardware
    mats["Metal_Brass"] = create_pbr_material("Metal_Brass", (0.95, 0.78, 0.28, 1.0), metallic=0.92, roughness=0.22)
    # Brushed Chrome / Satin Nickel
    mats["Metal_Chrome"] = create_pbr_material("Metal_Chrome", (0.85, 0.86, 0.88, 1.0), metallic=0.95, roughness=0.25)
    # Rustic Wrought Iron
    mats["Metal_Iron"] = create_pbr_material("Metal_Iron", (0.10, 0.10, 0.11, 1.0), metallic=0.85, roughness=0.55)
    # Frosted architectural glass
    mats["Glass_Frosted"] = create_pbr_material("Glass_Frosted", (0.88, 0.94, 0.96, 0.65), roughness=0.28, transmission=0.82, alpha=0.7)
    # Clear / Light Cyan architectural glass
    mats["Glass_Clear"] = create_pbr_material("Glass_Clear", (0.82, 0.92, 0.96, 0.45), roughness=0.10, transmission=0.92, alpha=0.5)
    # Threshold stone/slate
    mats["Stone_Threshold"] = create_pbr_material("Stone_Threshold", (0.25, 0.25, 0.26, 1.0), roughness=0.75)
    return mats

def make_cube(name, location, scale, mat=None, collection=None, parent=None):
    """Create a box mesh with dimensions given by scale=(sx, sy, sz)."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale cube vertices to match specified dimensions
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    if collection:
        collection.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
    return obj

def make_cylinder(name, location, radius, depth, mat=None, collection=None, parent=None, rot=(0,0,0)):
    """Create a cylinder mesh."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = location
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    if collection:
        collection.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
    return obj

def make_empty(name, location=(0,0,0), parent=None, collection=None):
    """Create an empty for pivot / parenting."""
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'ARROWS'
    empty.empty_display_size = 0.2
    empty.location = location
    if parent:
        empty.parent = parent
    if collection:
        collection.objects.link(empty)
    else:
        bpy.context.scene.collection.objects.link(empty)
    return empty

def join_objects(obj_list, final_name, parent=None):
    """Join a list of mesh objects into one single clean mesh object."""
    if not obj_list:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in obj_list:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obj_list[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = final_name
    if parent:
        joined.parent = parent
    return joined

# ==============================================================================
# 1. CLASSIC WOOD PANEL DOOR
# ==============================================================================
def build_classic_door(origin=(0,0,0), mats=None, col=None):
    """Builds a classic 4-panel beveled wood door with brass lever handle and hinges."""
    root = make_empty("Door_Classic", origin, collection=col)
    
    # Dimensions
    fw = 1.10   # Frame outer width
    fh = 2.22   # Frame outer height
    fd = 0.12   # Frame depth
    jw = 0.07   # Jamb width
    dw = 0.95   # Door leaf width
    dh = 2.13   # Door leaf height
    dd = 0.045  # Door thickness
    
    # 1. Door Frame
    frame_parts = []
    # Left jamb
    frame_parts.append(make_cube("Classic_Jamb_L", (-fw/2 + jw/2, 0, fh/2), (jw, fd, fh), mats["Paint_Ivory"], col))
    # Right jamb
    frame_parts.append(make_cube("Classic_Jamb_R", (fw/2 - jw/2, 0, fh/2), (jw, fd, fh), mats["Paint_Ivory"], col))
    # Header lintel
    frame_parts.append(make_cube("Classic_Header", (0, 0, fh - jw/2), (fw, fd, jw), mats["Paint_Ivory"], col))
    # Threshold sill
    frame_parts.append(make_cube("Classic_Threshold", (0, 0, 0.015), (fw + 0.06, fd + 0.04, 0.03), mats["Stone_Threshold"], col))
    # Decorative casing trim (front and back)
    for y_sign in (-1, 1):
        y_pos = y_sign * (fd/2 + 0.01)
        frame_parts.append(make_cube(f"Classic_Casing_L_{y_sign}", (-fw/2 - 0.015, y_pos, fh/2), (0.04, 0.02, fh), mats["Paint_Ivory"], col))
        frame_parts.append(make_cube(f"Classic_Casing_R_{y_sign}", (fw/2 + 0.015, y_pos, fh/2), (0.04, 0.02, fh), mats["Paint_Ivory"], col))
        frame_parts.append(make_cube(f"Classic_Casing_Top_{y_sign}", (0, y_pos, fh + 0.015), (fw + 0.07, 0.02, 0.04), mats["Paint_Ivory"], col))
    
    # 3 Brass Hinges on the Left Jamb
    hinge_z = [0.25, 1.10, 1.95]
    for i, hz in enumerate(hinge_z):
        frame_parts.append(make_cylinder(f"Classic_HingePin_{i}", (-dw/2 - 0.005, -dd/2 - 0.005, hz), 0.012, 0.07, mats["Metal_Brass"], col))
    
    frame_obj = join_objects(frame_parts, "Door_Classic_Frame", parent=root)
    
    # 2. Door Leaf Hinge Pivot (Hinged at the left edge)
    # Hinge line is at x = -dw/2
    hinge_pivot = make_empty("Classic_Hinge_Pivot", (-dw/2, 0, 0), parent=root, collection=col)
    
    # Door leaf parts (created relative to hinge_pivot: local origin is at (0,0,0) which is (-dw/2, 0, 0))
    leaf_parts = []
    # Main slab
    leaf_parts.append(make_cube("Classic_Slab", (dw/2, 0, dh/2 + 0.02), (dw, dd, dh), mats["Wood_Mahogany"], col))
    
    # 4 Beveled Panels (2 tall upper, 2 shorter lower) on both sides
    panels = [
        # (x_center, z_center, width, height)
        (dw * 0.28, dh * 0.72 + 0.02, dw * 0.32, dh * 0.38),  # Upper Left
        (dw * 0.72, dh * 0.72 + 0.02, dw * 0.32, dh * 0.38),  # Upper Right
        (dw * 0.28, dh * 0.28 + 0.02, dw * 0.32, dh * 0.32),  # Lower Left
        (dw * 0.72, dh * 0.28 + 0.02, dw * 0.32, dh * 0.32),  # Lower Right
    ]
    for pi, (px, pz, pw, ph) in enumerate(panels):
        for y_side in (-1, 1):
            py = y_side * (dd/2 + 0.004)
            # Outer raised molding
            leaf_parts.append(make_cube(f"Classic_PanelRim_{pi}_{y_side}", (px, py, pz), (pw, 0.008, ph), mats["Wood_Oak"], col))
            # Recessed center field
            leaf_parts.append(make_cube(f"Classic_PanelField_{pi}_{y_side}", (px, y_side * (dd/2 + 0.006), pz), (pw - 0.04, 0.006, ph - 0.04), mats["Wood_Mahogany"], col))
            
    leaf_obj = join_objects(leaf_parts, "Door_Classic_Leaf", parent=hinge_pivot)
    
    # 3. Handle Lever Pivot (Unlatches when opening)
    # Located at latch side (x = dw - 0.10) at standard latch height (z = 1.0)
    handle_pivot = make_empty("Classic_Handle_Pivot", (dw - 0.10, 0, 1.0), parent=hinge_pivot, collection=col)
    
    handle_parts = []
    for y_side in (-1, 1):
        py = y_side * (dd/2 + 0.008)
        # Brass backplate escutcheon
        handle_parts.append(make_cube(f"Classic_Escutcheon_{y_side}", (0, py, 0), (0.05, 0.008, 0.24), mats["Metal_Brass"], col))
        # Spindle collar
        handle_parts.append(make_cylinder(f"Classic_Spindle_{y_side}", (0, y_side * (dd/2 + 0.025), 0.04), 0.012, 0.035, mats["Metal_Brass"], col, rot=(math.radians(90), 0, 0)))
        # Lever handle
        handle_parts.append(make_cube(f"Classic_Lever_{y_side}", (-0.06, y_side * (dd/2 + 0.04), 0.04), (0.12, 0.02, 0.018), mats["Metal_Brass"], col))
    
    handle_obj = join_objects(handle_parts, "Door_Classic_Handle", parent=handle_pivot)
    
    return {
        "root": root,
        "frame": frame_obj,
        "hinge_pivot": hinge_pivot,
        "leaf": leaf_obj,
        "handle_pivot": handle_pivot,
        "handle": handle_obj
    }

# ==============================================================================
# 2. MODERN GLASS INSERT DOOR
# ==============================================================================
def build_modern_door(origin=(0,0,0), mats=None, col=None):
    """Builds a contemporary dark minimalist door with frosted glass panel and sleek vertical pull handle."""
    root = make_empty("Door_Modern", origin, collection=col)
    
    fw = 1.10
    fh = 2.22
    fd = 0.12
    jw = 0.06
    dw = 0.95
    dh = 2.13
    dd = 0.045
    
    # 1. Minimalist Frame
    frame_parts = []
    frame_parts.append(make_cube("Modern_Jamb_L", (-fw/2 + jw/2, 0, fh/2), (jw, fd, fh), mats["Metal_Anthracite"], col))
    frame_parts.append(make_cube("Modern_Jamb_R", (fw/2 - jw/2, 0, fh/2), (jw, fd, fh), mats["Metal_Anthracite"], col))
    frame_parts.append(make_cube("Modern_Header", (0, 0, fh - jw/2), (fw, fd, jw), mats["Metal_Anthracite"], col))
    frame_parts.append(make_cube("Modern_Threshold", (0, 0, 0.012), (fw + 0.02, fd + 0.02, 0.024), mats["Metal_Anthracite"], col))
    frame_obj = join_objects(frame_parts, "Door_Modern_Frame", parent=root)
    
    # 2. Door Leaf Hinge Pivot
    hinge_pivot = make_empty("Modern_Hinge_Pivot", (-dw/2, 0, 0), parent=root, collection=col)
    
    # Door Leaf with Cutout for Glass Pane
    leaf_parts = []
    # Glass dimensions
    gw = 0.28
    gh = 1.60
    gz = 1.15
    gx = dw * 0.65  # offset toward handle side for modern architectural asymmetry
    
    # Left stile of door leaf
    left_w = gx - gw/2
    leaf_parts.append(make_cube("Modern_Leaf_Left", (left_w/2, 0, dh/2 + 0.02), (left_w, dd, dh), mats["Metal_Anthracite"], col))
    # Right stile of door leaf
    right_w = dw - (gx + gw/2)
    leaf_parts.append(make_cube("Modern_Leaf_Right", (dw - right_w/2, 0, dh/2 + 0.02), (right_w, dd, dh), mats["Metal_Anthracite"], col))
    # Top rail over glass
    top_h = (dh + 0.02) - (gz + gh/2)
    leaf_parts.append(make_cube("Modern_Leaf_Top", (gx, 0, (gz + gh/2) + top_h/2), (gw, dd, top_h), mats["Metal_Anthracite"], col))
    # Bottom rail under glass
    bot_h = (gz - gh/2)
    leaf_parts.append(make_cube("Modern_Leaf_Bottom", (gx, 0, bot_h/2), (gw, dd, bot_h), mats["Metal_Anthracite"], col))
    
    # Stainless Steel Kickplate at bottom
    for y_side in (-1, 1):
        leaf_parts.append(make_cube(f"Modern_Kickplate_{y_side}", (dw/2, y_side * (dd/2 + 0.002), 0.12), (dw - 0.02, 0.004, 0.20), mats["Metal_Chrome"], col))
        
    leaf_obj = join_objects(leaf_parts, "Door_Modern_Leaf", parent=hinge_pivot)
    
    # Frosted Glass Pane
    glass_mesh = make_cube("Door_Modern_GlassPane", (gx, 0, gz), (gw - 0.01, 0.015, gh - 0.01), mats["Glass_Frosted"], col, parent=hinge_pivot)
    
    # 3. Modern Vertical Architectural Tubular Pull Handle
    # Stretches from z = 0.70 to z = 1.50 (length 0.8m)
    handle_pivot = make_empty("Modern_Handle_Pivot", (dw - 0.12, 0, 1.10), parent=hinge_pivot, collection=col)
    
    handle_parts = []
    for y_side in (-1, 1):
        hy = y_side * (dd/2 + 0.045)
        # Long vertical tubular bar
        handle_parts.append(make_cylinder(f"Modern_Bar_{y_side}", (0, hy, 0), 0.016, 0.80, mats["Metal_Chrome"], col))
        # Top and bottom standoff brackets connecting to the door face
        handle_parts.append(make_cylinder(f"Modern_Standoff_Top_{y_side}", (0, y_side * (dd/2 + 0.022), 0.35), 0.012, 0.045, mats["Metal_Chrome"], col, rot=(math.radians(90), 0, 0)))
        handle_parts.append(make_cylinder(f"Modern_Standoff_Bot_{y_side}", (0, y_side * (dd/2 + 0.022), -0.35), 0.012, 0.045, mats["Metal_Chrome"], col, rot=(math.radians(90), 0, 0)))
        
    handle_obj = join_objects(handle_parts, "Door_Modern_Handle", parent=handle_pivot)
    
    return {
        "root": root,
        "frame": frame_obj,
        "hinge_pivot": hinge_pivot,
        "leaf": leaf_obj,
        "glass": glass_mesh,
        "handle_pivot": handle_pivot,
        "handle": handle_obj
    }

# ==============================================================================
# 3. RUSTIC BARN / COTTAGE PLANK DOOR
# ==============================================================================
def build_rustic_door(origin=(0,0,0), mats=None, col=None):
    """Builds a rustic timber plank door with Z-brace ledgers, iron strap hinges, and forged iron latch."""
    root = make_empty("Door_Rustic", origin, collection=col)
    
    fw = 1.16
    fh = 2.24
    fd = 0.14
    tw = 0.10   # Heavy rough-hewn timber width
    dw = 0.95
    dh = 2.12
    dd = 0.05
    
    # 1. Heavy Rough-Hewn Timber Frame
    frame_parts = []
    frame_parts.append(make_cube("Rustic_Jamb_L", (-fw/2 + tw/2, 0, fh/2), (tw, fd, fh), mats["Wood_Rustic"], col))
    frame_parts.append(make_cube("Rustic_Jamb_R", (fw/2 - tw/2, 0, fh/2), (tw, fd, fh), mats["Wood_Rustic"], col))
    # Overhanging heavy lintel header
    frame_parts.append(make_cube("Rustic_Header", (0, 0, fh - tw/2 + 0.02), (fw + 0.16, fd + 0.04, tw + 0.04), mats["Wood_Rustic"], col))
    # Massive stone threshold
    frame_parts.append(make_cube("Rustic_Threshold", (0, 0, 0.025), (fw + 0.12, fd + 0.08, 0.05), mats["Stone_Threshold"], col))
    frame_obj = join_objects(frame_parts, "Door_Rustic_Frame", parent=root)
    
    # 2. Door Leaf Hinge Pivot
    hinge_pivot = make_empty("Rustic_Hinge_Pivot", (-dw/2, 0, 0), parent=root, collection=col)
    
    leaf_parts = []
    # Vertical timber planks (6 planks with chamfered seams)
    num_planks = 6
    pw = dw / num_planks
    for i in range(num_planks):
        px = i * pw + pw/2
        leaf_parts.append(make_cube(f"Rustic_Plank_{i}", (px, 0, dh/2 + 0.02), (pw - 0.006, dd, dh), mats["Wood_Rustic"], col))
        
    # Horizontal Ledgers (Top, Middle, Bottom)
    ledgers_z = [dh * 0.15 + 0.02, dh * 0.50 + 0.02, dh * 0.85 + 0.02]
    for li, lz in enumerate(ledgers_z):
        leaf_parts.append(make_cube(f"Rustic_Ledger_{li}", (dw/2, dd/2 + 0.015, lz), (dw - 0.06, 0.03, 0.14), mats["Wood_Rustic"], col))
        
    # Diagonal Z-Braces (between bottom & middle, middle & top)
    diag_h1 = (ledgers_z[1] - ledgers_z[0]) - 0.14
    diag_w = dw - 0.08
    diag_len1 = math.hypot(diag_w, diag_h1)
    diag_angle1 = math.atan2(diag_h1, diag_w)
    
    diag1 = make_cube("Rustic_ZBrace_1", (dw/2, dd/2 + 0.015, (ledgers_z[0] + ledgers_z[1])/2), (diag_len1, 0.028, 0.12), mats["Wood_Rustic"], col)
    diag1.rotation_euler = (0, -diag_angle1, 0)
    leaf_parts.append(diag1)
    
    diag2 = make_cube("Rustic_ZBrace_2", (dw/2, dd/2 + 0.015, (ledgers_z[1] + ledgers_z[2])/2), (diag_len1, 0.028, 0.12), mats["Wood_Rustic"], col)
    diag2.rotation_euler = (0, -diag_angle1, 0)
    leaf_parts.append(diag2)
    
    # Heavy Wrought-Iron Strap Hinges extending across the front face
    strap_z = [ledgers_z[0], ledgers_z[2]]
    for si, sz in enumerate(strap_z):
        # Long tapered iron strap
        leaf_parts.append(make_cube(f"Rustic_Strap_{si}", (dw * 0.32, -dd/2 - 0.008, sz), (dw * 0.60, 0.012, 0.07), mats["Metal_Iron"], col))
        # Hinge barrel socket at edge
        leaf_parts.append(make_cylinder(f"Rustic_Barrel_{si}", (0.01, -dd/2 - 0.01, sz), 0.02, 0.09, mats["Metal_Iron"], col))
        # Carriage bolts / rivets
        for bi in range(4):
            leaf_parts.append(make_cylinder(f"Rustic_Rivet_{si}_{bi}", (0.08 + bi * 0.14, -dd/2 - 0.016, sz), 0.01, 0.01, mats["Metal_Iron"], col, rot=(math.radians(90), 0, 0)))
            
    leaf_obj = join_objects(leaf_parts, "Door_Rustic_Leaf", parent=hinge_pivot)
    
    # 3. Forged Iron Thumb-Latch Handle & Drop Bar
    handle_pivot = make_empty("Rustic_Handle_Pivot", (dw - 0.12, 0, 1.05), parent=hinge_pivot, collection=col)
    
    handle_parts = []
    # Front curved grasp handle
    handle_parts.append(make_cube("Rustic_GraspHandle", (0, -dd/2 - 0.05, 0), (0.03, 0.025, 0.26), mats["Metal_Iron"], col))
    handle_parts.append(make_cube("Rustic_HandleStandoff_Top", (0, -dd/2 - 0.025, 0.11), (0.03, 0.04, 0.025), mats["Metal_Iron"], col))
    handle_parts.append(make_cube("Rustic_HandleStandoff_Bot", (0, -dd/2 - 0.025, -0.11), (0.03, 0.04, 0.025), mats["Metal_Iron"], col))
    # Back drop latch bar
    handle_parts.append(make_cube("Rustic_LatchBar", (0.04, dd/2 + 0.025, 0), (0.16, 0.015, 0.025), mats["Metal_Iron"], col))
    
    handle_obj = join_objects(handle_parts, "Door_Rustic_Handle", parent=handle_pivot)
    
    return {
        "root": root,
        "frame": frame_obj,
        "hinge_pivot": hinge_pivot,
        "leaf": leaf_obj,
        "handle_pivot": handle_pivot,
        "handle": handle_obj
    }

# ==============================================================================
# 4. DOUBLE FRENCH GLASS DOORS
# ==============================================================================
def build_double_french_door(origin=(0,0,0), mats=None, col=None):
    """Builds a grand double swinging French door with 8-lite glass grid panes on each leaf."""
    root = make_empty("Door_Double_French", origin, collection=col)
    
    fw = 1.94   # Double width frame
    fh = 2.25
    fd = 0.12
    jw = 0.07
    leaf_w = 0.88
    dh = 2.14
    dd = 0.045
    
    # 1. Grand Double Frame with Decorative Header
    frame_parts = []
    frame_parts.append(make_cube("French_Jamb_L", (-fw/2 + jw/2, 0, fh/2), (jw, fd, fh), mats["Paint_Ivory"], col))
    frame_parts.append(make_cube("French_Jamb_R", (fw/2 - jw/2, 0, fh/2), (jw, fd, fh), mats["Paint_Ivory"], col))
    frame_parts.append(make_cube("French_Header", (0, 0, fh - jw/2), (fw, fd, jw), mats["Paint_Ivory"], col))
    # Classical Crown Molding Header
    frame_parts.append(make_cube("French_CrownMolding", (0, 0, fh + 0.04), (fw + 0.14, fd + 0.06, 0.08), mats["Paint_Ivory"], col))
    frame_parts.append(make_cube("French_Threshold", (0, 0, 0.015), (fw + 0.04, fd + 0.04, 0.03), mats["Stone_Threshold"], col))
    frame_obj = join_objects(frame_parts, "Door_Double_French_Frame", parent=root)
    
    # 2. Left Leaf (Hinged at x = -leaf_w)
    left_hinge = make_empty("French_Hinge_L", (-leaf_w, 0, 0), parent=root, collection=col)
    
    def build_french_leaf(prefix, side_sign):
        # side_sign: 1 for left leaf (extends +X from hinge), -1 for right leaf (extends -X from hinge)
        parts = []
        # Outer stiles and rails
        stile_w = 0.12
        bottom_rail_h = 0.35  # solid panel at the bottom of French doors
        top_rail_h = 0.16
        
        # Hinge stile
        parts.append(make_cube(f"{prefix}_HingeStile", (side_sign * stile_w/2, 0, dh/2 + 0.015), (stile_w, dd, dh), mats["Paint_Ivory"], col))
        # Meeting lock stile
        parts.append(make_cube(f"{prefix}_LockStile", (side_sign * (leaf_w - stile_w/2), 0, dh/2 + 0.015), (stile_w, dd, dh), mats["Paint_Ivory"], col))
        # Bottom solid kick rail
        parts.append(make_cube(f"{prefix}_BottomRail", (side_sign * leaf_w/2, 0, bottom_rail_h/2 + 0.015), (leaf_w, dd, bottom_rail_h), mats["Paint_Ivory"], col))
        # Top rail
        parts.append(make_cube(f"{prefix}_TopRail", (side_sign * leaf_w/2, 0, dh + 0.015 - top_rail_h/2), (leaf_w, dd, top_rail_h), mats["Paint_Ivory"], col))
        
        # Grid Glass Opening:
        glass_w = leaf_w - stile_w * 2
        glass_h = dh - (bottom_rail_h + top_rail_h)
        glass_z = bottom_rail_h + 0.015 + glass_h / 2
        glass_x = side_sign * leaf_w / 2
        
        # Muntin Mullion Grid (8 glass panes: 2 columns x 4 rows)
        # Vertical center divider
        parts.append(make_cube(f"{prefix}_Muntin_Vert", (glass_x, 0, glass_z), (0.024, dd + 0.004, glass_h), mats["Paint_Ivory"], col))
        # 3 Horizontal dividers
        for ri in (1, 2, 3):
            rz = (bottom_rail_h + 0.015) + ri * (glass_h / 4)
            parts.append(make_cube(f"{prefix}_Muntin_Horiz_{ri}", (glass_x, 0, rz), (glass_w, dd + 0.004, 0.024), mats["Paint_Ivory"], col))
            
        leaf_mesh = join_objects(parts, f"{prefix}_Leaf")
        
        # Glass Pane
        glass_obj = make_cube(f"{prefix}_GlassPane", (glass_x, 0, glass_z), (glass_w, 0.012, glass_h), mats["Glass_Clear"], col)
        
        # Brass French Door Handle & Lever
        h_x = side_sign * (leaf_w - 0.06)
        h_z = bottom_rail_h + 0.015 + 0.15
        handle_parts = []
        for y_side in (-1, 1):
            py = y_side * (dd/2 + 0.006)
            handle_parts.append(make_cube(f"{prefix}_HandlePlate_{y_side}", (h_x, py, h_z), (0.04, 0.006, 0.18), mats["Metal_Brass"], col))
            handle_parts.append(make_cylinder(f"{prefix}_HandleSpindle_{y_side}", (h_x, y_side * (dd/2 + 0.02), h_z + 0.03), 0.01, 0.03, mats["Metal_Brass"], col, rot=(math.radians(90), 0, 0)))
            handle_parts.append(make_cube(f"{prefix}_HandleLever_{y_side}", (h_x - side_sign * 0.05, y_side * (dd/2 + 0.035), h_z + 0.03), (0.10, 0.018, 0.016), mats["Metal_Brass"], col))
        handle_mesh = join_objects(handle_parts, f"{prefix}_Handle")
        
        return leaf_mesh, glass_obj, handle_mesh
    
    left_leaf, left_glass, left_handle = build_french_leaf("French_L", 1)
    left_leaf.parent = left_hinge
    left_glass.parent = left_hinge
    left_handle.parent = left_hinge
    
    # 3. Right Leaf (Hinged at x = +leaf_w, extends -X)
    right_hinge = make_empty("French_Hinge_R", (leaf_w, 0, 0), parent=root, collection=col)
    right_leaf, right_glass, right_handle = build_french_leaf("French_R", -1)
    
    right_leaf.parent = right_hinge
    right_glass.parent = right_hinge
    right_handle.parent = right_hinge
    
    return {
        "root": root,
        "frame": frame_obj,
        "hinge_l": left_hinge,
        "leaf_l": left_leaf,
        "glass_l": left_glass,
        "handle_l": left_handle,
        "hinge_r": right_hinge,
        "leaf_r": right_leaf,
        "glass_r": right_glass,
        "handle_r": right_handle
    }

# ==============================================================================
# ANIMATIONS
# ==============================================================================
def get_all_fcurves(obj):
    """Retrieve fcurves across both legacy Blender actions and Blender 5.x layered/slotted actions."""
    if not obj.animation_data or not obj.animation_data.action:
        return []
    act = obj.animation_data.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    curves = []
    if hasattr(act, "layers"):
        for layer in act.layers:
            for strip in layer.strips:
                for cb in getattr(strip, "channelbags", []):
                    for fc in getattr(cb, "fcurves", []):
                        curves.append(fc)
    return curves

def create_smooth_fcurve(obj, data_path, index, keyframes):
    """Inserts keyframes and sets smooth cubic bezier interpolation."""
    obj.animation_data_create()
    for frame, value in keyframes:
        if data_path == "rotation_euler":
            obj.rotation_euler[index] = value
        obj.keyframe_insert(data_path=data_path, index=index, frame=frame)
        
    for fc in get_all_fcurves(obj):
        if fc.data_path == data_path and fc.array_index == index:
            for kf in fc.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.easing = 'EASE_IN_OUT'

def animate_all_doors(classic, modern, rustic, french):
    """Animate the 4 door varieties across a 120-frame seamless sequence at 30 fps."""
    # Frame sequence (120 frames total):
    # Frames 1-15:   Closed idle
    # Frames 15-25:  Handle unlatches
    # Frames 22-65:  Doors swing open to 90° - 95°
    # Frames 65-80:  Held fully open
    # Frames 80-115: Doors swing back to 0°
    # Frames 115-120: Latches click shut
    
    # 1. Classic Door Animation
    # Handle depression (rotation on Y)
    create_smooth_fcurve(classic["handle_pivot"], "rotation_euler", 1, [
        (1, 0.0),
        (15, 0.0),
        (24, math.radians(-22)),  # Handle turns down
        (35, 0.0),                # Springs back as door opens
        (65, 0.0),
        (80, 0.0),
        (105, math.radians(-15)), # Slightly depresses as latch catches strike
        (116, 0.0)                # Snaps closed
    ])
    # Door swing (rotation on Z around hinge)
    create_smooth_fcurve(classic["hinge_pivot"], "rotation_euler", 2, [
        (1, 0.0),
        (20, 0.0),
        (60, math.radians(95)),   # Full open 95 degrees
        (80, math.radians(95)),   # Hold open
        (116, 0.0),               # Smooth swing closed
        (120, 0.0)
    ])
    
    # 2. Modern Door Animation
    # Smooth modern hydraulic swing open and soft-close
    create_smooth_fcurve(modern["hinge_pivot"], "rotation_euler", 2, [
        (1, 0.0),
        (15, 0.0),
        (55, math.radians(92)),   # Smooth modern open
        (80, math.radians(92)),   # Hold open
        (114, 0.0),               # Soft close
        (120, 0.0)
    ])
    
    # 3. Rustic Door Animation
    # Iron latch lifts (rotation on Y)
    create_smooth_fcurve(rustic["handle_pivot"], "rotation_euler", 1, [
        (1, 0.0),
        (12, 0.0),
        (22, math.radians(18)),   # Thumb latch lifts
        (35, 0.0),
        (80, 0.0),
        (108, math.radians(14)),
        (118, 0.0)
    ])
    # Heavy timber door swing
    create_smooth_fcurve(rustic["hinge_pivot"], "rotation_euler", 2, [
        (1, 0.0),
        (18, 0.0),
        (64, math.radians(90)),   # Weighty open
        (78, math.radians(90)),   # Hold open
        (118, 0.0),               # Firm close
        (120, 0.0)
    ])
    
    # 4. Double French Doors Animation
    # Left Leaf swings open inward to +92° (swings +X toward +Y)
    create_smooth_fcurve(french["hinge_l"], "rotation_euler", 2, [
        (1, 0.0),
        (18, 0.0),
        (62, math.radians(92)),
        (80, math.radians(92)),
        (115, 0.0),
        (120, 0.0)
    ])
    # Right Leaf swings open inward to -92° (swings -X toward +Y)
    create_smooth_fcurve(french["hinge_r"], "rotation_euler", 2, [
        (1, 0.0),
        (18, 0.0),
        (62, math.radians(-92)),
        (80, math.radians(-92)),
        (115, 0.0),
        (120, 0.0)
    ])

def build_scene_environment():
    """Sets up a clean showroom floor, lighting, and camera to showcase the door varieties."""
    # Studio display floor
    m_floor = create_pbr_material("Studio_Floor", (0.22, 0.23, 0.25, 1.0), roughness=0.35)
    floor = make_cube("Studio_Floor", (0.2, 0.6, -0.05), (10.0, 4.0, 0.1), m_floor)
    
    # 3-Point Lighting
    # Key light
    key_data = bpy.data.lights.new(name="Key_Light", type='AREA')
    key_data.energy = 500
    key_data.size = 3.0
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = (0.0, -4.5, 4.0)
    key_obj.rotation_euler = (math.radians(50), 0, 0)
    bpy.context.scene.collection.objects.link(key_obj)
    
    # Fill light
    fill_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_data.energy = 220
    fill_data.size = 4.0
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (-4.0, -3.0, 3.0)
    fill_obj.rotation_euler = (math.radians(45), 0, math.radians(-35))
    bpy.context.scene.collection.objects.link(fill_obj)
    
    # Rim / Back light
    rim_data = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_data.energy = 350
    rim_data.size = 5.0
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (2.0, 3.5, 3.8)
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(160))
    bpy.context.scene.collection.objects.link(rim_obj)
    
    # Presentation Camera
    cam_data = bpy.data.cameras.new("Door_Showroom_Camera")
    cam_data.lens = 42
    cam_obj = bpy.data.objects.new("Door_Showroom_Camera", cam_data)
    cam_obj.location = (0.1, -6.5, 2.3)
    cam_obj.rotation_euler = (math.radians(80), 0, 0)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Timeline settings
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    bpy.context.scene.render.fps = 30

def export_assets():
    """Exports both individual door assets and the combined door variety pack for Unity."""
    export_dir = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Doors"
    os.makedirs(export_dir, exist_ok=True)
    
    blend_dir = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files"
    os.makedirs(blend_dir, exist_ok=True)
    blend_path = os.path.join(blend_dir, "Door_Varieties.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blender file: {blend_path}")
    
    def select_hierarchy(obj):
        obj.select_set(True)
        for child in obj.children:
            select_hierarchy(child)

    # 1. Export Complete Collection (All 4 Varieties in one showcase)
    all_fbx = os.path.join(export_dir, "Door_Varieties_All.fbx")
    all_glb = os.path.join(export_dir, "Door_Varieties_All.glb")
    
    door_roots = ["Door_Classic", "Door_Modern", "Door_Rustic", "Door_Double_French"]
    bpy.ops.object.select_all(action='DESELECT')
    for root_name in door_roots:
        root = bpy.data.objects.get(root_name)
        if root:
            select_hierarchy(root)
            
    active_obj = bpy.data.objects.get("Door_Classic")
    if active_obj:
        bpy.context.view_layer.objects.active = active_obj
        
    bpy.ops.export_scene.gltf(filepath=all_glb, export_format='GLB', use_selection=True, export_animations=True)
    print(f"Exported all varieties GLB: {all_glb}")
    
    bpy.ops.export_scene.fbx(filepath=all_fbx, use_selection=True, bake_anim=True, bake_anim_use_all_actions=True, add_leaf_bones=False)
    print(f"Exported all varieties FBX: {all_fbx}")
    
    # 2. Export Individual Doors centered at (0,0,0) for direct drag-and-drop Unity usage
    door_configs = [
        ("Door_Classic_Panel", "Door_Classic"),
        ("Door_Modern_Glass", "Door_Modern"),
        ("Door_Rustic_Barn", "Door_Rustic"),
        ("Door_Double_French", "Door_Double_French")
    ]
    
    for asset_name, root_name in door_configs:
        root_obj = bpy.data.objects.get(root_name)
        if not root_obj:
            continue
            
        orig_loc = root_obj.location.copy()
        root_obj.location = Vector((0, 0, 0))
        bpy.context.view_layer.update()
        
        # Select root and all recursive children
        bpy.ops.object.select_all(action='DESELECT')
        def select_hierarchy(obj):
            obj.select_set(True)
            for child in obj.children:
                select_hierarchy(child)
        select_hierarchy(root_obj)
        bpy.context.view_layer.objects.active = root_obj
        
        ind_fbx = os.path.join(export_dir, f"{asset_name}.fbx")
        ind_glb = os.path.join(export_dir, f"{asset_name}.glb")
        
        bpy.ops.export_scene.gltf(filepath=ind_glb, export_format='GLB', use_selection=True, export_animations=True)
        bpy.ops.export_scene.fbx(filepath=ind_fbx, use_selection=True, bake_anim=True, bake_anim_use_all_actions=True, add_leaf_bones=False)
        print(f"Exported {asset_name}: {ind_fbx} and {ind_glb}")
        
        root_obj.location = orig_loc
        bpy.context.view_layer.update()

def main():
    clear_scene()
    mats = create_materials()
    
    # Create collections
    col_doors = bpy.data.collections.new("Door_Varieties")
    bpy.context.scene.collection.children.link(col_doors)
    
    # Build 4 Door Varieties in a line
    classic = build_classic_door(origin=(-3.1, 0, 0), mats=mats, col=col_doors)
    modern = build_modern_door(origin=(-1.0, 0, 0), mats=mats, col=col_doors)
    rustic = build_rustic_door(origin=(1.0, 0, 0), mats=mats, col=col_doors)
    french = build_double_french_door(origin=(3.2, 0, 0), mats=mats, col=col_doors)
    
    # Animate all doors
    animate_all_doors(classic, modern, rustic, french)
    
    # Setup showroom environment (floor, lighting, camera)
    build_scene_environment()
    
    # Export assets
    export_assets()
    print("Door Varieties build, animation, and export complete!")

if __name__ == "__main__":
    main()
