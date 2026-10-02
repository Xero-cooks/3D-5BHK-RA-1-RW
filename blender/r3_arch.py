"""Round 3 - architectural detailing (door hardware, casings, sills, skirting, cove LEDs)  [module r3a].
Requires r1, r2, r3c (core) , r3f (furn)."""
import bpy, bmesh, math, re, sys, random
from mathutils import Vector, Matrix
c = sys.modules['r3c']; F = sys.modules['r3f']; r1 = sys.modules['r1']
Item = c.Item
FZ = {'GF': 0.6, 'FF': 3.8, 'RF': 7.0}


def RES():
    return r1.BLD['RES']


def wb(o):
    cs = [o.matrix_world @ Vector(v) for v in o.bound_box]
    mn = [min(p[i] for p in cs) for i in range(3)]; mx = [max(p[i] for p in cs) for i in range(3)]
    return [mn[0], mx[0], mn[1], mx[1], mn[2], mx[2]]


def WB(it, m, x0, x1, y0, y1, z0, z1, **kw):
    p = it.p
    it.box(m, x0 - p.x, x1 - p.x, y0 - p.y, y1 - p.y, z0 - p.z, z1 - p.z, **kw)


def WR(it, m, p0, p1, r, r2=None, seg=8, cap=True):
    p = it.p
    it.rod(m, (p0[0] - p.x, p0[1] - p.y, p0[2] - p.z), (p1[0] - p.x, p1[1] - p.y, p1[2] - p.z), r, r2, seg, cap)


def setc(coll, room='ARCH', fl=''):
    c.ctx(coll, RES(), room, fl, 'r3')


def wallhalf(axis, wc):
    """half thickness of the wall at centre-line coordinate wc (axis = direction the wall runs along)."""
    if axis == 'x':
        return 0.115 if (abs(wc) < 0.02 or abs(wc - 14) < 0.02) else 0.0575
    return 0.115 if (abs(wc) < 0.02 or abs(wc - 24) < 0.02) else 0.0575


def openings():
    out = []
    for o in bpy.data.objects:
        m = re.match(r'Res_CUT_(Door|Window)_(GF|FF|RF)_(.+?)(\.\d+)?$', o.name)
        if not m or o.parent != RES():
            continue
        kind, fl, tag, dup = m.group(1), m.group(2), m.group(3), m.group(4) or ''
        b = wb(o)
        dx, dy = b[1] - b[0], b[3] - b[2]
        if dy < dx:
            ax, wc, c0, c1 = 'x', (b[2] + b[3]) / 2, b[0], b[1]
        else:
            ax, wc, c0, c1 = 'y', (b[0] + b[1]) / 2, b[2], b[3]
        out.append(dict(obj=o, kind=kind, fl=fl, tag=tag, dup=dup, ax=ax, wc=wc, c0=c0, c1=c1, z0=b[4], z1=b[5],
                        slider=tag.startswith('Slider'), arch='Open' in tag, ext=wallhalf(ax, wc) > 0.1))
    return out


def inward(op):
    """+1/-1 along wall-normal pointing to building interior centre."""
    cen = 7.0 if op['ax'] == 'x' else 12.0
    if op['fl'] == 'RF':
        cen = 11.3 if op['ax'] == 'x' else 21.7
    return 1 if cen > op['wc'] else -1


def faces_box(it, m, op, a0, a1, side, n0, n1, z0, z1, **kw):
    """box in wall-aligned coords: a along wall, n offset from wall centre (side-signed), world placement."""
    wc = op['wc']
    ns = sorted([wc + side * n0, wc + side * n1])
    if op['ax'] == 'x':
        WB(it, m, a0, a1, ns[0], ns[1], z0, z1, **kw)
    else:
        WB(it, m, ns[0], ns[1], a0, a1, z0, z1, **kw)


