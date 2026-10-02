"""Round 2 - architectural reconstruction of the MAIN RESIDENCE only.
Builds on r1_foundation (module 'r1' must be loaded). Non-destructive: only adds objects / modifiers.
"""
import bpy, bmesh, sys, math
from mathutils import Vector

r1 = sys.modules['r1']
FFL = {'GF': 0.6, 'FF': 3.8, 'RF': 7.0}
CASED = ('HallCorr', 'FoyerOpen', 'StairOpen', 'LandingOpen', 'MumtyOpen')


def init():
    r1._colls()
    mats = {'BLK_Frame': (0.10, 0.12, 0.16), 'BLK_Glass': (0.55, 0.75, 0.90), 'BLK_Door_Wood': (0.36, 0.21, 0.11),
            'BLK_Stone_Sill': (0.72, 0.72, 0.70), 'BLK_Railing': (0.12, 0.28, 0.18), 'BLK_Ceiling': (0.97, 0.97, 0.95),
            'BLK_Cove': (0.93, 0.92, 0.88), 'BLK_Niche_Panel': (0.78, 0.70, 0.56)}
    for n, c in mats.items():
        r1._mat(n, c)
    g = bpy.data.materials['BLK_Glass']
    g.diffuse_color = (0.55, 0.75, 0.90, 0.35)
    try:
        g.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.3
    except Exception:
        pass
    return 'r2 init ok'


def W(o, c, u0, u1, d0, d1, z0, z1):
    return (u0, u1, c + d0, c + d1, z0, z1) if o == 'H' else (c + d0, c + d1, u0, u1, z0, z1)


