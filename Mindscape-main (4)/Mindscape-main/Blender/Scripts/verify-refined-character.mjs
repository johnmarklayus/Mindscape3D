import net from "node:net";

const code = String.raw`
import bpy
from mathutils import Vector

objects = [
    obj for obj in bpy.context.scene.objects
    if obj.type == 'MESH' and (obj.name in {
        'Head_Block',
        'Torso_Block',
        'Left_Arm_Block',
        'Right_Arm_Block',
        'Left_Leg_Block',
        'Right_Leg_Block',
    } or obj.name.startswith('Editable_Block_Character_'))
]

corners = []
for obj in objects:
    if hasattr(obj, 'bound_box'):
        corners.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])

result = {
    'cube_exists': bpy.data.objects.get('Cube') is not None,
    'root_location': [round(float(v), 3) for v in bpy.data.objects['Editable_Block_Character_Root'].location],
    'object_count': len(objects),
    'bounds': {
        'min': [round(float(min(getattr(c, axis) for c in corners)), 3) for axis in ('x', 'y', 'z')] if corners else None,
        'max': [round(float(max(getattr(c, axis) for c in corners)), 3) for axis in ('x', 'y', 'z')] if corners else None,
    },
    'rounded_parts': {
        obj.name: any(modifier.type == 'BEVEL' for modifier in obj.modifiers)
        for obj in objects
        if obj.type == 'MESH'
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
