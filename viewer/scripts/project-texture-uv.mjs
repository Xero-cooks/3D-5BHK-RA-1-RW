import {Matrix4,Vector3,Quaternion,Matrix3} from 'three';
// The original procedural shaders used box/world projection rather than UVs.
// Preserve authored UVs. Supply a lightweight metre-scale box projection only
// where a retained image has no texture coordinates. This is not a Blender bake.
export function projectMissingUVs(json,bin){
 const matrices=new Map();function visit(i,parent){const n=json.nodes[i];const local=n.matrix?new Matrix4().fromArray(n.matrix):new Matrix4().compose(new Vector3().fromArray(n.translation||[0,0,0]),new Quaternion().fromArray(n.rotation||[0,0,0,1]),new Vector3().fromArray(n.scale||[1,1,1]));const world=parent.clone().multiply(local);if(n.mesh!==undefined&&!matrices.has(n.mesh))matrices.set(n.mesh,world);for(const c of n.children||[])visit(c,world);}
 for(const i of json.scenes[json.scene||0].nodes)visit(i,new Matrix4());
 let offset=bin.length;const buffers=[bin];let repaired=0;
 function reader(index){const a=json.accessors[index],v=json.bufferViews[a.bufferView];if(a.componentType!==5126||a.type!=='VEC3')throw Error('Unexpected projection accessor');const start=(v.byteOffset||0)+(a.byteOffset||0),stride=v.byteStride||12;return i=>new Vector3(bin.readFloatLE(start+i*stride),bin.readFloatLE(start+i*stride+4),bin.readFloatLE(start+i*stride+8));}
 json.meshes.forEach((mesh,index)=>{const matrix=matrices.get(index)||new Matrix4(),normalMatrix=new Matrix3().getNormalMatrix(matrix);for(const primitive of mesh.primitives){if(primitive.attributes.TEXCOORD_0!==undefined||!json.materials[primitive.material]?.pbrMetallicRoughness?.baseColorTexture)continue;
 const position=reader(primitive.attributes.POSITION);const normal=primitive.attributes.NORMAL===undefined?null:reader(primitive.attributes.NORMAL);const count=json.accessors[primitive.attributes.POSITION].count;const data=Buffer.alloc(count*8);
 for(let i=0;i<count;i++){const p=position(i).applyMatrix4(matrix);const n=normal?normal(i).applyNormalMatrix(normalMatrix):new Vector3(0,1,0);const ax=Math.abs(n.x),ay=Math.abs(n.y),az=Math.abs(n.z);let u,v;if(ay>=ax&&ay>=az){u=p.x;v=-p.z;}else if(ax>=az){u=-p.z;v=p.y;}else{u=p.x;v=p.y;}data.writeFloatLE(u,i*8);data.writeFloatLE(v,i*8+4);}
 const pad=(4-offset%4)%4;if(pad){buffers.push(Buffer.alloc(pad));offset+=pad;}const view=json.bufferViews.length;json.bufferViews.push({buffer:0,byteOffset:offset,byteLength:data.length,target:34962});offset+=data.length;buffers.push(data);primitive.attributes.TEXCOORD_0=json.accessors.length;json.accessors.push({bufferView:view,componentType:5126,count,type:'VEC2'});repaired++;
 }});json.buffers=[{byteLength:offset}];return {bin:Buffer.concat(buffers),repaired};
}
