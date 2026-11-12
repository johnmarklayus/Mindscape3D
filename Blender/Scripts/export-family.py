"""Export each family character at the origin with the same three clips."""
import bpy
import json
import os
import shutil
from mathutils import Vector

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/family_set'
UNITY = '/Users/arieljerickogacilo/mindscape-3d/Assets/FamilySet'
os.makedirs(UNITY,exist_ok=True)
scene = bpy.context.scene
members = [(bpy.data.objects[n+'_Rig'],bpy.data.objects[n+'_Mesh']) for n in ('Mother','Father','Boy','Girl')]
report = {}
expected = [b.name for b in members[0][0].data.bones]
for rig,mesh in members:
    assert [b.name for b in rig.data.bones] == expected
    assert all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in mesh.data.vertices)
    assert len(rig.animation_data.nla_tracks)==3
    entry = {'bones':len(rig.data.bones),'vertices':len(mesh.data.vertices),'clips':{},'minimum_ground_z':1e9,'maximum_ground_z':-1e9}
    for track in rig.animation_data.nla_tracks:
        strip = track.strips[0]
        action = strip.action
        entry['clips'][track.name] = {'frames':int(strip.action_frame_end-strip.action_frame_start),'seconds':(strip.action_frame_end-strip.action_frame_start)/30}
        endpoints=[]
        for frame in (int(strip.frame_start),int(strip.frame_end)):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            endpoints.append([p.matrix.copy() for p in rig.pose.bones])
        error = max(abs(a[i][j]-b[i][j]) for a,b in zip(*endpoints) for i in range(4) for j in range(4))
        assert error<1e-5,(rig.name,track.name,error)
        for frame in range(int(strip.frame_start),int(strip.frame_end)+1):
            scene.frame_set(frame)
            deps = bpy.context.evaluated_depsgraph_get()
            evaluated = mesh.evaluated_get(deps)
            z = min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices)
            entry['minimum_ground_z'] = min(entry['minimum_ground_z'],z)
            entry['maximum_ground_z'] = max(entry['maximum_ground_z'],z)
    assert entry['minimum_ground_z']>-.008,(rig.name,entry)
    report[rig.name] = entry

for rig,mesh in members:
    name = rig.name.removesuffix('_Rig')
    location = rig.location.copy()
    rig.location = (0,0,0)
    scene.frame_start,scene.frame_end = 1,145
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = rig
    try:
        bpy.ops.export_scene.gltf(filepath=OUT+'/'+name+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,
            export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
            export_frame_range=False,export_anim_slide_to_zero=True,export_yup=True)
        bpy.ops.export_scene.fbx(filepath=OUT+'/'+name+'.fbx',use_selection=True,object_types={'ARMATURE','MESH'},
            add_leaf_bones=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
            bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,
            bake_anim_step=1,bake_anim_simplify_factor=0,path_mode='AUTO')
        shutil.copy2(OUT+'/'+name+'.fbx',UNITY+'/'+name+'.fbx')
    finally:
        rig.location = location
scene.frame_start,scene.frame_end = 1,60
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for rig,mesh in members: mesh.select_set(True)
bpy.context.view_layer.objects.active = members[0][1]
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/family_set.blend')
with open(OUT+'/validation.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report))
