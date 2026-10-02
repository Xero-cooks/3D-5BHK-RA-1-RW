"""Round 3 kitchen + bathroom + service fixtures (module r3k)."""
import bpy, math, sys, random
from mathutils import Vector
c = sys.modules['r3c']; F = sys.modules['r3f']
Item = c.Item


def _ring(it, mat, cx, cy, cz, r, tube, plane='XZ', seg=14):
    pts = []
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        if plane == 'XZ':
            pts.append((cx + r * math.cos(a), cy, cz + r * math.sin(a)))
        else:
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
    for p0, p1 in zip(pts, pts[1:]):
        it.rod(mat, p0, p1, tube, seg=5, cap=False)


# ------------------------------------------------------------------ kitchen
def counter_top(it, x0, x1, d, z, holes=(), mat='granite_brown', t=0.03, over=0.02, back_up=0.0):
    """counter slab with rectangular holes [(hx0,hx1,hy0,hy1)] ; granite with small drip edge."""
    y1 = d + over
    xs = sorted({x0, x1, *[h[0] for h in holes], *[h[1] for h in holes]})
    for a, b in zip(xs, xs[1:]):
        hs = [h for h in holes if h[0] <= a + 1e-6 and h[1] >= b - 1e-6]
        if not hs:
            it.box(mat, a, b, 0, y1, z - t, z, bev=0.004, seg=1)
        else:
            h = hs[0]
            it.box(mat, a, b, 0, h[2], z - t, z, bev=0.004, seg=1)
            it.box(mat, a, b, h[3], y1, z - t, z, bev=0.004, seg=1)
    if back_up:
        it.box(mat, x0, x1, 0, 0.012, z, z + back_up)


def base_run(name, x, y, z, face, units, depth=0.6, H=0.9, sinks=(), kind='floor'):
    """units: list of (width, type) type in drawers|door2|door1|blank|open. centred on x. returns item"""
    L = sum(u[0] for u in units)
    it = Item(name, x, y, z, face, kind=kind)
    x0 = -L / 2
    it.box('teal_trim', x0, x0 + L, 0.02, depth - 0.07, 0.0, 0.1)
    holes = []
    cur = x0
    for (w, tp) in units:
        a, b = cur, cur + w
        it.box('lam_cream', a + 0.003, b - 0.003, 0.0, depth - 0.03, 0.1, H - 0.03, bev=0.003, seg=1)
        fz0, fz1 = 0.105, H - 0.034
        yf0, yf1 = depth - 0.03, depth - 0.008
        if tp == 'drawers':
            n = 3 if w > 0.5 else 2
            hh = (fz1 - fz0) / n
            for k in range(n):
                it.box('lam_cream', a + 0.004, b - 0.004, yf0, yf1, fz0 + k * hh + 0.003, fz0 + (k + 1) * hh - 0.003, bev=0.004, seg=1)
                it.box('steel', a + 0.06, b - 0.06, yf1, yf1 + 0.012, fz0 + (k + 1) * hh - 0.03, fz0 + (k + 1) * hh - 0.012, bev=0.002, seg=1)
        elif tp in ('door2', 'sink'):
            hw = (b - a) / 2
            for k in range(2):
                a2 = a + k * hw
                it.box('lam_cream', a2 + 0.004, a2 + hw - 0.004, yf0, yf1, fz0, fz1, bev=0.004, seg=1)
                hx = a2 + (0.04 if k else hw - 0.04)
                it.box('steel', hx - 0.007, hx + 0.007, yf1, yf1 + 0.014, fz1 - 0.3, fz1 - 0.04, bev=0.002, seg=1)
        elif tp == 'door1':
            it.box('lam_cream', a + 0.004, b - 0.004, yf0, yf1, fz0, fz1, bev=0.004, seg=1)
            it.box('steel', a + 0.03, a + 0.044, yf1, yf1 + 0.014, fz1 - 0.3, fz1 - 0.04, bev=0.002, seg=1)
        elif tp == 'oven':
            it.box('lam_cream', a + 0.004, b - 0.004, yf0, yf1, fz0 + 0.6, fz1, bev=0.004, seg=1)
            it.box('lam_cream', a + 0.004, b - 0.004, yf0, yf1, fz0, fz0 + 0.58, bev=0.004, seg=1)
            it.box('steel', a + 0.06, b - 0.06, yf1, yf1 + 0.012, fz0 + 0.57, fz0 + 0.59, bev=0.002, seg=1)
        if tp == 'sink':
            cx = (a + b) / 2
            holes.append((cx - 0.30, cx + 0.30, 0.1, 0.5))
        cur = b
    counter_top(it, x0, x0 + L, depth, H, holes)
    for hx0, hx1, hy0, hy1 in holes:  # steel bowl + drain-board
        it.box('steel', hx0 + 0.005, hx1 - 0.005, hy0 + 0.005, hy1 - 0.005, H - 0.19, H - 0.185)
        for (ax, bx, ay, by) in ((hx0, hx0 + 0.01, hy0, hy1), (hx1 - 0.01, hx1, hy0, hy1), (hx0, hx1, hy0, hy0 + 0.01), (hx0, hx1, hy1 - 0.01, hy1)):
            it.box('steel', ax, bx, ay, by, H - 0.19, H + 0.003)
        it.lathe('graphite', [(0.0, H - 0.186), (0.025, H - 0.186)], cx=(hx0 + hx1) / 2, cy=(hy0 + hy1) / 2, seg=10)
        cx = (hx0 + hx1) / 2
        # gooseneck tap
        it.loft('chrome', [(cx, 0.06, H), (cx, 0.06, H + 0.26), (cx, 0.12, H + 0.34), (cx, 0.2, H + 0.3), (cx, 0.22, H + 0.22)], 0.011, seg=8)
        it.box('chrome', cx + 0.015, cx + 0.06, 0.045, 0.075, H + 0.1, H + 0.115, bev=0.004, seg=1)
        it.cyl('chrome', cx, 0.06, H, H + 0.04, 0.022, seg=10)
    return it.finish()


