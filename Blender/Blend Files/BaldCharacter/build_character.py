import bpy, math, random, os
from mathutils import Vector, Quaternion
from math import sin, cos, pi
OUT='/Users/arieljerickogacilo/mindscape-3d/Blender Files/BaldCharacter'
scene=bpy.context.scene
char=bpy.data.collections.new('Bald Character • rigged'); scene.collection.children.link(char)
parts=[]
def material(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.78
 return m
skin=material('Skin • warm peach',(.72,.335,.13)); teal=material('Shirt • lagoon teal',(.025,.39,.43)); shorts=material('Shorts • charcoal',(.095,.105,.13)); shoe=material('Sneakers • graphite',(.19,.185,.18)); white=material('Soles socks and laces • ivory',(.87,.83,.73)); eye=material('Eyes • espresso',(.045,.031,.024)); shine=material('Eye catchlights',(.99,.98,.92)); mouth=material('Smile and brows',(.22,.095,.037)); inner=material('Ear inner',(.63,.24,.10))
def finish(o,name,mat,bone):
 o.name=name
 for c in list(o.users_collection): c.objects.unlink(o)
 char.objects.link(o); o.data.materials.append(mat)
 if bone: o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 parts.append(o); return o
def ell(name,loc,scale,mat,bone,seg=24,rings=16):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
 o=bpy.context.object; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,name,mat,bone)
def tube(name,points,radii,mat,bone,n=12):
 verts=[]; faces=[]
 axis=(Vector(points[-1])-Vector(points[0])).normalized(); u=axis.cross(Vector((0,1,0))).normalized(); v=axis.cross(u).normalized()
 for p,r in zip(points,radii):
  rx,ry=r if isinstance(r,tuple) else (r,r)
  for j in range(n): verts.append(Vector(p)+u*cos(2*pi*j/n)*rx+v*sin(2*pi*j/n)*ry)
 for k in range(len(points)-1):
  for j in range(n): a=k*n+j; b=k*n+(j+1)%n; faces.append((a,b,b+n,a+n))
 faces += [tuple(reversed(range(n))),tuple((len(points)-1)*n+j for j in range(n))]
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); char.objects.link(o)
 return finish(o,name,mat,bone)
def line(name,pts,r,mat,bone):
 cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=2
 sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts): p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu); char.objects.link(ob); bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob.select_set(False)
 return finish(bpy.context.object,name,mat,bone)
# Body with a flared hem and narrow collar.
tube('T-shirt',[(0,0,1.00),(0,0,1.10),(0,0,1.40),(0,0,1.61),(0,0,1.67)],[(.30,.18),(.285,.17),(.25,.16),(.31,.16),(.15,.12)],teal,'chest',20)
tube('Neck',[(0,0,1.60),(0,0,1.82)],[.12,.13],skin,'neck')
ell('Bald head',(0,-.005,2.065),(.465,.37,.49),skin,'head',32,20)
for s,side in [(1,'L'),(-1,'R')]:
 ell('Ear.'+side,(s*.455,0,2.025),(.105,.083,.135),skin,'head',16,12)
 ell('Ear inset.'+side,(s*.482,-.064,2.027),(.056,.022,.081),inner,'head',16,12)
 ell('Eye.'+side,(s*.175,-.347,2.10),(.064,.025,.10),eye,'head')
 ell('Eye sparkle.'+side,(s*.16,-.373,2.142),(.019,.009,.024),shine,'head',12,8)
 pts=[(s*.175+(j-4)*.016,-.338,2.253+.02*sin(pi*j/8)) for j in range(9)]
 line('Brow.'+side,pts,.012,mouth,'head')
 # Sleeves and jointed arms.
 tube('Sleeve.'+side,[(s*.24,0,1.55),(s*.40,0,1.55)],[(.135,.15),(.13,.14)],teal,'upper_arm.'+side)
 arm=tube('Arm.'+side,[(s*.37,0,1.55),(s*.56,0,1.55),(s*.70,0,1.55),(s*.85,0,1.55),(s*1.00,0,1.55)],[.089,.081,.078,.068,.061],skin,None)
 g1=arm.vertex_groups.new(name='upper_arm.'+side); g2=arm.vertex_groups.new(name='forearm.'+side)
 for vert in arm.data.vertices:
  t=max(0,min(1,(abs(vert.co.x)-.63)/.14)); g1.add([vert.index],1-t,'REPLACE'); g2.add([vert.index],t,'REPLACE')
 ell('Hand.'+side,(s*1.075,-.002,1.55),(.115,.068,.071),skin,'hand.'+side,16,12)
 ell('Thumb.'+side,(s*1.028,-.055,1.517),(.061,.044,.040),skin,'hand.'+side,12,8)
 tube('Shorts leg.'+side,[(s*.155,0,.76),(s*.15,0,.93),(s*.145,0,1.035)],[(.153,.16),(.145,.16),(.151,.16)],shorts,'thigh.'+side)
 leg=tube('Leg.'+side,[(s*.16,0,.82),(s*.16,0,.65),(s*.16,0,.52),(s*.16,0,.38),(s*.16,0,.23)],[.092,.085,.078,.071,.064],skin,None)
 g1=leg.vertex_groups.new(name='thigh.'+side); g2=leg.vertex_groups.new(name='shin.'+side)
 for vert in leg.data.vertices:
  t=max(0,min(1,(.60-vert.co.z)/.14));g1.add([vert.index],1-t,'REPLACE');g2.add([vert.index],t,'REPLACE')
 tube('Sock.'+side,[(s*.16,0,.19),(s*.16,0,.34)],[.077,.081],white,'shin.'+side)
 ell('Sole.'+side,(s*.16,-.07,.075),(.125,.216,.065),white,'foot.'+side,20,12)
 ell('Sneaker.'+side,(s*.16,-.065,.147),(.117,.196,.107),shoe,'foot.'+side,20,12)
 ell('Toe cap.'+side,(s*.16,-.205,.115),(.112,.065,.064),white,'foot.'+side,16,12)
 for j in range(3):
  y=-.06-j*.043
  line('Lace.'+side+str(j),[(s*.16-.069,y,.228-j*.012),(s*.16,y-.007,.245-j*.014),(s*.16+.069,y,.228-j*.012)],.011,white,'foot.'+side)
