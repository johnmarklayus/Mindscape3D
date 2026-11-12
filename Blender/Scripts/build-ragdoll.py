"""Build the character_ragdoll.png reference as a smooth, skinned T-pose model."""
import bpy, math, os, json
from mathutils import Vector

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/character_ragdoll'
os.makedirs(OUT, exist_ok=True)
if not os.path.exists(OUT + '/before-ragdoll.blend'):
    bpy.ops.wm.save_as_mainfile(filepath=OUT + '/before-ragdoll.blend', copy=True)
scene = bpy.data.scenes.new('Ragdoll Character')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.render.fps = 30
parts = []

def ellipsoid(name, pos, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(obj)
    return obj

ellipsoid('Belly', (0,0,1.99), (.425,.285,.56))
ellipsoid('Chest', (0,0,2.34), (.435,.265,.32))
ellipsoid('Pelvis', (0,.005,1.68), (.385,.27,.28))
ellipsoid('Neck', (0,0,2.66), (.18,.18,.22))
ellipsoid('Head', (0,-.015,3.10), (.46,.405,.49))
for s in (-1,1):
    verts, faces = [], []
    rows = [(.30,.18),(.42,.175),(.60,.165),(.78,.15),(.94,.14),(1.10,.127),(1.28,.11),(1.43,.108),(1.49,.10)]
    for x,r in rows:
        for j in range(24):
            a=2*math.pi*j/24
            verts.append((s*x, math.cos(a)*r, 2.43+math.sin(a)*r))
    faces.append(tuple(reversed(range(24))))
    for i in range(len(rows)-1):
        for j in range(24):
            faces.append((i*24+j,i*24+(j+1)%24,(i+1)*24+(j+1)%24,(i+1)*24+j))
    faces.append(tuple(range((len(rows)-1)*24,len(rows)*24)))
    mesh=bpy.data.meshes.new('Smooth arm')
    mesh.from_pydata(verts,[],faces)
    obj=bpy.data.objects.new('Smooth arm',mesh)
    scene.collection.objects.link(obj)
    parts.append(obj)
    ellipsoid('Hand', (s*1.53,-.004,2.43), (.182,.164,.175))
    ellipsoid('Thigh', (s*.255,0,1.30), (.192,.198,.44))
    ellipsoid('Knee', (s*.275,-.005,.91), (.147,.148,.20))
    ellipsoid('Calf', (s*.285,.012,.59), (.18,.18,.355))
    ellipsoid('Ankle', (s*.29,0,.265), (.138,.145,.19))
    foot = ellipsoid('Foot', (s*.30,-.105,.145), (.235,.315,.225))
    for v in foot.data.vertices:
        v.co.z = max(v.co.z, -.135)
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.object
body.name = 'Ragdoll_Body'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
remesh = body.modifiers.new('Continuous soft silhouette', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = .024
remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = body.modifiers.new('Soften joins', 'SMOOTH')
smooth.factor = 1.15
smooth.iterations = 7
bpy.ops.object.modifier_apply(modifier=smooth.name)
for p in body.data.polygons: p.use_smooth = True
mat = bpy.data.materials.new('Warm ivory fabric')
mat.diffuse_color = (.72,.53,.32,1)
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.72,.53,.32,1)
bsdf.inputs['Roughness'].default_value = .83
bsdf.inputs['Subsurface Weight'].default_value = .055
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 185
noise.inputs['Detail'].default_value = 2
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .13
bump.inputs['Distance'].default_value = .009
mat.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
mat.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
body.data.materials.clear()
body.data.materials.append(mat)

arm = bpy.data.armatures.new('Ragdoll_Skeleton')
rig = bpy.data.objects.new('Ragdoll_Rig', arm)
scene.collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
def bone(name, head, tail, parent=None, deform=True):
    b = arm.edit_bones.new(name)
    b.head, b.tail = head, tail
    b.use_deform = deform
    if parent: b.parent = arm.edit_bones[parent]
bone('Root', (0,0,0), (0,0,.25), deform=False)
bone('Hips', (0,0,1.58), (0,0,1.85), 'Root')
bone('Spine', (0,0,1.85), (0,0,2.18), 'Hips')
bone('Chest', (0,0,2.18), (0,0,2.48), 'Spine')
bone('Neck', (0,0,2.48), (0,0,2.72), 'Chest')
bone('Head', (0,0,2.72), (0,0,3.40), 'Neck')
for s, side in [(1,'L'),(-1,'R')]:
    bone('Clavicle.'+side, (s*.05,0,2.43), (s*.40,0,2.43), 'Chest')
    bone('UpperArm.'+side, (s*.40,0,2.43), (s*.91,0,2.43), 'Clavicle.'+side)
    bone('Forearm.'+side, (s*.91,0,2.43), (s*1.38,0,2.43), 'UpperArm.'+side)
    bone('Hand.'+side, (s*1.38,0,2.43), (s*1.66,0,2.43), 'Forearm.'+side)
    bone('Thigh.'+side, (s*.255,0,1.58), (s*.275,-.02,.91), 'Hips')
    bone('Shin.'+side, (s*.275,-.02,.91), (s*.29,0,.23), 'Thigh.'+side)
    bone('Foot.'+side, (s*.29,0,.23), (s*.29,-.30,.12), 'Shin.'+side)
    bone('FootTarget.'+side, (s*.29,0,.23), (s*.29,-.30,.12), 'Root', False)
    bone('KneePole.'+side, (s*.275,-1,.91), (s*.275,-1,1.10), 'Root', False)
bpy.ops.object.mode_set(mode='OBJECT')
body.select_set(True)
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
assert len(body.vertex_groups) == 19 and all(v.groups for v in body.data.vertices), 'Automatic weights failed'
body.modifiers.get('Armature').use_deform_preserve_volume = True
subd = body.modifiers.new('Silhouette polish', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1
rig.show_in_front = True
arm.display_type = 'STICK'
rig['reference'] = '/Models/character_ragdoll.png'
rig['front'] = '-Y; Z up; feet on ground; T-pose rest skeleton'

# A separate presentation collection is excluded from character exports.
studio = bpy.data.collections.new('Studio (not exported)')
scene.collection.children.link(studio)
def move_to_studio(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    studio.objects.link(obj)
bpy.ops.mesh.primitive_plane_add(size=200)
floor = bpy.context.object
floor.name = 'Studio floor'
floor.location.z = -.012
move_to_studio(floor)
floor_mat = bpy.data.materials.new('Studio chalk')
floor_mat.diffuse_color = (.7,.72,.76,1)
floor.data.materials.append(floor_mat)
world = bpy.data.worlds.new('Ragdoll studio')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.65,.71,.8,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .35
scene.world = world
for name, pos, power, size in [('Key',(-3,-4,6),500,4),('Fill',(4,-2,4),300,3),('Rim',(1,3,5),550,3)]:
    data = bpy.data.lights.new(name, 'AREA')
    obj = bpy.data.objects.new(name,data)
    studio.objects.link(obj)
    obj.location=pos
    obj.rotation_euler=(Vector((0,0,1.8))-obj.location).to_track_quat('-Z','Y').to_euler()
    data.energy, data.shape, data.size=power,'DISK',size
cam_data=bpy.data.cameras.new('Ragdoll preview')
cam=bpy.data.objects.new('Ragdoll preview',cam_data)
studio.objects.link(cam)
cam.location=(4,-10,4.1)
cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'
cam_data.ortho_scale=4.4
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=800
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
            area.spaces.active.region_3d.view_distance=5.8
            area.spaces.active.region_3d.view_location=(0,0,1.8)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/character_ragdoll.blend')
print(json.dumps({'vertices':len(body.data.vertices),'bones':len(arm.bones),'file':bpy.data.filepath}))