def casing(it, op, side, mat, w=0.07, t=0.016, floor=True, top_only=False, bev=0.003):
    wf = wallhalf(op['ax'], op['wc'])
    n0, n1 = wf - 0.004, wf + t
    zf = op['z0'] if not floor else FZ[op['fl']] - 0.0
    z0 = zf if floor else op['z0'] - w
    if not top_only:
        faces_box(it, mat, op, op['c0'] - w, op['c0'], side, n0, n1, z0, op['z1'] + w, bev=bev, seg=1)
        faces_box(it, mat, op, op['c1'], op['c1'] + w, side, n0, n1, z0, op['z1'] + w, bev=bev, seg=1)
    faces_box(it, mat, op, op['c0'] - w, op['c1'] + w, side, n0, n1 + 0.006, op['z1'], op['z1'] + w, bev=bev, seg=1)


def lever(it, base, u, n, z, hdir, mat='steel', rose_r=0.027):
    """base=(x,y) of the wall-normal line on the leaf surface; u,n unit vectors (door axis, outward normal); hdir=+/-1 lever direction along u"""
    P = lambda a, b: (base[0] + u[0] * a + n[0] * b, base[1] + u[1] * a + n[1] * b, z)
    WR(it, mat, P(0, 0.0), P(0, 0.012), rose_r, seg=14)
    WR(it, mat, P(0, 0.012), P(0, 0.042), 0.009, seg=8)
    pts = [P(0, 0.042), P(hdir * 0.03, 0.05), P(hdir * 0.105, 0.05)]
    WR(it, mat, pts[0], pts[1], 0.0085, seg=8, cap=False)
    WR(it, mat, pts[1], pts[2], 0.0085, seg=8)
    p = it.p
    it.sph(mat, pts[2][0] - p.x, pts[2][1] - p.y, pts[2][2] - p.z, 0.0095, seg=8, rings=5)
    # key escutcheon
    WR(it, mat, (P(0, 0)[0], P(0, 0)[1], z - 0.085), (P(0, 0.006)[0], P(0, 0.006)[1], z - 0.085), 0.012, seg=10)
    WR(it, mat, (P(0, 0)[0], P(0, 0)[1], z - 0.1), (P(0, 0.004)[0], P(0, 0.004)[1], z - 0.1), 0.006, seg=8)


def door_hardware():
    coll = c.sub_coll(r1.C['DOOR'], '07_Door_Hardware')
    setc(coll, 'DOORS')
    cnt = 0
    for op in openings():
        if op['kind'] != 'Door' or op['slider'] or op['arch']:
            continue
        leaf = bpy.data.objects.get(f"Res_DOOR_Leaf_{op['fl']}_{op['tag']}{op['dup']}")
        if not leaf:
            continue
        lb = wb(leaf)
        ax = op['ax']; half = (lb[3] - lb[2]) / 2 if ax == 'x' else (lb[1] - lb[0]) / 2
        zf = FZ[op['fl']]
        a0, a1 = (lb[0], lb[1]) if ax == 'x' else (lb[2], lb[3])
        wc = op['wc']
        u = (1, 0) if ax == 'x' else (0, 1)
        nrm = (0, 1) if ax == 'x' else (1, 0)
        main = 'MainEntrance' in op['tag']
        org = (((lb[0] + lb[1]) / 2, wc) if ax == 'x' else (wc, (lb[2] + lb[3]) / 2))
        it = Item(f"Door_HW_{op['fl']}_{op['tag']}{op['dup']}", org[0], org[1], lb[4], kind='wall')
        zh = zf + 1.0
        for side in (1, -1):
            n = (nrm[0] * side, nrm[1] * side)
            base = (org[0] + n[0] * half, org[1] + n[1] * half)
            if main:
                for k in (-1, 1):
                    pa = (base[0] + u[0] * k * 0.17 + n[0] * 0.0, base[1] + u[1] * k * 0.17)
                    for zz in (zf + 0.7, zf + 1.35):
                        WR(it, 'steel', (pa[0] + n[0] * 0.012, pa[1] + n[1] * 0.012, zz), (pa[0] + n[0] * 0.05, pa[1] + n[1] * 0.05, zz), 0.01, seg=8)
                    WR(it, 'steel', (pa[0] + n[0] * 0.05, pa[1] + n[1] * 0.05, zf + 0.7), (pa[0] + n[0] * 0.05, pa[1] + n[1] * 0.05, zf + 1.35), 0.014, seg=10)
                lever(it, (base[0] + u[0] * 0.3, base[1] + u[1] * 0.3), u, n, zh, -1)
                # centre astragal strip
                ca = (base[0] + n[0] * 0.004, base[1] + n[1] * 0.004)
                WB(it, 'wood_dark', ca[0] - 0.01 * abs(u[0]) - 0.003 * abs(nrm[0]), ca[0] + 0.01 * abs(u[0]) + 0.003 * abs(nrm[0]),
                   ca[1] - 0.01 * abs(u[1]) - 0.003 * abs(nrm[1]), ca[1] + 0.01 * abs(u[1]) + 0.003 * abs(nrm[1]), lb[4], lb[5])
            else:
                hdir = 1
                hp = (base[0] + u[0] * (a1 - a0) * 0.5 * 0.0, base[1])
                # handle near free end (high coordinate); lever points back toward hinge (negative along u)
                hpos = (a1 - 0.075)
                bpos = (hpos, base[1]) if ax == 'x' else (base[0], hpos)
                lever(it, bpos, u, n, zh, -1)
        # hinges (3) at low end
        hpos = a0 + 0.012
        for zz in (lb[4] + 0.22, (lb[4] + lb[5]) / 2, lb[5] - 0.22):
            for side in (1, -1):
                p0 = (hpos, wc + side * (half + 0.003)) if ax == 'x' else (wc + side * (half + 0.003), hpos)
                WR(it, 'brass', (p0[0], p0[1], zz - 0.055), (p0[0], p0[1], zz + 0.055), 0.0085, seg=8)
        it.finish(); cnt += 1
    return cnt


