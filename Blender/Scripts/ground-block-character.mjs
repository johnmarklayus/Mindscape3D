import net from "node:net";

const code = String.raw`
import bpy
from mathutils import Matrix, Vector

root = bpy.data.objects.get('Editable_Block_Character_Root')
if root:
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)

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

corners = []
for obj in objects:
    corners.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])

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
        if root:
            obj.parent = root
            obj.matrix_parent_inverse = root.matrix_world.inverted()

corners_after = []
for obj in objects:
    corners_after.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])

bpy.ops.object.select_all(action='DESELECT')
for name in ['Head_Block', 'Torso_Block', 'Left_Arm_Block', 'Right_Arm_Block', 'Left_Leg_Block', 'Right_Leg_Block']:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.select_set(True)
if bpy.data.objects.get('Torso_Block'):
    bpy.context.view_layer.objects.active = bpy.data.objects['Torso_Block']

result = {
    'root_location': [round(float(v), 3) for v in root.location] if root else None,
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
