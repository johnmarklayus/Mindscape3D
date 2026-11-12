"""Export only the repaired clips, plus the composed dormitory preview."""
import bpy
import shutil
import json
import struct
from pathlib import Path
from mathutils import Matrix

ROOT=Path('/Users/arieljerickogacilo/mindscape-3d')
OUT=ROOT/'Assets/Characters/Animations'
REPORT=ROOT/'Documents/Reports/sleep-animation-fix'
CLIPS=('Walk_To_Bed_And_Sleep','Sleeping_Idle','Wake_Up_And_Get_Out_Of_Bed')


def clean_glb_library(path):
    # NLA export can gather compatible legacy tracks from other scene objects.
    # Keep only the three explicitly paired skeletal/morph clips.
    blob=path.read_bytes();length=struct.unpack_from('<I',blob,12)[0]
    doc=json.loads(blob[20:20+length]);tail=blob[20+length:]
    clips={a['name']:a for a in doc['animations']}
    assert all(n in clips for n in CLIPS)
    doc['animations']=[clips[n] for n in CLIPS]
    assert all(sum(c['target']['path']=='weights' for c in a['channels'])==1 for a in doc['animations'])
    encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(tail))+
                    struct.pack('<II',len(encoded),0x4E4F534A)+encoded+tail)


def pair_fbx_eyelids(path):
    # FBX bakes armature NLA strips separately but evaluates shape-key NLA as
    # one stack. Pair the baked lid curve with its corresponding armature take.
    from io_scene_fbx import parse_fbx,encode_bin,data_types
    root,version=parse_fbx.parse(str(path))
    objects={e.props[0]:e for e in next(e for e in root.elems if e.id==b'Objects').elems}
    connections=next(e for e in root.elems if e.id==b'Connections').elems
    def smooth(t):
        t=max(0.,min(1.,t));return t*t*t*(t*(t*6-15)+10)
    for ident,stack in objects.items():
        if stack.id!=b'AnimationStack':continue
        name=stack.props[1].split(b'\x00')[0].decode()
        assert name in CLIPS
        layers={c.props[1] for c in connections if c.props[2]==ident}
        nodes={c.props[1] for c in connections if c.props[2] in layers}
        morph={c.props[1] for c in connections if c.props[1] in nodes and len(c.props)>3 and c.props[3]==b'DeformPercent'}
        curves={c.props[1] for c in connections if c.props[2] in morph}
        assert len(curves)==1
        for cid in curves:
            e=objects[cid]
            values=next(x for x in e.elems if x.id==b'KeyValueFloat').props[0]
            for i in range(len(values)):
                f=i+1
                value=smooth((f-210)/26) if name==CLIPS[0] else 1. if name==CLIPS[1] else 1-smooth((f-8)/18)
                values[i]=100*value
            next(x for x in e.elems if x.id==b'Default').props[0]=values[0]
    methods={data_types.BOOL:'add_bool',data_types.CHAR:'add_char',
        data_types.INT8:'add_int8',data_types.INT16:'add_int16',
        data_types.INT32:'add_int32',data_types.INT64:'add_int64',
        data_types.FLOAT32:'add_float32',data_types.FLOAT64:'add_float64',
        data_types.STRING:'add_string',data_types.BYTES:'add_bytes',
        data_types.INT32_ARRAY:'add_int32_array',data_types.INT64_ARRAY:'add_int64_array',
        data_types.FLOAT32_ARRAY:'add_float32_array',data_types.FLOAT64_ARRAY:'add_float64_array',
        data_types.BOOL_ARRAY:'add_bool_array',data_types.BYTE_ARRAY:'add_byte_array'}
    def convert(e):
        out=encode_bin.FBXElem(e.id)
        for typ,value in zip(e.props_type,e.props):getattr(out,methods[typ])(value)
        out.elems=[convert(x) for x in e.elems]
        return out
    encode_bin.write(str(path),convert(root),version)


def nla(owner,name,action):
    owner.animation_data_create()
    t=owner.animation_data.nla_tracks.new();t.name=name
    s=t.strips.new(name,1,action);s.blend_type='REPLACE';s.extrapolation='NOTHING'