def wall_run(name, x, y, z, face, units, depth=0.34, z0=1.45, z1=2.25, loft=0.62, ceil_z=2.85):
    L = sum(u[0] for u in units)
    it = Item(name, x, y, z, face, kind='wall')
    cur = -L / 2
    it.box('lam_cream', cur, cur + L, 0.0, 0.03, z0, z1 + (ceil_z - z1))
    for (w, tp) in units:
        a, b = cur, cur + w
        if tp != 'gap':
            it.box('lam_cream', a + 0.003, b - 0.003, 0.0, depth - 0.02, z0, z1, bev=0.003, seg=1)
            if tp == 'glass':
                it.box('wood_dark', a + 0.004, b - 0.004, depth - 0.02, depth - 0.008, z0 + 0.01, z1 - 0.01, bev=0.003, seg=1)
                it.box('glass_dark', a + 0.04, b - 0.04, depth - 0.012, depth - 0.006, z0 + 0.05, z1 - 0.05)
                it.box('lam_white', a + 0.03, b - 0.03, 0.05, depth - 0.05, z0 + 0.5, z0 + 0.515)
            else:
                nd = 2 if w > 0.55 else 1
                dw = w / nd
                for k in range(nd):
                    a2 = a + k * dw
                    it.box('lam_cream', a2 + 0.004, a2 + dw - 0.004, depth - 0.02, depth - 0.006, z0 + 0.004, z1 - 0.004, bev=0.004, seg=1)
                    hx = a2 + (dw - 0.04 if k % 2 == 0 else 0.04)
                    it.box('steel', hx - 0.007, hx + 0.007, depth - 0.006, depth + 0.008, z0 + 0.04, z0 + 0.26, bev=0.002, seg=1)
            # loft above
            if loft > 0:
                nl = max(1, int(round(w / 0.5)))
                lw = w / nl
                for k in range(nl):
                    a3 = a + k * lw
                    it.box('lam_cream', a3 + 0.003, a3 + lw - 0.003, 0.0, depth - 0.02, z1 + 0.003, ceil_z, bev=0.003, seg=1)
        cur = b
    return it.finish()


