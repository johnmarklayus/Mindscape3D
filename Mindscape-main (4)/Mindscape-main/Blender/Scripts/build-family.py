"""Build the family reference as four skinned characters through Blender MCP."""
import bpy
import math
import os
from mathutils import Vector, Matrix

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/family_set'
os.makedirs(OUT, exist_ok=True)
scene = bpy.data.scenes.new('Family Set')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.render.fps = 30

def material(name, color, roughness=.72):
    m = bpy.data.materials.new('Family / ' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    return m

skin = material('warm skin', (.72,.43,.23))
inner_ear = material('ear and cheeks', (.72,.29,.18))
hair = material('chestnut hair', (.065,.032,.022))
black_hair = material('boy charcoal hair', (.025,.021,.024))
eye = material('espresso eyes', (.013,.009,.008), .3)
white = material('ivory', (.9,.87,.78))
smile = material('smile', (.38,.095,.052))
yellow = material('mother cardigan', (.88,.54,.08))
coral = material('mother coral tee', (.75,.18,.12))
navy = material('mother trousers', (.047,.069,.11))
brown = material('mother flats', (.13,.059,.029))
green = material('father overshirt', (.075,.20,.12))
denim = material('father denim', (.08,.18,.31))
blue = material('boy hoodie', (.025,.20,.8))
blue_trim = material('boy cuffs', (.018,.11,.46))
charcoal = material('charcoal trousers', (.048,.049,.059))
purple = material('girl sweater', (.46,.23,.69))
purple_trim = material('girl cuffs', (.33,.13,.53))
teal = material('girl shorts', (.025,.38,.43))

members = []
parts = []
collection = None
prefix = ''

def finish(o, name, mat, bone):
    o.name = prefix + '_' + name
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)
    o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for p in o.data.polygons: p.use_smooth = True
    o['bind'] = bone
    parts.append(o)
    return o

def oval(name, pos, scale, mat, bone='Head', rotation=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=pos)
    o = bpy.context.object
    o.scale, o.rotation_euler = scale, rotation
    return finish(o, name, mat, bone)

def box(name, pos, scale, mat, bone, bevel=.07):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = o.modifiers.new('Soft tailored edges', 'BEVEL')
    mod.width, mod.segments = bevel, 4
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o, name, mat, bone)

def tube(name, points, radius, mat, bone):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth, curve.bevel_resolution = radius, 3
    s = curve.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for b, p in zip(s.bezier_points, points):
        b.co = p
        b.handle_left_type = b.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH')
    return finish(bpy.context.object, name, mat, bone)

