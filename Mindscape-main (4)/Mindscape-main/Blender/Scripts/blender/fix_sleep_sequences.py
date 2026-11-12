"""Repair the existing dorm scene in place. Run inside Blender through MCP.

World-space contact targets are baked to ordinary local bone transforms; no
runtime IK constraints are required. Character placement stays on the object,
and the three reusable clips contain only pose-bone animation.
"""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path('/Users/arieljerickogacilo/mindscape-3d')
SCALE = .78
FPS = 30
NAMES = ('Walk_To_Bed_And_Sleep', 'Sleeping_Idle', 'Wake_Up_And_Get_Out_Of_Bed')


def smooth(t):
    t = max(0., min(1., t))
    return t*t*t*(t*(t*6-15)+10)


def mix(a, b, t):
    if isinstance(a, (tuple, list, Vector)):
        return Vector(a).lerp(Vector(b), t)
    return a+(b-a)*t


def rz(a):
    return Matrix.Rotation(a, 3, 'Z')


def rx(a):
    return Matrix.Rotation(math.radians(a), 3, 'X')


def pose(hip, yaw, pitch, feet, arm=0., bed=0., breath=0., stir=0., swing=0.):
    return dict(hip=Vector(hip), yaw=yaw, pitch=pitch,
                feet=[Vector(v) for v in feet], arm=arm, bed=bed,
                breath=breath, stir=stir, swing=swing)


def blend(a, b, t):
    t = smooth(t)
    out={k:mix(a[k], b[k], t) for k in a if k!='feet'}
    out['feet']=[mix(x,y,t) for x,y in zip(a['feet'],b['feet'])]
    return out


def walk(f):
    # Alternating planted soles, followed by a final closing step.
    start=-1.6
    targets=[(0,-1.35),(1,-1.1),(0,-.85),(1,-.6),(0,-.35),(1,-.10),(0,-.10)]
    phase=max(0.,min(7.,(f-1)/12.))
    idx=min(6,int(phase)); t=phase-idx
    ys=[start,start]
    for side,target in targets[:idx]: ys[side]=target
    side,target=targets[idx]
    ys[side]=mix(ys[side],target,smooth(t))
    feet=[Vector((-1.05-.16*SCALE,ys[0],.176*SCALE)),
          Vector((-1.05+.16*SCALE,ys[1],.176*SCALE))]
    feet[side].z+=.065*math.sin(math.pi*t)**2
    hip=(-1.05,sum(ys)*.5,.710-.009*math.sin(math.pi*t)**2)
    return pose(hip,math.pi,2.,feet,swing=math.sin(math.pi*phase)*.045)


STAND=pose((-.90,-.10,.730),1.5*math.pi,0.,
           [(-.89,-.10-.16*SCALE,.176*SCALE),(-.89,-.10+.16*SCALE,.176*SCALE)],arm=.25)
SIT=pose((-.55,-.10,.610),1.5*math.pi,-3.,
         STAND['feet'],arm=1.)
TUCK=pose((-.38,-.10,.725),1.5*math.pi,-24.,
          [(-.77,-.225,.83),(-.77,.025,.83)],arm=1.,bed=.55)
LONG_SIT=pose((0.,-.12,.72),2*math.pi,-40.,
              [(.16*SCALE,-.70,.68),(-.16*SCALE,-.70,.68)],arm=1.,bed=1.)
SLEEP=pose((0.,-.12,.72),2*math.pi,-78.,
           [(.16*SCALE,-.70,.68),(-.16*SCALE,-.70,.68)],arm=2.,bed=1.)


def enter(f):
    if f<=85:return walk(f)
    stops=[(85,walk(85)),(115,STAND),(150,SIT),(175,TUCK),(210,LONG_SIT),(240,SLEEP)]
    for (fa,a),(fb,b) in zip(stops,stops[1:]):
        if f<=fb:
            t=(f-fa)/(fb-fa);p=blend(a,b,t)
            if fb==115:
                p['hip'].z-=.040*math.sin(math.pi*t)**2
                # Two small steps turn the feet instead of twisting flat soles.
                for i in range(2):
                    u=max(0.,min(1.,t*2-i))
                    p['feet'][i]=mix(a['feet'][i],b['feet'][i],smooth(u))
                    p['feet'][i].z+=.025*math.sin(math.pi*u)**2
            return p
    return SLEEP


