"""Build Sleeping and Bed Interaction Animations for NPC and Player in Mindscape 3D / Unity.

Scenarios:
- Scenario 1: NPC sleeping in bunk bed (Bunk_Bed, bottom bunk, cozy pillow & duvet, looping peaceful slumber).
- Scenario 2: Player walks toward bed, sits on the mattress edge, swings legs up, reclines onto pillow, and sleeps.
- Complete Animations:
  * Sleeping_Idle (60 frames @ 30 FPS, looping rhythmic chest breathing & relaxed limb repose)
  * Walk_To_Bed_And_Sleep (180 frames @ 30 FPS, approach -> sit -> swing legs up -> recline -> sleep)
  * Wake_Up_And_Get_Out_Of_Bed (120 frames @ 30 FPS, stir -> sit up -> swing legs down -> stand upright)
"""

import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector, Quaternion, Euler

def ensure_object_mode_and_deselect():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in bpy.data.objects:
        o.select_set(False)

def clear_scene():
    """Clear existing objects and unused data blocks safely."""
    ensure_object_mode_and_deselect()
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block in list(bpy.data.meshes):
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        if block.users == 0: bpy.data.materials.remove(block)
    for block in list(bpy.data.actions):
        if block.users == 0: bpy.data.actions.remove(block)

