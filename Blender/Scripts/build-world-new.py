"""Run inside Blender through MCP to build the separate world_new scene.

Creates only world_new scene geometry. Source .blend files are never overwritten.
Blender XY is the ground plane, +Z up; glTF exporter converts to Unity Y-up.
"""
import bpy
import math
import json
from mathutils import Vector, Matrix

BASE = '/Users/arieljerickogacilo/mindscape-3d'
assert 'world_new' not in bpy.data.objects, 'World already built; inspect before rerunning.'
scene = bpy.data.scenes.get('world_new')
if scene is None:
    scene = bpy.data.scenes.new('world_new')
    bpy.context.window.scene = scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    for tag,filename in [('House','house-and-lot-cozy.blend'),('School','school-grounds.blend')]:
        with bpy.data.libraries.load(BASE+'/Blender/Blend Files/'+filename, link=False) as (src,dst):
            dst.objects = list(src.objects)
        col = bpy.data.collections.new('World | '+tag)
        scene.collection.children.link(col)
        for ob in dst.objects:
            if ob is not None and ob.type not in {'CAMERA','LIGHT'} and not ob.name.startswith(('Street |','Bus stop |')):
                col.objects.link(ob)
                ob['world_source_name'] = ob.name
bpy.context.window.scene = scene

