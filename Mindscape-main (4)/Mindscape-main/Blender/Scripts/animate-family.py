"""Shared, looping family actions and a neutral studio for inspection."""
import bpy
import math
import os
from mathutils import Matrix, Vector

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/family_set'
scene = bpy.context.scene
members = [(bpy.data.objects[n+'_Rig'],bpy.data.objects[n+'_Mesh']) for n in ('Mother','Father','Boy','Girl')]
rig,body = members[0]
arm = rig.data
rig.animation_data_create()
actions = []
rx = lambda a: Matrix.Rotation(a,3,'X')
ry = lambda a: Matrix.Rotation(a,3,'Y')
rz = lambda a: Matrix.Rotation(a,3,'Z')

def rotate(name,m):
    p = rig.pose.bones[name]
    basis = arm.bones[name].matrix_local.to_3x3()
    p.rotation_mode = 'QUATERNION'
    p.rotation_quaternion = (basis.inverted() @ m @ basis).to_quaternion()

def curves(action):
    return [f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]

for name,period in [('Idle',60),('Run',24)]:
    a = bpy.data.actions.new(name)
    a.use_fake_user = True
    rig.animation_data.action = a
    for frame in range(1,period+2):
        scene.frame_set(frame)
        phase = 2*math.pi*(frame-1)/period
        run = name=='Run'
        for p in rig.pose.bones:
            p.location = (0,0,0)
            p.rotation_mode = 'QUATERNION'
            p.rotation_quaternion = (1,0,0,0)
            p.scale = (1,1,1)
        rotate('Spine',rx(-.11 if run else .012*math.sin(phase)))
        rotate('Chest',rz(.045*math.sin(phase) if run else .009*math.sin(phase)))
        rotate('Head',rx(.08 if run else -.01*math.sin(phase)) @ rz(.01*math.sin(phase)))
        for s,side in ((1,'L'),(-1,'R')):
            q = phase + (math.pi if s<0 else 0)
            swing = math.sin(q)
            thigh = .78*swing if run else .012*math.sin(phase)
            knee = .22+1.16*max(0,math.cos(q)) if run else .02
            rotate('Thigh.'+side,rx(thigh))
            rotate('Shin.'+side,rx(knee))
            rotate('Foot.'+side,rx(-.48*knee-.40*thigh))
            rotate('UpperArm.'+side,rx(-.67*swing if run else .022*math.sin(q)) @ ry(s*(1.40 if run else 1.44)))
            rotate('Forearm.'+side,rz(-s*(1.15+.12*math.cos(q) if run else .09)))
        bpy.context.view_layer.update()
        deps = bpy.context.evaluated_depsgraph_get()
        evaluated = body.evaluated_get(deps)
        lowest = min((evaluated.matrix_world @ v.co).z for v in evaluated.data.vertices)
        flight = .10*max(0,math.sin(2*phase)) if run else 0
        world_lift = -lowest/rig.scale.z + flight
        rig.pose.bones['Root'].location = arm.bones['Root'].matrix_local.to_3x3().inverted() @ Vector((0,0,world_lift))
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name)
            if p.name=='Root': p.keyframe_insert('location',frame=frame,group=p.name)
    for fc in curves(a):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        fc.modifiers.new('CYCLES')
    actions.append((a,period,rig.animation_data.action_slot))

alias = actions[1][0].copy()
alias.name = 'Running'
alias.use_fake_user = True
actions.append((alias,24,alias.slots[0]))
for r,m in members:
    r.animation_data_create()
    r.animation_data.action = None
    for (a,period,slot),start in zip(actions,(1,81,121)):
        t = r.animation_data.nla_tracks.new()
        t.name = a.name
        st = t.strips.new(a.name,start,a)
        st.action_slot = slot
        st.extrapolation = 'NOTHING'
        st.blend_type = 'REPLACE'
    r['animation_fps'] = 30
scene.frame_start,scene.frame_end = 1,60
for name,frame in [('Idle',1),('Run',81),('Running',121)]: scene.timeline_markers.new(name,frame=frame)

studio = bpy.data.collections.new('Studio - excluded from exports')
scene.collection.children.link(studio)
def studio_object(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    studio.objects.link(o)
    return o
bpy.ops.mesh.primitive_plane_add(size=200)
floor = studio_object(bpy.context.object)
floor.name = 'Family studio floor'
floor.location.z = -.012
mat = bpy.data.materials.new('Family studio pale gray')
mat.diffuse_color = (.38,.42,.45,1)
floor.data.materials.append(mat)
world = bpy.data.worlds.new('Family studio world')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.60,.67,.75,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .4
scene.world = world
for name,pos,power,size in [('Key',(-3,-4,6),650,5),('Fill',(4,-2,3),400,4),('Rim',(0,3,5),700,3)]:
    data = bpy.data.lights.new('Family '+name,'AREA')
    o = bpy.data.objects.new('Family '+name,data)
    studio.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    data.energy,data.shape,data.size = power,'DISK',size
data = bpy.data.cameras.new('Family portrait')
camera = bpy.data.objects.new('Family portrait',data)
studio.objects.link(camera)
camera.location = (3,-12,4.0)
camera.rotation_euler = (Vector((0,0,1.02))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type = 'ORTHO'
data.ortho_scale = 5.25
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage = 1500,900,100
scene.view_settings.view_transform = 'AgX'
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for r,m in members: m.select_set(True)
bpy.context.view_layer.objects.active = members[0][1]
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_perspective = 'CAMERA'
        area.spaces.active.shading.type = 'MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/family_set.blend')
print('Shared actions:',[(a.name,period,len(curves(a))) for a,period,slot in actions])