def create_pbr_mat(name, base_color, metallic=0.0, roughness=0.5, emission=(0,0,0,1)):
    """Create a Principled BSDF material safely."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs: bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs: bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs: bsdf.inputs["Roughness"].default_value = roughness
        if "Emission Color" in bsdf.inputs: bsdf.inputs["Emission Color"].default_value = emission
    return mat

def get_action_fcurves(action):
    """Retrieve all fcurves from an action across Blender versions."""
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for cb in getattr(strip, "channelbags", []):
                    for fc in getattr(cb, "fcurves", []):
                        curves.append(fc)
    return curves

class CharacterRigController:
    """Controls character posing and keyframing using armature-space rotation transforms."""
    def __init__(self, rig_obj):
        self.rig = rig_obj
        self.arm = rig_obj.data
        self.bone_bases = {b.name: b.matrix_local.to_3x3() for b in self.arm.bones}
        
    def set_bone_rot(self, bone_name, rx=0.0, ry=0.0, rz=0.0):
        if bone_name not in self.rig.pose.bones:
            return
        pb = self.rig.pose.bones[bone_name]
        basis = self.bone_bases[bone_name]
        pb.rotation_mode = 'QUATERNION'
        m = (Matrix.Rotation(math.radians(rx), 3, 'X') @
             Matrix.Rotation(math.radians(ry), 3, 'Y') @
             Matrix.Rotation(math.radians(rz), 3, 'Z'))
        pb.rotation_quaternion = (basis.inverted() @ m @ basis).to_quaternion()
        
    def set_root_pos(self, x=0.0, y=0.0, z=0.0):
        if 'root' in self.rig.pose.bones:
            pb = self.rig.pose.bones['root']
            basis = self.bone_bases['root']
            pb.location = basis.inverted() @ Vector((x, y, z))

    def reset_to_standing(self):
        """Set standard relaxed upright standing idle pose."""
        self.set_root_pos(0, 0, 0)
        for pb in self.rig.pose.bones:
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = (1, 0, 0, 0)
        # Relax arms down beside hips
        self.set_bone_rot("upper_arm.L", rx=0, ry=0, rz=-72)
        self.set_bone_rot("forearm.L", rx=0, ry=0, rz=-12)
        self.set_bone_rot("upper_arm.R", rx=0, ry=0, rz=72)
        self.set_bone_rot("forearm.R", rx=0, ry=0, rz=12)

    def keyframe_all_bones(self, frame):
        for pb in self.rig.pose.bones:
            pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            if pb.name == "root":
                pb.keyframe_insert(data_path="location", frame=frame)

# ==============================================================================
# ANIMATION GENERATION
# ==============================================================================

def create_sleeping_idle_action(rig_obj, z_offset=-0.48):
    """Creates a seamless looping sleeping idle animation (60 frames @ 30 FPS).
    Character lies on back, head resting on pillow, gentle breathing expansion in chest,
    relaxed hands folded over abdomen, and slightly bent relaxed knees."""
    ctrl = CharacterRigController(rig_obj)
    act = bpy.data.actions.new("Sleeping_Idle")
    act.use_fake_user = True
    rig_obj.animation_data_create()
    rig_obj.animation_data.action = act
    
    for f in range(1, 61):
        bpy.context.scene.frame_set(f)
        # Sinusoidal breathing phase (1.0 full breath cycle per 60 frames / 2.0s)
        phase = 2.0 * math.pi * (f - 1) / 60.0
        breath_expand = math.sin(phase)  # -1.0 to +1.0
        
        # Base horizontal lying position (hips rotated -90 around X)
        ctrl.set_root_pos(0.0, 0.0, z_offset + 0.006 * breath_expand)
        ctrl.set_bone_rot("hips", rx=-90, ry=0, rz=0)
        
        # Breathing chest expansion and subtle head settling
        ctrl.set_bone_rot("chest", rx=4.0 + 1.8 * breath_expand, ry=0, rz=0)
        ctrl.set_bone_rot("neck", rx=6.0 - 0.4 * breath_expand, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=16.0 - 0.8 * breath_expand, ry=0, rz=4.0)
        
        # Arms resting comfortably folded over lower ribs / abdomen
        ctrl.set_bone_rot("upper_arm.L", rx=-12.0, ry=14.0, rz=-28.0 - 0.5 * breath_expand)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-68.0)
        ctrl.set_bone_rot("hand.L", rx=10.0, ry=0, rz=-10.0)
        
        ctrl.set_bone_rot("upper_arm.R", rx=-12.0, ry=-14.0, rz=28.0 + 0.5 * breath_expand)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=68.0)
        ctrl.set_bone_rot("hand.R", rx=10.0, ry=0, rz=10.0)
        
        # Relaxed legs with gentle knee bend
        ctrl.set_bone_rot("thigh.L", rx=8.0, ry=0, rz=-4.0)
        ctrl.set_bone_rot("shin.L", rx=-14.0, ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=12.0, ry=0, rz=-6.0)
        
        ctrl.set_bone_rot("thigh.R", rx=8.0, ry=0, rz=4.0)
        ctrl.set_bone_rot("shin.R", rx=-14.0, ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=12.0, ry=0, rz=6.0)
        
        ctrl.keyframe_all_bones(f)
        
    for fc in get_action_fcurves(act):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'
            k.easing = 'EASE_IN_OUT'
            
    return act

def create_walk_to_bed_and_sleep_action(rig_obj, z_bed=-0.48):
    """Creates full sequence (180 frames @ 30 FPS):
    - Frames 1-45: Walks up alongside the bed toward the center mattress edge
    - Frames 46-75: Turns around to face away from bed, sits down onto mattress edge
    - Frames 76-110: Plants hands on mattress, swings legs up onto the bed
    - Frames 111-145: Reclines torso backward onto pillow, folds arms over abdomen
    - Frames 146-180: Settle into smooth looping sleeping breathing cycle"""
    ctrl = CharacterRigController(rig_obj)
    act = bpy.data.actions.new("Walk_To_Bed_And_Sleep")
    act.use_fake_user = True
    rig_obj.animation_data_create()
    rig_obj.animation_data.action = act
    
    # 1. Approach Walk Cycle (Frames 1 - 45)
    # Character walks from y = -1.6 up to y = 0.0 at bedside (x = 0.65)
    for f in range(1, 46):
        bpy.context.scene.frame_set(f)
        progress = (f - 1) / 44.0
        cur_y = -1.60 + 1.60 * progress
        # Stride phase (2 full steps)
        walk_phase = 4.0 * math.pi * progress
        leg_swing = math.sin(walk_phase)
        arm_swing = math.sin(walk_phase)
        bounce = 0.03 * abs(math.sin(walk_phase))
        
        ctrl.set_root_pos(0.65, cur_y, bounce)
        ctrl.set_bone_rot("hips", rx=0, ry=0, rz=0)
        ctrl.set_bone_rot("chest", rx=-2.0, ry=0, rz=2.0 * leg_swing)
        ctrl.set_bone_rot("head", rx=2.0, ry=0, rz=0)
        
        # Legs swing
        ctrl.set_bone_rot("thigh.L", rx=-24.0 * leg_swing, ry=0, rz=0)
        ctrl.set_bone_rot("shin.L", rx=max(0.0, 35.0 * leg_swing), ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=-10.0 * leg_swing, ry=0, rz=0)
        
        ctrl.set_bone_rot("thigh.R", rx=24.0 * leg_swing, ry=0, rz=0)
        ctrl.set_bone_rot("shin.R", rx=max(0.0, -35.0 * leg_swing), ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=10.0 * leg_swing, ry=0, rz=0)
        
        # Arms counter-swing
        ctrl.set_bone_rot("upper_arm.L", rx=20.0 * arm_swing, ry=0, rz=-70.0)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-20.0)
        ctrl.set_bone_rot("upper_arm.R", rx=-20.0 * arm_swing, ry=0, rz=70.0)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=20.0)
        
        ctrl.keyframe_all_bones(f)
        
    # 2. Turn & Sit Down on Bed Edge (Frames 46 - 75)
    # Character rotates 90 deg (facing +X into room, back against bed edge) and lowers hips
    for f in range(46, 76):
        bpy.context.scene.frame_set(f)
        t = (f - 46) / 29.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        # Move closer to bed edge (from x=0.65 to x=0.48) and lower down to mattress height
        cur_x = 0.65 - 0.17 * ease_t
        cur_z = z_bed * ease_t
        ctrl.set_root_pos(cur_x, 0.0, cur_z)
        
        # Turn body 90 degrees to face out (+X)
        turn_angle = 90.0 * ease_t
        ctrl.set_bone_rot("hips", rx=0, ry=0, rz=turn_angle)
        
        # Hips and knees bend to 90 degrees as sitting down
        ctrl.set_bone_rot("thigh.L", rx=85.0 * ease_t, ry=0, rz=-turn_angle * 0.2)
        ctrl.set_bone_rot("shin.L", rx=-85.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=0, ry=0, rz=0)
        
        ctrl.set_bone_rot("thigh.R", rx=85.0 * ease_t, ry=0, rz=turn_angle * 0.2)
        ctrl.set_bone_rot("shin.R", rx=-85.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=0, ry=0, rz=0)
        
        # Hands place down onto mattress edge to support weight
        ctrl.set_bone_rot("upper_arm.L", rx=15.0 * ease_t, ry=0, rz=-70.0 + 10.0 * ease_t)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-20.0 - 25.0 * ease_t)
        ctrl.set_bone_rot("upper_arm.R", rx=15.0 * ease_t, ry=0, rz=70.0 - 10.0 * ease_t)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=20.0 + 25.0 * ease_t)
        
        ctrl.set_bone_rot("chest", rx=-5.0 * math.sin(math.pi * ease_t), ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=5.0 * ease_t, ry=0, rz=0)
        
        ctrl.keyframe_all_bones(f)
        
    # 3. Swing Legs up onto Bed (Frames 76 - 110)
    # Character pivots hips on mattress into bed center (x=0.0) and swings legs horizontal
    for f in range(76, 111):
        bpy.context.scene.frame_set(f)
        t = (f - 76) / 34.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        # Shift root onto mattress center
        cur_x = 0.48 * (1.0 - ease_t)
        ctrl.set_root_pos(cur_x, 0.0, z_bed)
        
        # Rotate hips from seated outward (rz=90) to aligned along bed (rx tilting back, rz returning to 0)
        hip_rx = -90.0 * 0.4 * ease_t   # torso reclining partially
        hip_rz = 90.0 * (1.0 - ease_t)
        ctrl.set_bone_rot("hips", rx=hip_rx, ry=0, rz=hip_rz)
        
        # Legs swing up onto mattress: shins unbend, thighs straighten
        ctrl.set_bone_rot("thigh.L", rx=85.0 * (1.0 - ease_t) + 10.0 * ease_t, ry=0, rz=-5.0 * ease_t)
        ctrl.set_bone_rot("shin.L", rx=-85.0 * (1.0 - ease_t) - 15.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=10.0 * ease_t, ry=0, rz=0)
        
        ctrl.set_bone_rot("thigh.R", rx=85.0 * (1.0 - ease_t) + 10.0 * ease_t, ry=0, rz=5.0 * ease_t)
        ctrl.set_bone_rot("shin.R", rx=-85.0 * (1.0 - ease_t) - 15.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=10.0 * ease_t, ry=0, rz=0)
        
        # Arms brace on mattress behind back
        ctrl.set_bone_rot("upper_arm.L", rx=-25.0 * ease_t, ry=0, rz=-60.0 + 20.0 * ease_t)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-45.0)
        ctrl.set_bone_rot("upper_arm.R", rx=-25.0 * ease_t, ry=0, rz=60.0 - 20.0 * ease_t)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=45.0)
        
        ctrl.keyframe_all_bones(f)
        
    # 4. Recline onto Pillow & Settle (Frames 111 - 145)
    # Upper body reclines all the way flat onto pillow, arms fold comfortably over abdomen
    for f in range(111, 146):
        bpy.context.scene.frame_set(f)
        t = (f - 111) / 34.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        ctrl.set_root_pos(0.0, 0.0, z_bed)
        # Hips tilt all the way back to -90
        hip_rx = -36.0 - 54.0 * ease_t
        ctrl.set_bone_rot("hips", rx=hip_rx, ry=0, rz=0)
        
        # Head and neck settle onto pillow
        ctrl.set_bone_rot("chest", rx=4.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("neck", rx=6.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=16.0 * ease_t, ry=0, rz=4.0 * ease_t)
        
        # Arms fold comfortably across lower chest / abdomen
        ctrl.set_bone_rot("upper_arm.L", rx=-25.0 * (1.0 - ease_t) - 12.0 * ease_t, ry=14.0 * ease_t, rz=-40.0 * (1.0 - ease_t) - 28.0 * ease_t)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-45.0 * (1.0 - ease_t) - 68.0 * ease_t)
        ctrl.set_bone_rot("hand.L", rx=10.0 * ease_t, ry=0, rz=-10.0 * ease_t)
        
        ctrl.set_bone_rot("upper_arm.R", rx=-25.0 * (1.0 - ease_t) - 12.0 * ease_t, ry=-14.0 * ease_t, rz=40.0 * (1.0 - ease_t) + 28.0 * ease_t)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=45.0 * (1.0 - ease_t) + 68.0 * ease_t)
        ctrl.set_bone_rot("hand.R", rx=10.0 * ease_t, ry=0, rz=10.0 * ease_t)
        
        ctrl.set_bone_rot("thigh.L", rx=8.0, ry=0, rz=-4.0)
        ctrl.set_bone_rot("shin.L", rx=-14.0, ry=0, rz=0)
        ctrl.set_bone_rot("thigh.R", rx=8.0, ry=0, rz=4.0)
        ctrl.set_bone_rot("shin.R", rx=-14.0, ry=0, rz=0)
        
        ctrl.keyframe_all_bones(f)
        
    # 5. Sleeping Breath Cycle (Frames 146 - 180)
    for f in range(146, 181):
        bpy.context.scene.frame_set(f)
        phase = 2.0 * math.pi * (f - 146) / 34.0
        breath_expand = math.sin(phase)
        
        ctrl.set_root_pos(0.0, 0.0, z_bed + 0.006 * breath_expand)
        ctrl.set_bone_rot("hips", rx=-90, ry=0, rz=0)
        ctrl.set_bone_rot("chest", rx=4.0 + 1.8 * breath_expand, ry=0, rz=0)
        ctrl.set_bone_rot("neck", rx=6.0 - 0.4 * breath_expand, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=16.0 - 0.8 * breath_expand, ry=0, rz=4.0)
        
        ctrl.set_bone_rot("upper_arm.L", rx=-12.0, ry=14.0, rz=-28.0 - 0.5 * breath_expand)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-68.0)
        ctrl.set_bone_rot("hand.L", rx=10.0, ry=0, rz=-10.0)
        
        ctrl.set_bone_rot("upper_arm.R", rx=-12.0, ry=-14.0, rz=28.0 + 0.5 * breath_expand)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=68.0)
        ctrl.set_bone_rot("hand.R", rx=10.0, ry=0, rz=10.0)
        
        ctrl.set_bone_rot("thigh.L", rx=8.0, ry=0, rz=-4.0)
        ctrl.set_bone_rot("shin.L", rx=-14.0, ry=0, rz=0)
        ctrl.set_bone_rot("thigh.R", rx=8.0, ry=0, rz=4.0)
        ctrl.set_bone_rot("shin.R", rx=-14.0, ry=0, rz=0)
        
        ctrl.keyframe_all_bones(f)
        
    for fc in get_action_fcurves(act):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'
            k.easing = 'EASE_IN_OUT'
            
    return act

def create_wake_up_and_get_out_of_bed_action(rig_obj, z_bed=-0.48):
    """Creates waking up & getting out of bed sequence (120 frames @ 30 FPS):
    - Frames 1-25: Stirs awake in bed, head stirs, arms stretch/rub eyes
    - Frames 26-55: Presses palms on bed, pushes torso up into sitting position
    - Frames 56-85: Swings legs off the mattress edge down to floor, rests hands on knees
    - Frames 86-120: Leans forward over feet, pushes off bed, stands upright to standing idle"""
    ctrl = CharacterRigController(rig_obj)
    act = bpy.data.actions.new("Wake_Up_And_Get_Out_Of_Bed")
    act.use_fake_user = True
    rig_obj.animation_data_create()
    rig_obj.animation_data.action = act
    
    # 1. Stir & Awaken (Frames 1 - 25)
    for f in range(1, 26):
        bpy.context.scene.frame_set(f)
        t = (f - 1) / 24.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        ctrl.set_root_pos(0.0, 0.0, z_bed)
        ctrl.set_bone_rot("hips", rx=-90, ry=0, rz=0)
        
        # Head stirs, tilts upward
        ctrl.set_bone_rot("chest", rx=4.0 + 4.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=16.0 + 8.0 * ease_t, ry=0, rz=4.0 * (1.0 - ease_t))
        
        # Hands move off stomach, stretch slightly
        ctrl.set_bone_rot("upper_arm.L", rx=-12.0 - 15.0 * ease_t, ry=14.0, rz=-28.0 - 15.0 * ease_t)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-68.0 + 25.0 * ease_t)
        ctrl.set_bone_rot("upper_arm.R", rx=-12.0 - 15.0 * ease_t, ry=-14.0, rz=28.0 + 15.0 * ease_t)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=68.0 - 25.0 * ease_t)
        
        ctrl.set_bone_rot("thigh.L", rx=8.0 + 4.0 * ease_t, ry=0, rz=-4.0)
        ctrl.set_bone_rot("shin.L", rx=-14.0, ry=0, rz=0)
        ctrl.set_bone_rot("thigh.R", rx=8.0 + 4.0 * ease_t, ry=0, rz=4.0)
        ctrl.set_bone_rot("shin.R", rx=-14.0, ry=0, rz=0)
        
        ctrl.keyframe_all_bones(f)
        
    # 2. Push Torso Up into Sitting Position (Frames 26 - 55)
    for f in range(26, 56):
        bpy.context.scene.frame_set(f)
        t = (f - 26) / 29.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        ctrl.set_root_pos(0.0, 0.0, z_bed)
        # Hips rotate up from -90 to -35 (propped up)
        hip_rx = -90.0 + 55.0 * ease_t
        ctrl.set_bone_rot("hips", rx=hip_rx, ry=0, rz=0)
        
        # Chest upright
        ctrl.set_bone_rot("chest", rx=8.0 - 10.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=24.0 - 15.0 * ease_t, ry=0, rz=0)
        
        # Hands plant on mattress behind back to push up
        ctrl.set_bone_rot("upper_arm.L", rx=-27.0 + 10.0 * ease_t, ry=0, rz=-43.0 - 15.0 * ease_t)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-43.0 + 10.0 * ease_t)
        ctrl.set_bone_rot("upper_arm.R", rx=-27.0 + 10.0 * ease_t, ry=0, rz=43.0 + 15.0 * ease_t)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=43.0 - 10.0 * ease_t)
        
        ctrl.set_bone_rot("thigh.L", rx=12.0 + 35.0 * ease_t, ry=0, rz=-4.0)
        ctrl.set_bone_rot("shin.L", rx=-14.0 - 25.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("thigh.R", rx=12.0 + 35.0 * ease_t, ry=0, rz=4.0)
        ctrl.set_bone_rot("shin.R", rx=-14.0 - 25.0 * ease_t, ry=0, rz=0)
        
        ctrl.keyframe_all_bones(f)
        
    # 3. Swing Legs Down & Sit on Bed Edge (Frames 56 - 85)
    for f in range(56, 86):
        bpy.context.scene.frame_set(f)
        t = (f - 56) / 29.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        # Shift body toward bed edge (x = 0 to 0.48)
        cur_x = 0.48 * ease_t
        ctrl.set_root_pos(cur_x, 0.0, z_bed)
        
        # Rotate hips 90 degrees outward to face room
        hip_rx = -35.0 * (1.0 - ease_t)
        hip_rz = 90.0 * ease_t
        ctrl.set_bone_rot("hips", rx=hip_rx, ry=0, rz=hip_rz)
        
        # Legs swing down over bed edge (90 degree bend)
        ctrl.set_bone_rot("thigh.L", rx=47.0 * (1.0 - ease_t) + 85.0 * ease_t, ry=0, rz=-18.0 * ease_t)
        ctrl.set_bone_rot("shin.L", rx=-39.0 * (1.0 - ease_t) - 85.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=0, ry=0, rz=0)
        
        ctrl.set_bone_rot("thigh.R", rx=47.0 * (1.0 - ease_t) + 85.0 * ease_t, ry=0, rz=18.0 * ease_t)
        ctrl.set_bone_rot("shin.R", rx=-39.0 * (1.0 - ease_t) - 85.0 * ease_t, ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=0, ry=0, rz=0)
        
        # Hands rest on mattress edge beside hips
        ctrl.set_bone_rot("upper_arm.L", rx=15.0 * ease_t, ry=0, rz=-60.0)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-45.0)
        ctrl.set_bone_rot("upper_arm.R", rx=15.0 * ease_t, ry=0, rz=60.0)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=45.0)
        
        ctrl.keyframe_all_bones(f)
        
    # 4. Lean Forward & Stand Up Upright (Frames 86 - 120)
    for f in range(86, 121):
        bpy.context.scene.frame_set(f)
        t = (f - 86) / 34.0
        ease_t = 0.5 - 0.5 * math.cos(math.pi * t)
        
        # Rise from z_bed (-0.48) to 0.0, step slightly forward off bed (x from 0.48 to 0.65)
        cur_x = 0.48 + 0.17 * ease_t
        cur_z = z_bed * (1.0 - ease_t)
        ctrl.set_root_pos(cur_x, 0.0, cur_z)
        
        # Legs straighten upright
        ctrl.set_bone_rot("thigh.L", rx=85.0 * (1.0 - ease_t), ry=0, rz=0)
        ctrl.set_bone_rot("shin.L", rx=-85.0 * (1.0 - ease_t), ry=0, rz=0)
        ctrl.set_bone_rot("foot.L", rx=0, ry=0, rz=0)
        
        ctrl.set_bone_rot("thigh.R", rx=85.0 * (1.0 - ease_t), ry=0, rz=0)
        ctrl.set_bone_rot("shin.R", rx=-85.0 * (1.0 - ease_t), ry=0, rz=0)
        ctrl.set_bone_rot("foot.R", rx=0, ry=0, rz=0)
        
        # Torso leans slightly forward to drive standing center of mass, then straightens
        lean = 18.0 * math.sin(math.pi * ease_t)
        ctrl.set_bone_rot("hips", rx=-lean, ry=0, rz=90.0)
        ctrl.set_bone_rot("chest", rx=lean * 0.5, ry=0, rz=0)
        ctrl.set_bone_rot("head", rx=0, ry=0, rz=0)
        
        # Arms relax down to sides
        ctrl.set_bone_rot("upper_arm.L", rx=0, ry=0, rz=-72.0)
        ctrl.set_bone_rot("forearm.L", rx=0, ry=0, rz=-12.0)
        ctrl.set_bone_rot("upper_arm.R", rx=0, ry=0, rz=72.0)
        ctrl.set_bone_rot("forearm.R", rx=0, ry=0, rz=12.0)
        
        ctrl.keyframe_all_bones(f)
        
    for fc in get_action_fcurves(act):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'
            k.easing = 'EASE_IN_OUT'
            
    return act

# ==============================================================================
# BEDROOM ENVIRONMENT & BED SCENARIOS
# ==============================================================================

def make_box(name, location, scale, mat=None, collection=None):
    """Helper to build a simple box mesh."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = location
    if mat: obj.data.materials.append(mat)
    if collection: collection.objects.link(obj)
    else: bpy.context.scene.collection.objects.link(obj)
    return obj

