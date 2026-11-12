import bpy,bmesh,math
from math import pi,sin,cos
OUT='/Users/arieljerickogacilo/mindscape-3d/Blender Files/BaldCharacter'
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
mesh=bpy.data.objects['BaldCharacter_Mesh'];rig=bpy.data.objects['BaldCharacter_Rig'];scene=bpy.context.scene
rig.animation_data.action=None
for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0)
scene.frame_set(1)
bm=bmesh.new();bm.from_mesh(mesh.data)
oldmats={i for i,m in enumerate(mesh.data.materials) if m and m.name in ['Soles socks and laces • ivory','Sneakers • graphite']}
verts={v for f in bm.faces if f.material_index in oldmats for v in f.verts}
bmesh.ops.delete(bm,geom=list(verts),context='VERTS');bm.to_mesh(mesh.data);bm.free();mesh.data.update()
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.72;return m
black=mat('Boots • matte black',(.018,.021,.026));sole=mat('Boots • black rubber',(.008,.010,.013))
boots=[]
for s,side in [(1,'L'),(-1,'R')]:
 # A continuous plain ankle boot, with a broad toe and a short shaft.
 rings=[(.014,-.060,.119,.194),(.035,-.060,.126,.201),(.067,-.060,.126,.201),(.082,-.060,.119,.195),(.135,-.055,.116,.187),(.190,-.037,.107,.156),(.235,-.007,.088,.095),(.340,0,.086,.083),(.357,0,.089,.086),(.369,0,.089,.086)]
 n=20;vs=[];fs=[]
 for z,cy,rx,ry in rings:
  for j in range(n):
   a=2*pi*j/n;x=cos(a);y=sin(a)
   vs.append((s*.16+rx*math.copysign(abs(x)**.72,x),cy+ry*math.copysign(abs(y)**.72,y),z))
 for k in range(len(rings)-1):
  for j in range(n):fs.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 fs.append(tuple(reversed(range(n))));fs.append(tuple((len(rings)-1)*n+j for j in range(n)))
 me=bpy.data.meshes.new('BlackBoot.'+side);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('BlackBoot.'+side,me);mesh.users_collection[0].objects.link(o);me.materials.append(black);me.materials.append(sole)
 for poly in me.polygons:poly.material_index=1 if poly.center.z<.07 else 0
 o.vertex_groups.new(name='foot.'+side).add(list(range(len(vs))),1,'REPLACE');boots.append(o)
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True)
for o in boots:o.select_set(True)
bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join()
# Refresh the ground offset for the new soles.
for name in ['Idle','Walk','Run','Conversation','Sit_Down','Seated_Idle']:
 action=bpy.data.actions[name];rig.animation_data.action=action
 for f in range(int(action.frame_range[0]),int(action.frame_range[1])+1):
  scene.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());z=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
  rig.pose.bones['root'].location.y+=.012-z;rig.pose.bones['root'].keyframe_insert('location',frame=f,group='root')
rig.animation_data.action=None
for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0)
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=OUT+'/BaldCharacter.glb',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/BaldCharacter.blend')
print('Updated black boots and exported all six animation clips.')
