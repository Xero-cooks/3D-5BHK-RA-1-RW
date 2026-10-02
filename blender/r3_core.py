"""Round 3 core - primitive mesh kit + item system for 3D-5BHK-RA-1-RW (main residence focus).
Units metres. Local item frame: origin = back-centre of the item on the floor, +Y = into the room, +Z up.
Rotation: face 'N' (rot 0) = item stands against a SOUTH wall looking north; 'E' looks east (against a west wall) ...
"""
import bpy, bmesh, math, sys, random
from mathutils import Vector, Matrix, Euler

CTX = {'coll': None, 'par': None, 'room': '', 'fl': '', 'tag': 'r3'}
REG = []
ROT = {'N': 0.0, 'E': -90.0, 'S': 180.0, 'W': 90.0}
SMOOTH_THR = 0.95

# key: (rgb, rough, metal, emit, alpha)
PAL = {
 'wood_dark': ((0.10, 0.045, 0.02), 0.42), 'wood_med': ((0.30, 0.15, 0.065), 0.45), 'wood_light': ((0.50, 0.33, 0.18), 0.5),
 'wood_teak': ((0.36, 0.19, 0.08), 0.4), 'lam_cream': ((0.62, 0.56, 0.45), 0.45), 'lam_grey': ((0.26, 0.245, 0.23), 0.5),
 'lam_white': ((0.80, 0.78, 0.72), 0.4), 'granite_brown': ((0.17, 0.12, 0.075), 0.22), 'granite_grey': ((0.22, 0.22, 0.23), 0.25),
 'mosaic': ((0.50, 0.42, 0.32), 0.35), 'steel': ((0.62, 0.62, 0.64), 0.3, 1.0), 'chrome': ((0.85, 0.85, 0.88), 0.12, 1.0),
 'brass': ((0.78, 0.52, 0.18), 0.28, 1.0), 'black_glass': ((0.008, 0.008, 0.01), 0.08), 'black_plastic': ((0.02, 0.02, 0.022), 0.4),
 'black_metal': ((0.02, 0.022, 0.025), 0.4, 0.8), 'graphite': ((0.12, 0.125, 0.135), 0.35, 0.6),
 'ceramic': ((0.86, 0.86, 0.84), 0.08), 'plastic_white': ((0.78, 0.78, 0.76), 0.35), 'paint_white': ((0.82, 0.81, 0.78), 0.7),
 'fab_grey': ((0.20, 0.20, 0.21), 0.95), 'fab_charcoal': ((0.07, 0.07, 0.08), 0.95), 'fab_cream': ((0.62, 0.55, 0.42), 0.95),
 'fab_white': ((0.78, 0.76, 0.72), 0.95), 'fab_mustard': ((0.55, 0.33, 0.05), 0.95), 'fab_ochre': ((0.42, 0.22, 0.04), 0.95),
 'fab_teal': ((0.03, 0.25, 0.27), 0.95), 'fab_maroon': ((0.22, 0.025, 0.03), 0.95), 'fab_floral': ((0.55, 0.5, 0.40), 0.95),
 'fab_mandala': ((0.62, 0.30, 0.12), 0.95), 'fab_brown': ((0.12, 0.07, 0.04), 0.9), 'fab_taupe': ((0.30, 0.26, 0.22), 0.95),
 'fab_black_floral': ((0.05, 0.045, 0.045), 0.9), 'fab_green': ((0.06, 0.16, 0.06), 0.95),
 'wicker': ((0.74, 0.72, 0.66), 0.7), 'cane': ((0.42, 0.28, 0.14), 0.7), 'terracotta': ((0.42, 0.16, 0.07), 0.8), 'clay_dark': ((0.2, 0.09, 0.05), 0.8),
 'leaf': ((0.04, 0.20, 0.035), 0.55), 'leaf_dark': ((0.02, 0.11, 0.03), 0.55), 'leaf_light': ((0.12, 0.30, 0.05), 0.55),
 'leaf_yellow': ((0.30, 0.34, 0.05), 0.55), 'leaf_red': ((0.35, 0.05, 0.04), 0.55), 'trunk': ((0.14, 0.10, 0.07), 0.9),
 'palm_trunk': ((0.30, 0.27, 0.22), 0.85), 'soil': ((0.06, 0.03, 0.02), 0.95), 'flower_pink': ((0.60, 0.08, 0.25), 0.6), 'flower_orange': ((0.75, 0.25, 0.03), 0.6),
 'glass': ((0.55, 0.75, 0.90), 0.02, 0.0, 0.0, 0.25), 'glass_dark': ((0.05, 0.08, 0.09), 0.02, 0.0, 0.0, 0.45), 'frosted': ((0.7, 0.8, 0.85), 0.3, 0.0, 0.0, 0.55),
 'mirror': ((0.55, 0.58, 0.62), 0.02, 1.0), 'emit_white': ((1.0, 1.0, 0.95), 0.5, 0.0, 6.0), 'emit_warm': ((1.0, 0.7, 0.35), 0.5, 0.0, 5.0),
 'rug_red': ((0.30, 0.025, 0.035), 0.97), 'rug_pink': ((0.55, 0.12, 0.17), 0.97), 'rug_cream': ((0.55, 0.50, 0.40), 0.97), 'rug_blue': ((0.06, 0.10, 0.22), 0.97),
 'teal_trim': ((0.02, 0.27, 0.32), 0.4), 'green_rail': ((0.025, 0.09, 0.055), 0.4, 0.7), 'red_plastic': ((0.45, 0.02, 0.02), 0.35), 'yellow_plastic': ((0.7, 0.5, 0.03), 0.35),
 'blue_plastic': ((0.03, 0.12, 0.45), 0.35), 'pink_plastic': ((0.65, 0.2, 0.3), 0.35), 'purple_plastic': ((0.2, 0.04, 0.25), 0.35), 'cardboard': ((0.42, 0.25, 0.1), 0.9),
 'tile_grey': ((0.18, 0.18, 0.19), 0.2), 'tile_cream': ((0.65, 0.6, 0.5), 0.2), 'tile_white': ((0.78, 0.78, 0.75), 0.15),
 'marble_white': ((0.80, 0.80, 0.78), 0.12), 'stone_grey': ((0.28, 0.28, 0.29), 0.7), 'stone_laterite': ((0.38, 0.14, 0.07), 0.9),
 'brick_red': ((0.35, 0.12, 0.08), 0.85), 'concrete': ((0.35, 0.35, 0.34), 0.9), 'tank_black': ((0.015, 0.015, 0.018), 0.45), 'pvc_grey': ((0.45, 0.45, 0.46), 0.5),
 'paper': ((0.8, 0.78, 0.7), 0.8), 'art_blue': ((0.05, 0.12, 0.25), 0.5), 'art_ochre': ((0.45, 0.28, 0.08), 0.5), 'art_red': ((0.35, 0.05, 0.04), 0.5), 'white_ceiling': ((0.9, 0.9, 0.88), 0.8),
 'car_white': ((0.8, 0.8, 0.78), 0.25, 0.3), 'rubber': ((0.01, 0.01, 0.01), 0.8), 'gold_leaf': ((0.7, 0.5, 0.1), 0.3, 1.0), 'olive_leaf': ((0.14, 0.2, 0.05), 0.55),
 'grass_dry': ((0.28, 0.30, 0.08), 0.9), 'hedge': ((0.03, 0.15, 0.03), 0.8), 'water': ((0.1, 0.35, 0.7), 0.05, 0.0, 0.0, 0.6),
}