def chimney(name, x, y, z, face, w=0.6, zb=1.5):
    it = Item(name, x, y, z, face, kind='wall'); hw = w / 2
    it.mesh('black_plastic', [(-hw, 0.0, zb + 0.15), (hw, 0.0, zb + 0.15), (hw, 0.0, zb + 0.3), (-hw, 0.0, zb + 0.3),
                              (-hw, 0.46, zb), (hw, 0.46, zb), (hw, 0.5, zb + 0.07), (-hw, 0.5, zb + 0.07),
                              (-hw, 0.2, zb + 0.3), (hw, 0.2, zb + 0.3)],
            [(0, 1, 5, 4), (4, 5, 6, 7), (7, 6, 1, 0), (0, 4, 7), (1, 6, 5), (0, 7, 6, 1)])
    it.box('graphite', -hw, hw, 0.0, 0.2, zb + 0.28, zb + 0.9, bev=0.005, seg=1)
    for k in range(4):
        it.cyl('chrome', -hw + 0.1 + k * 0.07, 0.4, zb + 0.07, zb + 0.075, 0.014, seg=8)
    return it.finish()


def hob(name, x, y, z, face, burners=3):
    it = Item(name, x, y, z, face, kind='prop')
    w, d = 0.72, 0.5
    it.box('black_glass', -w / 2, w / 2, 0, d, 0, 0.012, bev=0.005, seg=2)
    pos = [(-0.19, 0.17, 0.052), (0.15, 0.2, 0.062), (0.0, 0.34, 0.042)] if burners == 3 else [(-0.17, 0.25, 0.06), (0.17, 0.25, 0.06)]
    for (px, py, r) in pos:
        it.lathe('graphite', [(r * 1.2, 0.012), (r * 1.2, 0.02), (r, 0.03), (r * 0.5, 0.03)], cx=px, cy=py, seg=14)
        it.lathe('brass', [(r * 0.6, 0.03), (r * 0.6, 0.038), (r * 0.3, 0.04)], cx=px, cy=py, seg=12)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
        it.box('black_metal', px - r * 1.45, px + r * 1.45, py - 0.006, py + 0.006, 0.04, 0.048)
        it.box('black_metal', px - 0.006, px + 0.006, py - r * 1.45, py + r * 1.45, 0.04, 0.048)
    for k in range(3):
        it.rod('black_plastic', (-0.2 + k * 0.2, 0.0, 0.015), (-0.2 + k * 0.2, -0.02, 0.015), 0.014, seg=8)
    return it.finish()


def fridge(name, x, y, z, face, w=0.62, d=0.68, h=1.62):
    it = Item(name, x, y, z, face, kind='floor'); hw = w / 2
    it.box('graphite', -hw, hw, 0, d, 0.03, h, bev=0.02, seg=2)
    it.box('black_glass', -hw + 0.015, hw - 0.015, d - 0.002, d + 0.006, 0.05, h - 0.02, bev=0.004, seg=1)
    it.box('steel', -hw + 0.04, -hw + 0.055, d + 0.006, d + 0.03, 0.2, h * 0.7, bev=0.003, seg=1)
    it.box('steel', -hw, hw, d + 0.004, d + 0.007, h * 0.74 - 0.003, h * 0.74 + 0.003)
    it.box('steel', -hw + 0.03, hw - 0.03, 0.12, 0.2, 0.0, 0.03)
    for sx in (-1, 1):
        it.box('black_plastic', sx * (hw - 0.06) - 0.03, sx * (hw - 0.06) + 0.03, 0.04, 0.12, 0, 0.03)
    return it.finish()


