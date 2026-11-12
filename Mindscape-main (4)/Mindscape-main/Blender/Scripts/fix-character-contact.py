import bpy
import math
from mathutils import Vector
scene=bpy.context.scene
rig=bpy.data.objects['Reference_Character_Rig']
root=rig.pose.bones['Root']
shoes=[o for o in scene.objects if o.name.startswith('Reference_Character_') and o.name.endswith('_Shoe')]
tracks=rig.animation_data.nla_tracks
for track in tracks: track.mute=True
checks={}
for name,period in [('Walk',32),('Run',20)]:
    action=bpy.data.actions[name]
    rig.animation_data.action=action
    rig.animation_data.action_slot=action.slots[0]
    for f in range(1,period+2):
        scene.frame_set(f)
        root.location=(0,0,0)
        bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get()
        bottom=min((o.evaluated_get(deps).matrix_world@v.co).z for o in shoes for v in o.evaluated_get(deps).data.vertices)
        flight=.13*max(0,math.sin(4*math.pi*(f-1)/period)) if name=='Run' else 0
        root.location=rig.data.bones['Root'].matrix_local.to_3x3().inverted()@Vector((0,0,flight-bottom))
        root.keyframe_insert('location',frame=f,group='Root')
    positions=[]
    bottoms=[]
    for f in range(1,period+2):
        scene.frame_set(f)
        deps=bpy.context.evaluated_depsgraph_get()
        points=[o.evaluated_get(deps).matrix_world@v.co for o in shoes for v in o.evaluated_get(deps).data.vertices]
        bottoms.append(min(p.z for p in points))
        if f in (1,period+1): positions.append(points)
    error=max((a-b).length for a,b in zip(*positions))
    assert min(bottoms)>-.0001
    assert error<.0001
    checks[name]={'minimum_shoe_z':round(min(bottoms),5),'loop_seam_error':round(error,6)}
rig.animation_data.action=None
for track in tracks: track.mute=track.name!='Walk Cycle'
scene.frame_set(9)
scene.render.filepath='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/walk-cycle-preview.png'
bpy.ops.render.render(write_still=True)
for track in tracks: track.mute=track.name!='Run Cycle'
scene.frame_set(6)
scene.render.filepath='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/run-cycle-preview.png'
bpy.ops.render.render(write_still=True)
for track in tracks: track.mute=track.name!='Walk Cycle'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/reference-character.blend')
result=checks
