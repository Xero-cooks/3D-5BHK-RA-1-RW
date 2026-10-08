import { Mesh, Object3D, Texture } from "three";
const originalImages = new WeakMap<
  Texture,
  TexImageSource & { width: number; height: number }
>();
const resized = new WeakMap<object, Map<number, HTMLCanvasElement>>();
export function setTextureQuality(scene: Object3D, maximum: number) {
  const textures = new Set<Texture>();
  scene.traverse((o) => {
    if (!(o instanceof Mesh)) return;
    for (const m of Array.isArray(o.material) ? o.material : [o.material])
      for (const v of Object.values(m))
        if (v instanceof Texture) textures.add(v);
  });
  let bytes = 0;
  for (const t of textures) {
    let original = originalImages.get(t);
    const source = t.image as
      (TexImageSource & { width: number; height: number }) | undefined;
    if (!original && source?.width) {
      original = source;
      originalImages.set(t, original!);
    }
    if (!original) continue;
    const size = Math.max(original.width, original.height);
    let image: TexImageSource = original;
    if (size > maximum) {
      const cache = resized.get(original) || new Map();
      let c = cache.get(maximum);
      if (!c) {
        c = document.createElement("canvas");
        c.width = Math.max(1, Math.round((original.width * maximum) / size));
        c.height = Math.max(1, Math.round((original.height * maximum) / size));
        c.getContext("2d")!.drawImage(original, 0, 0, c.width, c.height);
        cache.set(maximum, c);
        resized.set(original, cache);
      }
      image = c;
    }
    if (t.image !== image) {
      t.image = image;
      t.needsUpdate = true;
    }
    const i = t.image as { width: number; height: number };
    bytes += (i.width * i.height * 4 * 4) / 3;
  }
  // Upper-bound estimate; GPU may share uploads across texture instances.
  return Math.round(bytes / 1048576);
}
