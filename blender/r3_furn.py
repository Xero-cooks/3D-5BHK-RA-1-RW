"""Round 3 furniture + decor catalogue (module r3f). Requires module r3c (r3_core)."""
import bpy, bmesh, math, sys, random
from mathutils import Vector
c = sys.modules['r3c']
Item = c.Item
rnd = random.Random(7)


def arc_band(it, m, cx, cy, r, th, a0, a1, z0, z1, seg=10):
    """band around vertical axis; angle measured from -Y toward +X (degrees)."""
    b = it._b(m)
    A = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        for rr in (r, r - th):
            for z in (z0, z1):
                A.append(b.verts.new((cx + rr * math.sin(t), cy - rr * math.cos(t), z)))
    for k in range(seg):
        i0 = k * 4; i1 = (k + 1) * 4
        # verts order per k: (r,z0),(r,z1),(r-th,z0),(r-th,z1)
        for q in ((0, 1, 5, 4), (2, 6, 7, 3), (1, 3, 7, 5), (0, 4, 6, 2)):
            b.faces.new([A[i0 + q[0]] if q[0] < 4 else A[i1 + q[0] - 4], A[i0 + q[1]] if q[1] < 4 else A[i1 + q[1] - 4],
                         A[i0 + q[2]] if q[2] < 4 else A[i1 + q[2] - 4], A[i0 + q[3]] if q[3] < 4 else A[i1 + q[3] - 4]])
    b.faces.new([A[0], A[1], A[3], A[2]])
    n = seg * 4
    b.faces.new([A[n], A[n + 2], A[n + 3], A[n + 1]])


# ------------------------------------------------------------------ seating
def sofa(name, x, y, z, face='N', w=2.1, d=0.92, fab='fab_grey', pill=('fab_mustard', 'fab_cream'), legs='wood_dark'):
    it = Item(name, x, y, z, face); h = w / 2
    for sx in (-1, 1):
        for yy in (0.1, d - 0.1):
            it.rod(legs, (sx * (h - 0.09), yy, 0.0), (sx * (h - 0.09), yy, 0.12), 0.018, 0.028, 8)
    it.box(fab, -h, h, 0.0, d, 0.12, 0.30, bev=0.025)
    it.box(fab, -h, -h + 0.17, 0.0, d, 0.12, 0.64, bev=0.055, seg=3)
    it.box(fab, h - 0.17, h, 0.0, d, 0.12, 0.64, bev=0.055, seg=3)
    it.box(fab, -h + 0.17, h - 0.17, 0.0, 0.2, 0.12, 0.86, bev=0.05, seg=3)
    n = 3 if w > 1.7 else 2
    cw = (w - 0.34) / n
    for i in range(n):
        x0 = -h + 0.17 + i * cw
        it.box(fab, x0 + 0.004, x0 + cw - 0.004, 0.2, d - 0.01, 0.30, 0.46, bev=0.05, seg=3)
        it.box(fab, x0 + 0.01, x0 + cw - 0.01, 0.17, 0.4, 0.44, 0.84, bev=0.06, seg=3, rot=(10, 0, 0))
    for k, pm in enumerate(pill[:2]):
        px = (-h + 0.45) if k == 0 else (h - 0.45)
        it.box(pm, px - 0.2, px + 0.2, 0.3, 0.46, 0.5, 0.88, bev=0.07, seg=3, rot=(15, 0, 12 if k == 0 else -12))
    return it.finish()


def armchair_wicker(name, x, y, z, face='N', w=0.7, d=0.72, cush='fab_brown', pillow='fab_black_floral'):
    it = Item(name, x, y, z, face); h = w / 2
    for sx in (-1, 1):
        for yy in (0.08, d - 0.08):
            it.rod('wicker', (sx * (h - 0.07), yy, 0.0), (sx * (h - 0.05), yy, 0.30), 0.016, 0.024, 8)
    it.box('wicker', -h, h, 0.02, d - 0.02, 0.30, 0.36, bev=0.025)
    it.box('wicker', -h + 0.03, h - 0.03, 0.05, d - 0.05, 0.2, 0.3, bev=0.02)
    it.box('wicker', -h + 0.02, h - 0.02, 0.02, d - 0.02, 0.13, 0.15, bev=0.008)
    cx, cy = 0.0, d * 0.52
    arc_band(it, 'wicker', cx, cy, h - 0.01, 0.04, -78, 78, 0.34, 0.95, 12)
    arc_band(it, 'wicker', cx, cy, h - 0.01, 0.04, -118, -78, 0.34, 0.66, 4)
    arc_band(it, 'wicker', cx, cy, h - 0.01, 0.04, 78, 118, 0.34, 0.66, 4)
    for t in (-118, 118):
        a = math.radians(t)
        px, py = (h - 0.03) * math.sin(a), cy - (h - 0.03) * math.cos(a)
        it.cyl('wicker', px, py, 0.34, 0.66, 0.02, seg=8)
    for zz in (0.5, 0.7, 0.9):  # weave rails
        arc_band(it, 'wicker', cx, cy, h - 0.005, 0.012, -76, 76, zz, zz + 0.012, 10)
    it.box(cush, -h + 0.07, h - 0.07, 0.1, d - 0.07, 0.36, 0.45, bev=0.04, seg=3)
    it.box(pillow, -0.2, 0.2, 0.14, 0.3, 0.46, 0.84, bev=0.06, seg=3, rot=(12, 0, 0))
    return it.finish()


def pouf(name, x, y, z, r=0.2, h=0.4, mat='fab_mustard'):
    it = Item(name, x, y, z)
    it.lathe(mat, [(0, 0.02), (r * .9, 0.03), (r, 0.1), (r, h - 0.1), (r * .92, h - 0.02), (r * .5, h), (0, h)], seg=20)
    return it.finish()


