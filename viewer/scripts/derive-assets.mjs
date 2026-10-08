import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
import {Mesh,MeshBasicMaterial,BoxGeometry,Group,Box3,BufferGeometry,Float32BufferAttribute} from 'three';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {unpackGLB,packGLB,geometryScene,components,linearHex} from './gltf-tools.mjs';
import {surfaceTexture} from './surface-textures.mjs';
import {projectMissingUVs} from './project-texture-uv.mjs';
const source=process.env.WEB_SOURCE_DIRECTORY||'.asset-cache';const output='public/assets';mkdirSync(output,{recursive:true});mkdirSync('reports',{recursive:true});
const palette=JSON.parse(readFileSync('scripts/source-material-palette.json','utf8'));
const original=readFileSync(`${source}/farmhouse_visual.glb`);const {json,bin}=unpackGLB(original);const repaired=[];const unresolved=[];
for(const mat of json.materials){
 const p=mat.pbrMetallicRoughness||={};if(p.baseColorTexture||p.baseColorFactor)continue;const row=palette[mat.name];
 if(!row){unresolved.push(mat.name);continue;}
 let color=row.linearColor||linearHex(row.parameters.base||row.parameters.hexc||row.parameters.h1||row.parameters.c1||row.parameters.dark||row.parameters.field||row.parameters.deep||row.colors[0]);
 if(row.piping){const sum=color.reduce((a,b)=>a+b,0);color=color.map(c=>sum>1.8?c*.18:Math.min(1,c*.2+.78));}
 p.baseColorFactor=[...color,1];p.metallicFactor=row.parameters.metallic??row.parameters.metal??0;if(typeof row.parameters.rough==='number')p.roughnessFactor=row.parameters.rough;
 mat.extras={...(mat.extras||{}),webSurface:{kind:row.kind,colors:row.colors,parameters:row.parameters,source:row.source}};
 if(row.kind==='glass'){p.baseColorFactor[3]=mat.name.includes('Smoked')?.32:.14;p.roughnessFactor=mat.name.includes('Frosted')?.4:.1;mat.alphaMode='BLEND';mat.doubleSided=true;}
 repaired.push({name:mat.name,source:row.source,kind:row.kind});
}
const imageBuffers=new Map();let sourceImageBytes=0,derivedImageBytes=0;
for(const image of json.images){const view=json.bufferViews[image.bufferView];const input=bin.subarray(view.byteOffset||0,(view.byteOffset||0)+view.byteLength);sourceImageBytes+=input.length;const metadata=await sharp(input).metadata();const resized=sharp(input).resize({width:1024,height:1024,fit:'inside',withoutEnlargement:true});
 const data=metadata.hasAlpha?await resized.png({compressionLevel:9}).toBuffer():await resized.jpeg({quality:90,chromaSubsampling:'4:4:4'}).toBuffer();image.mimeType=metadata.hasAlpha?'image/png':'image/jpeg';imageBuffers.set(image.bufferView,data);derivedImageBytes+=data.length;
}
const buffers=[];let offset=0;
for(let i=0;i<json.bufferViews.length;i++){const view=json.bufferViews[i];const data=imageBuffers.get(i)||bin.subarray(view.byteOffset||0,(view.byteOffset||0)+view.byteLength);const pad=(4-offset%4)%4;if(pad){buffers.push(Buffer.alloc(pad));offset+=pad;}view.byteOffset=offset;view.byteLength=data.length;view.buffer=0;buffers.push(data);offset+=data.length;}
let simplifiedSurfaces=0;json.textures||=[];json.samplers||=[];
for(const repairedMat of repaired){const mat=json.materials.find(m=>m.name===repairedMat.name);const texture=await surfaceTexture(palette[mat.name]);if(!texture)continue;
 const pad=(4-offset%4)%4;if(pad){buffers.push(Buffer.alloc(pad));offset+=pad;}
 const view=json.bufferViews.length;json.bufferViews.push({buffer:0,byteOffset:offset,byteLength:texture.data.length});buffers.push(texture.data);offset+=texture.data.length;
 const image=json.images.length;json.images.push({bufferView:view,mimeType:'image/png',name:mat.name+'_SourceApproximation'});
 const sampler=json.samplers.length;json.samplers.push({wrapS:10497,wrapT:10497,magFilter:9729,minFilter:9987});const index=json.textures.length;json.textures.push({sampler,source:image});
 mat.pbrMetallicRoughness.baseColorFactor=[1,1,1,1];mat.pbrMetallicRoughness.baseColorTexture={index,extensions:{KHR_texture_transform:{scale:texture.scale}}};simplifiedSurfaces++;
}
json.extensionsUsed=[...new Set([...(json.extensionsUsed||[]),'KHR_texture_transform'])];
json.buffers=[{byteLength:offset}];json.asset.extras={source:'Round7 web export, original geometry retained',webDerivative:'source-defined palette recovery + 1024px embedded textures'};
const projection=projectMissingUVs(json,Buffer.concat(buffers));
writeFileSync(`${output}/farmhouse_visual.glb`,packGLB(json,projection.bin));
// Decode ONLY structural geometry offline to repair the separate collision asset.
// Never feed the render scene, furniture, door leaves or vegetation to physics.
const visual=await geometryScene(original);const old=await geometryScene(readFileSync(`${source}/farmhouse_collision.glb`));const collision=new Group();collision.name='WEB_COLLISION_REPAIRED';const material=new MeshBasicMaterial();const measured=[];
function copy(o,name){const g=o.geometry.clone().applyMatrix4(o.matrixWorld);const mesh=new Mesh(g,material);mesh.name=name;collision.add(mesh);}
function box(name,min,max){if(max.some((v,i)=>v-min[i]<.0001))return;const g=new BoxGeometry(...max.map((v,i)=>v-min[i]));g.translate(...max.map((v,i)=>(v+min[i])/2));const mesh=new Mesh(g,material);mesh.name=name;collision.add(mesh);}
function subtract(bounds,hole){const lo=bounds.min.map((v,i)=>Math.max(v,hole.min[i]));const hi=bounds.max.map((v,i)=>Math.min(v,hole.max[i]));if(lo.some((v,i)=>v>=hi[i]))return [bounds];const result=[];const m=[...bounds.min],M=[...bounds.max];for(let axis=0;axis<3;axis++){if(m[axis]<lo[axis]){const end=[...M];end[axis]=lo[axis];result.push({min:[...m],max:end});m[axis]=lo[axis];}if(M[axis]>hi[axis]){const start=[...m];start[axis]=hi[axis];result.push({min:start,max:[...M]});M[axis]=hi[axis];}}return result;}
const stairData={};for(const key of ['Main','Roof','Club']){const wood=visual.getObjectByName(`R7_Stair${key}_wood`);if(!wood)throw Error(`Missing measured ${key} stairs`);const parts=components(wood);const groups=new Map();for(const p of parts){const k=[p.min[0],p.max[0]].map(v=>v.toFixed(3)).join(':');groups.set(k,[...(groups.get(k)||[]),p]);}const flights=[...groups.values()].filter(g=>g.length>=4);const landing=parts.find(p=>p.max[2]-p.min[2]>1&&p.max[0]-p.min[0]>2);if(flights.length!==2||!landing)throw Error('Unrecognized stair structure; refusing guessed ramps');const ext=new Box3().setFromObject(wood);stairData[key]={flights,landing,bounds:{min:ext.min.toArray(),max:ext.max.toArray()}};}
const roof=visual.getObjectByName('Res_ROOF_Slab');const roofTop=roof?new Box3().setFromObject(roof).max.y:7;
old.traverse(o=>{if(!(o instanceof Mesh))return;if(o.name.startsWith('COL_Wall')||o.name.startsWith('COL_Ramp'))return;
 const b=new Box3().setFromObject(o);let pieces=[{min:b.min.toArray(),max:b.max.toArray()}];
 if(o.name==='COL_Floor_Res_FF'){const s=stairData.Main.bounds;pieces=pieces.flatMap(p=>subtract(p,{min:[s.min[0]-.01,-100,s.min[2]-.01],max:[s.max[0]+.01,100,s.max[2]+.01]}));}
 if(o.name==='COL_Floor_Club_FF'){const s=stairData.Club.bounds;pieces=pieces.flatMap(p=>subtract(p,{min:[s.min[0]-.01,-100,s.min[2]-.01],max:[s.max[0]+.01,100,s.max[2]+.01]}));}
 if(o.name==='COL_Pool_Block'){box(o.name,[6,-1.4,14],[30,1,26]);return;}
 pieces.forEach((p,i)=>box(o.name+(pieces.length>1?`_Part${i}`:''),p.min,p.max));
});
let actualWalls=0;visual.traverse(o=>{if(!(o instanceof Mesh))return;
 if(/^(Res|Club|Pav)_WALL_/.test(o.name)){copy(o,'COL_Actual_'+o.name);actualWalls++;}
 if(/^Res_STEP_|^Res_PORCH_Slab$|^Pav_STEP_Veranda$|^Res_ROOF_Slab$/.test(o.name)){copy(o,'COL_Support_'+o.name);measured.push(o.name);}
});
if(actualWalls<35)throw Error('Not enough actual architecture walls; refusing incomplete collision');
for(const [key,data] of Object.entries(stairData)){
 const low=key==='Roof'?3.82:.62;const high=key==='Main'?3.82:key==='Roof'?roofTop:4.52;
 const landing=data.landing;box(`COL_MeasuredLanding_${key}`,landing.min,landing.max);
 const ordered=data.flights.sort((a,b)=>Math.min(...a.map(p=>p.min[1]))-Math.min(...b.map(p=>p.min[1])));
 for(let f=0;f<ordered.length;f++){const steps=ordered[f].sort((a,b)=>a.max[1]-b.max[1]);const first=steps[0],last=steps.at(-1);const sign=Math.sign((last.min[2]+last.max[2])-(first.min[2]+first.max[2]));const z0=f===0?(sign<0?first.max[2]:first.min[2]):(sign<0?landing.min[2]:landing.max[2]);const z1=f===0?(sign<0?landing.max[2]:landing.min[2]):(sign<0?last.min[2]:last.max[2]);const y0=f===0?low:landing.max[1],y1=f===0?landing.max[1]:high;const x0=first.min[0],x1=first.max[0];const slope=Math.atan2(y1-y0,Math.abs(z1-z0))*180/Math.PI;if(slope>41)throw Error(`${key} measured slope ${slope} too steep`);
 const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute([x0,y0,z0,x1,y0,z0,x0,y1,z1,x1,y0,z0,x1,y1,z1,x0,y1,z1],3));g.computeVertexNormals();const m=new Mesh(g,material);m.name=`COL_MeasuredRamp_${key}_${f+1}`;collision.add(m);measured.push({name:m.name,x0,x1,z0,z1,y0,y1,slope});}
}
// GLTFExporter uses FileReader even in Node. This adapter reads local Blob data only.
globalThis.FileReader=class {readAsArrayBuffer(blob){blob.arrayBuffer().then(result=>{this.result=result;this.onloadend?.();});}};
const collisionBuffer=await new GLTFExporter().parseAsync(collision,{binary:true});writeFileSync(`${output}/farmhouse_collision.glb`,Buffer.from(collisionBuffer));
const spawns=JSON.parse(readFileSync(`${source}/spawn_points.json`));spawns.spawns.find(s=>s.name==='SPAWN_ENTRANCE').yawDeg=0;spawns.spawns.find(s=>s.name==='SPAWN_ENTRANCE').pos[2]=.06;
const pool=spawns.spawns.find(s=>s.name==='SPAWN_POOL');pool.pos=[17,-12,.08];
writeFileSync(`${output}/spawn_points.json`,JSON.stringify(spawns));const rooms=JSON.parse(readFileSync(`${source}/room_metadata.json`));rooms.rooms.find(r=>r.room==='pool-deck').bounds={min:[2,-29,-.05],max:[32,-11,3]};writeFileSync(`${output}/room_metadata.json`,JSON.stringify(rooms));
const manifest={sourceCommit:'309f90e525a28975980f043c259c57ce773a2976',derivative:'source colors, smaller textures, actual wall apertures, measured stair ramps',assets:[]};for(const name of ['farmhouse_visual.glb','farmhouse_collision.glb','spawn_points.json','room_metadata.json']){const b=readFileSync(`${output}/${name}`);manifest.assets.push({name,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')});}writeFileSync('scripts/runtime-asset-manifest.json',JSON.stringify(manifest,null,2)+'\n');
const report={geometryPreserved:true,projectedTexturePrimitives:projection.repaired,simplifiedSourceSurfaces:simplifiedSurfaces,sourceBytes:original.length,derivedBytes:manifest.assets[0].bytes,sourceImageBytes,derivedImageBytes,materialsRepaired:repaired,unresolvedMaterials:unresolved,actualWallMeshes:actualWalls,collisionMeshes:collision.children.length,measuredSupports:measured,stairBounds:Object.fromEntries(Object.entries(stairData).map(([key,data])=>[key,data.bounds])),blendAvailable:false,exactRound7ProceduralBake:'Pending actual .blend and external/packed texture availability'};writeFileSync('reports/asset-repair.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({sourceMiB:original.length/1048576,derivedMiB:manifest.assets[0].bytes/1048576,imagesMiB:derivedImageBytes/1048576,repairedMaterials:repaired.length,unresolved,actualWalls,collisionMeshes:collision.children.length,measured:measured.filter(x=>typeof x==='object')},null,2));
