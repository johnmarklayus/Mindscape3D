import bpy
import math
import random
import os
from mathutils import Vector, Quaternion

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets'
random.seed(7)
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
# Preserve the current scene before replacing the previous character.
if not os.path.exists(OUT + '/before-reference-character.blend'):
    bpy.ops.wm.save_as_mainfile(filepath=OUT + '/before-reference-character.blend', copy=True)
old = {'Head_Block', 'Torso_Block', 'Left_Arm_Block', 'Right_Arm_Block', 'Left_Leg_Block', 'Right_Leg_Block'}
for obj in list(bpy.data.objects):
    if obj.name in old or obj.name.startswith(('Editable_Block_Character_', 'Reference_Character_', 'Reference_Preview_Camera')):
        bpy.data.objects.remove(obj, do_unlink=True)
collection = bpy.data.collections.new('Reference_Character_Editable')
bpy.context.scene.collection.children.link(collection)
root = bpy.data.objects.new('Reference_Character_Root', None)
collection.objects.link(root)
parts = []

def material(name, color):
    mat = bpy.data.materials.new('Reference_' + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .88
    return mat

skin = material('Skin', (.66, .34, .14))
teal = material('Teal_Shirt', (.025, .27, .29))
pants = material('Trousers', (.065, .085, .125))
white = material('White_Sneakers', (.83, .85, .89))
hair = material('Dark_Hair', (.045, .031, .03))
black = material('Eyes_Brows', (.028, .018, .014))

def mesh(name, verts, faces, mat, facets=False):
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new('Reference_Character_' + name, data)
    collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(mat)
    if facets:
        for factor in (.94, 1.035, .985):
            color = tuple(c * factor for c in mat.diffuse_color[:3])
            obj.data.materials.append(material(name + '_Facet', color))
        for polygon in data.polygons:
            polygon.material_index = random.choices([0, 1, 2, 3], [7, 1, 1, 1])[0]
    parts.append(obj)
    return obj

# Eight-sided rectangular rings retain broad flat surfaces and chamfered corners.
def rings(name, rows, mat, axis='z', triangulate=False):
    verts = []
    for center, width, depth, bevel in rows:
        x, y, z = center
        outline = [(-width/2+bevel,-depth/2),(width/2-bevel,-depth/2),(width/2,-depth/2+bevel),(width/2,depth/2-bevel),(width/2-bevel,depth/2),(-width/2+bevel,depth/2),(-width/2,depth/2-bevel),(-width/2,-depth/2+bevel)]
        verts.extend([(x+a,y+b,z) if axis=='z' else (x,y+b,z+a) for a,b in outline])
    faces = [tuple(reversed(range(8)))]
    for j in range(len(rows)-1):
        for i in range(8):
            a,b,c,d = j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i
            if triangulate and (i+j)%3 == 0:
                faces.extend([(a,b,c),(a,c,d)])
            else:
                faces.append((a,b,c,d))
    faces.append(tuple(range((len(rows)-1)*8,len(rows)*8)))
    obj = mesh(name,verts,faces,mat,triangulate)
    # Ring orientation is normalized for mirrored limbs as well.
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    return obj

def box(name, center, size, mat, bevel=.01):
    x,y,z=center
    w,d,h=size
    return rings(name,[((x,y,z-h/2),w,d,bevel),((x,y,z+h/2),w,d,bevel)],mat)

torso=rings('Torso',[((0,0,2.62),1.10,.55,.13),((0,0,3.32),1.05,.57,.13),((0,0,3.88),1.13,.61,.14),((0,0,4.18),1.12,.53,.12)],teal,triangulate=True)
rings('Neck',[((0,0,4.13),.30,.30,.055),((0,0,4.50),.34,.32,.065)],skin)
head=rings('Head',[((0,-.015,4.43),.40,.38,.085),((0,-.015,4.49),.56,.48,.095),((0,0,4.97),.65,.53,.08),((0,.015,5.20),.60,.49,.075),((0,.015,5.28),.43,.38,.09)],skin)
for s,side in [(-1,'Right'),(1,'Left')]:
    box(side+'_Ear',(s*.365,.0,4.76),(.15,.21,.25),skin,.025)
    box(side+'_Eye',(s*.14,-.279,4.84),(.095,.023,.12),black,.002)
    box(side+'_Eyebrow',(s*.145,-.275,4.995),(.18,.034,.067),black,.003)
    rings(side+'_Sleeve',[((s*.51,0,4.04),.50,.53,.065),((s*1.20,0,4.035),.44,.47,.06),((s*1.84,0,4.025),.39,.41,.05)],teal,axis='x',triangulate=True)
    rings(side+'_Forearm',[((s*1.82,0,4.025),.30,.32,.05),((s*2.24,-.015,4.01),.25,.28,.045)],skin,axis='x')
    rings(side+'_Hand',[((s*2.22,-.015,4.01),.25,.28,.04),((s*2.34,-.025,3.985),.32,.32,.06),((s*2.55,-.025,3.99),.17,.25,.045)],skin,axis='x',triangulate=True)
    rings(side+'_Leg',[((s*.30,0,2.64),.49,.48,.075),((s*.44,0,1.50),.42,.42,.065),((s*.59,0,.48),.39,.37,.06)],pants,triangulate=True)
    box(side+'_Ankle',(s*.59,0,.45),(.29,.29,.20),skin,.045)
    rings(side+'_Shoe',[((s*.60,-.13,0),.44,.71,.045),((s*.60,-.13,.20),.43,.69,.04),((s*.59,-.01,.43),.31,.40,.055)],white)

# Polygonal hair cap and overlapping swept locks give the reference its silhouette.
rings('Hair_Cap',[((0,.10,4.91),.67,.47,.10),((0,.025,5.26),.77,.64,.13),((-.04,.035,5.43),.64,.53,.12),((-.10,.05,5.50),.38,.37,.09)],hair,triangulate=True)
def lock(name, outline, depth):
    verts=[(x,y,z) for x,y,z in outline]
    verts += [(x,y+depth,z-.025) for x,y,z in outline]
    n=len(outline)
    center=tuple(sum(v[i] for v in outline)/n for i in range(3))
    verts.append((center[0],center[1]-.075,center[2]+.015))
    faces=[(i,(i+1)%n,2*n) for i in range(n)]
    faces += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    faces.append(tuple(reversed(range(n,2*n))))
    return mesh(name,verts,faces,hair,True)
lock('Hair_Swept_Fringe',[(-.40,-.20,5.13),(-.49,-.16,5.27),(-.32,-.22,5.46),(.04,-.25,5.50),(.22,-.29,5.24),(-.06,-.32,5.19),(-.29,-.32,5.07)],.22)
lock('Hair_Left_Lock',[(-.35,-.25,4.76),(-.44,-.20,5.12),(-.29,-.30,5.34),(-.17,-.31,5.30),(-.29,-.30,5.04)],.18)
lock('Hair_Right_Lock',[(.31,-.22,4.77),(.27,-.27,5.14),(.19,-.27,5.32),(.39,-.15,5.38),(.45,-.10,5.24)],.22)
lock('Hair_Top_Sweep',[(-.15,-.15,5.34),(-.48,-.02,5.52),(-.23,-.01,5.59),(.10,-.05,5.54),(.24,-.15,5.28)],.24)
lock('Hair_Crown_Tip',[(.03,-.01,5.43),(-.12,.04,5.71),(.09,.04,5.61),(.24,-.04,5.46),(.21,-.12,5.29)],.19)

root['reference_image']='/Users/arieljerickogacilo/mindscape-blender/models/character_1.png'
root['description']='Editable low-poly reference reconstruction; front faces -Y; feet at ground level.'
scene=bpy.context.scene
camera_data=bpy.data.cameras.new('Reference_Preview_Camera')
camera=bpy.data.objects.new('Reference_Preview_Camera',camera_data)
scene.collection.objects.link(camera)
camera.location=(7,-23,8)
camera.rotation_euler=(Vector((0,0,2.85))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO'
camera_data.ortho_scale=6.65
scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=.4
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_ridge_factor=.65
scene.display.shading.cavity_valley_factor=.5
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.world.color=(.19,.19,.19)
scene.render.resolution_x=1000
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=OUT+'/reference-character-preview.png'
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=torso
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
            area.spaces.active.region_3d.view_distance=8
            area.spaces.active.region_3d.view_location=(0,0,2.85)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/reference-character.blend')
bpy.ops.render.render(write_still=True)
result={'mesh_parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),'root':list(root.location),'blend':bpy.data.filepath,'preview':scene.render.filepath,'old_character_remaining':any(o.name in old for o in bpy.data.objects)}