def trims():
    """casings for doors/sliders/arches, windows (inner & outer surrounds), interior marble sills, slider tracks + handles."""
    ops = openings()
    coll = c.sub_coll(r1.C['DOOR'], '07_Door_Trims')
    wcoll = c.sub_coll(r1.C['WIN'], '08_Window_Trims')
    n = 0
    for fl in ('GF', 'FF'):
        setc(coll, 'TRIM', fl)
        it = Item(f'Trim_{fl}_DoorCasings_Timber', 0, 0, 0, kind='wall')
        it2 = Item(f'Trim_{fl}_ArchCasings_Painted', 0, 0, 0, kind='wall')
        it3 = Item(f'Trim_{fl}_SliderCasings_Painted', 0, 0, 0, kind='wall')
        for op in ops:
            if op['fl'] != fl or op['kind'] != 'Door':
                continue
            for side in (1, -1):
                if op['slider']:
                    casing(it3, op, side, 'paint_white', w=0.07, t=0.014)
                elif op['arch']:
                    casing(it2, op, side, 'paint_white', w=0.1, t=0.02, bev=0.004)
                    casing(it2, op, side, 'paint_white', w=0.04, t=0.034, bev=0.002)   # stepped moulding
                else:
                    casing(it, op, side, 'wood_dark', w=0.075, t=0.017)
        for i_ in (it, it2, it3):
            if i_.bms:
                i_.finish(); n += 1
        # windows
        c.ctx(wcoll, RES(), 'TRIM', fl, 'r3')
        sill = Item(f'Trim_{fl}_WindowSills_Marble', 0, 0, 0, kind='wall')
        sur = Item(f'Trim_{fl}_WindowSurrounds_Painted', 0, 0, 0, kind='wall')
        for op in ops:
            if op['fl'] != fl or op['kind'] != 'Window':
                continue
            ins = inward(op)
            wf = wallhalf(op['ax'], op['wc'])
            zb = op['z0']
            # interior marble sill with slight overhang
            faces_box(sill, 'marble_white', op, op['c0'] - 0.06, op['c1'] + 0.06, ins, wf - 0.01, wf + 0.1, zb - 0.032, zb + 0.004, bev=0.004, seg=1)
            # interior surround (all 4 sides) + exterior surround
            for side, t, w in ((ins, 0.012, 0.055), (-ins, 0.02, 0.085)):
                zlo, zhi = zb - (0.0 if side == ins else 0.0), op['z1']
                faces_box(sur, 'paint_white', op, op['c0'] - w, op['c0'], side, wf - 0.004, wf + t, zlo - w * (1 if side != ins else 0), zhi + w, bev=0.002, seg=1)
                faces_box(sur, 'paint_white', op, op['c1'], op['c1'] + w, side, wf - 0.004, wf + t, zlo - w * (1 if side != ins else 0), zhi + w, bev=0.002, seg=1)
                faces_box(sur, 'paint_white', op, op['c0'] - w, op['c1'] + w, side, wf - 0.004, wf + t + 0.004, zhi, zhi + w, bev=0.002, seg=1)
        for i_ in (sill, sur):
            if i_.bms:
                i_.finish(); n += 1
        # slider tracks + handles
        setc(c.sub_coll(r1.C['WIN'], '08_Slider_Hardware'), 'SLIDER', fl)
        for op in ops:
            if op['fl'] != fl or not op['slider']:
                continue
            ctr = (op['c0'] + op['c1']) / 2
            org = (ctr, op['wc']) if op['ax'] == 'x' else (op['wc'], ctr)
            h = Item(f"Slider_HW_{fl}_{op['tag']}", org[0], org[1], FZ[fl], kind='wall')
            ins = inward(op)
            faces_box(h, 'black_metal', op, op['c0'], op['c1'], 1, -0.07, 0.07, FZ[fl], FZ[fl] + 0.02, bev=0.003, seg=1)
            faces_box(h, 'black_metal', op, op['c0'], op['c1'], 1, -0.06, 0.06, op['z1'] - 0.1, op['z1'] - 0.075, bev=0.002, seg=1)
            for side in (1, -1):
                for k in (-1, 1):
                    a = ctr + k * 0.035
                    p0 = [0, 0]
                    wcn = op['wc'] + side * 0.05
                    if op['ax'] == 'x':
                        WR(h, 'steel', (a, wcn, FZ[fl] + 0.85), (a, wcn, FZ[fl] + 1.35), 0.011, seg=8)
                        for zz in (FZ[fl] + 0.9, FZ[fl] + 1.3):
                            WR(h, 'steel', (a, wcn - side * 0.017, zz), (a, op['wc'] + side * 0.034, zz), 0.006, seg=6)
                    else:
                        WR(h, 'steel', (wcn, a, FZ[fl] + 0.85), (wcn, a, FZ[fl] + 1.35), 0.011, seg=8)
                        for zz in (FZ[fl] + 0.9, FZ[fl] + 1.3):
                            WR(h, 'steel', (wcn - side * 0.017, a, zz), (op['wc'] + side * 0.034, a, zz), 0.006, seg=6)
            h.finish(); n += 1
    return n