def collection(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col

infrastructure = collection('World | Streets and sidewalks')
blocks = collection('World | Nine blocks')
markings = collection('World | Road markings')
connections = collection('World | Entrance connections')
presentation = collection('World | Presentation')
guides = collection('World | Layout guides - non-export')
root = bpy.data.objects.new('world_new', None)
infrastructure.objects.link(root)
root['layout'] = '3 columns x 3 rows; house southwest, updated campus northeast'
root['block_land_dimensions_m'] = [90, 40]
root['road_width_m'] = 8.0
root['sidewalk_width_m'] = 2.0
root['world_dimensions_m'] = [314, 164]
root['house_source'] = 'Blender/Blend Files/house-and-lot-cozy.blend'
root['school_source'] = 'Blender/Blend Files/school-grounds.blend'
root['integration'] = 'Model only: Unity physics, navigation and episode integration are separate.'

def material(name, color):
    mat = bpy.data.materials.new('World | ' + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = .9
    return mat

asphalt = material('Asphalt', (.115, .135, .15))
concrete = material('Sidewalk', (.59, .61, .58))
grass = material('Open blocks', (.29, .43, .23))
white = material('Road paint', (.88, .88, .79))
route_mat = material('Route guide', (1.0, .34, .045))
edge = material('Foundation', (.20, .26, .20))

def box(name, xyz, size, mat, col, parent=root):
    x, y, z = [s / 2 for s in size]
    verts = [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
             (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    col.objects.link(ob)
    ob.location = xyz
    ob.parent = parent
    return ob

# Each original model is parented without modifying any original geometry or scale.
bpy.context.view_layer.update()
for tag, offset, angle in [('House',(-102,-43,.35),math.pi),('School',(102,48,.14),0)]:
    col = bpy.data.collections['World | '+tag]
    originals = list(col.objects)
    anchor = bpy.data.objects.new('World | '+tag+' anchor', None)
    col.objects.link(anchor)
    anchor.parent = root
    for ob in originals:
        if ob.parent not in originals:
            world = ob.matrix_world.copy()
            ob.parent = anchor
            ob.matrix_world = world
    anchor.location = offset
    anchor.rotation_euler.z = angle
    anchor['original_scale_preserved'] = True

# Open the existing pedestrian gate inward around its actual hinge.
gate = next(o for o in bpy.data.collections['World | House'].objects
            if o.name.startswith('Pedestrian gate | assembly'))
pivot = Vector((-.7,-9.8,0))
gate.matrix_basis = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(95),4,'Z') @ Matrix.Translation(-pivot)
gate['world_note'] = 'Opened inward for pedestrian access; original asset unchanged.'

box('World foundation',(0,0,-.22),(314,164,.4),edge,infrastructure)
road_x = [-153,-51,51,153]
road_y = [-78,-26,26,78]
# Vertical strips and horizontal spans meet without coplanar overlaps.
for x in road_x:
    box('Road NS '+str(x),(x,0,-.04),(8,164,.08),asphalt,infrastructure)
for y in road_y:
    for x in [-102,0,102]:
        box('Road EW '+str(x)+' '+str(y),(x,y,-.04),(94,8,.08),asphalt,infrastructure)

for row,y in enumerate([52,0,-52],1):
    for column,x in enumerate([-102,0,102],1):
        name = 'Block %d%d' % (row,column)
        land = box(name+' | land',(x,y,-.10),(90,40,.40),grass,blocks)
        if (row,column)==(1,3):
            land.location.z -= .03  # Keep the source campus lawn above the block base.
        land['grid_row'] = row
        land['grid_column'] = column
        land['usage'] = 'School campus' if (row,column)==(1,3) else 'House' if (row,column)==(3,1) else 'Reserved / empty'
        # The complete pavement ring is 2 m wide with a low 6 cm road edge.
        for dx in [-46,46]:
            box(name+' | sidewalk side '+str(dx),(x+dx,y,.015),(2,44,.09),concrete,infrastructure)
        for dy in [-21,21]:
            box(name+' | sidewalk end '+str(dy),(x,y+dy,.015),(90,2,.09),concrete,infrastructure)

# Dashed center markings stop before every junction and crossing.
for x in road_x:
    for y in range(-73,74,6):
        if min(abs(y-iy) for iy in road_y)>10:
            box('Lane dash NS',(x,y,.006),(.14,2.8,.012),white,markings)
for y in road_y:
    for x in range(-147,148,6):
        if min(abs(x-ix) for ix in road_x)>10:
            box('Lane dash EW',(x,y,.006),(2.8,.14,.012),white,markings)

def crossing_ns_road(x,y):
    for k in range(8):
        box('Crosswalk NS road',(x-3.5+k,y,.012),(.55,2.6,.024),white,markings)

def crossing_ew_road(x,y):
    for k in range(8):
        box('Crosswalk EW road',(x,y-3.5+k,.012),(2.6,.55,.024),white,markings)

# Crossings on the four inner junctions, located beside sidewalk corners.
for x in [-51,51]:
    for y in [-26,26]:
        for side in [-1,1]:
            crossing_ns_road(x,y+side*6)
            crossing_ew_road(x+side*6,y)

# Short approach paths connect the existing gates with the new pavement rings.
box('House | pedestrian approach',(-102,-32,.13),(1.5,2.4,.16),concrete,connections)
box('House | driveway approach',(-106.35,-32,.08),(4.25,2.4,.10),concrete,connections)
box('School | main gate approach',(102,32,.09),(4.0,2.1,.06),concrete,connections)

# Optional visual route follows sidewalks, not vacant lots. Non-export collection.
route = [(-102,-33.0,.28),(-102,-31,.28),(-57,-31,.28),(-57,-32,.28),
         (-45,-32,.28),(-45,-31,.28),(45,-31,.28),(45,-32,.28),
         (57,-32,.28),(57,-20,.28),(56,-20,.28),(56,20,.28),
         (57,20,.28),(57,32,.28),(102,32,.28),(102,34,.28)]
for a,b in zip(route,route[1:]):
    a,b = Vector(a),Vector(b)
    length = (b-a).length
    direction = (b-a).normalized()
    for k in range(max(1,int(length/2))):
        center = a+direction*(min(length-.1,k*2+.45))
        length_dash = min(.8,length)
        size = (length_dash,.18,.025) if abs(direction.x)>.5 else (.18,length_dash,.025)
        box('Guide | home to campus',center,size,route_mat,guides,parent=None)
guides.hide_render = True
guides.hide_viewport = True
root['route_waypoints_blender_xyz'] = json.dumps(route)

for name,pos in [('Spawn | House sidewalk',(-102,-31,.12)),('Arrival | School gate',(102,34,.14))]:
    marker = bpy.data.objects.new(name,None)
    connections.objects.link(marker)
    marker.parent = root
    marker.location = pos
    marker.empty_display_type = 'ARROWS'
    marker.empty_display_size = 1.5

def camera(name,pos,target,scale):
    data=bpy.data.cameras.new(name)
    data.type='ORTHO'
    data.ortho_scale=scale
    ob=bpy.data.objects.new(name,data)
    presentation.objects.link(ob)
    ob.location=pos
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

cam=camera('World | Overview camera',(0,-220,300),(0,0,0),342)
camera('World | Top-down camera',(0,0,340),(0,0,0),340)
scene.camera=cam
sun_data=bpy.data.lights.new('World | Sun','SUN')
sun_data.energy=2.5
sun_data.angle=math.radians(20)
sun=bpy.data.objects.new('World | Sun',sun_data)
presentation.objects.link(sun)
sun.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-25))
world=bpy.data.worlds.new('World | Daylight')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.73,.85,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.world=world
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1800
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
bpy.context.view_layer.update()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active
        space.region_3d.view_distance=280
        space.region_3d.view_location=(0,0,0)
        space.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
        space.region_3d.view_perspective='ORTHO'
        space.clip_end=2000
        space.shading.type='MATERIAL'

print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'blocks':len(blocks.objects),
                  'house_parts':len(bpy.data.collections['World | House'].objects),
                  'school_parts':len(bpy.data.collections['World | School'].objects),
                  'dimensions':[314,164],'route_length_m':sum((Vector(b)-Vector(a)).length for a,b in zip(route,route[1:]))}))
