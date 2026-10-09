export function unpackGLB(buffer: Buffer): {json: any;bin: Buffer};
export function packGLB(json: any,bin: Buffer): Buffer;
export function geometryScene(buffer: Buffer): Promise<import('three').Object3D>;
export function linearHex(hex: string): number[];
export function components(mesh: import('three').Mesh): {min:number[];max:number[]}[];