def export():
    source=bpy.context.scene
    backup=REPORT/'backups';backup.mkdir(parents=True,exist_ok=True)
    for name in ['Sleeping_Animations.fbx','Sleeping_Animations.glb','Dormitory_Sleep_Scenarios.fbx','Dormitory_Sleep_Scenarios.glb']:
        p=OUT/name
        if p.exists() and not (backup/name).exists():shutil.copy2(p,backup/name)
    temp=bpy.data.scenes.new('Sleep_Clip_Export_Temporary')
    temp.render.fps=30;temp.frame_start=1;temp.frame_end=240
    original_rig=bpy.data.objects['Player_BaldCharacter_Rig']
    rig=original_rig.copy();rig.data=original_rig.data.copy()
    rig.name='Sleep_Export_Rig';rig.animation_data_clear()
    temp.collection.objects.link(rig)
    rig.location=(0,0,0);rig.rotation_mode='XYZ';rig.rotation_euler=(0,0,0)
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    original_mesh=bpy.data.objects['BaldCharacter_Mesh']
    mesh=original_mesh.copy();mesh.data=original_mesh.data.copy()
    mesh.name='Sleep_Export_Character';mesh.animation_data_clear()
    temp.collection.objects.link(mesh)
    mesh.parent=rig;mesh.matrix_parent_inverse=original_mesh.matrix_parent_inverse.copy()
    for m in mesh.modifiers:
        if m.type=='ARMATURE':m.object=rig
    keys=mesh.data.shape_keys
    keys.animation_data_clear()
    for name in CLIPS:
        nla(rig,name,bpy.data.actions[name])
        nla(keys,name,bpy.data.actions[name+'_Eyes'])
    # Preserve existing model/bone binding paths in the replacement assets.
    rig_name=original_rig.name;mesh_name=original_mesh.name
    original_rig.name='__Sleep_Source_Rig';original_mesh.name='__Sleep_Source_Mesh'
    rig.name=rig_name;mesh.name=mesh_name
    bpy.context.window.scene=temp
    try:
        rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
        bpy.ops.export_scene.gltf(filepath=str(OUT/'Sleeping_Animations.glb'),
            export_format='GLB',use_selection=True,export_animations=True,
            export_animation_mode='NLA_TRACKS',export_merge_animation='NLA_TRACK',
            export_frame_range=False,export_anim_slide_to_zero=True,
            export_force_sampling=True,export_morph=True,export_morph_animation=True)
        bpy.ops.export_scene.fbx(filepath=str(OUT/'Sleeping_Animations.fbx'),
            use_selection=True,object_types={'ARMATURE','MESH'},
            bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,
            bake_anim_simplify_factor=0.,add_leaf_bones=False,
            axis_forward='-Z',axis_up='Y')
        clean_glb_library(OUT/'Sleeping_Animations.glb')
        pair_fbx_eyelids(OUT/'Sleeping_Animations.fbx')
    finally:
        bpy.context.window.scene=source
        md=mesh.data;ad=rig.data
        bpy.data.objects.remove(mesh,do_unlink=True);bpy.data.objects.remove(rig,do_unlink=True)
        bpy.data.meshes.remove(md);bpy.data.armatures.remove(ad)
        bpy.data.scenes.remove(temp)
        original_rig.name=rig_name;original_mesh.name=mesh_name
    for o in source.objects:o.select_set(False)
    for o in bpy.data.collections['Dormitory_Sleep_Scene'].all_objects:
        if o.type in {'ARMATURE','MESH'}:o.select_set(True)
    bpy.context.view_layer.objects.active=original_rig
    source.frame_set(1)
    bpy.ops.export_scene.gltf(filepath=str(OUT/'Dormitory_Sleep_Scenarios.glb'),
        export_format='GLB',use_selection=True,export_animations=True,
        export_animation_mode='SCENE',export_anim_scene_split_object=False,
        export_nla_strips_merged_animation_name='Dormitory_Sleep_Sequence',
        export_frame_range=True,export_anim_slide_to_zero=True,
        export_force_sampling=True,export_morph=True,export_morph_animation=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/'Dormitory_Sleep_Scenarios.fbx'),
        use_selection=True,object_types={'ARMATURE','MESH'},
        bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.,add_leaf_bones=False,axis_forward='-Z',axis_up='Y')
    for o in source.objects:o.select_set(False)
    original_rig.select_set(True)
    source.frame_set(1)
    source.render.engine='BLENDER_EEVEE'
    source.camera=bpy.data.objects[source['sleep_review_original_camera']]
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Blender/Blend Files/Dormitory_Sleep_Scenarios.blend'))
    print('Saved repaired source, three-clip FBX/GLB library, and complete-sequence FBX/GLB.')


if __name__=='__main__':export()
