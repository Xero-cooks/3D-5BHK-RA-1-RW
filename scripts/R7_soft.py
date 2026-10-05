# R7_soft.py - procedural soft goods (pillows, cushions, throws) for Round 7
import bpy, bmesh, math
from mathutils import Vector, Matrix, noise

def fab_mat(name, col, rough=0.88, sheen=0.55, weave=420.0, bump=0.35, slub=0.25):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.location = (600, 0)
    bs.inputs['Base Color'].default_value = (*col, 1)
    bs.inputs['Roughness'].default_value = rough
    for k, v in (('Sheen Weight', sheen), ('Sheen Roughness', 0.5), ('Specular IOR Level', 0.25)):
        if k in bs.inputs: bs.inputs[k].default_value = v
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.location = (-900, 0)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.location = (-700, 0)
    mp.inputs['Scale'].default_value = (weave, weave, weave)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    # plain weave: two crossed wave bands
    w1 = nt.nodes.new('ShaderNodeTexWave'); w1.location = (-450, 200)
    w1.wave_type = 'BANDS'; w1.bands_direction = 'X'; w1.inputs['Scale'].default_value = 1.0
    w1.inputs['Distortion'].default_value = 0.4; w1.inputs['Detail'].default_value = 0
    w2 = nt.nodes.new('ShaderNodeTexWave'); w2.location = (-450, 0)
    w2.wave_type = 'BANDS'; w2.bands_direction = 'Y'; w2.inputs['Scale'].default_value = 1.0
    w2.inputs['Distortion'].default_value = 0.4; w2.inputs['Detail'].default_value = 0
    nt.links.new(mp.outputs['Vector'], w1.inputs['Vector']); nt.links.new(mp.outputs['Vector'], w2.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; mx.location = (-250, 100)
    nt.links.new(w1.outputs['Fac'], mx.inputs[0]); nt.links.new(w2.outputs['Fac'], mx.inputs[1])
    # slubs / low frequency thread irregularity
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.location = (-450, -250)
    nz.inputs['Scale'].default_value = 60.0; nz.inputs['Detail'].default_value = 6
    nz.inputs['Roughness'].default_value = 0.6
    tc2 = nt.nodes.new('ShaderNodeMapping'); tc2.location = (-700, -250)
    tc2.inputs['Scale'].default_value = (1, 1, 1)
    nt.links.new(tc.outputs['Object'], tc2.inputs['Vector'])
    nt.links.new(tc2.outputs['Vector'], nz.inputs['Vector'])
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; ad.location = (-50, 0)
    nt.links.new(mx.outputs['Value'], ad.inputs[0])
    sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.location = (-250, -200)
    sc.inputs[1].default_value = slub / max(bump, 1e-3)
    nt.links.new(nz.outputs['Fac'], sc.inputs[0]); nt.links.new(sc.outputs['Value'], ad.inputs[1])
    bp = nt.nodes.new('ShaderNodeBump'); bp.location = (250, -100)
    bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.002
    nt.links.new(ad.outputs['Value'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], bs.inputs['Normal'])
    # subtle colour mottling
    mix = nt.nodes.new('ShaderNodeMixRGB'); mix.location = (350, 200)
    mix.inputs['Color1'].default_value = (*col, 1)
    mix.inputs['Color2'].default_value = (col[0]*0.72, col[1]*0.72, col[2]*0.72, 1)
    nt.links.new(nz.outputs['Fac'], mix.inputs['Fac'])
    nt.links.new(mix.outputs['Color'], bs.inputs['Base Color'])
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    return m

def _wrinkle(u, v, seed, amp):
    """radial creases from the four corners + soft crumple, returns signed offset 0..1 range"""
    s = 0.0
    for cx in (-1, 1):
        for cy in (-1, 1):
            dx, dy = u - cx, v - cy
            r = math.hypot(dx, dy)
            if r < 1e-4: continue
            th = math.atan2(dy * -cy, dx * -cx)       # angle measured into the pillow
            k = 7.0 + 2.0 * noise.noise(Vector((cx * 3 + seed, cy * 5, 0.3)))
            ph = 6.28 * noise.noise(Vector((cx * 1.7, cy * 2.3 + seed, 1.1)))
            env = math.exp(-r * 1.55)
            s += env * math.sin(th * k + ph) * (0.6 + 0.4 * noise.noise(Vector((th * 3, r * 2, seed))))
    s *= 0.5
    n1 = noise.fractal(Vector((u * 2.2 + seed, v * 2.2, 0.7)), 0.5, 2.0, 4)
    return amp * (s + 0.8 * n1)

def pillow(name, w=0.50, h=0.50, d=0.15, n=44, boxy=2.0, a=0.55, seed=1.0, wrinkle=0.012,
           mat=None, pipe_mat=None, pipe_r=0.0055, dimple=0.18, loc=(0, 0, 0), basis=None, coll=None):
    """returns the new object (pillow lying in XY, thickness along Z)."""
    bm = bmesh.new()
    verts = {}
    def idx(i, j):
        return (i, j)
    # build top and bottom as separate grids that are welded on the border
    layers = []
    for sgn in (1, -1):
        L = {}
        for i in range(n + 1):
            for j in range(n + 1):
                u = -1 + 2 * i / n; v = -1 + 2 * j / n
                fu = max(0.0, 1 - abs(u) ** boxy) ** a
                fv = max(0.0, 1 - abs(v) ** boxy) ** a
                prof = fu * fv
                z = (d / 2) * prof
                z -= dimple * (d / 2) * math.exp(-(u * u + v * v) * 5.0) * prof          # lived-in dent in the middle
                z += _wrinkle(u, v, seed, wrinkle) * prof ** 0.6 * 0.9
                z += 0.0025 * noise.fractal(Vector((u * 7 + seed * 3, v * 7, sgn * 0.5)), 0.5, 2.0, 3) * prof
                # fabric gets drawn in where the pillow is fat, corners get pulled up slightly
                pull = 1 - 0.10 * prof
                x = u * w / 2 * pull; y = v * h / 2 * pull
                border = (i in (0, n)) or (j in (0, n))
                if border:
                    key = ('b', i, j)
                    if key not in verts: verts[key] = bm.verts.new((x, y, 0.0))
                    L[(i, j)] = verts[key]
                else:
                    L[(i, j)] = bm.verts.new((x, y, sgn * z))
        layers.append(L)
    for si, L in enumerate(layers):
        for i in range(n):
            for j in range(n):
                f = [L[(i, j)], L[(i + 1, j)], L[(i + 1, j + 1)], L[(i, j + 1)]]
                if si == 1: f.reverse()
                try: bm.faces.new(f)
                except ValueError: pass
    bm.normal_update()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    sd = ob.modifiers.new('Sub', 'SUBSURF'); sd.levels = 1; sd.render_levels = 1
    if mat: ob.data.materials.append(mat)
    # piping along the seam
    if pipe_mat is not None:
        pb = bmesh.new(); pts = []
        for i in range(n): pts.append((i, 0))
        for j in range(n): pts.append((n, j))
        for i in range(n, 0, -1): pts.append((i, n))
        for j in range(n, 0, -1): pts.append((0, j))
        P = []
        for (i, j) in pts:
            u = -1 + 2 * i / n; v = -1 + 2 * j / n
            P.append(Vector((u * w / 2, v * h / 2, 0.0)))
        m = len(P); rings = []
        for k in range(m):
            t = (P[(k + 1) % m] - P[k - 1]).normalized()
            out_ = Vector((t.y, -t.x, 0.0))
            ring = []
            for q in range(8):
                ang = q * math.pi / 4
                pos = P[k] + out_ * (math.cos(ang) * pipe_r) + Vector((0, 0, math.sin(ang) * pipe_r))
                pos += noise.noise(Vector((k * 0.35 + seed, 2.0, 1.0))) * Vector((0, 0, 0.0015))
                ring.append(pb.verts.new(pos))
            rings.append(ring)
        for k in range(m):
            for q in range(8):
                pb.faces.new([rings[k][q], rings[k][(q + 1) % 8], rings[(k + 1) % m][(q + 1) % 8], rings[(k + 1) % m][q]])
        pb.normal_update()
        pm = bpy.data.meshes.new(name + '_pipe'); pb.to_mesh(pm); pb.free()
        po = bpy.data.objects.new(name + '_pipe', pm); (coll or bpy.context.scene.collection).objects.link(po)
        for p in pm.polygons: p.use_smooth = True
        po.data.materials.append(pipe_mat); po.parent = ob
    # placement
    M = Matrix.Translation(Vector(loc))
    if basis is not None: M = M @ basis.to_4x4()
    ob.matrix_world = M
    return ob

# ---------- island tools ----------
def island_list(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    seen = set(); res = []
    for v in bm.verts:
        if v.index in seen: continue
        st = [v]; seen.add(v.index); idxs = []
        while st:
            a = st.pop(); idxs.append(a.index)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen: seen.add(b.index); st.append(b)
        co = [o.matrix_world @ bm.verts[i].co for i in idxs]
        mn = Vector([min(c[i] for c in co) for i in range(3)]); mx = Vector([max(c[i] for c in co) for i in range(3)])
        res.append((idxs, mn, mx))
    bm.free(); return res

def delete_islands(o, idx_lists):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    vs = [bm.verts[i] for L in idx_lists for i in L]
    bmesh.ops.delete(bm, geom=vs, context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()

def base_col(m):
    if m is None: return (0.8, 0.8, 0.8)
    if 'r7_col' in m.keys():
        c = m['r7_col']; return tuple(c)[:3]
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                return tuple(n.inputs['Base Color'].default_value)[:3]
    return (0.8, 0.8, 0.8)

def soft_pass(oname, coll, kind='bed', seedbase=1.0, log=None):
    """replace soft-good islands inside mesh object oname by generated pillows / duvets"""
    o = bpy.data.objects[oname]
    mat0 = o.data.materials[0] if o.data.materials else None
    pattern = mat0 is not None and any(k in mat0.name.lower() for k in ('mandala', 'floral', 'stripe'))
    col = base_col(mat0)
    fm = mat0 if pattern else fab_mat('R7_Fab_' + (mat0.name if mat0 else 'x') , col)
    dark = tuple(max(0.0, c * 0.18) for c in col) if sum(col) > 1.8 else tuple(min(1.0, c * 0.2 + 0.78) for c in col)
    pm = fab_mat('R7_Pipe_' + (mat0.name if mat0 else 'x'), dark, rough=0.7, sheen=0.3)
    kill = []; made = []
    k = 0
    for idxs, mn, mx in island_list(o):
        d = mx - mn; dims = sorted([d.x, d.y, d.z], reverse=True)
        a, b, c = dims
        if c >= 0.2 and a >= 1.5: continue                      # mattress / base - keep
        cen = (mn + mx) / 2
        k += 1; seed = seedbase + k * 1.7
        if a >= 1.1 and c <= 0.3 and kind == 'bed':             # duvet / throw
            w, h = (d.x, d.y)
            ob = pillow(oname + '_duvet%d' % k, w=w, h=h, d=max(c, 0.09) * 1.25, n=56, boxy=7.0, a=0.35, seed=seed,
                        wrinkle=0.016, dimple=0.0, mat=fm, pipe_mat=None, loc=(cen.x, cen.y, mn.z + max(c, 0.09) * 0.62), coll=coll)
        elif a <= 1.05 and c <= 0.42 and d.z <= 0.42:           # pillow / cushion
            lx, ly = (d.x, d.y)
            rot = Matrix.Identity(3) if lx >= ly else Matrix.Rotation(math.pi / 2, 3, 'Z')
            w, h = max(lx, ly), min(lx, ly)
            th = max(d.z, 0.12) * 1.5
            piped = (k % 2 == 0)
            ob = pillow(oname + '_pillow%d' % k, w=w * 1.03, h=h * 1.03, d=th, n=40, boxy=2.0, a=0.55, seed=seed, wrinkle=0.012,
                        mat=fm, pipe_mat=pm if piped else None, loc=(cen.x, cen.y, mn.z + th * 0.5 - 0.01), basis=rot, coll=coll)
        else:
            continue
        kill.append(idxs); made.append(ob.name)
    if kill: delete_islands(o, kill)
    return made
