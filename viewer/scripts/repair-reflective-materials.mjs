// Repair lost procedural scalar parameters from the tracked Blender library.
// Never clear or replace image textures; no architecture changes.
export function repairReflectiveMaterials(json,palette){const repairs=[];
 for(const mat of json.materials){const source=palette[mat.name];if(!source)continue;const p=mat.pbrMetallicRoughness||={};const s=source.parameters;const changed=[];
  if(typeof s.rough==='number'&&p.roughnessFactor===undefined&&!p.metallicRoughnessTexture){p.roughnessFactor=s.rough;changed.push('roughness');}
  if(source.kind==='metal'&&p.metallicFactor===undefined){p.metallicFactor=s.metallic??s.metal??1;changed.push('metallic');}
  if(typeof s.coat==='number'&&s.coat>0&&!mat.extensions?.KHR_materials_clearcoat){(mat.extensions||={}).KHR_materials_clearcoat={clearcoatFactor:s.coat,clearcoatRoughnessFactor:.1};changed.push('clearcoat');}
  if(source.kind==='glass'){
   // Source clear/smoked are Transparent+Glossy Fresnel node graphs, not exportable
   // as glTF Principled. Frosted is already Principled transmission. The handoff
   // explicitly prescribes transmission=1, thickness=.02 and ior=1.5.
   p.metallicFactor=0;p.roughnessFactor=s.frosted?.28:Math.max(s.rough||0,.01);
   const tint=source.colors[0];const rgb=tint.match(/[a-f\d]{2}/gi).map(x=>{const c=parseInt(x,16)/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;});
   // Absorption handles tint over thickness; opaque surface stays white so dark
   // smoked tint is not incorrectly multiplied into both Fresnel and background.
   p.baseColorFactor=[1,1,1,1];mat.alphaMode='OPAQUE';mat.doubleSided=true;
   Object.assign(mat.extensions||={}, {KHR_materials_transmission:{transmissionFactor:1},KHR_materials_ior:{ior:s.frosted?1.45:1.5},KHR_materials_volume:{thicknessFactor:.02,attenuationColor:rgb,attenuationDistance:s.smoked?.15:1}});
   mat.extras={...(mat.extras||{}),webReflectiveSurface:{kind:'glass',source:'blender/r4_mat.py glass() + WEB_ASSET_HANDOFF.md section 8'}};changed.push('transmission','volume','ior');
  }
  if(changed.length)repairs.push({name:mat.name,changed});
 }
 const used=new Set(json.extensionsUsed||[]);for(const m of json.materials)for(const name of Object.keys(m.extensions||{}))used.add(name);json.extensionsUsed=[...used];return repairs;
}