def kettle(name, x, y, z, mat='red_plastic'):
    it = Item(name, x, y, z, kind='prop')
    it.lathe(mat, [(0.0, 0.0), (0.08, 0.0), (0.085, 0.02), (0.075, 0.2), (0.06, 0.22), (0.0, 0.225)], seg=14)
    it.lathe('black_plastic', [(0.0, 0.0), (0.095, 0.0), (0.095, 0.02), (0.0, 0.02)], seg=14)
    it.loft('black_plastic', [(0.06, 0.0, 0.2), (0.12, 0.0, 0.22), (0.12, 0.0, 0.12), (0.075, 0.0, 0.05)], 0.008, seg=5)
    return it.finish()


def bottle(name, x, y, z, mat='blue_plastic', h=0.26, r=0.032):
    it = Item(name, x, y, z, kind='prop')
    it.lathe(mat, [(0, 0), (r, 0), (r, h * 0.7), (r * 0.7, h * 0.85), (r * 0.35, h * 0.9), (r * 0.35, h * 0.97), (0, h * 0.97)], seg=10)
    it.cyl('white' if False else 'plastic_white', 0, 0, h * 0.95, h, r * 0.4, seg=8)
    return it.finish()


def bowl(name, x, y, z, r=0.07, mat='pink_plastic'):
    it = Item(name, x, y, z, kind='prop')
    it.lathe(mat, [(0, 0), (r * 0.5, 0), (r, r * 0.6), (r * 1.02, r * 0.65), (r * 0.95, r * 0.62), (r * 0.5, 0.012)], seg=16)
    return it.finish()


def mixer_jar(name, x, y, z):
    it = Item(name, x, y, z, kind='prop')
    it.box('plastic_white', -0.1, 0.1, -0.08, 0.1, 0, 0.12, bev=0.03, seg=2)
    it.lathe('steel', [(0.0, 0.12), (0.085, 0.12), (0.075, 0.3), (0.0, 0.3)], cx=0.0, cy=0.0, seg=14)
    it.cyl('red_plastic', 0.0, 0.0, 0.3, 0.32, 0.06, seg=12)
    return it.finish()


def rice_cooker(name, x, y, z):
    it = Item(name, x, y, z, kind='prop')
    it.lathe('plastic_white', [(0, 0), (0.14, 0), (0.15, 0.02), (0.15, 0.17), (0.12, 0.25), (0.0, 0.27)], seg=18)
    it.rod('black_cable' if False else 'black_plastic', (0.15, 0, 0.05), (0.3, 0.06, 0.0), 0.005, seg=4)
    it.lathe('red_plastic', [(0.15, 0.1), (0.153, 0.12), (0.153, 0.14), (0.15, 0.14)], seg=18)
    return it.finish()


def knife_block(name, x, y, z):
    it = Item(name, x, y, z, kind='prop')
    it.box('wood_med', -0.07, 0.07, -0.05, 0.05, 0, 0.2, bev=0.01)
    for k in range(3):
        it.box('blue_plastic', -0.045 + k * 0.045, -0.03 + k * 0.045, -0.02, 0.02, 0.2, 0.25)
    return it.finish()


def exhaust_fan(name, x, y, z, face='N', s=0.25):
    it = Item(name, x, y, z, face, kind='wall'); h = s / 2
    it.box('plastic_white', -h, h, 0, 0.05, 0, s, bev=0.015, seg=2)
    it.rod('graphite', (0, 0.049, h), (0, 0.055, h), h * 0.82, seg=22)
    for k in range(5):
        a = 72 * k
    for k in range(3):
        a = math.radians(120 * k + 20)
        it.rod('plastic_white', (0, 0.056, h), (h * 0.7 * math.cos(a), 0.056, h + h * 0.7 * math.sin(a)), 0.012, 0.006, 5)
    return it.finish()