def skirting():
    ops = [o for o in openings() if o['kind'] == 'Door']
    dark = ('bed', 'master', 'study', 'office', 'lounge', 'dress')
    cream = ('hall', 'dining', 'foyer', 'corridor', 'landing', 'lobby')
    coll = c.sub_coll(r1.C['WALL'], '04_Skirting')
    cnt = 0
    for o in bpy.data.objects:
        if not (o.get('room_type') and o.parent == RES()):
            continue
        fl, nm = o['floor'], o['room_name']
        low = nm.lower()
        mat = 'wood_dark' if any(k in low for k in dark) else ('paint_white' if any(k in low for k in cream) else None)
        if not mat or 'bath' in low:
            continue
        b = tuple(o['bbox'][:4])
        xa = b[0] + (0.115 if abs(b[0]) < 1e-6 else 0.0575); xb = b[1] - (0.115 if abs(b[1] - 24) < 1e-6 else 0.0575)
        ya = b[2] + (0.115 if abs(b[2]) < 1e-6 else 0.0575); yb = b[3] - (0.115 if abs(b[3] - 14) < 1e-6 else 0.0575)
        z = FZ[fl]
        h = 0.11 if mat == 'wood_dark' else 0.12
        d = 0.016
        setc(coll, f'{fl}_{nm}', fl)
        it = Item(f'{fl}_{nm.replace(" ", "")}_Skirting', xa, ya, z, kind='wall')

        def segs(ax, wc, lo, hi):
            iv = [(lo, hi)]
            for op in ops:
                if op['fl'] != fl or op['ax'] != ax or abs(op['wc'] - wc) > 0.03 or op['z0'] > z + 0.15:
                    continue
                cut0, cut1 = op['c0'] - 0.075, op['c1'] + 0.075
                nxt = []
                for (s0, s1) in iv:
                    if cut1 <= s0 or cut0 >= s1:
                        nxt.append((s0, s1)); continue
                    if cut0 > s0: nxt.append((s0, cut0))
                    if cut1 < s1: nxt.append((cut1, s1))
                iv = nxt
            return [(s0, s1) for (s0, s1) in iv if s1 - s0 > 0.05]
        for (s0, s1) in segs('x', b[2], xa, xb):
            WB(it, mat, s0, s1, ya, ya + d, z, z + h, bev=0.003, seg=1)
            if mat != 'wood_dark': WB(it, mat, s0, s1, ya, ya + d * 0.55, z + h, z + h + 0.016, bev=0.002, seg=1)
        for (s0, s1) in segs('x', b[3], xa, xb):
            WB(it, mat, s0, s1, yb - d, yb, z, z + h, bev=0.003, seg=1)
            if mat != 'wood_dark': WB(it, mat, s0, s1, yb - d * 0.55, yb, z + h, z + h + 0.016, bev=0.002, seg=1)
        for (s0, s1) in segs('y', b[0], ya + d, yb - d):
            WB(it, mat, xa, xa + d, s0, s1, z, z + h, bev=0.003, seg=1)
            if mat != 'wood_dark': WB(it, mat, xa, xa + d * 0.55, s0, s1, z + h, z + h + 0.016, bev=0.002, seg=1)
        for (s0, s1) in segs('y', b[1], ya + d, yb - d):
            WB(it, mat, xb - d, xb, s0, s1, z, z + h, bev=0.003, seg=1)
            if mat != 'wood_dark': WB(it, mat, xb - d * 0.55, xb, s0, s1, z + h, z + h + 0.016, bev=0.002, seg=1)
        if it.finish():
            cnt += 1
    return cnt