# Small triangular nose and curved smile.
me=bpy.data.meshes.new('Nose');me.from_pydata([(-.035,-.369,2.009),(.035,-.369,2.009),(0,-.385,2.10),(0,-.426,2.028)],[],[(0,1,3),(1,2,3),(2,0,3),(0,2,1)]);me.update();ob=bpy.data.objects.new('Nose',me);char.objects.link(ob);finish(ob,'Nose',skin,'head')
line('Smile',[(.085*(j/8-1),-.356- .008*sin(pi*j/16),1.935-.018*sin(pi*j/16)) for j in range(17)],.007,mouth,'head')
# Skeleton in a true T-pose.
bpy.ops.object.select_all(action='DESELECT'); data=bpy.data.armatures.new('BaldCharacterSkeleton'); rig=bpy.data.objects.new('BaldCharacter_Rig',data);char.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
 b=data.edit_bones.new(name);b.head=head;b.tail=tail
 if parent:b.parent=data.edit_bones[parent]
 return b
bone('root',(0,0,0),(0,0,.25));bone('hips',(0,0,.95),(0,0,1.12),'root');bone('chest',(0,0,1.12),(0,0,1.60),'hips');bone('neck',(0,0,1.60),(0,0,1.80),'chest');bone('head',(0,0,1.80),(0,0,2.42),'neck')
for s,side in [(1,'L'),(-1,'R')]:
 bone('upper_arm.'+side,(s*.30,0,1.55),(s*.70,0,1.55),'chest');bone('forearm.'+side,(s*.70,0,1.55),(s*1.00,0,1.55),'upper_arm.'+side);bone('hand.'+side,(s*1.00,0,1.55),(s*1.17,0,1.55),'forearm.'+side)
 bone('thigh.'+side,(s*.16,0,.97),(s*.16,0,.54),'hips');bone('shin.'+side,(s*.16,0,.54),(s*.16,0,.19),'thigh.'+side);bone('foot.'+side,(s*.16,0,.19),(s*.16,-.23,.10),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='BaldCharacter_Mesh';mod=mesh.modifiers.new('Character skin','ARMATURE');mod.object=rig;mesh.parent=rig
# Actions: all rotations expressed around world-aligned axes in the rest pose.
axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
def rot(name,angles):
 b=rig.pose.bones[name]; basis=b.bone.matrix_local.to_3x3();q=Quaternion()
 for axis,a in zip(axes,angles):q=q@Quaternion(basis.inverted()@axis,math.radians(a))
 b.rotation_mode='QUATERNION';b.rotation_quaternion=q

def pose(kind,t):
 for b in rig.pose.bones:b.location=(0,0,0);b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0)
 phase=2*pi*t
 for s,side in [(1,'L'),(-1,'R')]:rot('upper_arm.'+side,(0,s*76,0));rot('forearm.'+side,(0,0,s*-8))
 if kind=='Idle':
  rig.pose.bones['hips'].location.y=.009*sin(phase);rot('chest',(1.2*sin(phase),0,1*sin(phase)));rot('head',(1.4*sin(phase+.4),0,-1*sin(phase)))
 elif kind in ['Walk','Run']:
  run=kind=='Run';amp=43 if run else 26
  rig.pose.bones['hips'].location.y=(.035 if run else .018)*(1-cos(phase*2));rot('chest',(9 if run else 3,0,3*sin(phase)))
  for s,side in [(1,'L'),(-1,'R')]:
   p=phase+(0 if s==1 else pi);a=sin(p)
   rot('thigh.'+side,(-amp*a,0,0));rot('shin.'+side,((68 if run else 42)*max(0,-a),0,0));rot('foot.'+side,(-12*max(0,a),0,0))
   rot('upper_arm.'+side,((30 if run else 18)*a,s*76,0));rot('forearm.'+side,(-65 if run else -18,0,0))
 elif kind=='Conversation':
  rot('head',(4*sin(phase*2),0,6*sin(phase)));rot('chest',(0,0,3*sin(phase)))
  for s,side in [(1,'L'),(-1,'R')]:
   rot('upper_arm.'+side,(-15-10*sin(phase+s),s*(52+8*sin(phase)),0));rot('forearm.'+side,(-40-18*sin(phase+s),0,s*-12));rot('hand.'+side,(0,12*sin(phase*2+s),0))
 elif kind in ['Sit_Down','Seated_Idle']:
  a=(t*t*(3-2*t)) if kind=='Sit_Down' else 1
  rig.pose.bones['root'].location.y=-.43*a;rig.pose.bones['root'].location.z=-.14*a
  rot('chest',(12*sin(pi*t) if kind=='Sit_Down' else 1.5*sin(phase),0,0))
  for s,side in [(1,'L'),(-1,'R')]:
   rot('thigh.'+side,(-88*a,0,0));rot('shin.'+side,(88*a,0,0));rot('upper_arm.'+side,(-18*a,s*(76-10*a),0));rot('forearm.'+side,(-55*a,0,0))
