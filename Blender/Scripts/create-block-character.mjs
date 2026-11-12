import net from "node:net";

const code = String.raw`
import bpy

for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Editable_Block_Character') or obj.name.startswith(('Head_Block','Torso_Block','Left_Arm_Block','Right_Arm_Block','Left_Leg_Block','Right_Leg_Block')):
        bpy.data.objects.remove(obj, do_unlink=True)

def mat(name, color):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    return material

skin = mat('Block_Character_Skin', (0.92, 0.68, 0.48, 1.0))
shirt = mat('Block_Character_Shirt', (0.12, 0.38, 0.82, 1.0))
pants = mat('Block_Character_Pants', (0.08, 0.11, 0.18, 1.0))
shoe = mat('Block_Character_Shoes', (0.03, 0.03, 0.035, 1.0))
eye = mat('Block_Character_Eyes', (0.02, 0.025, 0.03, 1.0))

def cube_obj(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + '_Mesh'
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj['editable_part'] = True
    obj['character_style'] = 'minecraft/roblox low-poly block'
    return obj

torso = cube_obj('Torso_Block', (0, 0, 2.45), (1.35, 0.62, 1.55), shirt)
head = cube_obj('Head_Block', (0, 0, 3.55), (1.05, 0.92, 1.05), skin)
left_arm = cube_obj('Left_Arm_Block', (-1.02, 0, 2.45), (0.48, 0.52, 1.48), skin)
right_arm = cube_obj('Right_Arm_Block', (1.02, 0, 2.45), (0.48, 0.52, 1.48), skin)
left_leg = cube_obj('Left_Leg_Block', (-0.36, 0, 1.15), (0.52, 0.54, 1.48), pants)
right_leg = cube_obj('Right_Leg_Block', (0.36, 0, 1.15), (0.52, 0.54, 1.48), pants)

left_eye = cube_obj('Editable_Block_Character_Left_Eye', (-0.23, -0.468, 3.68), (0.16, 0.025, 0.16), eye)
right_eye = cube_obj('Editable_Block_Character_Right_Eye', (0.23, -0.468, 3.68), (0.16, 0.025, 0.16), eye)
left_shoe = cube_obj('Editable_Block_Character_Left_Shoe', (-0.36, -0.04, 0.37), (0.56, 0.62, 0.20), shoe)
right_shoe = cube_obj('Editable_Block_Character_Right_Shoe', (0.36, -0.04, 0.37), (0.56, 0.62, 0.20), shoe)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 2.0))
root = bpy.context.object
root.name = 'Editable_Block_Character_Root'

parts = [head, torso, left_arm, right_arm, left_leg, right_leg]
details = [left_eye, right_eye, left_shoe, right_shoe]
for obj in parts + details:
    obj.parent = root

for obj in parts:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.select_set(False)

for obj in parts:
    bevel = obj.modifiers.new('Tiny_Edit_Friendly_Bevel', 'BEVEL')
    bevel.width = 0.015
    bevel.segments = 1
    bevel.affect = 'EDGES'
    obj.modifiers.new('Weighted_Block_Normals', 'WEIGHTED_NORMAL')

bpy.ops.object.light_add(type='AREA', location=(0, -4, 6))
light = bpy.context.object
light.name = 'Editable_Block_Character_Key_Light'
light.data.energy = 400
light.data.size = 4

bpy.ops.object.camera_add(location=(3.2, -6, 3.1), rotation=(1.18, 0, 0.48))
bpy.context.scene.camera = bpy.context.object

bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = torso

result = {
    'created_parts': [obj.name for obj in parts],
    'detail_parts': [obj.name for obj in details],
    'root': root.name,
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
