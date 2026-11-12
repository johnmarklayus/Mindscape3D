import net from "node:net";

const code = String.raw`
import bpy
from mathutils import Matrix, Vector

root = bpy.data.objects.get('Editable_Block_Character_Root')
if root is None:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.object
    root.name = 'Editable_Block_Character_Root'

objects = [
    obj for obj in bpy.context.scene.objects
    if obj.type == 'MESH' and (
        obj.name in {
            'Head_Block',
            'Torso_Block',
            'Left_Arm_Block',
            'Right_Arm_Block',
            'Left_Leg_Block',
            'Right_Leg_Block',
        } or obj.name.startswith('Editable_Block_Character_')
    )
]

# Bake the current visible transforms into unparented world matrices first.
world_matrices = {obj.name: obj.matrix_world.copy() for obj in objects}
for obj in objects:
    obj.parent = None
    obj.matrix_world = world_matrices[obj.name]

root.parent = None
root.location = (0, 0, 0)
root.rotation_euler = (0, 0, 0)
root.scale = (1, 1, 1)

def mesh_bounds(meshes):
    corners = []
    for mesh in meshes:
        corners.extend([mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box])
    return corners

corners = mesh_bounds(objects)
if corners:
    min_x = min(corner.x for corner in corners)
    max_x = max(corner.x for corner in corners)
    min_y = min(corner.y for corner in corners)
    max_y = max(corner.y for corner in corners)
    min_z = min(corner.z for corner in corners)
    offset = Vector((-(min_x + max_x) / 2.0, -(min_y + max_y) / 2.0, -min_z))
    transform = Matrix.Translation(offset)
    for obj in objects:
        obj.matrix_world = transform @ obj.matrix_world

# Reparent to an identity root without inverse offsets.
for obj in objects:
    obj.parent = root
    obj.matrix_parent_inverse.identity()

bpy.context.view_layer.update()

corners_after = mesh_bounds(objects)

bpy.ops.object.select_all(action='DESELECT')
for name in ['Head_Block', 'Torso_Block', 'Left_Arm_Block', 'Right_Arm_Block', 'Left_Leg_Block', 'Right_Leg_Block']:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.select_set(True)
if bpy.data.objects.get('Torso_Block'):
    bpy.context.view_layer.objects.active = bpy.data.objects['Torso_Block']

result = {
    'root_location': [round(float(v), 3) for v in root.location],
    'root_rotation': [round(float(v), 3) for v in root.rotation_euler],
    'root_scale': [round(float(v), 3) for v in root.scale],
    'bounds': {
        'min': [round(float(min(getattr(c, axis) for c in corners_after)), 3) for axis in ('x', 'y', 'z')] if corners_after else None,
        'max': [round(float(max(getattr(c, axis) for c in corners_after)), 3) for axis in ('x', 'y', 'z')] if corners_after else None,
    },
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