# ------------------------------------------------------------------ bathroom
def wc(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='floor')
    it.box('ceramic', -0.19, 0.19, 0.0, 0.2, 0.2, 0.78, bev=0.04, seg=3)
    it.box('plastic_white', -0.2, 0.2, 0.0, 0.215, 0.76, 0.8, bev=0.015, seg=2)
    it.rod('chrome', (0, 0.1, 0.8), (0, 0.1, 0.82), 0.03, seg=12)
    it.lathe('ceramic', [(0.0, 0.0), (0.11, 0.0), (0.16, 0.12), (0.19, 0.28), (0.2, 0.43), (0.12, 0.43)], cx=0.0, cy=0.36, sy=1.45, seg=24)
    it.lathe('ceramic', [(0.0, 0.0), (0.1, 0.0), (0.12, 0.12), (0.12, 0.22)], cx=0.0, cy=0.12, seg=14)
    it.lathe('plastic_white', [(0.12, 0.435), (0.2, 0.435), (0.205, 0.452), (0.2, 0.462), (0.12, 0.462)], cx=0.0, cy=0.36, sy=1.45, seg=24)
    it.lathe('plastic_white', [(0.0, 0.466), (0.19, 0.466), (0.188, 0.474), (0.0, 0.474)], cx=0.0, cy=0.36, sy=1.38, seg=24)
    it.rod('chrome', (0.3, 0.0, 0.1), (0.3, 0.06, 0.1), 0.01, seg=6)
    return it.finish()


def basin_wall(name, x, y, z, face='N', w=0.5, d=0.4, zt=0.82):
    it = Item(name, x, y, z, face, kind='wall'); hw = w / 2
    t = 0.03
    it.box('ceramic', -hw, -hw + t, 0, d, zt - 0.14, zt, bev=0.02, seg=2)
    it.box('ceramic', hw - t, hw, 0, d, zt - 0.14, zt, bev=0.02, seg=2)
    it.box('ceramic', -hw, hw, 0, t, zt - 0.14, zt + 0.02, bev=0.012, seg=2)
    it.box('ceramic', -hw, hw, d - t, d, zt - 0.14, zt, bev=0.02, seg=2)
    it.box('ceramic', -hw + 0.02, hw - 0.02, 0, d - 0.02, zt - 0.14, zt - 0.1, bev=0.02, seg=2)
    it.cyl('graphite', 0, d * 0.5, zt - 0.1, zt - 0.098, 0.022, seg=10)
    cx = 0.0
    it.cyl('chrome', cx, 0.07, zt + 0.02, zt + 0.1, 0.018, seg=10)
    it.rod('chrome', (cx, 0.07, zt + 0.1), (cx, 0.2, zt + 0.12), 0.011, seg=8)
    it.rod('chrome', (cx + 0.02, 0.07, zt + 0.08), (cx + 0.07, 0.07, zt + 0.1), 0.007, seg=6)
    # trap + brackets
    it.rod('chrome', (0, 0.12, zt - 0.14), (0, 0.12, zt - 0.3), 0.017, seg=8)
    it.rod('chrome', (0, 0.12, zt - 0.3), (0, 0.025, zt - 0.3), 0.017, seg=8)
    it.rod('chrome', (0, 0.025, zt - 0.3), (0, 0.0, zt - 0.3), 0.025, seg=8)
    for sx in (-1, 1):
        it.rod('chrome', (sx * (hw - 0.05), 0.0, zt - 0.2), (sx * (hw - 0.05), 0.22, zt - 0.14), 0.007, seg=5)
    return it.finish()


def vanity(name, x, y, z, face='N', w=0.9, d=0.5, h=0.82):
    it = Item(name, x, y, z, face, kind='floor'); hw = w / 2
    it.box('teal_trim' if False else 'black_plastic', -hw, hw, 0.02, d - 0.07, 0.0, 0.08)
    it.box('lam_grey', -hw, hw, 0.0, d - 0.03, 0.08, h - 0.03, bev=0.005, seg=1)
    for k in range(2):
        a = -hw + k * hw
        it.box('wood_med', a + 0.004, a + hw - 0.004, d - 0.03, d - 0.01, 0.09, h - 0.035, bev=0.004, seg=1)
        hx = a + (hw - 0.05 if k == 0 else 0.05)
        it.box('chrome', hx - 0.007, hx + 0.007, d - 0.01, d + 0.012, h - 0.3, h - 0.07, bev=0.002, seg=1)
    it.box('marble_white', -hw - 0.01, hw + 0.01, 0.0, d + 0.01, h - 0.03, h, bev=0.004, seg=1)
    it.lathe('ceramic', [(0.0, h), (0.17, h), (0.2, h + 0.03), (0.2, h + 0.12), (0.185, h + 0.12), (0.18, h + 0.04), (0.0, h + 0.035)], cx=0.0, cy=d * 0.55, seg=22)
    it.cyl('chrome', 0.0, 0.08, h, h + 0.22, 0.016, seg=10)
    it.rod('chrome', (0.0, 0.08, h + 0.22), (0.0, 0.2, h + 0.22), 0.011, seg=8)
    it.box('marble_white', -hw - 0.01, hw + 0.01, 0.0, 0.012, h, h + 0.1)
    return it.finish()


