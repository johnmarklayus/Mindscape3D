import bpy
import math
import os
from mathutils import Matrix, Vector

OUT='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets'
scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
if not os.path.exists(OUT+'/reference-character-before-animation.blend'):
    bpy.ops.wm.save_as_mainfile(filepath=OUT+'/reference-character-before-animation.blend',copy=True)
root=bpy.data.objects['Reference_Character_Root']
parts=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Reference_Character_')]
assert len(parts)==27, 'Unexpected character structure'
assert not bpy.data.objects.get('Reference_Character_Rig'), 'Character already has this rig'
arm=bpy.data.armatures.new('Character_Skeleton')
rig=bpy.data.objects.new('Reference_Character_Rig',arm)
root.users_collection[0].objects.link(rig)
rig.parent=root
rig.show_in_front=True
arm.display_type='STICK'
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=arm.edit_bones.new(name)
    b.head=head
    b.tail=tail
    if parent: b.parent=arm.edit_bones[parent]
bone('Root',(0,0,0),(0,0,.4))
bone('Hips',(0,0,2.62),(0,0,2.95),'Root')
bone('Spine',(0,0,2.95),(0,0,4.15),'Hips')
bone('Head',(0,0,4.15),(0,0,5.2),'Spine')
for s,side in [(-1,'Right'),(1,'Left')]:
    bone(side+'_UpperArm',(s*.52,0,4.04),(s*1.20,0,4.035),'Spine')
    bone(side+'_Forearm',(s*1.20,0,4.035),(s*2.24,0,4.01),side+'_UpperArm')
    bone(side+'_Hand',(s*2.24,0,4.01),(s*2.5,0,4.01),side+'_Forearm')
    bone(side+'_Thigh',(s*.30,0,2.64),(s*.44,0,1.50),'Hips')
    bone(side+'_Shin',(s*.44,0,1.50),(s*.59,0,.43),side+'_Thigh')
    bone(side+'_Foot',(s*.59,0,.43),(s*.59,-.45,.16),side+'_Shin')
bpy.ops.object.mode_set(mode='OBJECT')

def assign(obj,name,indices,weight=1):
    group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
    if indices: group.add(indices,weight,'REPLACE')
for obj in parts:
    name=obj.name.removeprefix('Reference_Character_')
    side='Left' if name.startswith('Left_') else 'Right'
    if name.endswith('_Leg'):
        for v in obj.data.vertices:
            w=max(0,min(1,(v.co.z-1.35)/.30))
            if w: assign(obj,side+'_Thigh',[v.index],w)
            if w<1: assign(obj,side+'_Shin',[v.index],1-w)
    elif name.endswith('_Sleeve'):
        for v in obj.data.vertices:
            w=max(0,min(1,(1.35-abs(v.co.x))/.30))
            if w: assign(obj,side+'_UpperArm',[v.index],w)
            if w<1: assign(obj,side+'_Forearm',[v.index],1-w)
    else:
        target=('Spine' if name=='Torso' else side+'_Forearm' if name.endswith('_Forearm') else side+'_Hand' if name.endswith('_Hand') else side+'_Foot' if name.endswith(('_Ankle','_Shoe')) else 'Head')
        assign(obj,target,list(range(len(obj.data.vertices))))
    mod=obj.modifiers.new('Character_Armature','ARMATURE')
    mod.object=rig
    mod.use_deform_preserve_volume=True

def rotate(name,global_rotation):
    p=rig.pose.bones[name]
    basis=arm.bones[name].matrix_local.to_3x3()
    p.rotation_mode='QUATERNION'
    p.rotation_quaternion=(basis.inverted()@global_rotation@basis).to_quaternion()
