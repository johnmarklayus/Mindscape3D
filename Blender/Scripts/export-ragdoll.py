import bpy, json, math
OUT='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/character_ragdoll'
s=bpy.context.scene
r=bpy.data.objects['Ragdoll_Rig']
b=bpy.data.objects['Ragdoll_Body']
report={}
for name in ('T_Pose','Idle','Walk','Run'):
    a=bpy.data.actions[name]
    r.animation_data.action=a
    endpoints=[]
    for frame in (int(a.frame_range[0]),int(a.frame_range[1])):
        s.frame_set(frame)
        bpy.context.view_layer.update()
        endpoints.append({p.name:p.matrix.copy() for p in r.pose.bones})
    seam=max(abs(endpoints[0][n][i][j]-endpoints[1][n][i][j]) for n in endpoints[0] for i in range(4) for j in range(4))
    assert seam<.001, (name,'loop mismatch',seam)
    report[name]={'frames':list(a.frame_range),'loop_seam_max_matrix_error':seam}
# Export only model and skeleton, all four actions, no studio or reference scene.
bpy.ops.object.select_all(action='DESELECT')
r.select_set(True)
b.select_set(True)
bpy.context.view_layer.objects.active=r
r.animation_data.action=bpy.data.actions['T_Pose']
s.frame_set(1)
bpy.ops.export_scene.gltf(filepath=OUT+'/character_ragdoll.glb',export_format='GLB',
    use_selection=True,export_animations=True,export_animation_mode='ACTIONS',
    export_anim_single_armature=True,export_force_sampling=True,export_frame_range=False,
    export_apply=False,export_skins=True,export_yup=True)
bpy.ops.export_scene.fbx(filepath=OUT+'/character_ragdoll.fbx',use_selection=True,
    object_types={'ARMATURE','MESH'},add_leaf_bones=False,use_armature_deform_only=True,
    bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
    bake_anim_simplify_factor=0,axis_forward='-Z',axis_up='Y',apply_unit_scale=True)
r.animation_data.action=bpy.data.actions['Idle']
s.frame_start=1
s.frame_end=121
s.frame_set(1)
b.select_set(False)
# Open in a clean material viewport, with idle ready to play.
r.show_in_front=False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.overlay.show_extras=False
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/character_ragdoll.blend')
with open(OUT+'/validation.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report))