def sleep(f):
    p=blend(SLEEP,SLEEP,0.)
    # Matched end pose and zero breathing velocity at the loop seam.
    p['breath']=.5-.5*math.cos(2*math.pi*(f-1)/120.)
    return p


def wake(f):
    stir=blend(SLEEP,SLEEP,0.)
    stir['stir']=1.
    alert=blend(LONG_SIT,LONG_SIT,0.)
    alert['pitch']=-25.
    lean=blend(SIT,SIT,0.)
    lean['hip']=Vector((-.65,-.10,.64));lean['pitch']=18.
    stand=blend(STAND,STAND,0.);stand['arm']=0.
    stops=[(1,SLEEP),(25,stir),(65,alert),(95,TUCK),(125,SIT),(143,lean),(170,stand),(180,stand)]
    for (fa,a),(fb,b) in zip(stops,stops[1:]):
        if f<=fb:return blend(a,b,(f-fa)/(fb-fa))
    return stand


class Solver:
    def __init__(self, rig):
        self.rig=rig
        self.bones=list(rig.data.bones)
        self.rest={b.name:b.matrix_local.copy() for b in self.bones}
        self.m={}
        self.max_reach_error=0.
        self.previous={}

    def neutral(self,name):
        b=self.rig.data.bones[name]
        return self.m[b.parent.name] @ self.rest[b.parent.name].inverted() @ self.rest[name] if b.parent else self.rest[name].copy()

    def orient(self,name,rot):
        m=(rot@self.rest[name].to_3x3()).to_4x4()
        m.translation=self.neutral(name).translation
        self.m[name]=m

    def aim(self,name,head,tail):
        b=self.rig.data.bones[name]
        q=(b.tail_local-b.head_local).normalized().rotation_difference((tail-head).normalized())
        m=(q.to_matrix()@self.rest[name].to_3x3()).to_4x4()
        m.translation=head
        self.m[name]=m

    def limb(self,a,b,c,target,pole,foot_rotation=None):
        start=self.neutral(a).translation
        rest_a=self.rig.data.bones[a];rest_b=self.rig.data.bones[b]
        l1=rest_a.length;l2=rest_b.length
        target=Vector(target)/SCALE
        delta=target-start;actual=delta.length
        self.max_reach_error=max(self.max_reach_error,max(0.,actual-l1-l2)*SCALE)
        dist=min(l1+l2-.00001,max(abs(l1-l2)+.00001,actual))
        axis=delta.normalized()
        pole=Vector(pole);bend=pole-axis*pole.dot(axis)
        if bend.length<1e-6:bend=axis.cross(Vector((1,0,0)))
        bend.normalize()
        along=(l1*l1-l2*l2+dist*dist)/(2*dist)
        elbow=start+axis*along+bend*math.sqrt(max(0.,l1*l1-along*along))
        end=start+axis*dist
        self.aim(a,start,elbow);self.aim(b,elbow,end)
        if foot_rotation is None:
            self.aim(c,end,end+(end-elbow).normalized()*.3)
        else:
            m=(foot_rotation@self.rest[c].to_3x3()).to_4x4();m.translation=end;self.m[c]=m

    def apply(self,p):
        self.m={}
        heading=rz(p['yaw'])
        # Translate the origin so the hips, rather than the foot-level root,
        # rotate about their physical support point.
        m=(heading@self.rest['root'].to_3x3()).to_4x4()
        m.translation=p['hip']/SCALE-heading@self.rest['hips'].translation
        self.m['root']=m
        self.orient('hips',heading@rx(p['pitch']))
        self.orient('chest',heading@rx(p['pitch']+p['bed']*2.+p['breath']*.7))
        self.orient('neck',heading@rx(p['pitch']+p['bed']*5.+p['stir']*5.))
        self.orient('head',heading@rx(p['pitch']+p['bed']*7.+p['stir']*10.))
        front=heading@Vector((0,-1,0))
        # Knees bend forward when standing and upward when on the mattress.
        leg_pole=(front*(1-p['bed'])+Vector((0,0,1))*p['bed']).normalized()
        for side,target in zip(('L','R'),p['feet']):
            self.limb('thigh.'+side,'shin.'+side,'foot.'+side,target,leg_pole,
                      heading@rx(-78*p['bed']))
        for side,sign in [('L',1),('R',-1)]:
            hip=p['hip']
            relaxed=hip+heading@Vector((sign*.28,-.015,-.005))
            brace=hip+heading@Vector((sign*.30,.13,.055))
            rest=hip+heading@Vector((sign*.14,.075,.21))
            if p['arm']<=1:wrist=relaxed.lerp(brace,p['arm'])
            else:wrist=brace.lerp(rest,p['arm']-1)
            wrist+=heading@Vector((0,sign*p['swing'],0))
            # Subtle preparatory stretch before pushing upright.
            wrist+=heading@Vector((sign*.05*p['stir'],.035*p['stir'],.04*p['stir']))
            pole=heading@Vector((sign, -.2, .05))
            self.limb('upper_arm.'+side,'forearm.'+side,'hand.'+side,wrist,pole)
        for b in self.bones:
            if b.name not in self.m:self.m[b.name]=self.neutral(b.name)
            desired=self.m[b.name]
            args=dict(parent_matrix=self.m[b.parent.name],parent_matrix_local=self.rest[b.parent.name]) if b.parent else {}
            basis=b.convert_local_to_pose(desired,self.rest[b.name],invert=True,**args)
            pb=self.rig.pose.bones[b.name]
            loc,q,scale=basis.decompose()
            if b.name in self.previous and q.dot(self.previous[b.name])<0:q.negate()
            self.previous[b.name]=q.copy()
            pb.rotation_mode='QUATERNION';pb.location=loc;pb.rotation_quaternion=q;pb.scale=(1,1,1)