def cove_leds():
    coll = c.sub_coll(r1.C['LIGHT'], '17_Cove_LED')
    cnt = 0
    for o in bpy.data.objects:
        if not o.name.startswith('Res_COVE_'):
            continue
        b = wb(o)
        fl = 'GF' if '_GF_' in o.name else 'FF'
        setc(coll, 'COVE', fl)
        tag = o.name[len('Res_COVE_'):]
        it = Item(f'Fx_CoveLED_{tag}', b[0], b[2], b[5], kind='ceil')
        x0, x1, y0, y1 = b[0] + 0.125, b[3 - 2] - 0.125, b[2] + 0.125, b[3] - 0.125
        zt = b[5]
        s = 0.022
        WB(it, 'emit_warm', x0, x1, y0, y0 + s, zt - 0.016, zt - 0.004)
        WB(it, 'emit_warm', x0, x1, y1 - s, y1, zt - 0.016, zt - 0.004)
        WB(it, 'emit_warm', x0, x0 + s, y0 + s, y1 - s, zt - 0.016, zt - 0.004)
        WB(it, 'emit_warm', x1 - s, x1, y0 + s, y1 - s, zt - 0.016, zt - 0.004)
        it.finish(); cnt += 1
    return cnt


def run_arch():
    r1._colls()
    out = {}
    out['door_hw'] = door_hardware()
    out['trims'] = trims()
    out['skirting'] = skirting()
    out['cove'] = cove_leds()
    return out