def rx(a): return Matrix.Rotation(a,3,'X')
def ry(a): return Matrix.Rotation(a,3,'Y')
def rz(a): return Matrix.Rotation(a,3,'Z')
scene.render.fps=24
rig.animation_data_create()
actions=[]
ground_checks={}
for label,period in [('Walk',32),('Run',20)]:
    action=bpy.data.actions.new(label)
    action.use_fake_user=True
    rig.animation_data.action=action
    is_run=label=='Run'
    heights=[]
    for f in range(1,period+2):
        scene.frame_set(f)
        phase=2*math.pi*(f-1)/period
        for p in rig.pose.bones:
            p.location=(0,0,0)
            p.rotation_mode='QUATERNION'
            p.rotation_quaternion=(1,0,0,0)
            p.scale=(1,1,1)
        rotate('Spine',rx(-.13 if is_run else -.025)@rz(.035*math.sin(phase)))
        rotate('Head',rx(.09 if is_run else .025))
        for s,side in [(-1,'Right'),(1,'Left')]:
            q=phase+(math.pi if s<0 else 0)
            swing=math.sin(q)
            thigh=(.68 if is_run else .34)*swing
            knee=(.23 if is_run else .055)+(1.08 if is_run else .53)*max(0,math.cos(q))
            rotate(side+'_Thigh',rx(thigh))
            rotate(side+'_Shin',rx(knee))
            rotate(side+'_Foot',rx(-.55*knee-.45*thigh))
            arm_swing=-(.65 if is_run else .32)*swing
            rotate(side+'_UpperArm',rx(arm_swing)@ry(s*1.49))
            rotate(side+'_Forearm',rz(-s*((1.1 if is_run else .20)+.12*math.cos(q))))
        bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get()
        # Match the lowest shoe to the floor, with a short flight phase for running.
        lowest=min((obj.evaluated_get(deps).matrix_world@v.co).z for obj in parts if obj.name.endswith('_Shoe') for v in obj.evaluated_get(deps).data.vertices)
        flight=.13*max(0,math.sin(2*phase)) if is_run else 0
        rig.pose.bones['Root'].location=arm.bones['Root'].matrix_local.to_3x3().inverted()@Vector((0,0,-lowest+flight))
        heights.append(round(flight,4))
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_quaternion',frame=f,group=p.name)
            if p.name=='Root': p.keyframe_insert('location',frame=f,group=p.name)
    # Layered actions are used by Blender 4.4+; retain compatibility with older files.
    curves=[]
    if hasattr(action,'layers'):
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags: curves.extend(bag.fcurves)
    elif hasattr(action,'fcurves'): curves=list(action.fcurves)
    for curve in curves:
        for key in curve.keyframe_points: key.interpolation='LINEAR'
        curve.modifiers.new('CYCLES')
    actions.append((action,period,rig.animation_data.action_slot))
    ground_checks[label]={'frames':period,'flight_height_max':max(heights),'curves':len(curves)}

rig.animation_data.action=None
for action,period,slot in actions:
    track=rig.animation_data.nla_tracks.new()
    track.name=action.name+' Cycle'
    strip=track.strips.new(action.name,1,action)
    if hasattr(strip,'action_slot'): strip.action_slot=slot
    strip.repeat=6
    strip.extrapolation='NOTHING'
    track.mute=action.name!='Walk'
scene.frame_start=1
scene.frame_end=192
scene.frame_set(9)
rig['animation_notes']='24 fps. Walk: 32 frames. Run: 20 frames. In NLA, unmute exactly one cycle track. Meshes remain editable; select rig for Pose Mode.'
scene.render.filepath=OUT+'/walk-cycle-preview.png'
bpy.ops.render.render(write_still=True)
for track in rig.animation_data.nla_tracks: track.mute=track.name!='Run Cycle'
scene.frame_set(6)
scene.render.filepath=OUT+'/run-cycle-preview.png'
bpy.ops.render.render(write_still=True)
for track in rig.animation_data.nla_tracks: track.mute=track.name!='Walk Cycle'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/reference-character.blend')
result={'file':bpy.data.filepath,'bones':len(arm.bones),'actions':ground_checks,'active':'Walk Cycle','meshes':len(parts)}