def curves(action):
    return [f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]


def bake(rig,name,length,fn):
    old=bpy.data.actions.get(name)
    if old:
        if 'contact_solver_max_reach_error_m' in old:
            bpy.data.actions.remove(old)
        else:
            old.name=name+'__BeforeContactFix'
            old.use_fake_user=True
    action=bpy.data.actions.new(name);action.use_fake_user=True
    rig.animation_data.action=action
    solver=Solver(rig)
    for f in range(1,length+1):
        solver.apply(fn(f))
        for pb in rig.pose.bones:
            pb.keyframe_insert('location',frame=f,group=pb.name)
            pb.keyframe_insert('rotation_quaternion',frame=f,group=pb.name)
            pb.keyframe_insert('scale',frame=f,group=pb.name)
    for fc in curves(action):
        for kp in fc.keyframe_points:kp.interpolation='LINEAR'
    action['contact_solver_max_reach_error_m']=solver.max_reach_error
    action['fps']=FPS
    action['loop']=name=='Sleeping_Idle'
    print(name, 'frames', length, 'reach error',solver.max_reach_error)
    return action


def track(rig,name,action,start,end=None,repeat=1.):
    t=rig.animation_data.nla_tracks.new();t.name=name
    strip=t.strips.new(name,start,action)
    strip.blend_type='REPLACE';strip.extrapolation='NOTHING'
    strip.repeat=repeat
    if end is not None:strip.frame_end=end
    return t


def eyelids(obj,npc=False):
    """A reversible morph of just the separate eye and catchlight vertices."""
    if not obj.data.shape_keys:obj.shape_key_add(name='Basis')
    keys=obj.data.shape_keys
    closed=keys.key_blocks.get('Sleep_Eyes_Closed') or obj.shape_key_add(name='Sleep_Eyes_Closed')
    basis=keys.key_blocks[0]
    for v,src in zip(closed.data,basis.data):v.co=src.co
    for mi in (3,4):
        ids={i for poly in obj.data.polygons if poly.material_index==mi for i in poly.vertices}
        for i in ids:
            src=basis.data[i].co
            closed.data[i].co.z=2.0326+(src.z-2.0326)*.065
            if mi==4:closed.data[i].co.y=src.y+.08
    keys.animation_data_create();keys.animation_data.action=None
    for t in list(keys.animation_data.nla_tracks):
        if t.name in NAMES or t.name=='NPC_Sleeping_Idle':keys.animation_data.nla_tracks.remove(t)
    configs=[('NPC_Sleeping_Idle',121,1,lambda f:1.)] if npc else [
        (NAMES[0],240,1,lambda f:smooth((f-210)/26)),
        (NAMES[1],121,240,lambda f:1.),
        (NAMES[2],180,360,lambda f:1-smooth((f-8)/18))]
    for name,length,start,fn in configs:
        aname=name+'_Eyes'
        old=bpy.data.actions.get(aname)
        if old:bpy.data.actions.remove(old)
        a=bpy.data.actions.new(aname);a.use_fake_user=True;keys.animation_data.action=a
        for f in range(1,length+1):
            closed.value=fn(f);closed.keyframe_insert('value',frame=f)
        for fc in curves(a):
            for k in fc.keyframe_points:k.interpolation='LINEAR'
        keys.animation_data.action=None
        track(keys,name,a,start,repeat=5. if npc else 1.)


