"""Create seamless, in-place T_Pose / Idle / Walk / Run skeletal clips."""
import bpy, math, json
from mathutils import Matrix, Vector
OUT='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/character_ragdoll'
scene=bpy.context.scene
rig=bpy.data.objects['Ragdoll_Rig']
body=bpy.data.objects['Ragdoll_Body']
arm=rig.data
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
rig.animation_data_create()
def reset():
    for p in rig.pose.bones:
        p.location=(0,0,0)
        p.rotation_mode='QUATERNION'
        p.rotation_quaternion=(1,0,0,0)
        p.scale=(1,1,1)
def rot(name,mat):
    basis=arm.bones[name].matrix_local.to_3x3()
    rig.pose.bones[name].rotation_quaternion=(basis.inverted()@mat@basis).to_quaternion()
def loc(name,xyz):
    basis=arm.bones[name].matrix_local.to_3x3()
    rig.pose.bones[name].location=basis.inverted()@Vector(xyz)
def rx(a): return Matrix.Rotation(a,3,'X')
def ry(a): return Matrix.Rotation(a,3,'Y')
def rz(a): return Matrix.Rotation(a,3,'Z')
constraints=[]
for side in ('L','R'):
    ik=rig.pose.bones['Shin.'+side].constraints.new('IK')
    ik.name='Foot placement (baked)'
    ik.target=rig
    ik.subtarget='FootTarget.'+side
    ik.pole_target=rig
    ik.pole_subtarget='KneePole.'+side
    ik.chain_count=2
    ik.use_stretch=False
    constraints.append(ik)
    copy=rig.pose.bones['Foot.'+side].constraints.new('COPY_ROTATION')
    copy.target=rig
    copy.subtarget='FootTarget.'+side
    copy.target_space='WORLD'
    copy.owner_space='WORLD'
    constraints.append(copy)
# Calibrate pole axes against a bent standing stance.
reset()
loc('Hips',(0,0,-.065))
for side in ('L','R'):
    ik=rig.pose.bones['Shin.'+side].constraints[0]
    hipx=arm.bones['Thigh.'+side].head_local.x
    scores=[]
    for a in (-math.pi,-math.pi/2,0,math.pi/2):
        ik.pole_angle=a
        bpy.context.view_layer.update()
        knee=rig.pose.bones['Shin.'+side].head
        scores.append(((knee.x-hipx)**2+max(0,knee.y+.05)**2,a))
    ik.pole_angle=min(scores)[1]