def bath_mirror(name, x, y, z, face='N', w=0.62, h=0.82, zb=1.2, shelf=True):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('black_metal', -w / 2, w / 2, 0.0, 0.025, zb, zb + h, bev=0.004, seg=1)
    it.box('mirror', -w / 2 + 0.012, w / 2 - 0.012, 0.024, 0.027, zb + 0.012, zb + h - 0.012)
    if shelf:
        it.box('ceramic', -w / 2, w / 2, 0.0, 0.1, zb + h + 0.06, zb + h + 0.075, bev=0.003, seg=1)
        it.box('chrome', -w / 2 + 0.03, -w / 2 + 0.036, 0.0, 0.03, zb + h + 0.04, zb + h + 0.06)
        it.box('chrome', w / 2 - 0.036, w / 2 - 0.03, 0.0, 0.03, zb + h + 0.04, zb + h + 0.06)
    return it.finish()


def towel_ring(name, x, y, z, face='N', towel=True):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('chrome', -0.02, 0.02, 0.0, 0.012, -0.02, 0.02)
    _ring(it, 'chrome', 0.0, 0.05, 0.05, 0.075, 0.006, 'XZ')
    if towel:
        it.grid('fab_white', [[(-0.1, 0.07, 0.11), (0.1, 0.07, 0.11)], [(-0.1, 0.072, -0.4), (0.1, 0.072, -0.4)]], 0.01)
        it.grid('blue_plastic', [[(-0.1, 0.07, -0.25), (0.1, 0.07, -0.25)], [(-0.1, 0.072, -0.28), (0.1, 0.072, -0.28)]], 0.012)
    return it.finish()


def shower(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='wall')
    it.rod('chrome', (0, 0.0, 2.2), (0, 0.22, 2.2), 0.012, seg=8)
    it.lathe('chrome', [(0.0, 2.17), (0.1, 2.17), (0.1, 2.19), (0.0, 2.2)], cx=0.0, cy=0.3, seg=18)
    it.rod('chrome', (0.0, 0.22, 2.2), (0, 0.3, 2.19), 0.012, seg=8)
    it.box('chrome', -0.08, 0.08, 0.0, 0.02, 1.0, 1.14, bev=0.006, seg=2)
    it.rod('chrome', (0, 0.02, 1.07), (0.07, 0.07, 1.07), 0.008, seg=6)
    it.rod('chrome', (-0.3, 0.02, 1.07), (-0.3, 0.08, 1.07), 0.01, seg=8)
    it.rod('chrome', (-0.3, 0.0, 1.6), (-0.3, 0.05, 1.6), 0.013, seg=8)
    it.loft('plastic_white', [(-0.3, 0.06, 1.07), (-0.34, 0.1, 0.9), (-0.3, 0.12, 0.7), (-0.2, 0.06, 0.65), (-0.18, 0.02, 0.9), (-0.22, 0.04, 1.4), (-0.28, 0.07, 1.57)], 0.007, seg=5, cap=False)
    it.rod('chrome', (-0.28, 0.07, 1.55), (-0.3, 0.07, 1.65), 0.012, seg=6)
    return it.finish()


