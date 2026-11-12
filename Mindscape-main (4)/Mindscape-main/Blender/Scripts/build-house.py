import bpy
import bmesh
import os
from mathutils import Vector

OUT = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets'
REFERENCE = '/Users/arieljerickogacilo/mindscape-3d/Models/house_model.png'
assert os.path.isfile(REFERENCE)
assert not bpy.data.scenes.get('House_Room_Shell'), 'House scene already exists; inspect before replacing it.'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/before-house.blend', copy=True)
scene = bpy.data.scenes.new('House_Room_Shell')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
scene.unit_settings.scale_length = 1

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

walls = collection('House | Walls')
floors = collection('House | Room Floors')
presentation = collection('House | Cameras')
root = bpy.data.objects.new('House_Root', None)
walls.objects.link(root)
root['reference'] = REFERENCE
root['dimensions'] = 'Approximate: 10 x 9 m footprint; 2.8 m walls; 0.22 m exterior; 0.14 m partitions.'
root['layout'] = 'Front: open kitchen/dining and living. Rear: two bedrooms and central bathroom accessed through a hall.'
root['openings'] = 'Door and window openings only. No furniture, fittings, glazing, or roof.'

def material(name, color):
    mat = bpy.data.materials.new('House_' + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = .85
    return mat

plaster = material('Plaster', (.77, .74, .68))
cap = material('Wall_Tops', (.14, .15, .17))
floor_neutral = material('Floor', (.51, .54, .55))
floor_bath = material('Bathroom_Floor', (.29, .43, .49))
floor_kitchen = material('Kitchen_Floor', (.62, .61, .55))
floor_bed = material('Bedroom_Floor', (.53, .49, .43))
slab_mat = material('Foundation', (.30, .32, .34))
meshes = []

def object_mesh(name, verts, faces, mats, target):
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    target.objects.link(obj)
    obj.parent = root
    for mat in mats: data.materials.append(mat)
    meshes.append(obj)
    return obj

def box(name, bounds, mat, target):
    x0, x1, y0, y1, z0, z1 = bounds
    verts = [(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
    faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return object_mesh(name, verts, faces, [mat], target)

def wall(name, axis, fixed, start, end, thickness, openings=()):
    height = 2.8
    us = sorted(set([start,end] + [p for hole in openings for p in hole[:2]]))
    zs = sorted(set([0,height] + [p for hole in openings for p in hole[2:]]))
    occupied = set()
    for i in range(len(us)-1):
        for j in range(len(zs)-1):
            u,z = (us[i]+us[i+1])/2,(zs[j]+zs[j+1])/2
            if not any(a<u<b and c<z<d for a,b,c,d in openings): occupied.add((i,j))
    verts, faces, ids = [], [], {}
    def vertex(u,v,z):
        xyz = (u,fixed+v,z) if axis == 'X' else (fixed+v,u,z)
        if xyz not in ids:
            ids[xyz] = len(verts)
            verts.append(xyz)
        return ids[xyz]
    # Emit only the exposed cell surfaces, so openings are actual manifold geometry.
    for i,j in sorted(occupied):
        a,b,c,d = us[i],us[i+1],zs[j],zs[j+1]
        lo,hi = -thickness/2,thickness/2
        faces += [[vertex(a,lo,c),vertex(b,lo,c),vertex(b,lo,d),vertex(a,lo,d)],
                  [vertex(a,hi,c),vertex(a,hi,d),vertex(b,hi,d),vertex(b,hi,c)]]
        for neighbor,quad in [((i-1,j),[(a,lo,c),(a,lo,d),(a,hi,d),(a,hi,c)]),
                              ((i+1,j),[(b,lo,c),(b,hi,c),(b,hi,d),(b,lo,d)]),
                              ((i,j-1),[(a,lo,c),(a,hi,c),(b,hi,c),(b,lo,c)]),
                              ((i,j+1),[(a,lo,d),(b,lo,d),(b,hi,d),(a,hi,d)])]:
            if neighbor not in occupied: faces.append([vertex(*p) for p in quad])
    obj = object_mesh(name, verts, faces, [plaster,cap], walls)
    for polygon in obj.data.polygons:
        if all(abs(obj.data.vertices[v].co.z-height)<.0001 for v in polygon.vertices): polygon.material_index=1
    obj['wall_height_m'] = height
    obj['openings'] = str(list(openings))
    return obj

# Y negative is the front entrance; the rear rooms run across Y positive.
wall('Wall_Exterior_Front','X',-4.39,-5,5,.22,[(-3.7,-2.15,.95,2.05),(-.58,.58,0,2.15),(2.15,3.7,.95,2.05)])
wall('Wall_Exterior_Back','X',4.39,-5,5,.22)
wall('Wall_Exterior_Left','Y',-4.89,-4.28,4.28,.22,[(-3.15,-1.6,.95,2.05),(1.7,3.25,.95,2.05)])
wall('Wall_Exterior_Right','Y',4.89,-4.28,4.28,.22,[(1.7,3.25,.95,2.05)])
wall('Wall_Bedroom_Left_Front','X',.40,-4.78,-.65,.14)
wall('Wall_Bedroom_Right_Front','X',.40,.65,4.78,.14)
wall('Wall_Bedroom_Left_Hall_Bath','Y',-1.50,.47,4.28,.14,[(.55,1.50,0,2.10)])
wall('Wall_Bedroom_Right_Hall_Bath','Y',1.50,.47,4.28,.14,[(.55,1.50,0,2.10)])
wall('Wall_Bathroom_Entrance','X',1.64,-1.43,1.43,.14,[(-.5,.5,0,2.10)])

box('Floor_Foundation',(-5,5,-4.5,4.5,-.22,-.10),slab_mat,floors)
box('Floor_Kitchen_Dining',(-4.78,-.65,-4.28,.33,-.10,0),floor_kitchen,floors)
box('Floor_Living',(.65,4.78,-4.28,.33,-.10,0),floor_neutral,floors)
box('Floor_Entry_Passage',(-.65,.65,-4.28,.47,-.10,0),floor_neutral,floors)
box('Floor_Hall',(-1.43,1.43,.47,1.57,-.10,0),floor_neutral,floors)
box('Floor_Bedroom_Left',(-4.78,-1.57,.47,4.28,-.10,0),floor_bed,floors)
box('Floor_Bedroom_Right',(1.57,4.78,.47,4.28,-.10,0),floor_bed,floors)
box('Floor_Bathroom',(-1.43,1.43,1.71,4.28,-.10,0),floor_bath,floors)
box('Threshold_Entrance',(-.58,.58,-4.5,-4.28,-.10,0),floor_neutral,floors)
box('Threshold_Bathroom',(-.5,.5,1.57,1.71,-.10,0),floor_bath,floors)
for side,x0,x1 in [('Left',-1.57,-1.43),('Right',1.43,1.57)]:
    box('Threshold_Bedroom_'+side,(x0,x1,.55,1.5,-.10,0),floor_bed,floors)

world = bpy.data.worlds.new('House_Preview_World')
world.color = (.23,.25,.28)
scene.world = world
scene.render.engine = 'BLENDER_WORKBENCH'
shading = scene.display.shading
shading.light = 'STUDIO'
shading.color_type = 'MATERIAL'
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = 'BOTH'
shading.cavity_ridge_factor = .7
shading.cavity_valley_factor = .8
shading.background_type = 'WORLD'
scene.render.resolution_x = 1300
scene.render.resolution_y = 1300
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
def camera(name,position,target,scale):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name,data)
    presentation.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type = 'ORTHO'
    data.ortho_scale = scale
    return obj
iso = camera('House_Camera_Overview',(4,-12,18),(0,0,.5),14)
plan = camera('House_Camera_Floor_Plan',(0,0,22),(0,0,0),11.6)
scene.camera = iso
bpy.context.view_layer.update()

# Validate topology and walk-through clearances instead of relying on appearance alone.
bad = []
for obj in meshes:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if any(not edge.is_manifold for edge in bm.edges): bad.append(obj.name)
    bm.free()
assert not bad, 'Non-manifold mesh: ' + str(bad)
deps = bpy.context.evaluated_depsgraph_get()
routes = [('Front entrance',(0,-5,1),(0,-3.8,1)),('Hall entry',(0,-.1,1),(0,.9,1)),('Bathroom',(0,1.2,1),(0,2,1)),('Left bedroom',(-1,.98,1),(-2,.98,1)),('Right bedroom',(1,.98,1),(2,.98,1))]
for name,start,end in routes:
    direction = Vector(end)-Vector(start)
    hit = scene.ray_cast(deps,Vector(start),direction.normalized(),distance=direction.length)[0]
    assert not hit, 'Blocked opening: ' + name

bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
bpy.context.view_layer.objects.active = root
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.color_type = 'MATERIAL'
            area.spaces.active.region_3d.view_rotation = iso.rotation_euler.to_quaternion()
            area.spaces.active.region_3d.view_location = (0,0,.5)
            area.spaces.active.region_3d.view_distance = 17
scene.render.filepath = OUT + '/house-shell-preview.png'
bpy.ops.render.render(write_still=True)
scene.camera = plan
scene.render.filepath = OUT + '/house-floor-plan.png'
bpy.ops.render.render(write_still=True)
scene.camera = iso
scene.render.filepath = OUT + '/house-shell-preview.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/house-shell.blend')
result = {'file':bpy.data.filepath,'scene':scene.name,'wall_objects':9,'mesh_objects':len(meshes),'manifold':True,'door_routes_clear':len(routes),'dimensions_m':[10,9,2.8],'furniture_objects':0,'previews':[OUT+'/house-shell-preview.png',OUT+'/house-floor-plan.png']}