clips={}
for label,period in [('T_Pose',1),('Idle',120),('Walk',36),('Run',24)]:
    source=bpy.data.actions.new('_Source_'+label)
    rig.animation_data.action=source
    for c in constraints: c.influence=0 if label=='T_Pose' else 1
    for f in range(1,period+2):
        scene.frame_set(f)
        reset()
        q=2*math.pi*(f-1)/period
        if label=='Idle':
            # Planted feet, relaxed knees, breathing chest, slow asymmetrical sway.
            loc('Hips',(.012*math.sin(q),.004*math.sin(q),-.045+.006*math.sin(2*q)))
            rot('Hips',rz(.015*math.sin(q)))
            rot('Spine',ry(.014*math.sin(q+.4))@rx(.010*math.sin(2*q)))
            rot('Chest',rx(.014*math.sin(2*q-.3))@rz(-.012*math.sin(q)))
            rig.pose.bones['Chest'].scale=(1+.012*math.sin(2*q),1+.008*math.sin(2*q),1+.018*math.sin(2*q))
            rot('Head',ry(-.014*math.sin(q+.6))@rz(.018*math.sin(q-.6)))
            for s,side in [(1,'L'),(-1,'R')]:
                rot('UpperArm.'+side,rx(.025*math.sin(q+s*.45))@ry(s*1.30))
                rot('Forearm.'+side,rz(-s*(.10+.018*math.sin(q+s))))
                rot('Hand.'+side,ry(s*.025*math.sin(q+.8)))
        elif label in ('Walk','Run'):
            run=label=='Run'
            stride=.94 if run else .64
            stance=.38 if run else .60
            bob=(.05 if run else .018)*math.cos(2*q)
            loc('Hips',((.022 if run else .018)*math.sin(q),0,(-.11 if run else -.065)+bob))
            rot('Hips',rz(.045*math.sin(q)))
            rot('Spine',rx(-.11 if run else -.025)@ry(.022*math.sin(q)))
            rot('Chest',rz(-.065*math.sin(q))@rx(-.035 if run else 0))
            rot('Head',rx(.09 if run else .02)@rz(.022*math.sin(q)))
            for s,side in [(1,'L'),(-1,'R')]:
                t=((f-1)/period+(0 if s==1 else .5))%1
                if t < stance:
                    u=t/stance
                    y=-stride/2+stride*u
                    lift=0
                    pitch=0
                else:
                    u=(t-stance)/(1-stance)
                    # Smooth return of the lifted foot; planted phase moves at constant speed.
                    ease=u*u*(3-2*u)
                    y=stride/2-stride*ease
                    lift=(.36 if run else .16)*math.sin(math.pi*u)**2
                    pitch=(-.35 if run else -.14)*math.sin(math.pi*u)
                loc('FootTarget.'+side,(0,y,lift))
                rot('FootTarget.'+side,rx(pitch))
                swing=(.65 if run else .34)*math.cos(2*math.pi*t)
                rot('UpperArm.'+side,rx(swing)@ry(s*1.32))
                rot('Forearm.'+side,rz(-s*((1.05 if run else .22)+.10*math.sin(2*math.pi*t))))
                rot('Hand.'+side,rz(-s*.06))
        for p in rig.pose.bones:
            p.keyframe_insert('location',frame=f,group=p.name)
            p.keyframe_insert('rotation_quaternion',frame=f,group=p.name)
            p.keyframe_insert('scale',frame=f,group=p.name)
    # Bake evaluated IK into portable local bone transforms.
    bpy.ops.nla.bake(frame_start=1,frame_end=period+1,step=1,only_selected=False,
        visual_keying=True,clear_constraints=False,clear_parents=False,
        use_current_action=False,clean_curves=False,bake_types={'POSE'})
    action=rig.animation_data.action
    action.name=label
    action.use_fake_user=True
    action['loop']=True
    action['duration_seconds']=period/30
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points: key.interpolation='LINEAR'
                    fc.modifiers.new('CYCLES')
    clips[label]=action
    rig.animation_data.action=None
    bpy.data.actions.remove(source)
for p in rig.pose.bones:
    for c in list(p.constraints): p.constraints.remove(c)

# Keep every sole above the floor after skin deformation, with a small run flight phase.
# Only translate the root; IK-baked relative joint motion remains intact.
ground_report={}
for label,action in clips.items():
    rig.animation_data.action=action
    period=int(action.frame_range[1])-1
    heights=[]
    for f in range(1,period+2):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get()
        evaluated=body.evaluated_get(deps)
        lowest=min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices)
        flight=.025*max(0,-math.cos(4*math.pi*(f-1)/period)) if label=='Run' else 0
        loc('Root',(0,0,-lowest+flight))
        rig.pose.bones['Root'].keyframe_insert('location',frame=f,group='Root')
        heights.append(flight)
    ground_report[label]={'frames':[1,period+1],'seconds':period/30,'max_flight':max(heights)}

rig['animation_notes']='Four baked, in-place actions at 30 fps. T_Pose is the rest pose. Idle: standing breathing/weight shift, 4 s. Walk: 1.2 s. Run: 0.8 s. Change Action in the Dope Sheet Action Editor.'
rig.animation_data.action=clips['Idle']
scene.frame_start=1
scene.frame_end=121
scene.frame_set(1)
readme=bpy.data.texts.new('README - Ragdoll Character')
readme.write(rig['animation_notes']+'\n\nReference: Models/character_ragdoll.png\nOne continuous smooth mesh, 19 deform bones, 24 total bones.\nFront faces -Y, Z up. Reference height about 3.59 Blender units.\nStudio collection is presentation only and omitted from exports.\nFBX is suitable for Unity Generic rigs; set clip Loop Time on Idle, Walk, Run.\nProcedural fabric grain is Blender-only; exports retain the base material.\n')
with open(OUT+'/animation-report.json','w') as f: json.dump(ground_report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/character_ragdoll.blend')
print(json.dumps(ground_report))