def glass_panel(name, x0, y0, x1, y1, z0, z1, frame=True):
    it = Item(name, 0, 0, 0, 'N', kind='wall')
    d = Vector((x1 - x0, y1 - y0, 0)); L = d.length; a = math.degrees(math.atan2(d.y, d.x))
    it = Item(name, x0, y0, 0, 'N', kind='wall', rotdeg=a)
    it.box('glass', 0, L, -0.004, 0.004, z0, z1)
    it.box('chrome', 0, L, -0.008, 0.008, z1 - 0.02, z1, bev=0.002, seg=1)
    it.box('chrome', 0, 0.02, -0.008, 0.008, z0, z1, bev=0.002, seg=1)
    it.box('chrome', L - 0.015, L, -0.008, 0.008, z0, z1, bev=0.002, seg=1)
    return it.finish()


def geyser(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='wall')
    it.lathe('plastic_white', [(0.0, 0.0), (0.14, 0.0), (0.16, 0.05), (0.16, 0.45), (0.14, 0.5), (0.0, 0.5)], cx=0.0, cy=0.17, seg=20, z=0.0)
    it.box('plastic_white', -0.12, 0.12, 0.0, 0.05, 0.0, 0.5)
    it.rod('black_plastic', (0.0, 0.34, 0.05), (0.0, 0.345, 0.05), 0.04, seg=12)
    it.rod('red_plastic', (0.0, 0.34, 0.25), (0.0, 0.345, 0.25), 0.012, seg=8)
    return it.finish()


def bucket_mug(name, x, y, z):
    it = Item(name, x, y, z, kind='prop')
    it.lathe('red_plastic', [(0.0, 0.0), (0.12, 0.0), (0.18, 0.28), (0.17, 0.29), (0.115, 0.01), (0.0, 0.01)], seg=18)
    it.loft('steel', [(-0.18, 0, 0.27), (-0.18, 0, 0.36), (0, 0, 0.4), (0.18, 0, 0.36), (0.18, 0, 0.27)], 0.004, seg=4, cap=False)
    it.lathe('yellow_plastic', [(0.0, 0.0), (0.05, 0.0), (0.06, 0.12), (0.055, 0.12), (0.045, 0.01), (0.0, 0.01)], cx=0.34, cy=0.0, seg=12)
    return it.finish()


def floor_drain(name, x, y, z, r=0.06):
    it = Item(name, x, y, z, kind='prop')
    it.lathe('chrome', [(r, 0.0), (r, 0.004), (0.0, 0.004)], seg=20)
    it.lathe('graphite', [(r * 0.8, 0.0045), (r * 0.8, 0.005), (0, 0.005)], seg=14)
    return it.finish()


def toilet_roll(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('chrome', -0.07, 0.07, 0.0, 0.012, 0.0, 0.14)
    it.rod('chrome', (-0.07, 0.03, 0.07), (0.07, 0.03, 0.07), 0.005, seg=5)
    it.rod('paper', (-0.05, 0.05, 0.07), (0.05, 0.05, 0.07), 0.05, seg=14)
    return it.finish()


def soap_dispenser(name, x, y, z):
    it = Item(name, x, y, z, kind='prop')
    it.lathe('ceramic', [(0, 0), (0.035, 0), (0.037, 0.14), (0.0, 0.14)], seg=12)
    it.rod('chrome', (0, 0, 0.14), (0, 0, 0.17), 0.008, seg=6)
    it.rod('chrome', (0, 0, 0.17), (0.03, 0, 0.175), 0.006, seg=6)
    return it.finish()


def washing_machine(name, x, y, z, face='N', cover=False):
    it = Item(name, x, y, z, face, kind='floor')
    it.box('plastic_white', -0.3, 0.3, 0.0, 0.58, 0.0, 0.95, bev=0.02, seg=2)
    it.box('graphite', -0.29, 0.29, 0.0, 0.24, 0.94, 0.99, bev=0.01, seg=1)
    if cover:
        it.box('cardboard', -0.33, 0.33, -0.03, 0.62, 0.0, 1.0, bev=0.06, seg=3)
    return it.finish()