def M(key):
    nm = 'R3_' + key
    m = bpy.data.materials.get(nm)
    if m:
        return m
    p = PAL[key]
    col = p[0]; rough = p[1] if len(p) > 1 else 0.6; met = p[2] if len(p) > 2 else 0.0
    em = p[3] if len(p) > 3 else 0.0; al = p[4] if len(p) > 4 else 1.0
    m = bpy.data.materials.new(nm)
    m.diffuse_color = (col[0], col[1], col[2], al)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (col[0], col[1], col[2], 1)
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = met
        b.inputs['Alpha'].default_value = al
        if em > 0:
            b.inputs['Emission Color'].default_value = (col[0], col[1], col[2], 1)
            b.inputs['Emission Strength'].default_value = em
    if al < 1:
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    return m


def ctx(coll, par, room='', fl='', tag='r3'):
    CTX.update(coll=coll, par=par, room=room, fl=fl, tag=tag)


class Item:
    def __init__(s, name, x=0.0, y=0.0, z=0.0, face='N', kind='floor', rotdeg=None):
        s.name = name; s.p = Vector((x, y, z + (0.022 if kind == 'rug' else 0.0))); s.kind = kind
        s.rot = math.radians(ROT[face] if rotdeg is None else rotdeg)
        s.bms = {}

    def _b(s, m):
        if m not in s.bms:
            s.bms[m] = bmesh.new()
        return s.bms[m]

    # ---------------- primitives (local coordinates)
    def box(s, m, x0, x1, y0, y1, z0, z1, bev=0.0, seg=2, rot=None, spin=None):
        b = s._b(m)
        before = set(b.verts)
        vs = [b.verts.new((X, Y, Z)) for Z in (z0, z1) for Y in (y0, y1) for X in (x0, x1)]
        fs = [b.faces.new([vs[i] for i in q]) for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5))]
        bmesh.ops.recalc_face_normals(b, faces=fs)
        if rot:
            R = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix()
            bmesh.ops.rotate(b, cent=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), matrix=R, verts=vs)
        if bev > 0:
            r = min(bev, min(x1 - x0, y1 - y0, z1 - z0) / 2 * 0.95)
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(b, geom=es, offset=r, segments=seg, affect='EDGES', profile=0.5)
        if spin:
            deg, scx, scy = spin
            nv = [v for v in b.verts if v not in before]
            bmesh.ops.rotate(b, cent=(scx, scy, 0), matrix=Matrix.Rotation(math.radians(deg), 3, 'Z'), verts=nv)

    def ring_pts(s, c, u, v, r, seg, a0=0.0):
        return [c + u * (r * math.cos(a0 + 2 * math.pi * i / seg)) + v * (r * math.sin(a0 + 2 * math.pi * i / seg)) for i in range(seg)]

    def rod(s, m, p0, p1, r, r2=None, seg=10, cap=True):
        b = s._b(m)
        p0 = Vector(p0); p1 = Vector(p1)
        d = p1 - p0
        if d.length < 1e-6:
            return
        d.normalize()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.99 else Vector((1, 0, 0))
        u = d.cross(up).normalized(); v = d.cross(u).normalized()
        r2 = r if r2 is None else r2
        A = [b.verts.new(p) for p in s.ring_pts(p0, u, v, r, seg)]
        B = [b.verts.new(p) for p in s.ring_pts(p1, u, v, r2, seg)]
        for i in range(seg):
            j = (i + 1) % seg
            b.faces.new([A[i], A[j], B[j], B[i]])
        if cap:
            if r > 1e-5:
                b.faces.new(A[::-1])
            if r2 > 1e-5:
                b.faces.new(B)

    def cyl(s, m, cx, cy, z0, z1, r, r2=None, seg=16, cap=True):
        s.rod(m, (cx, cy, z0), (cx, cy, z1), r, r2, seg, cap)

    def lathe(s, m, prof, cx=0.0, cy=0.0, z=0.0, seg=20, sx=1.0, sy=1.0, cap_top=False, cap_bot=False):
        b = s._b(m)
        rings = []
        for (r, h) in prof:
            if r < 1e-5:
                rings.append([b.verts.new((cx, cy, z + h))])
            else:
                rings.append([b.verts.new((cx + r * sx * math.cos(2 * math.pi * i / seg), cy + r * sy * math.sin(2 * math.pi * i / seg), z + h)) for i in range(seg)])
        for a, c in zip(rings, rings[1:]):
            for i in range(seg):
                j = (i + 1) % seg
                if len(a) == 1 and len(c) == 1:
                    continue
                if len(a) == 1:
                    b.faces.new([a[0], c[j], c[i]])
                elif len(c) == 1:
                    b.faces.new([a[i], a[j], c[0]])
                else:
                    b.faces.new([a[i], a[j], c[j], c[i]])
        if cap_bot and len(rings[0]) > 1:
            b.faces.new(rings[0][::-1])
        if cap_top and len(rings[-1]) > 1:
            b.faces.new(rings[-1])

    def sph(s, m, cx, cy, cz, r, sx=1.0, sy=1.0, sz=1.0, seg=12, rings=8):
        prof = [(r * math.sin(math.pi * k / rings), -r * sz * math.cos(math.pi * k / rings)) for k in range(rings + 1)]
        s.lathe(m, prof, cx, cy, cz, seg, sx, sy)

    def poly(s, m, pts, z0, z1, bev=0.0):
        b = s._b(m)
        A = [b.verts.new((x, y, z0)) for x, y in pts]
        B = [b.verts.new((x, y, z1)) for x, y in pts]
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            b.faces.new([A[i], A[j], B[j], B[i]])
        b.faces.new(A[::-1]); b.faces.new(B)

    def mesh(s, m, verts, faces):
        b = s._b(m)
        vs = [b.verts.new(v) for v in verts]
        for f in faces:
            try:
                b.faces.new([vs[i] for i in f])
            except ValueError:
                pass

    def grid(s, m, P, thick=0.0):
        """P: rows of 3D points (list of lists). Quad surface; optional solidify."""
        b = s._b(m)
        V = [[b.verts.new(p) for p in row] for row in P]
        fs = []
        for i in range(len(V) - 1):
            for j in range(len(V[0]) - 1):
                fs.append(b.faces.new([V[i][j], V[i][j + 1], V[i + 1][j + 1], V[i + 1][j]]))
        if thick > 0:
            bmesh.ops.solidify(b, geom=fs, thickness=thick)

    def loft(s, m, path, radii, seg=8, cap=True):
        b = s._b(m)
        path = [Vector(p) for p in path]
        rings = []
        prev_u = None
        for i, p in enumerate(path):
            if i == 0:
                t = path[1] - path[0]
            elif i == len(path) - 1:
                t = path[-1] - path[-2]
            else:
                t = path[i + 1] - path[i - 1]
            t.normalize()
            if prev_u is None:
                up = Vector((0, 0, 1)) if abs(t.z) < 0.99 else Vector((1, 0, 0))
                u = t.cross(up).normalized()
            else:
                u = (prev_u - t * prev_u.dot(t)).normalized()
            v = t.cross(u).normalized()
            prev_u = u
            r = radii[i] if isinstance(radii, (list, tuple)) else radii
            rings.append([b.verts.new(q) for q in s.ring_pts(p, u, v, r, seg)])
        for a, c in zip(rings, rings[1:]):
            for i in range(seg):
                j = (i + 1) % seg
                b.faces.new([a[i], a[j], c[j], c[i]])
        if cap:
            b.faces.new(rings[0][::-1]); b.faces.new(rings[-1])

    def leaf(s, m, base, direction, length, width, droop=0.3, rise=0.1, rows=5, up=(0, 0, 1)):
        """curved blade with V-fold; direction horizontal-ish vector."""
        b = s._b(m)
        base = Vector(base); d = Vector(direction).normalized()
        side = d.cross(Vector(up)).normalized()
        if side.length < 1e-4:
            side = Vector((1, 0, 0))
        prev = None
        rowsv = []
        for k in range(rows + 1):
            t = k / rows
            pos = base + d * (length * t) + Vector((0, 0, 1)) * (rise * length * math.sin(t * math.pi * 0.5) - droop * length * t * t)
            w = width * math.sin(math.pi * min(1.0, 0.18 + 0.82 * t)) * (1 - 0.15 * t) if k < rows else 0.0
            fold = 0.22 * w
            rowsv.append((b.verts.new(pos - side * w / 2 + Vector((0, 0, fold))), b.verts.new(pos + Vector((0, 0, fold * 1.8))), b.verts.new(pos + side * w / 2 + Vector((0, 0, fold)))))
        for r0, r1_ in zip(rowsv, rowsv[1:]):
            for q in ((0, 1), (1, 2)):
                try:
                    b.faces.new([r0[q[0]], r0[q[1]], r1_[q[1]], r1_[q[0]]])
                except ValueError:
                    pass

    # ---------------- finish
    def finish(s, coll=None, par=None, props=None):
        coll = coll or CTX['coll']; par = par or CTX['par']
        T = Matrix.Translation(s.p) @ Matrix.Rotation(s.rot, 4, 'Z')
        mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
        parts = []
        for m, b in s.bms.items():
            if not b.verts:
                b.free(); continue
            bmesh.ops.recalc_face_normals(b, faces=b.faces)
            for f in b.faces:
                f.smooth = True
            for e in b.edges:
                if len(e.link_faces) == 2:
                    try:
                        e.smooth = e.calc_face_angle(0.0) < SMOOTH_THR
                    except Exception:
                        e.smooth = True
            for v in b.verts:
                w = T @ v.co
                mn = Vector((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
                mx = Vector((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
            me = bpy.data.meshes.new(f'{s.name}.{m}')
            b.to_mesh(me); b.free()
            me.materials.append(M(m))
            parts.append((m, me))
        s.bms = {}
        if not parts:
            return None
        props = dict(props or {})
        props.update({CTX['tag']: 1, 'room': CTX['room'], 'floor': CTX['fl'], 'kind': s.kind})
        if len(parts) == 1:
            ob = bpy.data.objects.new(s.name, parts[0][1])
            top = ob
            ob.matrix_world = T
            coll.objects.link(ob)
            if par:
                ob.parent = par
                ob.matrix_parent_inverse = par.matrix_world.inverted()
        else:
            top = bpy.data.objects.new(s.name, None)
            top.empty_display_type = 'PLAIN_AXES'; top.empty_display_size = 0.12
            top.matrix_world = T
            coll.objects.link(top)
            if par:
                top.parent = par
                top.matrix_parent_inverse = par.matrix_world.inverted()
            for m, me in parts:
                ob = bpy.data.objects.new(f'{s.name}.{m}', me)
                coll.objects.link(ob)
                ob.parent = top
        for k, v in props.items():
            top[k] = v
        REG.append({'name': s.name, 'room': CTX['room'], 'fl': CTX['fl'], 'kind': s.kind,
                    'bb': (mn.x, mx.x, mn.y, mx.y, mn.z, mx.z)})
        return top


def sub_coll(parent, name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        parent.children.link(c)
    return c