def coffee_table_round(name, x, y, z, r=0.42, h=0.46, leg='wicker'):
    it = Item(name, x, y, z)
    it.lathe('glass', [(r, h - 0.012), (r, h), (0, h)], seg=36, cap_bot=False)
    it.lathe('glass', [(0, h - 0.012), (r, h - 0.012)], seg=36)
    it.lathe(leg, [(r * 0.84, h - 0.03), (r * 0.9, h - 0.03), (r * 0.9, h - 0.012), (r * 0.84, h - 0.012)], seg=32)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        it.rod(leg, (r * 0.78 * math.cos(a), r * 0.78 * math.sin(a), h - 0.03), (r * 0.9 * math.cos(a), r * 0.9 * math.sin(a), 0.0), 0.02, 0.014, 8)
    it.lathe(leg, [(r * 0.8, 0.12), (r * 0.82, 0.12), (r * 0.82, 0.14), (r * 0.8, 0.14)], seg=32)
    return it.finish()


def coffee_table_rect(name, x, y, z, face='N', w=1.1, d=0.6, h=0.42):
    it = Item(name, x, y, z, face)
    it.box('wood_dark', -w / 2, w / 2, -d / 2, d / 2, h - 0.04, h, bev=0.012)
    it.box('glass', -w / 2 + 0.04, w / 2 - 0.04, -d / 2 + 0.04, d / 2 - 0.04, h, h + 0.008)
    it.box('wood_dark', -w / 2 + 0.03, w / 2 - 0.03, -d / 2 + 0.03, d / 2 - 0.03, 0.1, 0.13, bev=0.008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            it.rod('wood_dark', (sx * (w / 2 - 0.05), sy * (d / 2 - 0.05), 0), (sx * (w / 2 - 0.05), sy * (d / 2 - 0.05), h - 0.04), 0.022, 0.03, 8)
    return it.finish()


def side_table(name, x, y, z, r=0.24, h=0.55, top='wood_dark'):
    it = Item(name, x, y, z)
    it.lathe(top, [(r, h - 0.03), (r, h), (0, h)], seg=24)
    it.rod('black_metal', (0, 0, 0.02), (0, 0, h - 0.03), 0.018, seg=8)
    it.lathe('black_metal', [(0, 0), (r * 0.8, 0), (r * 0.8, 0.02), (0, 0.025)], seg=24)
    return it.finish()


def rug(name, x, y, z, w, d, base='rug_red', stripe='rug_pink', n=0, face='N'):
    it = Item(name, x, y, z, face, kind='rug')
    it.box(base, -w / 2, w / 2, -d / 2, d / 2, 0.0, 0.012, bev=0.004, seg=1)
    if n:
        sw = d / (n * 2 + 1)
        for k in range(n):
            y0 = -d / 2 + sw * (2 * k + 1.0)
            it.box(stripe, -w / 2, w / 2, y0, y0 + sw, 0.0, 0.0135)
    return it.finish()


def tv(name, x, y, z, face='N', w=1.22, hgt=0.7, wall=True):
    it = Item(name, x, y, z, face, kind='wall' if wall else 'prop')
    it.box('black_plastic', -w / 2, w / 2, 0.0, 0.035, 0, hgt, bev=0.008)
    it.box('black_glass', -w / 2 + 0.012, w / 2 - 0.012, 0.034, 0.037, 0.012, hgt - 0.012)
    return it.finish()


def tv_unit(name, x, y, z, face='N', w=1.8, d=0.42, h=0.5, top='wood_dark', body='lam_grey'):
    it = Item(name, x, y, z, face); hw = w / 2
    for sx in (-1, 1):
        it.box('black_metal', sx * (hw - 0.08) - 0.025, sx * (hw - 0.08) + 0.025, 0.04, d - 0.04, 0, 0.08)
    it.box(top, -hw, hw, 0, d, h - 0.035, h, bev=0.008)
    it.box(body, -hw + 0.01, hw - 0.01, 0.0, d - 0.01, 0.08, h - 0.035, bev=0.006)
    n = 4
    cw = (w - 0.02) / n
    for i in range(n):
        x0 = -hw + 0.01 + i * cw
        it.box('wood_med' if i % 3 == 0 else 'lam_grey', x0 + 0.004, x0 + cw - 0.004, d - 0.012, d, 0.09, h - 0.04, bev=0.004, seg=1)
        it.box('steel', x0 + cw / 2 - 0.1, x0 + cw / 2 + 0.1, d, d + 0.01, h - 0.085, h - 0.075)
    return it.finish()


def console(name, x, y, z, face='N', w=1.2, d=0.35, h=0.85, mat='wood_med'):
    it = Item(name, x, y, z, face); hw = w / 2
    it.box(mat, -hw, hw, 0, d, h - 0.04, h, bev=0.01)
    it.box(mat, -hw + 0.03, hw - 0.03, 0.02, d - 0.02, 0.25, 0.29, bev=0.005)
    for sx in (-1, 1):
        for yy in (0.04, d - 0.04):
            it.rod(mat, (sx * (hw - 0.05), yy, 0), (sx * (hw - 0.05), yy, h - 0.04), 0.014, 0.022, 8)
    it.box('wood_dark', -hw + 0.06, hw - 0.06, 0.02, d - 0.02, h - 0.14, h - 0.04, bev=0.006)
    it.box('brass', -0.03, 0.03, d - 0.005, d + 0.012, h - 0.1, h - 0.085)
    return it.finish()


def dining_table(name, x, y, z, face='N', w=1.8, d=0.95, h=0.76):
    it = Item(name, x, y, z, face)
    it.box('wood_teak', -w / 2, w / 2, -d / 2, d / 2, h - 0.045, h, bev=0.014, seg=3)
    it.box('wood_dark', -w / 2 + 0.1, w / 2 - 0.1, -d / 2 + 0.1, d / 2 - 0.1, h - 0.12, h - 0.045, bev=0.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            it.rod('wood_teak', (sx * (w / 2 - 0.1), sy * (d / 2 - 0.1), 0), (sx * (w / 2 - 0.1), sy * (d / 2 - 0.1), h - 0.045), 0.026, 0.04, 8)
    it.box('glass', -w / 2 + 0.2, w / 2 - 0.2, -d / 2 + 0.2, d / 2 - 0.2, h, h + 0.008)
    return it.finish()


def dining_chair(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face)
    s = 0.225
    for sx in (-1, 1):
        for sy in (-1, 1):
            it.rod('wood_teak', (sx * (s - 0.02), sy * (s - 0.02), 0), (sx * (s - 0.02), sy * (s - 0.02), 0.45), 0.014, 0.02, 8)
    for sx in (-1, 1):
        it.rod('wood_teak', (sx * (s - 0.02), -s + 0.02, 0.45), (sx * (s - 0.03), -s + 0.0, 0.98), 0.016, 0.014, 8)
    it.box('wood_teak', -s, s, -s, s, 0.42, 0.46, bev=0.01)
    it.box('fab_brown', -s + 0.015, s - 0.015, -s + 0.02, s - 0.015, 0.46, 0.51, bev=0.02, seg=3)
    it.box('wood_teak', -s + 0.02, s - 0.02, -s - 0.01, -s + 0.015, 0.84, 0.95, bev=0.006, rot=(-5, 0, 0))
    it.box('wood_teak', -s + 0.02, s - 0.02, -s - 0.005, -s + 0.015, 0.62, 0.7, bev=0.006, rot=(-5, 0, 0))
    it.box('fab_brown', -s + 0.04, s - 0.04, -s + 0.005, -s + 0.03, 0.7, 0.84, bev=0.015, seg=2, rot=(-5, 0, 0))
    return it.finish()


# ------------------------------------------------------------------ beds + storage
def bed(name, x, y, z, face='S', w=1.8, l=2.05, cover='fab_floral', pill='fab_white', frame='wood_dark', accent='wood_med', throw='fab_mustard'):
    it = Item(name, x, y, z, face); h = w / 2
    # storage base with drawer lines (ref: dark carved storage bed)
    it.box(frame, -h - 0.02, h + 0.02, 0.05, l, 0.08, 0.36, bev=0.012)
    for sx in (-1, 1):
        it.box(accent, sx * (h + 0.02) - (0.004 if sx > 0 else -0.004), sx * (h + 0.02) + (0.01 if sx > 0 else -0.01), 0.45, l - 0.35, 0.14, 0.31, bev=0.004, seg=1)
    it.box(accent, -h + 0.1, h - 0.1, l - 0.004, l + 0.012, 0.14, 0.31, bev=0.004, seg=1)
    # headboard
    it.box(frame, -h - 0.06, h + 0.06, 0.0, 0.09, 0.08, 1.12, bev=0.014)
    nph = 3 if w > 1.5 else 2
    pw = (2 * h - 0.12) / nph
    for k in range(nph):
        x0 = -h + 0.06 + k * pw
        it.box(accent, x0 + 0.02, x0 + pw - 0.02, 0.085, 0.105, 0.5, 1.02, bev=0.006, seg=1)
    it.box(frame, -h - 0.08, h + 0.08, 0.0, 0.12, 1.08, 1.14, bev=0.014)
    it.box(frame, -h - 0.02, h + 0.02, l - 0.06, l, 0.08, 0.5, bev=0.012)
    # mattress + cover
    it.box('fab_white', -h + 0.02, h - 0.02, 0.1, l - 0.06, 0.36, 0.60, bev=0.05, seg=3)
    it.box(cover, -h - 0.03, h + 0.03, 0.62, l - 0.02, 0.48, 0.66, bev=0.05, seg=3)
    it.box(cover, -h + 0.02, h - 0.02, 0.58, l - 0.04, 0.6, 0.675, bev=0.04, seg=3)
    it.box(throw, -h + 0.0, h - 0.0, l - 0.62, l - 0.34, 0.66, 0.72, bev=0.025, seg=2)
    npil = 2 if w < 1.5 else 3
    pw2 = (w - 0.1) / npil
    for k in range(npil):
        px = -h + 0.05 + pw2 * (k + 0.5)
        it.box(pill, px - pw2 / 2 + 0.015, px + pw2 / 2 - 0.015, 0.14, 0.58, 0.6, 0.74, bev=0.07, seg=3, rot=(8, 0, 0))
    it.box(throw if throw != pill else 'fab_cream', -0.2, 0.2, 0.62, 0.9, 0.68, 0.76, bev=0.07, seg=3, rot=(12, 0, 8))
    return it.finish()


def _lamp(it, cx, cy, z0, h=0.34, base='ceramic', shade='fab_cream'):
    it.lathe(base, [(0, z0), (0.06, z0), (0.075, z0 + 0.04), (0.06, z0 + 0.12), (0.025, z0 + 0.2), (0.015, z0 + h * 0.7), (0, z0 + h * 0.7)], cx=cx, cy=cy, seg=14)
    it.lathe('emit_warm', [(0.095, z0 + h * 0.64), (0.13, z0 + h * 0.98)], cx=cx, cy=cy, seg=16)
    it.lathe(shade, [(0.105, z0 + h * 0.62), (0.15, z0 + h)], cx=cx, cy=cy, seg=16)


def table_lamp(name, x, y, z, h=0.34, base='ceramic', shade='fab_cream'):
    it = Item(name, x, y, z, kind='prop')
    _lamp(it, 0, 0, 0, h, base, shade)
    return it.finish()


def bedside(name, x, y, z, face='S', w=0.46, d=0.4, h=0.52, lamp=True, mat='wood_dark', accent='wood_med'):
    it = Item(name, x, y, z, face); hw = w / 2
    for sx in (-1, 1):
        for yy in (0.04, d - 0.04):
            it.rod(mat, (sx * (hw - 0.04), yy, 0), (sx * (hw - 0.04), yy, 0.14), 0.014, 0.02, 8)
    it.box(mat, -hw, hw, 0, d, 0.14, h, bev=0.01)
    it.box(accent, -hw + 0.02, hw - 0.02, d - 0.004, d + 0.012, 0.3, h - 0.03, bev=0.005, seg=1)
    it.box(accent, -hw + 0.02, hw - 0.02, d - 0.004, d + 0.012, 0.17, 0.29, bev=0.005, seg=1)
    it.rod('brass', (0, d + 0.012, 0.42), (0, d + 0.035, 0.42), 0.012, seg=8)
    it.rod('brass', (0, d + 0.012, 0.23), (0, d + 0.035, 0.23), 0.012, seg=8)
    if lamp:
        _lamp(it, 0, d * 0.5, h, 0.34)
    return it.finish()


def wardrobe(name, x, y, z, face='N', w=2.4, h=2.85, d=0.6, cols=None, loft=0.6, body='lam_cream', handle='steel'):
    it = Item(name, x, y, z, face); hw = w / 2
    cols = cols or max(2, int(round(w / 0.62)))
    it.box('wood_dark', -hw, hw, 0.0, d - 0.02, 0.0, 0.09, bev=0.004, seg=1)
    it.box(body, -hw, hw, 0.0, d - 0.03, 0.09, h, bev=0.004, seg=1)
    cw = w / cols
    for i in range(cols):
        x0 = -hw + i * cw
        it.box(body, x0 + 0.003, x0 + cw - 0.003, d - 0.03, d - 0.005, 0.095, h - loft - 0.003, bev=0.004, seg=1)
        it.box(body, x0 + 0.003, x0 + cw - 0.003, d - 0.03, d - 0.005, h - loft + 0.003, h - 0.005, bev=0.004, seg=1)
        hx = x0 + (cw - 0.04) if i % 2 == 0 else x0 + 0.04
        it.box(handle, hx - 0.008, hx + 0.008, d - 0.005, d + 0.018, 0.85, 1.25, bev=0.004, seg=1)
        it.box(handle, hx - 0.008, hx + 0.008, d - 0.005, d + 0.018, h - loft + 0.1, h - loft + 0.3, bev=0.004, seg=1)
    return it.finish()


def dresser(name, x, y, z, face='N', w=1.1, d=0.45, h=0.78, mirror=True):
    it = Item(name, x, y, z, face); hw = w / 2
    for sx in (-1, 1):
        it.rod('wood_dark', (sx * (hw - 0.05), d / 2, 0), (sx * (hw - 0.05), d / 2, 0.12), 0.016, 0.026, 8)
    it.box('wood_med', -hw, hw, 0, d, 0.12, h, bev=0.012)
    for k in range(3):
        z0 = 0.15 + k * 0.2
        it.box('wood_dark', -hw + 0.03, hw - 0.03, d - 0.004, d + 0.012, z0, z0 + 0.18, bev=0.006, seg=1)
        it.box('brass', -0.07, 0.07, d + 0.012, d + 0.03, z0 + 0.08, z0 + 0.1, bev=0.004, seg=1)
    it.box('wood_dark', -hw - 0.01, hw + 0.01, 0, d, h, h + 0.03, bev=0.01)
    if mirror:
        it.box('wood_dark', -0.42, 0.42, 0.02, 0.05, h + 0.2, h + 1.2, bev=0.012)
        it.box('mirror', -0.39, 0.39, 0.05, 0.055, h + 0.23, h + 1.17)
    return it.finish()


def stool(name, x, y, z, r=0.2, h=0.45, mat='fab_taupe'):
    it = Item(name, x, y, z)
    it.lathe(mat, [(0, h), (r, h), (r, h - 0.06), (0, h - 0.06)], seg=18)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        it.rod('wood_dark', (r * .7 * math.cos(a), r * .7 * math.sin(a), h - 0.06), (r * .85 * math.cos(a), r * .85 * math.sin(a), 0), 0.018, 0.012, 8)
    return it.finish()


def ottoman_bench(name, x, y, z, face='S', w=1.4, d=0.42, h=0.44, fab='fab_taupe'):
    it = Item(name, x, y, z, face); hw = w / 2
    for sx in (-1, 1):
        for yy in (0.06, d - 0.06):
            it.rod('wood_dark', (sx * (hw - 0.05), yy, 0), (sx * (hw - 0.05), yy, 0.1), 0.014, 0.02, 8)
    it.box(fab, -hw, hw, 0, d, 0.1, h, bev=0.05, seg=3)
    return it.finish()


# ------------------------------------------------------------------ workspace
def desk(name, x, y, z, face='N', w=1.5, d=0.7, h=0.75):
    it = Item(name, x, y, z, face); hw = w / 2
    it.box('wood_med', -hw, hw, 0, d, h - 0.035, h, bev=0.01)
    it.box('wood_dark', -hw + 0.03, -hw + 0.05, 0.03, d - 0.03, 0.0, h - 0.035)
    pw = 0.4
    it.box('wood_med', hw - pw, hw - 0.02, 0.03, d - 0.03, 0.0, h - 0.035, bev=0.008)
    for k in range(3):
        z0 = 0.1 + k * 0.2
        it.box('wood_dark', hw - pw + 0.02, hw - 0.04, d - 0.034, d - 0.02, z0, z0 + 0.18, bev=0.004, seg=1)
        it.box('steel', hw - pw / 2 - 0.05, hw - pw / 2 + 0.05, d - 0.02, d - 0.005, z0 + 0.12, z0 + 0.135, bev=0.003, seg=1)
    it.box('wood_dark', -hw + 0.03, hw - pw, 0.03, 0.06, h - 0.3, h - 0.035)
    return it.finish()


def office_chair(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face)
    for k in range(5):
        a = math.radians(72 * k + 10)
        e = (0.28 * math.cos(a), 0.28 * math.sin(a), 0.06)
        it.rod('black_plastic', (0, 0, 0.1), e, 0.016, 0.014, 6)
        it.sph('black_plastic', e[0], e[1], 0.03, 0.03, sz=1.0, seg=8, rings=5)
    it.rod('steel', (0, 0, 0.1), (0, 0, 0.42), 0.022, seg=8)
    it.box('fab_charcoal', -0.25, 0.25, -0.24, 0.24, 0.42, 0.5, bev=0.03, seg=3)
    it.box('black_plastic', -0.025, 0.025, -0.28, -0.2, 0.44, 0.7, bev=0.01)
    it.box('fab_charcoal', -0.23, 0.23, -0.3, -0.24, 0.55, 1.05, bev=0.04, seg=3, rot=(-8, 0, 0))
    for sx in (-1, 1):
        it.box('black_plastic', sx * 0.27 - 0.015, sx * 0.27 + 0.015, -0.2, 0.1, 0.66, 0.7)
        it.box('black_plastic', sx * 0.27 - 0.01, sx * 0.27 + 0.01, -0.16, -0.12, 0.5, 0.66)
    return it.finish()


def laptop(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='prop')
    it.box('graphite', -0.17, 0.17, 0.0, 0.23, 0.0, 0.015, bev=0.004, seg=1)
    it.box('graphite', -0.17, 0.17, 0.225, 0.24, 0.0, 0.23, bev=0.004, seg=1, rot=(-12, 0, 0))
    it.box('black_glass', -0.16, 0.16, 0.2, 0.205, 0.01, 0.22, rot=(-12, 0, 0))
    return it.finish()


def monitor(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='prop')
    it.box('black_plastic', -0.3, 0.3, 0.0, 0.03, 0.17, 0.53, bev=0.006)
    it.box('black_glass', -0.29, 0.29, 0.028, 0.031, 0.18, 0.52)
    it.box('black_plastic', -0.02, 0.02, 0.0, 0.04, 0.05, 0.17)
    it.box('black_plastic', -0.1, 0.1, -0.06, 0.1, 0.0, 0.012, bev=0.004)
    return it.finish()


def bookshelf(name, x, y, z, face='N', w=1.0, h=2.0, d=0.32, rows=5, seed=1, fill=0.8, mat='lam_cream'):
    it = Item(name, x, y, z, face); hw = w / 2
    r = random.Random(seed)
    it.box(mat, -hw, -hw + 0.02, 0, d, 0, h, bev=0.003, seg=1)
    it.box(mat, hw - 0.02, hw, 0, d, 0, h, bev=0.003, seg=1)
    it.box(mat, -hw, hw, 0, 0.012, 0, h)
    gap = (h - 0.06) / rows
    for k in range(rows + 1):
        zz = 0.05 + k * gap if k < rows else h - 0.02
        it.box(mat, -hw, hw, 0, d, zz - 0.01 if k else 0.0, zz + 0.012, bev=0.003, seg=1)
    bk = ['fab_maroon', 'fab_teal', 'fab_ochre', 'fab_cream', 'fab_green', 'rug_blue', 'wood_dark', 'fab_mustard', 'fab_grey']
    for k in range(rows):
        zb = 0.062 + k * gap
        xx = -hw + 0.03
        while xx < hw - 0.05 and r.random() < fill + 0.2:
            bw = r.uniform(0.018, 0.045); bh = r.uniform(gap * 0.55, gap * 0.9)
            if xx + bw > hw - 0.03:
                break
            lean = 0
            it.box(r.choice(bk), xx, xx + bw, 0.04, d - 0.02 - r.uniform(0, 0.03), zb, zb + bh, bev=0.002, seg=1)
            xx += bw + 0.002
            if r.random() < 0.06:
                xx += r.uniform(0.05, 0.2)
    return it.finish()


# ------------------------------------------------------------------ soft furnishings
def curtains(name, x, y, z, face, W, rod_z, panels, floor_z=None, rod_off=0.11, sheer=True, ring_mat='brass'):
    """x,y = wall-surface centre of rod. panels = [(u0,u1,material)], u relative to centre along item X. hangs to floor."""
    it = Item(name, x, y, z, face, kind='wall')
    it.rod('brass', (-W / 2 - 0.03, rod_off, rod_z), (W / 2 + 0.03, rod_off, rod_z), 0.012, seg=10)
    for sx in (-1, 1):
        it.sph('brass', sx * (W / 2 + 0.05), rod_off, rod_z, 0.025, seg=10, rings=6)
        it.box('brass', sx * (W / 2 - 0.02) - 0.01, sx * (W / 2 - 0.02) + 0.01, 0.0, rod_off, rod_z - 0.012, rod_z + 0.012)
    it.box('brass', -0.01, 0.01, 0.0, rod_off, rod_z - 0.012, rod_z + 0.012)
    bot = (floor_z if floor_z is not None else 0.0) + 0.02
    top = rod_z - 0.03
    if sheer:
        P = [[(-W / 2 + 0.05 + (W - 0.1) * k / 24, rod_off - 0.045 + 0.012 * math.sin(k * 1.9), zz) for k in range(25)] for zz in (top, (top + bot) / 2, bot)]
        it.grid('frosted', P, 0.002)
    for (u0, u1, mat) in panels:
        wd = u1 - u0
        folds = max(2, int(wd / 0.085))
        nx = folds * 6
        P = []
        for zz, amp in ((top, 1.0), ((top + bot) / 2, 0.85), (bot, 0.75)):
            row = []
            for k in range(nx + 1):
                t = k / nx
                row.append((u0 + wd * t, rod_off + 0.012 + 0.032 * amp * math.sin(2 * math.pi * folds * t), zz))
            P.append(row)
        it.grid(mat, P, 0.008)
        for k in range(folds):
            px = u0 + wd * (k + 0.25) / folds
            it.rod(ring_mat, (px, rod_off, rod_z - 0.005), (px, rod_off, rod_z - 0.045), 0.0045, seg=4)
    return it.finish()


def pillow(name, x, y, z, mat='fab_cream', w=0.4, h=0.4):
    it = Item(name, x, y, z, kind='prop')
    it.box(mat, -w / 2, w / 2, -0.07, 0.07, 0, h, bev=0.06, seg=3)
    return it.finish()


# ------------------------------------------------------------------ appliances / fixtures
def ceiling_fan(name, x, y, zc, blade='plastic_white', hub='plastic_white'):
    it = Item(name, x, y, zc, kind='ceil')
    it.lathe(hub, [(0.0, 0.0), (0.065, 0.0), (0.065, -0.04), (0.02, -0.05), (0.0, -0.05)], seg=14)
    it.rod('steel', (0, 0, -0.05), (0, 0, -0.3), 0.011, seg=8)
    it.lathe(hub, [(0.025, -0.3), (0.085, -0.31), (0.1, -0.33), (0.1, -0.37), (0.085, -0.4), (0.04, -0.41), (0, -0.41)], seg=18)
    for k in range(3):
        a = 120 * k + 15
        it.box(blade, 0.1, 0.62, -0.055, 0.055, -0.375, -0.368, bev=0.003, seg=1, rot=(7, 0, 0), spin=(a, 0, 0))
        it.box('graphite', 0.085, 0.16, -0.025, 0.025, -0.382, -0.364, bev=0.004, seg=1, spin=(a, 0, 0))
    return it.finish()


def split_ac(name, x, y, z, face='N', w=0.95, h=0.3, d=0.22):
    it = Item(name, x, y, z, face, kind='wall'); hw = w / 2
    it.box('plastic_white', -hw, hw, 0, d, 0, h, bev=0.045, seg=3)
    it.box('graphite', -hw + 0.04, hw - 0.04, d - 0.045, d - 0.02, 0.012, 0.045, bev=0.004, seg=1, rot=(-25, 0, 0))
    it.box('black_glass', hw - 0.12, hw - 0.06, d - 0.004, d + 0.002, h - 0.1, h - 0.07)
    it.rod('plastic_white', (hw - 0.05, 0.03, 0.04), (hw - 0.05, -0.05, 0.04), 0.028, seg=10)
    return it.finish()


def ac_outdoor(name, x, y, z, face='N', w=0.8, h=0.55, d=0.3):
    it = Item(name, x, y, z, face, kind='floor'); hw = w / 2
    it.box('plastic_white', -hw, hw, 0, d, 0.06, 0.06 + h, bev=0.02, seg=2)
    it.rod('graphite', (-0.08, d, 0.06 + h / 2), (-0.08, d + 0.01, 0.06 + h / 2), 0.19, seg=22)
    for k in range(7):
        zz = 0.06 + h / 2 - 0.17 + 0.057 * k
        it.box('graphite', -0.08 - 0.18, -0.08 + 0.18, d + 0.005, d + 0.012, zz, zz + 0.006)
    it.box('graphite', hw - 0.18, hw - 0.04, d, d + 0.01, 0.12, 0.6)
    for sx in (-1, 1):
        it.box('black_metal', sx * (hw - 0.1) - 0.04, sx * (hw - 0.1) + 0.04, 0.04, d - 0.04, 0, 0.06)
    return it.finish()


def tube_light(name, x, y, z, face='N', L=1.2):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('plastic_white', -L / 2, L / 2, 0, 0.032, 0, 0.045, bev=0.008, seg=1)
    it.rod('emit_white', (-L / 2 + 0.02, 0.05, 0.022), (L / 2 - 0.02, 0.05, 0.022), 0.0165, seg=10)
    for sx in (-1, 1):
        it.box('plastic_white', sx * (L / 2 - 0.02) - 0.012, sx * (L / 2 - 0.02) + 0.012, 0.028, 0.07, 0.0, 0.045)
    return it.finish()


def sconce(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('wood_dark', -0.05, 0.05, 0, 0.02, 0, 0.2, bev=0.005, seg=1)
    it.box('brass', -0.015, 0.015, 0.02, 0.1, 0.09, 0.11)
    it.box('emit_warm', -0.06, 0.06, 0.06, 0.17, 0.02, 0.22)
    for sx in (-1, 1):
        it.box('fab_cream', sx * 0.07 - 0.004, sx * 0.07 + 0.004, 0.05, 0.18, 0.015, 0.225)
    it.box('fab_cream', -0.07, 0.07, 0.176, 0.184, 0.015, 0.225)
    it.box('wood_dark', -0.07, 0.07, 0.05, 0.18, 0.21, 0.225, bev=0.003, seg=1)
    return it.finish()


def switchplate(name, x, y, z, face='N', n=2):
    it = Item(name, x, y, z, face, kind='wall')
    h = 0.075 + 0.04 * (n // 2)
    it.box('plastic_white', -0.04, 0.04, 0, 0.012, 0, h, bev=0.003, seg=1)
    for k in range(min(n, 4)):
        zz = 0.015 + k * 0.032
        it.box('paint_white', -0.012, 0.012, 0.012, 0.016, zz, zz + 0.022, bev=0.002, seg=1)
    return it.finish()


def downlight(name, x, y, zc, r=0.045):
    it = Item(name, x, y, zc, kind='ceil')
    it.lathe('plastic_white', [(r + 0.012, 0), (r + 0.012, -0.012), (r, -0.012)], seg=16)
    it.lathe('emit_warm', [(r, -0.011), (0, -0.011)], seg=16)
    return it.finish()


def pendant(name, x, y, zc, drop=0.8, kind='globe'):
    it = Item(name, x, y, zc, kind='ceil')
    it.lathe('black_metal', [(0.0, 0.0), (0.05, 0.0), (0.05, -0.02), (0.0, -0.02)], seg=12)
    it.rod('black_metal', (0, 0, -0.02), (0, 0, -drop), 0.004, seg=5)
    if kind == 'globe':
        it.sph('emit_warm', 0, 0, -drop - 0.12, 0.12, seg=14, rings=9)
    else:
        it.lathe('brass', [(0.05, -drop), (0.2, -drop - 0.18)], seg=18)
        it.lathe('emit_warm', [(0.045, -drop - 0.01), (0.18, -drop - 0.17)], seg=18)
    return it.finish()


def chandelier(name, x, y, zc, drop=0.6, r=0.38, arms=6):
    it = Item(name, x, y, zc, kind='ceil')
    it.lathe('brass', [(0, 0), (0.07, 0), (0.07, -0.03), (0.02, -0.04), (0.0, -0.04)], seg=14)
    it.rod('brass', (0, 0, -0.04), (0, 0, -drop), 0.012, seg=8)
    it.lathe('brass', [(0, -drop + 0.12), (0.05, -drop + 0.08), (0.045, -drop), (0.0, -drop - 0.1)], seg=14)
    for k in range(arms):
        a = 2 * math.pi * k / arms
        p1 = (r * math.cos(a), r * math.sin(a), -drop - 0.02)
        p0 = (0, 0, -drop + 0.02)
        pm = (r * 0.55 * math.cos(a), r * 0.55 * math.sin(a), -drop - 0.12)
        it.loft('brass', [p0, pm, p1, (p1[0], p1[1], p1[2] + 0.05)], 0.007, seg=6, cap=False)
        it.cyl('brass', p1[0], p1[1], p1[2] + 0.03, p1[2] + 0.07, 0.025, 0.018, seg=10)
        it.lathe('emit_warm', [(0.0, p1[2] + 0.2), (0.016, p1[2] + 0.17), (0.018, p1[2] + 0.07)], cx=p1[0], cy=p1[1], seg=8)
    return it.finish()


# ------------------------------------------------------------------ plants + decor
def _pot(it, kind, r, h):
    mat = {'terracotta': 'terracotta', 'ceramic': 'ceramic', 'black': 'black_plastic', 'blue': 'blue_plastic', 'clay_dark': 'clay_dark', 'brass': 'brass'}[kind]
    it.lathe(mat, [(r * 0.62, 0.0), (r * 0.62, 0.012), (r * 0.78, h * 0.05), (r, h * 0.9), (r * 1.06, h * 0.92), (r * 1.06, h), (r * 0.94, h), (r * 0.92, h - 0.02)], seg=18)
    it.lathe('soil', [(r * 0.93, h - 0.03), (0, h - 0.03)], seg=18)


def pot_plant(name, x, y, z, kind='snake', pot='terracotta', h=0.6, pot_r=0.14, pot_h=0.28, seed=3, kindtag='prop'):
    r = random.Random(seed)
    it = Item(name, x, y, z, kind=kindtag)
    _pot(it, pot, pot_r, pot_h)
    zt = pot_h - 0.02
    if kind == 'snake':
        for k in range(11):
            a = r.uniform(0, 2 * math.pi); rr = r.uniform(0.0, pot_r * 0.6)
            L = h * r.uniform(0.6, 1.0)
            d = (math.cos(a) * 0.12, math.sin(a) * 0.12, 1.0)
            it.leaf(r.choice(['leaf', 'leaf_dark', 'leaf_dark']), (rr * math.cos(a + 1), rr * math.sin(a + 1), zt), d, L, r.uniform(0.045, 0.07), droop=0.0, rise=0.0, rows=5)
    elif kind == 'aloe':
        for k in range(16):
            a = 2 * math.pi * k / 16 + r.uniform(-0.2, 0.2)
            up = r.uniform(0.7, 2.2)
            it.leaf('olive_leaf', (0, 0, zt), (math.cos(a), math.sin(a), up), h * r.uniform(0.7, 1.0), 0.085, droop=0.0, rise=0.0, rows=4)
    elif kind == 'areca' or kind == 'palm_small':
        for k in range(7):
            a = 2 * math.pi * k / 7 + r.uniform(-0.2, 0.2)
            L = h * r.uniform(0.7, 1.0)
            frond(it, 'leaf', (0.03 * math.cos(a), 0.03 * math.sin(a), zt), a, L, tilt=r.uniform(0.25, 0.7), leaflets=9, ll=h * 0.22)
    elif kind == 'money':
        for k in range(7):
            a = r.uniform(0, 2 * math.pi)
            pts = [(0.03 * math.cos(a), 0.03 * math.sin(a), zt), (0.06 * math.cos(a), 0.06 * math.sin(a), zt + h * 0.5), (0.14 * math.cos(a), 0.14 * math.sin(a), zt + h * 0.6),
                   (0.2 * math.cos(a), 0.2 * math.sin(a), zt + h * 0.2), (0.22 * math.cos(a), 0.22 * math.sin(a), zt - h * 0.2)]
            it.loft('leaf_dark', pts, 0.004, seg=4)
            for p in pts[1:]:
                for j in range(3):
                    it.sph('leaf' if j % 2 else 'leaf_light', p[0] + r.uniform(-0.05, 0.05), p[1] + r.uniform(-0.05, 0.05), p[2] + r.uniform(-0.04, 0.05), 0.045, sz=0.35, seg=7, rings=4)
    elif kind in ('ficus', 'rubber'):
        it.loft('trunk', [(0, 0, zt), (0.01, 0.0, zt + h * 0.5), (0.0, 0.02, zt + h * 0.8)], [0.012, 0.01, 0.006], seg=6)
        for k in range(46):
            zz = zt + h * r.uniform(0.35, 1.0); a = r.uniform(0, 6.28); rr = (1.0 - (zz - zt) / h * 0.4) * h * 0.18
            it.leaf('leaf' if k % 3 else 'leaf_dark', (0.01, 0.01, zz), (math.cos(a), math.sin(a), r.uniform(0.1, 0.8)), 0.16 + 0.1 * r.random(), 0.075, droop=0.35, rise=0.15, rows=3)
    elif kind == 'fern':
        for k in range(24):
            a = 2 * math.pi * k / 24 + r.uniform(-0.1, 0.1)
            it.leaf('leaf_light' if k % 2 else 'leaf', (0, 0, zt), (math.cos(a), math.sin(a), r.uniform(0.8, 1.6)), h * 0.9, 0.09, droop=0.5, rise=0.0, rows=5)
    return it.finish()


def frond(it, mat, base, ang, L, tilt=0.5, leaflets=12, ll=0.3, lw=0.03, droop=0.8, seg=7):
    base = Vector(base)
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    pts = []
    for k in range(seg + 1):
        t = k / seg
        pts.append(base + d * (L * t * (tilt + 0.3)) + Vector((0, 0, L * (t * (1.2 - tilt) - droop * t * t * (0.3 + tilt)))))
    it.loft('trunk' if mat == 'leaf' and False else 'leaf_dark', pts, [0.006 * (1 - 0.7 * k / seg) for k in range(seg + 1)], seg=4, cap=False)
    side = Vector((-d.y, d.x, 0.0))
    for k in range(1, leaflets + 1):
        t = k / (leaflets + 1)
        idx = min(seg - 1, int(t * seg)); fr = t * seg - idx
        p = pts[idx].lerp(pts[idx + 1], fr)
        tang = (pts[idx + 1] - pts[idx]).normalized()
        sc = math.sin(math.pi * (0.15 + 0.85 * t)) * 0.9 + 0.2
        for sgn in (-1, 1):
            dirv = (side * sgn * 0.85 + tang * 0.55 + Vector((0, 0, -0.35)))
            it.leaf(mat, p, dirv, ll * sc, lw + 0.02 * sc, droop=0.3, rise=0.0, rows=2)


def vase_tall(name, x, y, z, h=0.9, r=0.17, mat='terracotta', branches=True, seed=5):
    rr = random.Random(seed)
    it = Item(name, x, y, z)
    s = [(0.0, 0.0), (r * 0.5, 0.0), (r * 0.62, 0.03), (r * 1.0, h * 0.32), (r * 0.85, h * 0.55), (r * 0.42, h * 0.8), (r * 0.36, h * 0.92), (r * 0.5, h), (r * 0.42, h), (r * 0.3, h * 0.92)]
    it.lathe(mat, s, seg=22)
    if branches:
        for k in range(5):
            a = rr.uniform(0, 6.28); tl = rr.uniform(0.5, 0.9)
            it.rod('trunk', (0, 0, h * 0.9), (0.2 * math.cos(a) * tl, 0.2 * math.sin(a) * tl, h + tl), 0.005, 0.002, 4)
            for j in range(3):
                t = 0.45 + 0.2 * j
                it.sph('leaf_yellow', 0.2 * math.cos(a) * tl * t, 0.2 * math.sin(a) * tl * t, h * 0.9 + (h * 0.1 + tl) * t, 0.03, sz=0.5, seg=6, rings=4)
    return it.finish()


def wall_plate(name, x, y, z, face='N', r=0.13, mat='black_metal', rim='brass'):
    it = Item(name, x, y, z, face, kind='wall')
    it.lathe(mat, [(0, 0.012), (r * 0.8, 0.015), (r, 0.005), (r, 0.0), (0, 0.0)], seg=24)
    it.lathe(rim, [(r * 0.72, 0.013), (r * 0.75, 0.016), (r * 0.5, 0.017), (r * 0.46, 0.014)], seg=24)
    return it.finish()


def framed_art(name, x, y, z, face='N', w=0.9, h=0.6, c1='art_blue', c2='art_ochre', frame='wood_dark', seed=1):
    r = random.Random(seed)
    it = Item(name, x, y, z, face, kind='wall')
    it.box(frame, -w / 2, w / 2, 0, 0.03, 0, h, bev=0.006)
    it.box('paper', -w / 2 + 0.035, w / 2 - 0.035, 0.028, 0.032, 0.035, h - 0.035)
    for k in range(5):
        bw = r.uniform(0.12, 0.35) * w; bh = r.uniform(0.12, 0.4) * h
        px = r.uniform(-w / 2 + 0.05, w / 2 - 0.05 - bw); pz = r.uniform(0.05, h - 0.05 - bh)
        it.box(c1 if k % 2 else c2, px, px + bw, 0.032, 0.034, pz, pz + bh)
    return it.finish()


def wall_mirror(name, x, y, z, face='N', w=0.7, h=1.0, frame='wood_dark', shelf=False):
    it = Item(name, x, y, z, face, kind='wall')
    it.box(frame, -w / 2, w / 2, 0, 0.028, 0, h, bev=0.006)
    it.box('mirror', -w / 2 + 0.02, w / 2 - 0.02, 0.026, 0.03, 0.02, h - 0.02)
    return it.finish()


def doormat(name, x, y, z, face='N', w=0.8, d=0.5, mat='rug_red'):
    it = Item(name, x, y, z, face, kind='rug')
    it.box(mat, -w / 2, w / 2, -d / 2, d / 2, 0, 0.012, bev=0.004, seg=1)
    it.box('black_plastic', -w / 2 + 0.03, w / 2 - 0.03, -d / 2 + 0.03, d / 2 - 0.03, 0.0, 0.014)
    return it.finish()
