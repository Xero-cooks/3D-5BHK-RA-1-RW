import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
export function unpackGLB(buffer){const length=buffer.readUInt32LE(12);return {json:JSON.parse(buffer.toString('utf8',20,20+length)),bin:buffer.subarray(28+length)};}
export function packGLB(json,bin){const text=Buffer.from(JSON.stringify(json));const padded=Buffer.alloc(Math.ceil(text.length/4)*4,32);text.copy(padded);const body=Buffer.alloc(Math.ceil(bin.length/4)*4);bin.copy(body);const h=Buffer.alloc(20);h.write('glTF');h.writeUInt32LE(2,4);h.writeUInt32LE(28+padded.length+body.length,8);h.writeUInt32LE(padded.length,12);h.writeUInt32LE(0x4e4f534a,16);const bh=Buffer.alloc(8);bh.writeUInt32LE(body.length);bh.writeUInt32LE(0x004e4942,4);return Buffer.concat([h,padded,bh,body]);}
export async function geometryScene(buffer){const {json,bin}=unpackGLB(buffer);function strip(o){for(const k of Object.keys(o)){if(k.toLowerCase().endsWith('texture'))delete o[k];else if(o[k]&&typeof o[k]==='object')strip(o[k]);}}json.materials?.forEach(strip);delete json.images;delete json.textures;delete json.samplers;const b=packGLB(json,bin);const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');gltf.scene.updateMatrixWorld(true);return gltf.scene;}
export function linearHex(hex){return hex.match(/[a-f\d]{2}/gi).map(x=>{const c=parseInt(x,16)/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;});}
export function components(mesh){
 const g=mesh.geometry.clone().applyMatrix4(mesh.matrixWorld),p=g.getAttribute('position'),ix=g.index?.array||Array.from({length:p.count},(_,i)=>i);const parent=Array.from({length:p.count},(_,i)=>i);
 function find(i){while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;}
 function union(a,b){a=find(a);b=find(b);if(a!==b)parent[a]=b;}
 const weld=new Map();for(let i=0;i<p.count;i++){const key=[p.getX(i),p.getY(i),p.getZ(i)].map(v=>Math.round(v*100000)).join(':');if(weld.has(key))union(i,weld.get(key));else weld.set(key,i);}
 for(let i=0;i<ix.length;i+=3){union(ix[i],ix[i+1]);union(ix[i],ix[i+2]);}
 const result=new Map();for(let i=0;i<p.count;i++){const key=find(i);const b=result.get(key)||{min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};const v=[p.getX(i),p.getY(i),p.getZ(i)];for(let a=0;a<3;a++){b.min[a]=Math.min(b.min[a],v[a]);b.max[a]=Math.max(b.max[a],v[a]);}result.set(key,b);}
 g.dispose();return [...result.values()];
}
