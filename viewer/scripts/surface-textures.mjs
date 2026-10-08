import sharp from 'sharp';
// Lightweight, source-palette approximations of UV-free tile/wood shaders.
// These are deliberately not represented as exact Round7 node-graph bakes.
export async function surfaceTexture(row){const p=row.parameters;let svg='';let scale=[1,1];
 if(row.kind==='tile'){const base=p.base,varc=p.varc||base,grout=p.grout||base;const sx=p.sx||.6,sy=p.sy||.6;scale=[1/sx,1/sy];const gx=Math.max(1,512*(p.gw||.003)/sx),gy=Math.max(1,512*(p.gw||.003)/sy);svg=`<defs><linearGradient id="tone"><stop stop-color="${base}"/><stop offset="1" stop-color="${varc}"/></linearGradient></defs><rect width="512" height="512" fill="url(#tone)"/><path d="M0 0H512M0 0V512" fill="none" stroke="${grout}" stroke-width="${Math.max(gx,gy)*2}"/>`;}
 else if(row.kind==='wood'||row.kind==='planks'){const dark=p.dark||p.base,light=p.light||p.base;svg=`<defs><linearGradient id="wood"><stop stop-color="${dark}"/><stop offset=".55" stop-color="${light}"/><stop offset="1" stop-color="${dark}"/></linearGradient></defs><rect width="512" height="512" fill="url(#wood)"/>`;for(let i=0;i<38;i++){const x=i*14;svg+=`<path d="M${x} 0 C${x+17} 150 ${x-14} 330 ${x} 512" fill="none" stroke="${dark}" stroke-width="${i%3===0?2:1}" opacity=".28"/>`;}if(row.kind==='planks'){scale=[1/(p.width||.19),1/(p.length||1.2)];svg+=`<path d="M0 0H512M0 0V512" stroke="${p.gap}" stroke-width="3"/>`;}}
 else return null;
 const data=await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">${svg}</svg>`)).png().toBuffer();return {data,scale};}
