import RAPIER from "@dimforge/rapier3d-compat";
import { Mesh, Object3D, Vector3 } from "three";
import { Spawn, worldPosition } from "./metadata";
let initialization: Promise<void> | undefined;
export async function createPhysics(scene: Object3D) {
  await (initialization ??= RAPIER.init());
  const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
  scene.updateMatrixWorld(true);
  let count = 0;
  scene.traverse((o) => {
    if (!(o instanceof Mesh)) return;
    const g = o.geometry.clone().applyMatrix4(o.matrixWorld);
    const p = g.getAttribute("position");
    const vertices = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) {
      vertices[i * 3] = p.getX(i);
      vertices[i * 3 + 1] = p.getY(i);
      vertices[i * 3 + 2] = p.getZ(i);
    }
    const indices = g.index
      ? new Uint32Array(g.index.array)
      : Uint32Array.from({ length: p.count }, (_, i) => i);
    world.createCollider(
      RAPIER.ColliderDesc.trimesh(
        vertices,
        indices,
        RAPIER.TriMeshFlags.FIX_INTERNAL_EDGES_TWO_SIDED,
      ),
    );
    g.dispose();
    count++;
  });
  const body = world.createRigidBody(
    RAPIER.RigidBodyDesc.kinematicPositionBased(),
  );
  // Radius .35, total height 1.8, center .9 above feet.
  const capsule = world.createCollider(
    RAPIER.ColliderDesc.capsule(0.55, 0.35),
    body,
  );
  const controller = world.createCharacterController(0.025);
  controller.setUp({ x: 0, y: 1, z: 0 });
  controller.setSlideEnabled(true);
  controller.setMaxSlopeClimbAngle((42 * Math.PI) / 180);
  controller.setMinSlopeSlideAngle((46 * Math.PI) / 180);
  controller.enableAutostep(0.3, 0.2, true);
  controller.enableSnapToGround(0.25);
  let velocityY = 0;
  let last: Spawn;
  let grounded = false;
  function teleport(spawn: Spawn) {
    last = spawn;
    velocityY = 0;
    const p = worldPosition(spawn.pos);
    body.setTranslation({ x: p.x, y: p.y + 0.94, z: p.z }, true);
    body.setNextKinematicTranslation(body.translation());
    world.step();
    grounded = false;
  }
  function step(dx: number, dz: number, dt: number) {
    velocityY = grounded ? 0 : Math.max(velocityY - 9.81 * dt, -30);
    controller.computeColliderMovement(capsule, {
      x: dx,
      y: velocityY * dt,
      z: dz,
    });
    const movement = controller.computedMovement();
    grounded = controller.computedGrounded();
    const p = body.translation();
    body.setNextKinematicTranslation({
      x: p.x + movement.x,
      y: p.y + movement.y,
      z: p.z + movement.z,
    });
    world.timestep = dt;
    world.step();
    if (body.translation().y < -2 && last) teleport(last);
    return {
      grounded,
      collisions: controller.numComputedCollisions(),
      feet: feet(),
    };
  }
  function feet() {
    const p = body.translation();
    return new Vector3(p.x, p.y - 0.9, p.z);
  }
  return {
    world,
    body,
    capsule,
    controller,
    count,
    teleport,
    step,
    feet,
    dispose() {
      world.removeCharacterController(controller);
      world.free();
    },
  };
}
export type PlayerPhysics = Awaited<ReturnType<typeof createPhysics>>;
