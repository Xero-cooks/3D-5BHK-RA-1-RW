import {PMREMGenerator,WebGLRenderer,Scene,Vector3,DataTexture,RGBAFormat,FloatType,EquirectangularReflectionMapping,Color} from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
// No network HDR dependency. These are baseline lighting environments, not exact
// surveyed room reflections or a claim to restore the missing Blender HDRI.
export function createReflectionEnvironments(renderer:WebGLRenderer){
 const pmrem=new PMREMGenerator(renderer);const room=new RoomEnvironment();
 const interior=pmrem.fromScene(room,.03,.1,100,{size:128});room.dispose();
 const panorama=createDaylightPanorama();
 const exterior=pmrem.fromEquirectangular(panorama);panorama.dispose();pmrem.dispose();
 return {interior:interior.texture,exterior:exterior.texture,dispose(){interior.dispose();exterior.dispose();}};
}
export function reflectionZone(p:{x:number;y:number;z:number}){
 const residence=p.x>=0&&p.x<=24&&p.z>=-14&&p.z<=0&&p.y<6.7;
 const club=p.x>=32&&p.x<=48&&p.z>=10&&p.z<=26&&p.y<7.8;
 const pavilion=p.x>=-34&&p.x<=-22&&p.z>=22&&p.z<=32&&p.y<4;
 return residence||club||pavilion?'interior':'exterior';
}
export function transmissionScale(quality:'LOW'|'MEDIUM'|'HIGH'|'ULTRA'){return quality==='LOW'?.35:quality==='MEDIUM'?.5:1;}

export function createDaylightPanorama(){
 // Bounded analytic HDR radiance avoids Three's atmospheric sky's very high
 // physical radiance washing out the house when captured with no exposure.
 const width=512,height=256,pixels=new Float32Array(width*height*4);
 const sky=new Color('#b8d0e3'),ground=new Color('#9b886d'),sun=new Vector3(20,45,15).normalize();
 for(let y=0;y<height;y++){const elevation=((y+.5)/height-.5)*Math.PI,dy=Math.sin(elevation),r=Math.cos(elevation);const t=Math.max(0,Math.min(1,(dy+.12)/.35));const mix=t*t*(3-2*t);
  for(let x=0;x<width;x++){const azimuth=((x+.5)/width-.5)*Math.PI*2;const dot=r*Math.cos(azimuth)*sun.x+dy*sun.y+r*Math.sin(azimuth)*sun.z;const glow=8*Math.exp(400*(dot-1));const i=(y*width+x)*4;
   pixels[i]=ground.r*(1-mix)+sky.r*mix+glow;pixels[i+1]=ground.g*(1-mix)+sky.g*mix+glow*.93;pixels[i+2]=ground.b*(1-mix)+sky.b*mix+glow*.8;pixels[i+3]=1;
  }
 }
 const panorama=new DataTexture(pixels,width,height,RGBAFormat,FloatType);panorama.mapping=EquirectangularReflectionMapping;panorama.needsUpdate=true;
 return panorama;

}