def bars(name, segs, w, coll, par, mat):
    verts, faces = [], []
    for p0, p1 in segs:
        p0 = Vector(p0); p1 = Vector(p1)
        d = (p1 - p0).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.99 else Vector((1, 0, 0))
        n1 = d.cross(up).normalized(); n2 = d.cross(n1).normalized()
        i = len(verts)
        for p in (p0, p1):
            for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                verts.append(p + n1 * s1 * w / 2 + n2 * s2 * w / 2)
        faces += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7)]
        faces += [(i + k, i + (k + 1) % 4, i + 4 + (k + 1) % 4, i + 4 + k) for k in range(4)]
    o = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v - o) for v in verts], [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = o
    return r1.link(ob, coll, par, mat, {'r2': 1})


# ------------------------------------------------------------------ roof terrace + mumty
def roof_terrace():
    C, par = r1.C, r1.BLD['RES']
    cu = bpy.data.objects['Res_CUT_Door_FF_StairOpen']
    cu.location.x += 2.3
    b = list(cu['bbox']); b[0] += 2.3; b[1] += 2.3; cu['bbox'] = b
    bpy.data.objects['Res_ROOM_FF_Utility2']['room_name'] = 'Roof Stair Hall'
    r1.stair_u('RES', 'FF_Roof', 20.0, 21.2, 22.4, 23.6, 9.0, 1, 3.8, 5.4, 7.0, 9, 0.28, 11.52, 13.6, 20.0, 23.6)
    void = r1.box('Res_CUT_RoofStairVoid', 19.9, 23.7, 9.05, 13.9, 6.7, 7.1, C['ROOF'], par)
    void.display_type = 'WIRE'; void.hide_render = True
    m = bpy.data.objects['Res_ROOF_Slab'].modifiers.new('RoofStairVoid', 'BOOLEAN')
    m.operation = 'DIFFERENCE'; m.object = void; m.solver = 'EXACT'
    void.hide_set(True)
    h = 0.115
    walls = {}
    spec = {'S': (19.5 - h, 24 + h, 8.5 - h, 8.5 + h), 'N': (19.5 - h, 24 + h, 14 - h, 14 + h),
            'W': (19.5 - h, 19.5 + h, 8.5 - h, 14 + h), 'E': (24 - h, 24 + h, 8.5 - h, 14 + h)}
    for k, (x0, x1, y0, y1) in spec.items():
        walls[k] = r1.box(f'Res_WALL_RF_Mumty_{k}', x0, x1, y0, y1, 7.0, 9.3, C['WALL'], par, 'BLK_Wall_Exterior',
                          is_wall=1, bld='RES', floor='RF', bbox=[x0, x1, y0, y1, 7.0, 9.3], r2=1)
    d = r1.cutter('RES', 'RF', 'H', 8.5, 22.5, 23.5, 0, 2.2, 'MumtyOpen', 7.0)
    w = r1.cutter('RES', 'RF', 'H', 14, 21.0, 23.0, 1.0, 1.8, 'MumtyWin', 7.0)
    for wall, cut in ((walls['S'], d), (walls['N'], w)):
        mm = wall.modifiers.new('Open_' + cut.name, 'BOOLEAN')
        mm.operation = 'DIFFERENCE'; mm.object = cut; mm.solver = 'EXACT'
        cut.hide_set(True)
    r1.box('Res_ROOF_MumtySlab', 19.2, 24.22, 8.35, 14.22, 9.3, 9.5, C['ROOF'], par, 'BLK_Slab_Concrete', r2=1)
    z0, z1 = 7.9, 7.96
    for nm, bx in (('S', (-0.27, 24.27, -0.27, -0.04)), ('N', (-0.27, 24.27, 14.08, 14.27)),
                   ('W', (-0.27, -0.04, -0.04, 14.08)), ('E', (24.04, 24.27, -0.04, 14.08))):
        r1.box(f'Res_ROOF_Coping_{nm}', bx[0], bx[1], bx[2], bx[3], z0, z1, C['ROOF'], par, 'BLK_Slab_Concrete', r2=1)
    return 'roof terrace + mumty ok'


# ------------------------------------------------------------------ door / window fixtures
def fixtures():
    C, par = r1.C, r1.BLD['RES']
    cuts = [o for o in bpy.data.objects if o.get('cutter') and o.get('bld') == 'RES']
    n = 0
    for cu in cuts:
        b = list(cu['bbox'])
        parts = cu.name.split('_')
        kind, fl, nm = parts[2], parts[3], '_'.join(parts[4:])
        ffl = FFL[fl]
        if abs((b[3] - b[2]) - 0.6) < 1e-3:
            o = 'H'; c = (b[2] + b[3]) / 2; u0, u1 = b[0], b[1]
        else:
            o = 'V'; c = (b[0] + b[1]) / 2; u0, u1 = b[2], b[3]
        z0, z1 = b[4], b[5]
        ext = (o == 'H' and (abs(c) < 1e-6 or abs(c - 14) < 1e-6)) or (o == 'V' and (abs(c) < 1e-6 or abs(c - 24) < 1e-6))
        t = 0.23 if (ext or fl == 'RF') else 0.115
        s = -1 if abs(c) < 1e-6 else 1
        tag = f'{fl}_{nm}'
        if kind == 'Window':
            fw, fd = 0.05, 0.07
            bx = [W(o, c, u0, u0 + fw, -fd / 2, fd / 2, z0, z1), W(o, c, u1 - fw, u1, -fd / 2, fd / 2, z0, z1),
                  W(o, c, u0, u1, -fd / 2, fd / 2, z1 - fw, z1), W(o, c, u0, u1, -fd / 2, fd / 2, z0, z0 + fw)]
            npan = max(1, round((u1 - u0) / 0.9))
            for k in range(1, npan):
                um = u0 + (u1 - u0) * k / npan
                bx.append(W(o, c, um - 0.02, um + 0.02, -fd / 2, fd / 2, z0, z1))
            r1.multibox(f'Res_FRAME_Window_{tag}', bx, C['WIN'], par, 'BLK_Frame', r2=1)
            r1.box(f'Res_GLASS_Window_{tag}', *W(o, c, u0 + fw, u1 - fw, -0.006, 0.006, z0 + fw, z1 - fw), C['WIN'], par, 'BLK_Glass', r2=1)
            if ext:
                dd = sorted((s * (t / 2 - 0.03), s * (t / 2 + 0.10)))
                r1.box(f'Res_SILL_Window_{tag}', *W(o, c, u0 - 0.05, u1 + 0.05, dd[0], dd[1], z0 - 0.04, z0), C['EXT'], par, 'BLK_Stone_Sill', r2=1)
        elif 'Slider' in nm:
            fw, fd = 0.06, 0.08
            um = (u0 + u1) / 2
            bx = [W(o, c, u0, u0 + fw, -fd / 2, fd / 2, z0, z1), W(o, c, u1 - fw, u1, -fd / 2, fd / 2, z0, z1),
                  W(o, c, u0, u1, -fd / 2, fd / 2, z1 - fw, z1), W(o, c, u0, u1, -fd / 2, fd / 2, z0, z0 + 0.05),
                  W(o, c, um - 0.03, um + 0.03, -fd / 2, fd / 2, z0 + 0.05, z1 - fw)]
            r1.multibox(f'Res_FRAME_Slider_{tag}', bx, C['DOOR'], par, 'BLK_Frame', r2=1)
            gl = [W(o, c, u0 + fw, um + 0.03, -0.032, -0.02, z0 + 0.05, z1 - fw), W(o, c, um - 0.03, u1 - fw, 0.02, 0.032, z0 + 0.05, z1 - fw)]
            r1.multibox(f'Res_GLASS_Slider_{tag}', gl, C['DOOR'], par, 'BLK_Glass', r2=1)
        else:
            cw, D = 0.07, t / 2 + 0.01
            bx = [W(o, c, u0, u0 + cw, -D, D, z0, z1), W(o, c, u1 - cw, u1, -D, D, z0, z1), W(o, c, u0, u1, -D, D, z1 - cw, z1)]
            r1.multibox(f'Res_FRAME_Door_{tag}', bx, C['DOOR'], par, 'BLK_Door_Wood' if nm not in CASED else 'BLK_Cove', r2=1)
            if nm not in CASED:
                if nm == 'MainEntrance':
                    um = (u0 + u1) / 2
                    lv = [W(o, c, u0 + cw + 0.005, um - 0.005, -0.025, 0.025, z0 + 0.01, z1 - cw),
                          W(o, c, um + 0.005, u1 - cw - 0.005, -0.025, 0.025, z0 + 0.01, z1 - cw)]
                else:
                    lv = [W(o, c, u0 + cw + 0.005, u1 - cw - 0.005, -0.02, 0.02, z0 + 0.01, z1 - cw)]
                r1.multibox(f'Res_DOOR_Leaf_{tag}', lv, C['DOOR'], par, 'BLK_Door_Wood', r2=1)
        n += 1
    return f'fixtures for {n} openings'


# ------------------------------------------------------------------ ceilings + cove
def ceilings():
    C, par = r1.C, r1.BLD['RES']
    rooms = [o for o in bpy.data.objects if o.get('room_type') and o.parent == par]
    n = 0
    for ro in rooms:
        x0, x1, y0, y1, z0, top = list(ro['bbox'])
        fl, key = ro['floor'], ro.name.split('_')[-1]
        if (fl == 'GF' and key == 'Stair') or (fl == 'FF' and key == 'Utility2'):
            continue
        r1.box(f'Res_CEILING_{fl}_{key}', x0, x1, y0, y1, top - 0.03, top, C['CEIL'], par, 'BLK_Ceiling', r2=1)
        n += 1
        if ro['room_type'] in ('living', 'bed'):
            i, wd, zb, zt = 0.06, 0.12, top - 0.15, top - 0.03
            bx = [(x0 + i, x1 - i, y0 + i, y0 + i + wd, zb, zt), (x0 + i, x1 - i, y1 - i - wd, y1 - i, zb, zt),
                  (x0 + i, x0 + i + wd, y0 + i + wd, y1 - i - wd, zb, zt), (x1 - i - wd, x1 - i, y0 + i + wd, y1 - i - wd, zb, zt)]
            r1.multibox(f'Res_COVE_{fl}_{key}', bx, C['CEIL'], par, 'BLK_Cove', r2=1)
    return f'{n} ceilings'


# ------------------------------------------------------------------ railings
def _stair_rail(name, x, ys, ydir, zf, n, tread, rise, coll, par):
    ye = ys + ydir * n * tread
    rail = [((x, ys, zf + 0.9), (x, ye, zf + 0.9 + n * rise))]
    rail += [((x, ys, zf), (x, ys, zf + 0.9 + 0.0)), ((x, ye, zf + n * rise), (x, ye, zf + n * rise + 0.9))]
    bars(name + '_Rail', rail, 0.06, coll, par, 'BLK_Railing')
    bal = []
    for i in range(0, n, 2):
        ym = ys + ydir * (i + 0.5) * tread
        bal.append(((x, ym, zf + (i + 1) * rise), (x, ym, zf + 0.9 + rise * (i + 0.5))))
    bars(name + '_Balusters', bal, 0.02, coll, par, 'BLK_Railing')


def railings():
    C, par = r1.C, r1.BLD['RES']
    R = C['RAIL']
    y, zb, zt = -1.95, 3.8, 4.8
    xs = [-0.05 + 24.1 * i / 12 for i in range(13)]
    frame = [((x, y, zb), (x, y, zt)) for x in xs] + [((xs[0], y, zt), (xs[-1], y, zt)), ((xs[0], y, zb + 0.15), (xs[-1], y, zb + 0.15))]
    inf = []
    for i in range(12):
        inf += [((xs[i], y, zb + 0.15), (xs[i + 1], y, zt)), ((xs[i], y, zt), (xs[i + 1], y, zb + 0.15))]
    ys = [-1.95, -1.0, -0.15]
    for xr in (-0.05, 24.05):
        frame += [((xr, v, zb), (xr, v, zt)) for v in ys] + [((xr, ys[0], zt), (xr, ys[-1], zt)), ((xr, ys[0], zb + 0.15), (xr, ys[-1], zb + 0.15))]
        for i in range(2):
            inf += [((xr, ys[i], zb + 0.15), (xr, ys[i + 1], zt)), ((xr, ys[i], zt), (xr, ys[i + 1], zb + 0.15))]
    bars('Res_RAILING_FF_Balcony_Frame', frame, 0.05, R, par, 'BLK_Railing')
    bars('Res_RAILING_FF_Balcony_Diagonals', inf, 0.02, R, par, 'BLK_Railing')
    rise, tread = 1.6 / 9, 0.28
    _stair_rail('Res_RAILING_Stair_GF_A', 16.45, 9.0, 1, 0.6, 9, tread, rise, R, par)
    _stair_rail('Res_RAILING_Stair_GF_B', 17.75, 11.52, -1, 2.2, 9, tread, rise, R, par)
    _stair_rail('Res_RAILING_Stair_Roof_A', 21.15, 9.0, 1, 3.8, 9, tread, rise, R, par)
    _stair_rail('Res_RAILING_Stair_Roof_B', 22.45, 11.52, -1, 5.4, 9, tread, rise, R, par)
    for nm, xa, xb, z0 in (('FF_StairVoid', 15.25, 17.65, 3.8), ('RF_StairVoid', 19.95, 22.35, 7.0)):
        seg = [((xa, 9.1, z0 + 0.9), (xb, 9.1, z0 + 0.9)), ((xa, 9.1, z0 + 0.1), (xb, 9.1, z0 + 0.1))]
        k = int((xb - xa) / 0.12)
        seg += [((xa + (xb - xa) * i / k, 9.1, z0), (xa + (xb - xa) * i / k, 9.1, z0 + 0.9)) for i in range(k + 1)]
        bars(f'Res_RAILING_Guard_{nm}', seg, 0.02, R, par, 'BLK_Railing')
    return 'railings ok'


# ------------------------------------------------------------------ facade, beams, niches
def facade():
    C, par = r1.C, r1.BLD['RES']
    E = C['EXT']
    M = 'BLK_Column'
    def band(prefix, z0, z1, p, mat, sides='NEW'):
        bx = {'N': (-0.115 - p, 24.115 + p, 14.115, 14.115 + p), 'S': (-0.115 - p, 24.115 + p, -0.115 - p, -0.115),
              'W': (-0.115 - p, -0.115, -0.115, 14.115), 'E': (24.115, 24.115 + p, -0.115, 14.115)}
        for k in sides:
            b = bx[k]
            r1.box(f'Res_{prefix}_{k}', b[0], b[1], b[2], b[3], z0, z1, E, par, mat, r2=1)
    band('BAND_Plinth', 0.0, 0.6, 0.06, 'BLK_Stone_Sill')
    band('BAND_StringCourse', 3.55, 3.85, 0.06, M)
    band('CORNICE', 6.6, 6.8, 0.18, M, 'NSWE')
    for ob in [o for o in bpy.data.objects if o.name.startswith('Res_COLUMN_Veranda_') or o.name.startswith('Res_COLUMN_Porch_')]:
        cx, cy = ob.location.x, ob.location.y
        top = 3.6 if 'Veranda' in ob.name else 3.4
        r1.box(ob.name.replace('COLUMN', 'COLBASE'), cx - 0.25, cx + 0.25, cy - 0.25, cy + 0.25, 0.6, 0.75, E, par, M, r2=1)
        r1.box(ob.name.replace('COLUMN', 'COLCAP'), cx - 0.22, cx + 0.22, cy - 0.22, cy + 0.22, top - 0.2, top, E, par, M, r2=1)
    r1.box('Res_BEAM_FF_VerandaEdge', -0.115, 24.115, -2.0, -1.85, 3.2, 3.6, E, par, 'BLK_Slab_Concrete', r2=1)
    r1.box('Res_BEAM_GF_HallDining', 7.8, 8.2, 0.0, 7.0, 3.2, 3.6, E, par, 'BLK_Slab_Concrete', r2=1)
    r1.box('Res_PORCH_Fascia_Front', 9.8, 14.2, 16.6, 16.7, 3.6, 3.72, E, par, M, r2=1)
    r1.box('Res_PORCH_Fascia_West', 9.8, 9.9, 14.115, 16.6, 3.6, 3.72, E, par, M, r2=1)
    r1.box('Res_PORCH_Fascia_East', 14.1, 14.2, 14.115, 16.6, 3.6, 3.72, E, par, M, r2=1)
    D = C['DECOR']
    def panel(name, x0, x1, y0, y1, z0, z1, niches, axis):
        p = r1.box(name, x0, x1, y0, y1, z0, z1, D, par, 'BLK_Niche_Panel', r2=1)
        for i, (u0, u1, n0, n1) in enumerate(niches):
            if axis == 'Y':
                cb = (u0, u1, y0 - 0.01, y1 + 0.003, n0, n1)
            else:
                cb = (x0 - 0.01, x1 + 0.003, u0, u1, n0, n1)
            cu = r1.box(f'{name}_CUT_Niche{i + 1}', *cb, D, par, None, r2=1)
            cu.display_type = 'WIRE'; cu.hide_render = True
            m = p.modifiers.new(f'Niche{i + 1}', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cu; m.solver = 'EXACT'
            cu.hide_set(True)
    panel('Res_NICHE_GF_Hall_TVPanel', 5.2, 7.7, 6.82, 6.9425, 0.6, 3.0, [(5.5, 7.4, 1.2, 2.5)], 'Y')
    panel('Res_NICHE_FF_Master_Headboard', 2.2, 4.5, 4.82, 4.9425, 3.8, 6.2, [(2.35, 2.85, 5.3, 6.1), (3.85, 4.35, 5.3, 6.1)], 'Y')
    panel('Res_NICHE_GF_Dining_Crockery', 12.82, 12.9425, 3.8, 6.4, 0.6, 3.4, [(4.1, 6.1, 1.0, 2.5)], 'X')
    return 'facade ok'


def bevels():
    par = r1.BLD['RES']
    toks = ('COLUMN', 'SLAB', 'STEP', 'COPING', 'BAND', 'CORNICE', 'PARAPET', 'FRAME', 'DOOR_Leaf', 'COLBASE', 'COLCAP', 'BEAM', 'SILL', 'WALL_GF_EXT', 'WALL_FF_EXT')
    n = 0
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.parent == par and any(t in o.name for t in toks) and 'CUT' not in o.name:
            m = o.modifiers.new('Bevel', 'BEVEL')
            m.width = 0.012 if 'WALL' in o.name else 0.006
            m.segments = 2
            m.limit_method = 'ANGLE'
            n += 1
    return f'{n} bevels'
