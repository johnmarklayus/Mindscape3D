import net from "node:net";

const code = String.raw`
import bpy

names = [
    'Head_Block',
    'Torso_Block',
    'Left_Arm_Block',
    'Right_Arm_Block',
    'Left_Leg_Block',
    'Right_Leg_Block',
]

result = {
    'parts': {
        name: {
            'exists': bpy.data.objects.get(name) is not None,
            'dimensions': [round(float(v), 3) for v in bpy.data.objects[name].dimensions] if bpy.data.objects.get(name) else None,
            'parent': bpy.data.objects[name].parent.name if bpy.data.objects.get(name) and bpy.data.objects[name].parent else None,
        }
        for name in names
    },
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