def repair():
    scene=bpy.context.scene
    player=bpy.data.objects['Player_BaldCharacter_Rig'];npc=bpy.data.objects['NPC_Maya_Rig']
    for rig,bed in [(player,'Scenario2_PlayerBed'),(npc,'Scenario1_BunkBed')]:
        rig.animation_data_create();rig.animation_data.action=None
        for t in list(rig.animation_data.nla_tracks):
            if t.name.startswith(('01 Walk','02 Sleeping','03 Wake','Sleeping —')):
                rig.animation_data.nla_tracks.remove(t)
        # Preserve the unrelated imported tracks, but isolate this preview.
        for t in rig.animation_data.nla_tracks:
            t.mute=True;t.is_solo=False
        rig.location=bpy.data.objects[bed].location
        rig.rotation_euler=(0,0,0);rig.scale=(SCALE,)*3
    # This bed was imported facing the opposite way from the pillow and clips.
    bed=bpy.data.objects['Scenario2_PlayerBed']
    bed.rotation_mode='XYZ';bed.rotation_euler=(0,0,math.pi)
    # Fold the two extra duvet blocks at the foot so they do not intersect legs.
    for name in ('Bed_Blanket','Bed_Blanket.001'):
        blanket=bpy.data.objects[name]
        blanket.location.y=-.88;blanket.location.z=.575
        blanket.dimensions=(.92,.20,.05)
    for rig in (player,npc):
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    actions=[bake(player,NAMES[0],240,enter),bake(player,NAMES[1],121,sleep),bake(player,NAMES[2],180,wake)]
    # Same rest-pose rig, independently baked to its actual bone bases.
    npc_action=bake(npc,'NPC_Sleeping_Idle',121,sleep)
    eyelids(bpy.data.objects['BaldCharacter_Mesh'])
    eyelids(bpy.data.objects['Mesh_NPC_01_Maya'],npc=True)
    for rig in (player,npc):rig.animation_data.action=None
    track(player,'01 Walk to bed and settle',actions[0],1)
    track(player,'02 Sleeping breath loop',actions[1],240)
    track(player,'03 Wake and get out of bed',actions[2],360)
    track(npc,'Sleeping — continuous',npc_action,1,repeat=5.)
    for rig in (player,npc):
        rig['sleep_clip_space']='Bed center, head +Y, feet -Y, approach at left side (-X)'
        rig['sleep_preview_scale']=SCALE
    scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=539
    labels={1:'WALK • planted steps',85:'TURN toward room',115:'SIT on edge',150:'LIFT feet',175:'SWING onto bed',210:'RECLINE',240:'SLEEP • seamless breath',360:'WAKE',424:'SIT UP',454:'LEGS over edge',484:'FEET planted',502:'STAND',530:'UPRIGHT'}
    for m in list(scene.timeline_markers):
        if m.name in labels.values():scene.timeline_markers.remove(m)
    for f,label in labels.items():
        m=scene.timeline_markers.new(label);m.frame=f
    scene.frame_set(280)
    bpy.context.view_layer.objects.active=player
    for o in scene.objects:o.select_set(False)
    player.select_set(True)
    bpy.context.view_layer.update()
    print('Sleep repair complete; preview timeline 1–539 at 30 FPS.')


if __name__=='__main__':repair()
