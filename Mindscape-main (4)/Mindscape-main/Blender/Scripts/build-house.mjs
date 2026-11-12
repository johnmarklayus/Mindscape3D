import net from 'node:net';
import { readFileSync } from 'node:fs';
const code = readFileSync(new URL(process.argv.includes('--preview') ? './preview-house.py' : './build-house.py', import.meta.url), 'utf8');
const socket = net.createConnection(9876, '127.0.0.1');
let buffer = '';
socket.setTimeout(120000);
socket.on('connect', () => socket.write(JSON.stringify({ type: 'execute', code, strict_json: true }) + '\0'));
socket.on('data', chunk => {
  buffer += chunk;
  if (!buffer.includes('\0')) return;
  const response = JSON.parse(buffer.split('\0')[0]);
  console.log(JSON.stringify(response));
  if (response.status !== 'ok') process.exitCode = 1;
  socket.end();
});
socket.on('timeout', () => { socket.destroy(); process.exitCode = 1; });
socket.on('error', error => { console.error(error.message); process.exitCode = 1; });
