import net from 'node:net';
import { readFileSync } from 'node:fs';
const code = process.argv.includes('--inspect')
  ? "import bpy\nresult={'file':bpy.data.filepath,'objects':[(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.context.scene.objects]}"
  : readFileSync(new URL(process.argv.includes('--fix-contact') ? './fix-character-contact.py' : './animate-reference-character.py', import.meta.url), 'utf8');
const client = net.createConnection(9876, '127.0.0.1');
let buffer = '';
client.setTimeout(120000);
client.on('connect', () => client.write(JSON.stringify({type:'execute',code,strict_json:true})+'\0'));
client.on('data', chunk => {
  buffer += chunk;
  if (buffer.includes('\0')) {
    const response=JSON.parse(buffer.split('\0')[0]);
    console.log(JSON.stringify(response));
    if(response.status!=='ok') process.exitCode=1;
    client.end();
  }
});
client.on('timeout',()=>{client.destroy();process.exitCode=1;});
client.on('error',error=>{console.error(error);process.exitCode=1;});
