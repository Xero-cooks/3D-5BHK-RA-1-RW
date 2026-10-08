import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {
  Box3,
  BufferGeometry,
  LoadingManager,
  Mesh,
  MeshStandardMaterial,
  Object3D,
  Texture,
  Vector3,
} from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import {downloadBinary, DownloadOptions} from './download';
export async function loadGLB(url:string,onProgress:(loaded:number,total:number)=>void,options:DownloadOptions & {onDecode?:(done:number,total:number)=>void}={}){
 const data=await downloadBinary(url,onProgress,options);
 if(options.signal?.aborted)throw options.signal.reason;
 options.onDecode?.(0,0);
 // Yield before decoding so the completed download/next phase actually paints.
 await new Promise(resolve=>setTimeout(resolve,20));
 const manager=new LoadingManager();manager.onProgress=(_,done,total)=>options.onDecode?.(done,total);
 const result=await new GLTFLoader(manager).parseAsync(data.buffer as ArrayBuffer,new URL('.',new URL(url,typeof location==='undefined'?'http://localhost':location.href)).href);
 if(options.signal?.aborted)throw options.signal.reason;
 return result;
}
// Tile + material batching reduces draw submissions without deleting architecture.
// Transparent/transmissive/multi-material objects keep original ordering and geometry.
export async function optimizeScene(scene: Object3D) {
  scene.updateMatrixWorld(true);
  const groups = new Map<string, Mesh[]>();
  const center = new Vector3();
  let meshes = 0;
  const textures = new Set<Texture>();
  scene.traverse((o) => {
    if (!(o instanceof Mesh)) return;
    meshes++;
    for (const mat of Array.isArray(o.material) ? o.material : [o.material])
      for (const value of Object.values(mat))
        if (value instanceof Texture) textures.add(value);
    if (Array.isArray(o.material)) return;
    const m = o.material as MeshStandardMaterial & { transmission?: number };
    o.receiveShadow = true;
    o.castShadow = !m.transparent;
    if (
      m.transparent ||
      m.transmission ||
      o.geometry.morphAttributes.position?.length
    )
      return;
    new Box3().setFromObject(o).getCenter(center);
    const key = [
      m.uuid,
      Math.floor(center.x / 12),
      Math.floor(center.z / 12),
      Math.floor(center.y / 4),
    ].join(":");
    groups.set(key, [...(groups.get(key) || []), o]);
  });
  const triangleCount = () => {
    let n = 0;
    scene.traverse((o) => {
      if (o instanceof Mesh)
        n +=
          (o.geometry.index?.count ||
            o.geometry.getAttribute("position").count) / 3;
    });
    return n;
  };
  const trianglesBefore = triangleCount();
  let batches = 0;
  for (const list of groups.values()) {
    if (list.length < 2) continue;
    const geometries: BufferGeometry[] = list.map((m) =>
      m.geometry.clone().applyMatrix4(m.matrixWorld),
    );
    // Attributes differ for some asset meshes; merge only compatible layouts.
    const compatible = new Map<
      string,
      { meshes: Mesh[]; geometries: BufferGeometry[] }
    >();
    geometries.forEach((g, i) => {
      const key =
        Object.keys(g.attributes)
          .sort()
          .map(
            (k) =>
              `${k}:${g.attributes[k].itemSize}:${g.attributes[k].normalized}`,
          )
          .join("|") + Boolean(g.index);
      const entry = compatible.get(key) || { meshes: [], geometries: [] };
      entry.meshes.push(list[i]);
      entry.geometries.push(g);
      compatible.set(key, entry);
    });
    for (const { meshes: ms, geometries: gs } of compatible.values()) {
      if (ms.length > 1) {
        const g = mergeGeometries(gs, false);
        if (g) {
          const batch = new Mesh(g, ms[0].material);
          batch.name = `RuntimeBatch_${batches++}`;
          batch.castShadow = true;
          batch.receiveShadow = true;
          scene.add(batch);
          ms.forEach((m) => {
            for (const child of [...m.children]) scene.attach(child);
            m.removeFromParent();
          });
        }
      }
      gs.forEach((g) => g.dispose());
    }
    if (batches % 20 === 0) await new Promise((r) => setTimeout(r, 0));
  }
  let textureBytes = 0;
  for (const t of textures) {
    const image = t.image as { width?: number; height?: number };
    textureBytes += ((image?.width || 0) * (image?.height || 0) * 4 * 4) / 3;
  }
  const trianglesAfter = triangleCount();
  if (Math.abs(trianglesBefore - trianglesAfter) > 0.01)
    throw Error(
      `Runtime batching lost visible geometry (${trianglesBefore} => ${trianglesAfter})`,
    );
  return {
    trianglesBefore,
    trianglesAfter,
    sourceMeshes: meshes,
    batches,
    textures: textures.size,
    estimatedTextureMiB: Math.round(textureBytes / 1048576),
  };
}
