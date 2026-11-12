import net from "node:net";

const code = String.raw`
import bpy
from mathutils import Matrix, Vector

# Remove the default cube if it is still in the scene.
cube = bpy.data.objects.get('Cube')
if cube:
    bpy.data.objects.remove(cube, do_unlink=True)

def mat(name, color):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    return material

skin = mat('Block_Character_Skin', (0.92, 0.68, 0.48, 1.0))
shirt = mat('Block_Character_Shirt', (0.12, 0.38, 0.82, 1.0))
pants = mat('Block_Character_Pants', (0.08, 0.11, 0.18, 1.0))
shoe = mat('Block_Character_Shoes', (0.03, 0.03, 0.035, 1.0))
eye = mat('Block_Character_Eyes', (0.02, 0.025, 0.03, 1.0))
hair = mat('Block_Character_Hair', (0.12, 0.07, 0.035, 1.0))
mouth = mat('Block_Character_Mouth', (0.34, 0.07, 0.08, 1.0))
cheek = mat('Block_Character_Cheeks', (0.95, 0.45, 0.42, 1.0))

main_names = [
    'Head_Block',
    'Torso_Block',
    'Left_Arm_Block',
    'Right_Arm_Block',
    'Left_Leg_Block',
    'Right_Leg_Block',
]
main_parts = [bpy.data.objects[name] for name in main_names if bpy.data.objects.get(name)]

# Remove old generated detail pieces, keeping the six major editable parts.
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Editable_Block_Character_') and obj.name not in {'Editable_Block_Character_Root'}:
        bpy.data.objects.remove(obj, do_unlink=True)

root = bpy.data.objects.get('Editable_Block_Character_Root')
if root is None:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.object
    root.name = 'Editable_Block_Character_Root'

def cube_obj(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + '_Mesh'
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj['editable_part'] = True
    obj['character_style'] = 'minecraft/roblox rounded low-poly block'
    return obj

# Add rounded, editable facial and clothing details on the front (-Y).
details = [
    cube_obj('Editable_Block_Character_Hair_Cap', (0, -0.015, 4.11), (1.12, 0.96, 0.20), hair),
    cube_obj('Editable_Block_Character_Hair_Front', (0, -0.50, 3.98), (1.05, 0.10, 0.22), hair),
    cube_obj('Editable_Block_Character_Left_Eye', (-0.24, -0.472, 3.70), (0.17, 0.035, 0.17), eye),
    cube_obj('Editable_Block_Character_Right_Eye', (0.24, -0.472, 3.70), (0.17, 0.035, 0.17), eye),
    cube_obj('Editable_Block_Character_Left_Brow', (-0.24, -0.49, 3.88), (0.25, 0.035, 0.055), hair),
    cube_obj('Editable_Block_Character_Right_Brow', (0.24, -0.49, 3.88), (0.25, 0.035, 0.055), hair),
    cube_obj('Editable_Block_Character_Nose', (0, -0.50, 3.52), (0.13, 0.08, 0.18), skin),
    cube_obj('Editable_Block_Character_Mouth', (0, -0.505, 3.34), (0.35, 0.035, 0.07), mouth),
    cube_obj('Editable_Block_Character_Left_Cheek', (-0.38, -0.485, 3.43), (0.14, 0.025, 0.11), cheek),
    cube_obj('Editable_Block_Character_Right_Cheek', (0.38, -0.485, 3.43), (0.14, 0.025, 0.11), cheek),
    cube_obj('Editable_Block_Character_Shirt_Collar', (0, -0.325, 3.16), (0.55, 0.06, 0.16), skin),
    cube_obj('Editable_Block_Character_Left_Sleeve', (-1.02, -0.01, 2.98), (0.50, 0.54, 0.34), shirt),
    cube_obj('Editable_Block_Character_Right_Sleeve', (1.02, -0.01, 2.98), (0.50, 0.54, 0.34), shirt),
    cube_obj('Editable_Block_Character_Left_Shoe', (-0.36, -0.04, 0.37), (0.58, 0.66, 0.22), shoe),
    cube_obj('Editable_Block_Character_Right_Shoe', (0.36, -0.04, 0.37), (0.58, 0.66, 0.22), shoe),
]

# Make the block character feel softer while preserving low-poly editability.
for obj in main_parts + details:
    for modifier in list(obj.modifiers):
        if modifier.type in {'BEVEL', 'WEIGHTED_NORMAL'}:
            obj.modifiers.remove(modifier)
    bevel = obj.modifiers.new('Rounded_Block_Edges', 'BEVEL')
    bevel.width = 0.055 if obj in main_parts else 0.025
    bevel.segments = 2 if obj in main_parts else 1
    bevel.affect = 'EDGES'
    obj.modifiers.new('Weighted_Block_Normals', 'WEIGHTED_NORMAL')

# Center character on X/Y and place the lowest part on Z=0.
character_objs = main_parts + details
world_corners = []
for obj in character_objs:
    world_corners.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])

if world_corners:
    min_x = min(corner.x for corner in world_corners)
    max_x = max(corner.x for corner in world_corners)
    min_y = min(corner.y for corner in world_corners)
    max_y = max(corner.y for corner in world_corners)
    min_z = min(corner.z for corner in world_corners)
    offset = Vector((-(min_x + max_x) / 2.0, -(min_y + max_y) / 2.0, -min_z))
    transform = Matrix.Translation(offset)
    for obj in character_objs:
        obj.matrix_world = transform @ obj.matrix_world

root.location = (0, 0, 0)
for obj in character_objs:
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()

bpy.ops.object.select_all(action='DESELECT')
for obj in main_parts:
    obj.select_set(True)
if main_parts:
    bpy.context.view_layer.objects.active = main_parts[1] if len(main_parts) > 1 else main_parts[0]

result = {
    'removed_default_cube': cube is not None,
    'root_location': [round(float(v), 3) for v in root.location],
    'main_parts': [obj.name for obj in main_parts],
    'added_details': [obj.name for obj in details],
    'selected': [obj.name for obj in bpy.context.selected_objects],
}
`;

const request = { type: "execute", code, strict_json: true };
const client = net.createConnection(9876, "127.0.0.1");
let buffer = "";

client.setTimeout(10000);
client.on("connect", () => client.write(`${JSON.stringify(request)}\0`));
client.on("data", (chunk) => {
  buffer += chunk.toString();
  if (buffer.includes("\0")) {
    console.log(buffer.split("\0")[0]);
    client.end();
  }
});
client.on("timeout", () => {
  console.error("timeout");
  client.destroy();
  process.exitCode = 2;
});
client.on("error", (error) => {
  console.error(error.message);
  process.exitCode = 1;
});
