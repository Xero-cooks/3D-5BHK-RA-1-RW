import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createPhysics} from '../lib/physics';
import {Spawn} from '../lib/metadata';
const spawns=JSON.parse(readFileSync('public/assets/spawn_points.json','utf8')).spawns as Spawn[];
async function physics(){const b=readFileSync('public/assets/farmhouse_collision.glb');return createPhysics((await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')).scene);}
function spawn(x:number,z:number,y:number):Spawn{return {...spawns[0],pos:[x,-z,y]};}
function move(p:Awaited<ReturnType<typeof physics>>,x:number,z:number){for(let i=0;i<400;i++){const q=p.feet();const dx=x-q.x,dz=z-q.z,d=Math.hypot(dx,dz);if(d<.07)break;p.step(dx/d*.035,dz/d*.035,1/60);}return p.feet();}
function settle(p:Awaited<ReturnType<typeof physics>>){for(let i=0;i<120;i++)p.step(0,0,1/60);}
test('actual front door and porch steps allow entry, adjacent wall still blocks',async()=>{const p=await physics();p.teleport(spawn(12,-19,.06));settle(p);let q=move(p,12,-12);assert.ok(q.z>-13,`Front door blocked at ${q.toArray()}`);assert.ok(q.y>.55,`Porch not supported ${q.toArray()}`);p.teleport(spawn(10,-15,.62));settle(p);q=move(p,10,-12);assert.ok(q.z<-14,`Adjacent wall failed ${q.toArray()}`);p.dispose();});
test('all supplied room spawns have supporting floors',async()=>{const p=await physics();for(const s of spawns){p.teleport(s);settle(p);assert.ok(p.feet().y>=s.pos[2]-.2,`${s.name} unsupported: ${p.feet().toArray()}`);}p.dispose();});
const stairs=[{name:'Main',x1:15.8,x2:18.5,z0:-8.3,z1:-12,z2:-8.5,low:.62,high:3.82},{name:'Roof',x1:20.6,x2:23,z0:-8.95,z1:-12,z2:-8.95,low:3.82,high:7},{name:'Club',x1:33.7,x2:35.7,z0:15.5,z1:11.6,z2:15.5,low:.62,high:4.52}];
for(const s of stairs)test(`measured ${s.name} stairs: up, landing, down`,async()=>{const p=await physics();p.teleport(spawn(s.x1,s.z0,s.low));settle(p);const points=[[s.x1,s.z1],[s.x2,s.z1],[s.x2,s.z2]];for(const [x,z] of points)move(p,x,z);settle(p);let q=p.feet();assert.ok(q.y>s.high-.18,`${s.name} ascent failed: ${q.toArray()}`);for(const [x,z] of [[s.x2,s.z1],[s.x1,s.z1],[s.x1,s.z0]])move(p,x,z);if(s.name==='Club'){move(p,34.95,15.5);}settle(p);q=p.feet();assert.ok(Math.abs(q.y-s.low)<.2,`${s.name} descent failed: ${q.toArray()}`);p.dispose();});
test('interior doors on both floors are walk-through',async()=>{const p=await physics();for(const d of [{x:15,z:-5,y:.62},{x:22.75,z:-5,y:.62},{x:5.25,z:-5,y:3.82},{x:11.5,z:-5,y:3.82}]){p.teleport(spawn(d.x,d.z-1,d.y));settle(p);const q=move(p,d.x,d.z+1);assert.ok(q.z>d.z+.6,`Door at ${d.x},${d.z} blocked ${q.toArray()}`);}p.dispose();});