def limb(name, start, end, r1, r2, mat, bone):
    a,b = Vector(start),Vector(end)
    direction = b-a
    q = direction.to_track_quat('Z','Y')
    verts, faces = [], []
    for i in range(13):
        t = i/12
        r = r1*(1-t)+r2*t
        for j in range(20):
            angle = 2*math.pi*j/20
            p = a + direction*t + q @ Vector((r*math.cos(angle), r*math.sin(angle), 0))
            verts.append(p)
    faces.append(tuple(reversed(range(20))))
    for i in range(12):
        for j in range(20):
            k = i*20+j
            faces.append((k,i*20+(j+1)%20,(i+1)*20+(j+1)%20,k+20))
    faces.append(tuple(range(240,260)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o = bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    return finish(o,name,mat,bone)

def make_member(name, scale, offset):
    global parts, collection, prefix
    prefix, parts = name, []
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    mother, father, boy, girl = [name==x for x in ('Mother','Father','Boy','Girl')]
    cloth = yellow if mother else green if father else blue if boy else purple
    trim = cloth if mother or father else blue_trim if boy else purple_trim
    pants = navy if mother else denim if father else charcoal
    hair_mat = black_hair if boy else hair
    width = .39 if father else .34
    box('torso', (0,0,1.96), (width*2,.43,.86), coral if mother else white if father else cloth, 'Chest', .11)
    box('hips',(0,.01,1.47),(.64,.4,.29),pants,'Hips',.10)
    if mother or father:
        box('jacket back',(0,.14,1.96),(width*2+.035,.20,.88),cloth,'Chest',.06)
        for s in (-1,1):
            box('jacket panel',(s*.235,-.16,1.94),(.245,.16,.88),cloth,'Chest',.045)
            if father:
                box('breast pocket',(s*.25,-.256,2.11),(.15,.024,.18),green,'Chest',.025)
                tube('collar',[(s*.11,-.26,2.38),(s*.18,-.27,2.25),(s*.24,-.22,2.34)],.032,cloth,'Chest')
        if father:
            for z in (1.66,1.83,2.0,2.17): oval('button',(-.125,-.251,z),(.016,.01,.016),green,'Chest')
    else:
        box('waist ribbing',(0,-.008,1.56),(.69,.45,.10),trim,'Chest',.04)
        if boy:
            oval('hood',(0,.205,2.3),(.31,.18,.25),blue,'Chest')
            box('kangaroo pocket',(0,-.23,1.77),(.43,.065,.21),blue,'Chest',.045)
            for s in (-1,1): tube('hood cord',[(s*.10,-.24,2.32),(s*.105,-.25,2.17),(s*.11,-.25,2.05)],.012,white,'Chest')
        else:
            oval('collar',(0,0,2.34),(.18,.18,.06),white,'Chest')
    oval('neck',(0,0,2.43),(.135,.135,.18),skin,'Neck')
    oval('face',(0,-.018,2.9),(.405,.335,.445),skin)
    for s in (-1,1):
        oval('ear',(s*.395,-.004,2.86),(.085,.063,.112),skin)
        oval('ear inset',(s*.425,-.05,2.86),(.035,.016,.058),inner_ear)
        oval('eye',(s*.147,-.327,2.928),(.037,.022,.067),eye)
        oval('eye catchlight',(s*.147-.009,-.347,2.95),(.009,.006,.013),white)
        tube('eyebrow',[(s*.10,-.325,3.052),(s*.145,-.331,3.069),(s*.191,-.31,3.057)],.015,hair_mat,'Head')
        oval('cheek',(s*.226,-.297,2.801),(.046,.008,.023),inner_ear)
    oval('nose',(0,-.359,2.827),(.038,.045,.046),skin)
    tube('smile',[(-.066,-.332,2.752),(0,-.35,2.733),(.066,-.332,2.752)],.009,smile,'Head')
    # Hair stays behind the face; shaped locks establish each reference silhouette.
    oval('hair crown',(0,.058,3.116),(.418,.315,.30),hair_mat)
    oval('hair back',(0,.184,2.99),(.37,.205,.34),hair_mat)
    if mother:
        for s in (-1,1):
            for i in range(3):
                oval('bob lock',(s*(.30+.035*i),.08+.055*i,2.82),(.15,.19,.33),hair_mat,rotation=(0,s*-.20,0))
        for i in range(3): oval('swept fringe',(-.24+i*.12,-.193,3.175+i*.025),(.15,.15,.255-i*.024),hair_mat,rotation=(0,.65,0))
    elif father:
        for i in range(3): oval('quiff',(-.20+i*.145,-.11,3.25+i*.02),(.17,.205,.14),hair_mat,rotation=(0,-.24,0))
        for s in (-1,1):
            oval('sideburn',(s*.354,-.065,2.96),(.045,.13,.17),hair_mat)
            tube('beard edge',[(s*.325,-.16,2.84),(s*.275,-.25,2.68),(s*.12,-.29,2.60),(0,-.31,2.61)],.056,hair_mat,'Head')
            oval('moustache',(s*.065,-.338,2.754),(.077,.027,.025),hair_mat)
    elif boy:
        for i in range(7):
            x = -.32+i*.103
            oval('tousled fringe',(x,-.205,3.13+.035*math.cos(i*2)),(.10,.13,.20),hair_mat,rotation=(0,.35+.28*math.sin(i),0))
        for i in range(5):
            oval('crown tuft',(-.28+i*.14,.025,3.35+.03*math.sin(i)),(.12,.14,.10),hair_mat,rotation=(0,-.45+i*.20,0))
    else:
        for i in range(3): oval('side swept fringe',(-.23+i*.115,-.205,3.15+i*.025),(.12,.12,.23),hair_mat,rotation=(0,.62,0))
        oval('ponytail tie',(0,.37,2.83),(.10,.10,.09),purple_trim)
        oval('ponytail',(0,.43,2.59),(.16,.15,.28),hair_mat,rotation=(-.20,0,0))
        for s in (-1,1): tube('temple strand',[(s*.32,-.16,3.12),(s*.365,-.16,2.92),(s*.34,-.12,2.69)],.04,hair_mat,'Head')
    for s, side in ((1,'L'),(-1,'R')):
        upper, fore, hand = 'UpperArm.'+side,'Forearm.'+side,'Hand.'+side
        thigh, shin, foot = 'Thigh.'+side,'Shin.'+side,'Foot.'+side
        limb('arm',(s*.31,0,2.28),(s*1.31,0,2.28),.13,.082,skin,'ARM.'+side)
        end = .87 if father else 1.20
        limb('sleeve',(s*.29,0,2.28),(s*end,0,2.28),.177,.12,cloth,'ARM.'+side)
        limb('cuff',(s*(end-.06),0,2.28),(s*(end+.015),0,2.28),.128,.128,trim,'ARM.'+side)
        oval('hand',(s*1.37,-.008,2.28),(.145,.095,.105),skin,hand)
        oval('thumb',(s*1.32,-.07,2.24),(.060,.052,.065),skin,hand)
        limb('leg',(s*.185,0,1.47),(s*.205,0,.23),.155,.105,pants if mother or father or girl else skin,'LEG.'+side)
        if boy or girl:
            limb('shorts',(s*.185,0,1.45),(s*.20,0,1.03),.175,.17,charcoal if boy else teal,thigh)
            limb('socks',(s*.205,0,.21),(s*.205,0,.40),.109,.107,white,shin)
        else:
            limb('trouser hem',(s*.205,0,.25),(s*.205,0,.33),.114,.116,pants,shin)
        shoe_mat = brown if mother else charcoal if father else blue if boy else purple
        box('sole',(s*.205,-.088,.052),(.28,.46,.10),brown if mother else white,foot,.042)
        oval('shoe',(s*.205,-.075,.134),(.137,.22,.103),shoe_mat,foot)
        if not mother:
            oval('toe cap',(s*.205,-.222,.117),(.133,.087,.075),white,foot)
            for y in (-.11,-.06,-.01): tube('lace',[(s*.205-.077,y,.211),(s*.205,y-.013,.232),(s*.205+.077,y,.211)],.011,white,foot)
    arm = bpy.data.armatures.new(name+'_Skeleton')
    rig = bpy.data.objects.new(name+'_Rig',arm)
    collection.objects.link(rig)
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    def bone(n,h,t,parent=None):
        b = arm.edit_bones.new(n)
        b.head,b.tail = h,t
        if parent: b.parent = arm.edit_bones[parent]
    bone('Root',(0,0,0),(0,0,.2))
    bone('Hips',(0,0,1.45),(0,0,1.65),'Root')
    bone('Spine',(0,0,1.65),(0,0,1.99),'Hips')
    bone('Chest',(0,0,1.99),(0,0,2.31),'Spine')
    bone('Neck',(0,0,2.31),(0,0,2.56),'Chest')
    bone('Head',(0,0,2.56),(0,0,3.29),'Neck')
    for s,side in ((1,'L'),(-1,'R')):
        bone('UpperArm.'+side,(s*.32,0,2.28),(s*.80,0,2.28),'Chest')
        bone('Forearm.'+side,(s*.80,0,2.28),(s*1.27,0,2.28),'UpperArm.'+side)
        bone('Hand.'+side,(s*1.27,0,2.28),(s*1.48,0,2.28),'Forearm.'+side)
        bone('Thigh.'+side,(s*.185,0,1.45),(s*.20,0,.80),'Hips')
        bone('Shin.'+side,(s*.20,0,.80),(s*.205,0,.23),'Thigh.'+side)
        bone('Foot.'+side,(s*.205,0,.23),(s*.205,-.30,.12),'Shin.'+side)
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in parts:
        bind = o['bind']
        for v in o.data.vertices:
            if bind.startswith('ARM.'):
                side = bind[-1]
                w = max(0,min(1,(.90-abs(v.co.x))/.20))
                weights = [('UpperArm.'+side,w),('Forearm.'+side,1-w)]
            elif bind.startswith('LEG.'):
                side = bind[-1]
                w = max(0,min(1,(v.co.z-.69)/.22))
                weights = [('Thigh.'+side,w),('Shin.'+side,1-w)]
            else: weights = [(bind,1)]
            for n,w in weights:
                if w: (o.vertex_groups.get(n) or o.vertex_groups.new(name=n)).add([v.index],w,'REPLACE')
        o.parent = rig
    # One skinned mesh per character keeps runtime draw-object overhead low.
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = name+'_Mesh'
    mod = body.modifiers.new('Shared skeleton', 'ARMATURE')
    mod.object = rig
    mod.use_deform_preserve_volume = True
    rig.scale = (scale,)*3
    rig.location.x = offset
    rig.show_in_front = True
    arm.display_type = 'STICK'
    rig['reference'] = 'Models/family_set_characters.png'
    rig['clips'] = 'Idle, Run, Running (alias of Run). Shared action datablocks and bone layout.'
    members.append((rig,body))

for args in [('Mother',.52,-1.6),('Father',.56,-.52),('Boy',.425,.53),('Girl',.405,1.46)]:
    make_member(*args)
print('Built', [(r.name,len(m.data.vertices)) for r,m in members])