def build_cozy_bed_props(origin, z_mattress, col, mat_pillow, mat_blanket):
    """Creates a soft pillow and a cozy folded blanket/duvet over the bed."""
    ox, oy, oz = origin
    # Fluffy Pillow (at head of bed, y = +0.70)
    pillow = make_box("Bed_Pillow", (ox, oy + 0.72, oz + z_mattress + 0.05), (0.65, 0.38, 0.10), mat_pillow, col)
    # Cozy Folded Blanket / Duvet (covering from feet y = -0.85 up to chest y = +0.25)
    blanket_len = 1.15
    blanket_y = oy - 0.30
    blanket = make_box("Bed_Blanket", (ox, blanket_y, oz + z_mattress + 0.12), (0.92, blanket_len, 0.14), mat_blanket, col)
    return pillow, blanket

def build_dorm_room(col):
    """Builds a warm cozy dormitory room with floor, walls, rug, and lighting."""
    # Materials
    m_floor = create_pbr_mat("Dorm_Floor_Wood", (0.55, 0.40, 0.26, 1.0), roughness=0.35)
    m_wall = create_pbr_mat("Dorm_Wall_Ivory", (0.92, 0.90, 0.86, 1.0), roughness=0.60)
    m_rug = create_pbr_mat("Dorm_Rug_Teal", (0.22, 0.45, 0.48, 1.0), roughness=0.85)
    m_pillow = create_pbr_mat("Bed_Pillow_Mat", (0.95, 0.95, 0.96, 1.0), roughness=0.5)
    m_blanket_npc = create_pbr_mat("NPC_Blanket_Mat", (0.32, 0.48, 0.62, 1.0), roughness=0.65)
    m_blanket_player = create_pbr_mat("Player_Blanket_Mat", (0.72, 0.38, 0.32, 1.0), roughness=0.65)
    m_lamp_glow = create_pbr_mat("Lamp_Glow_Mat", (1.0, 0.92, 0.75, 1.0), emission=(1.0, 0.90, 0.70, 3.0))
    
    # Floor slab (10m x 8m)
    make_box("Dorm_Floor", (0, 0, -0.05), (9.0, 7.0, 0.1), m_floor, col)
    # Back wall (y = +2.5m)
    make_box("Dorm_BackWall", (0, 2.5, 1.8), (9.0, 0.15, 3.6), m_wall, col)
    # Left wall (x = -4.5m)
    make_box("Dorm_LeftWall", (-4.5, 0, 1.8), (0.15, 7.0, 3.6), m_wall, col)
    # Bedside rugs
    make_box("Dorm_Rug_1", (-2.3, 0.0, 0.005), (1.6, 2.4, 0.01), m_rug, col)
    make_box("Dorm_Rug_2", (1.8, 0.0, 0.005), (1.6, 2.4, 0.01), m_rug, col)
    
    # Cozy Bedroom Lights
    # Warm ceiling ambient
    amb_data = bpy.data.lights.new(name="Dorm_Ceiling_Light", type='POINT')
    amb_data.energy = 250
    amb_data.color = (1.0, 0.92, 0.82)
    amb_obj = bpy.data.objects.new("Dorm_Ceiling_Light", amb_data)
    amb_obj.location = (0, 0, 3.2)
    col.objects.link(amb_obj)
    
    # Bedside Nightstand Warm Lamp
    lamp_data = bpy.data.lights.new(name="Bedside_Lamp_Light", type='POINT')
    lamp_data.energy = 80
    lamp_data.color = (1.0, 0.85, 0.60)
    lamp_obj = bpy.data.objects.new("Bedside_Lamp_Light", lamp_data)
    lamp_obj.location = (0.75, 1.25, 1.1)
    col.objects.link(lamp_obj)
    
    # Studio Camera
    cam_data = bpy.data.cameras.new("Dorm_Showcase_Camera")
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new("Dorm_Showcase_Camera", cam_data)
    cam_obj.location = (0.0, -5.2, 2.6)
    cam_obj.rotation_euler = (math.radians(72), 0, 0)
    col.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    return {
        "pillow": m_pillow,
        "blanket_npc": m_blanket_npc,
        "blanket_player": m_blanket_player
    }