scene.render.fps=24
rig.animation_data_create()
for kind,end in [('Idle',73),('Walk',25),('Run',19),('Conversation',97),('Sit_Down',37),('Seated_Idle',73)]:
 action=bpy.data.actions.new(kind);action.use_fake_user=True;rig.animation_data.action=action
 for frame in range(1,end+1):
  pose(kind,(frame-1)/(end-1))
  for b in rig.pose.bones:b.keyframe_insert('location',frame=frame,group=b.name);b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
 action['description']='Transition to sitting' if kind=='Sit_Down' else 'Looping in-place animation'
 action['fps']=24
for name in ['Idle','Walk','Run','Conversation','Sit_Down','Seated_Idle']:
 action=bpy.data.actions[name];rig.animation_data.action=action
 for f in range(int(action.frame_range[0]),int(action.frame_range[1])+1):
  scene.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());z=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
  rig.pose.bones['root'].location.y+=.012-z
  rig.pose.bones['root'].keyframe_insert('location',frame=f,group='root')
rig.animation_data.action=None;pose('T_Pose',0)
for b in rig.pose.bones:b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
scene.frame_start=1;scene.frame_end=97;scene.frame_set(1)
rig['Animation clips']='Idle, Walk, Run, Conversation, Sit_Down, Seated_Idle';rig['Usage']='Rest pose is T-pose. Select rig and choose an action in Action Editor. Walk/Run are in-place. Character faces -Y, Z up.'
# Presentation stage.
stage=bpy.data.collections.new('Studio');scene.collection.children.link(stage)
def stageobj(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 stage.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(material('Backdrop',(.055,.072,.083)));stageobj(floor)
def camera(name,loc,target):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=3.05;stageobj(o);return o
scene.camera=camera('Camera • three quarter',(3,-7,3),(0,0,1.30));camera('Camera • front',(0,-8,1.35),(0,0,1.35));camera('Camera • side',(8,0,1.35),(0,0,1.35));camera('Camera • back',(0,8,1.35),(0,0,1.35))
for name,loc,power,size in [('Key',(-3,-4,6),650,4),('Fill',(4,-2,3.5),400,3),('Rim',(1,3,5),850,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler();stageobj(o)
scene.world.color=(.22,.22,.22);scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_distance=4.7;area.spaces.active.region_3d.view_location=(0,0,1.3)
  area.spaces.active.region_3d.view_rotation=Quaternion((1,0,0),math.radians(90));area.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/BaldCharacter.blend')
print('CREATED',len(mesh.data.vertices),'vertices;',len(data.bones),'bones; actions:',[a.name for a in bpy.data.actions if a.name in ['Idle','Walk','Run','Conversation','Sit_Down','Seated_Idle']])