def main():
    clear_scene()
    
    # Set up master collection
    col_dorm = bpy.data.collections.new("Dormitory_Sleep_Scene")
    bpy.context.scene.collection.children.link(col_dorm)
    
    mats = build_dorm_room(col_dorm)
    
    # ==========================================================================
    # SCENARIO 1: NPC SLEEPING IN BUNK BED
    # ==========================================================================
    # 1. Import Bunk Bed
    bunk_bed_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/single_objects/Bunk_Bed.glb"
    bpy.ops.import_scene.gltf(filepath=bunk_bed_path)
    bunk_bed = bpy.context.selected_objects[0]
    bunk_bed.name = "Scenario1_BunkBed"
    bunk_bed.location = Vector((-2.3, 0.0, 0.0))
    bunk_bed.rotation_euler = Euler((0, 0, 0))
    col_dorm.objects.link(bunk_bed)
    if bunk_bed.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(bunk_bed)
        
    # Cozy pillow and blanket on bottom bunk
    build_cozy_bed_props((-2.3, 0.0, 0.0), 0.48, col_dorm, mats["pillow"], mats["blanket_npc"])
    
    # 2. Import NPC (Maya) for Scenario 1
    npc_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Characters/NPCs/NPC_01_Maya.fbx"
    bpy.ops.import_scene.fbx(filepath=npc_path)
    npc_rig = next((o for o in bpy.context.selected_objects if o.type == 'ARMATURE'), None)
    npc_rig.name = "NPC_Maya_Rig"
    npc_rig.location = Vector((-2.3, 0.0, 0.0))
    npc_rig.rotation_euler = Euler((0, 0, 0))
    col_dorm.objects.link(npc_rig)
    for child in npc_rig.children:
        col_dorm.objects.link(child)
        if child.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(child)
    if npc_rig.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(npc_rig)
        
    # Animate NPC in Scenario 1: Sleeping Idle Loop (on bottom bunk at z=-0.48 so body rests at z=0.50)
    act_sleep_npc = create_sleeping_idle_action(npc_rig, z_offset=-0.48)
    npc_rig.animation_data.action = act_sleep_npc
    
    # ==========================================================================
    # SCENARIO 2: PLAYER WALKS TO BED AND SLEEPS
    # ==========================================================================
    # 1. Import Furniture Bed for Player
    bed_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Furniture/Furniture_Bed.glb"
    bpy.ops.import_scene.gltf(filepath=bed_path)
    player_bed = next((o for o in bpy.context.selected_objects if "Furniture_Bed" in o.name), bpy.context.selected_objects[0])
    player_bed.name = "Scenario2_PlayerBed"
    player_bed.location = Vector((1.8, 0.0, 0.0))
    player_bed.rotation_euler = Euler((0, 0, 0))
    col_dorm.objects.link(player_bed)
    if player_bed.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(player_bed)
        
    # Bedside table and lamp
    table_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Furniture/Furniture_BedsideTable.glb"
    bpy.ops.import_scene.gltf(filepath=table_path)
    table_obj = bpy.context.selected_objects[0]
    table_obj.location = Vector((0.75, 0.95, 0.0))
    col_dorm.objects.link(table_obj)
    if table_obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(table_obj)
        
    lamp_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Models/Furniture/Furniture_BedsideLamp.glb"
    bpy.ops.import_scene.gltf(filepath=lamp_path)
    lamp_prop = bpy.context.selected_objects[0]
    lamp_prop.location = Vector((0.75, 0.95, 0.70))
    col_dorm.objects.link(lamp_prop)
    if lamp_prop.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lamp_prop)
        
    # Pillow and blanket for Player Bed
    build_cozy_bed_props((1.8, 0.0, 0.0), 0.48, col_dorm, mats["pillow"], mats["blanket_player"])
    
    # 2. Import Player (BaldCharacter) for Scenario 2
    player_path = "/Users/arieljerickogacilo/mindscape-3d/Assets/Characters/BaldCharacter/BaldCharacter.glb"
    bpy.ops.import_scene.gltf(filepath=player_path)
    player_rig = next((o for o in bpy.context.selected_objects if o.type == 'ARMATURE'), None)
    player_rig.name = "Player_BaldCharacter_Rig"
    player_rig.location = Vector((1.8, 0.0, 0.0))
    player_rig.rotation_euler = Euler((0, 0, 0))
    col_dorm.objects.link(player_rig)
    for child in player_rig.children:
        col_dorm.objects.link(child)
        if child.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(child)
    if player_rig.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(player_rig)
        
    # Animate Player in Scenario 2: Walk to Bed and Sleep
    act_walk_sleep = create_walk_to_bed_and_sleep_action(player_rig, z_bed=-0.48)
    player_rig.animation_data.action = act_walk_sleep
    
    # Also generate the Wake Up and Get Out of Bed action on player rig
    act_wake_up = create_wake_up_and_get_out_of_bed_action(player_rig, z_bed=-0.48)
    
    # Keep Player on the primary scenario action (Walk to Bed and Sleep)
    player_rig.animation_data.action = act_walk_sleep
    
    # Timeline settings
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 180
    bpy.context.scene.frame_set(1)
    bpy.context.scene.render.fps = 30
    
    # ==========================================================================
    # SAVE BLENDER PROJECT & EXPORT ASSETS
    # ==========================================================================
    blend_dir = "/Users/arieljerickogacilo/mindscape-3d/Blender/Blend Files"
    os.makedirs(blend_dir, exist_ok=True)
    blend_file = os.path.join(blend_dir, "Dormitory_Sleep_Scenarios.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"Saved Blender project: {blend_file}")
    
    export_dir = "/Users/arieljerickogacilo/mindscape-3d/Assets/Characters/Animations"
    os.makedirs(export_dir, exist_ok=True)
    
    # Export Generic/Humanoid animation clips on the Player Armature
    ensure_object_mode_and_deselect()
    player_rig.select_set(True)
    for child in player_rig.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = player_rig
    
    anim_fbx = os.path.join(export_dir, "Sleeping_Animations.fbx")
    anim_glb = os.path.join(export_dir, "Sleeping_Animations.glb")
    
    bpy.ops.export_scene.gltf(filepath=anim_glb, export_format='GLB', use_selection=True, export_animations=True)
    bpy.ops.export_scene.fbx(filepath=anim_fbx, use_selection=True, bake_anim=True, bake_anim_use_all_actions=True, add_leaf_bones=False)
    print(f"Exported Character Sleeping Animations: {anim_fbx} and {anim_glb}")
    
    # Export Complete Dormitory Scene with Scenarios
    scene_fbx = os.path.join(export_dir, "Dormitory_Sleep_Scenarios.fbx")
    scene_glb = os.path.join(export_dir, "Dormitory_Sleep_Scenarios.glb")
    
    ensure_object_mode_and_deselect()
    for o in col_dorm.all_objects:
        if o.type in {'MESH', 'ARMATURE'}:
            o.select_set(True)
    if col_dorm.all_objects:
        bpy.context.view_layer.objects.active = col_dorm.all_objects[0]
        
    bpy.ops.export_scene.gltf(filepath=scene_glb, export_format='GLB', use_selection=True, export_animations=True)
    bpy.ops.export_scene.fbx(filepath=scene_fbx, use_selection=True, bake_anim=True, bake_anim_use_all_actions=True, add_leaf_bones=False)
    print(f"Exported Dormitory Scene Scenarios: {scene_fbx} and {scene_glb}")
    
    print("All sleeping animations and scenarios built and exported successfully!")

if __name__ == "__main__":
    main()
