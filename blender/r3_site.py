"""Round 3 - site: gate, boundary, drive details, landscaping, site lighting  [module r3s]."""
import bpy, bmesh, math, sys, random
from mathutils import Vector, Matrix
c = sys.modules['r3c']; F = sys.modules['r3f']; r1 = sys.modules['r1']; E = sys.modules['r3e']
Item = c.Item
A = sys.modules['r3a']
WB, WR = A.WB, A.WR


def setl(sub):
    r1._colls()
    coll = c.sub_coll(r1.C['LAND'], sub)
    c.ctx(coll, None, 'SITE', '', 'r3')


# ------------------------------------------------------------------ plants
def palm(name, x, y, h=6.0, seed=1, fronds=11, lean=0.0):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    r0, r1_ = 0.16, 0.1
    n = int(h / 0.22)
    prof = [(0.0, 0.0), (0.22, 0.0), (0.2, 0.12)]
    for k in range(n):
        t = k / n
        rr_ = r0 + (r1_ - r0) * t
        zz = 0.12 + k * (h - 0.4) / n
        prof += [(rr_, zz), (rr_ * 1.12, zz + 0.02), (rr_ * 1.12, zz + 0.045), (rr_, zz + 0.07)]
    prof += [(r1_, h - 0.4), (r1_ * 0.95, h - 0.1), (r1_ * 1.25, h - 0.1), (r1_ * 1.25, h + 0.25), (0.08, h + 0.28)]
    it.lathe('palm_trunk', prof, seg=14)
    it.lathe('leaf_dark', [(r1_ * 1.3, h - 0.1), (r1_ * 1.1, h + 0.28), (r1_ * 0.9, h + 0.9), (r1_ * 0.5, h + 1.0)], seg=10)
    for k in range(fronds):
        a = 2 * math.pi * k / fronds + rr.uniform(-0.2, 0.2)
        L = rr.uniform(2.1, 2.7)
        tilt = 0.35 + 0.7 * ((k % 3) / 2.0)
        F.frond(it, 'leaf', (0.05 * math.cos(a), 0.05 * math.sin(a), h + 0.15 + (k % 3) * 0.05), a, L, tilt=tilt * 0.8, leaflets=14, ll=0.75, lw=0.03, droop=0.9 - 0.25 * (k % 3) / 2, seg=7)
    # fruit cluster
    for k in range(10):
        a = rr.uniform(0, 6.28)
        it.sph('flower_orange', 0.14 * math.cos(a), 0.14 * math.sin(a), h - 0.25 - rr.uniform(0, 0.2), 0.035, seg=6, rings=4)
    return it.finish()


def blob_cluster(it, cx, cy, cz, rad, n, mats, rr, sz=0.75, size=(0.3, 0.55), seg=7):
    for k in range(n):
        a = rr.uniform(0, 6.28); d = rr.uniform(0, rad) ** 1.0; zz = rr.uniform(0, 1.0)
        r = rr.uniform(*size) * rad
        it.sph(rr.choice(mats), cx + d * math.cos(a), cy + d * math.sin(a), cz + zz * rad * 0.9, r, sz=sz, seg=seg, rings=5)


def tree_round(name, x, y, h=7.0, crown=3.2, seed=1, mats=('leaf', 'leaf_dark', 'leaf_light', 'leaf_dark')):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    th = h * 0.5
    it.loft('trunk', [(0, 0, 0), (0.03, 0.0, th * 0.4), (0.0, 0.05, th * 0.8), (0.02, 0.03, th)], [0.24, 0.17, 0.13, 0.1], seg=9)
    br = []
    for k in range(6):
        a = 2 * math.pi * k / 6 + rr.uniform(-0.3, 0.3)
        e = (crown * 0.55 * math.cos(a), crown * 0.55 * math.sin(a), th + crown * 0.55)
        it.loft('trunk', [(0, 0, th * 0.85), (e[0] * 0.5, e[1] * 0.5, th + crown * 0.2), e], [0.08, 0.055, 0.03], seg=6)
        br.append(e)
    cz = th + crown * 0.35
    for k in range(90):
        a = rr.uniform(0, 6.28); u = rr.random() ** 0.6; v = rr.uniform(0.05, 1.0)
        rad = crown * u * math.sqrt(max(0.0, 1 - (v - 0.5) ** 2 * 3.0))
        px, py, pz = rad * math.cos(a), rad * math.sin(a), cz + (v - 0.35) * crown * 1.15
        it.sph(rr.choice(mats), px, py, pz, crown * rr.uniform(0.17, 0.27), sz=0.72, seg=8, rings=5)
    return it.finish()


def tree_column(name, x, y, h=9.0, w=1.1, seed=2):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    it.loft('trunk', [(0, 0, 0), (0.0, 0.0, h * 0.35)], [0.16, 0.1], seg=8)
    for k in range(70):
        t = rr.random() ** 0.8
        zz = h * 0.25 + t * h * 0.75
        prof = math.sin(math.pi * min(1.0, 0.25 + 0.75 * (1 - t) ** 0.9)) * 0.9 + 0.12
        rad = w * prof * (1 - 0.25 * t)
        a = rr.uniform(0, 6.28); d = rad * math.sqrt(rr.random())
        it.sph(rr.choice(('leaf', 'leaf_dark', 'leaf_light', 'leaf_dark')), d * math.cos(a), d * math.sin(a), zz, w * rr.uniform(0.28, 0.42) * (1 - 0.4 * t), sz=0.9, seg=7, rings=5)
    return it.finish()


def shrub(name, x, y, r=0.5, kind='bush', seed=1):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    if kind == 'bush':
        blob_cluster(it, 0, 0, 0.0, r, 14, ['leaf', 'leaf_dark', 'leaf_light'], rr, sz=0.8, size=(0.35, 0.55), seg=7)
    elif kind == 'flower':
        blob_cluster(it, 0, 0, 0.0, r, 12, ['leaf', 'leaf_dark'], rr, sz=0.8, size=(0.35, 0.55), seg=7)
        for k in range(14):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, r * 0.9)
            it.sph(rr.choice(('flower_pink', 'flower_orange', 'flower_pink')), d * math.cos(a), d * math.sin(a), r * rr.uniform(0.45, 0.95), 0.045 * (1 + r), seg=6, rings=4)
    elif kind == 'croton':
        for k in range(26):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, 0.12)
            it.leaf(rr.choice(('leaf_yellow', 'leaf_red', 'leaf', 'leaf_yellow')), (d * math.cos(a), d * math.sin(a), 0.05), (math.cos(a), math.sin(a), rr.uniform(0.5, 1.8)), r * rr.uniform(0.9, 1.4), 0.09, droop=0.3, rise=0.1, rows=3)
    elif kind == 'agave':
        for k in range(18):
            a = 2 * math.pi * k / 18 + rr.uniform(-0.1, 0.1)
            it.leaf('olive_leaf', (0, 0, 0.05), (math.cos(a), math.sin(a), rr.uniform(0.6, 2.4)), r * rr.uniform(1.0, 1.5), 0.11, droop=0.0, rise=0.0, rows=4)
    elif kind == 'grass':
        for k in range(36):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, 0.1)
            it.leaf(rr.choice(('leaf_light', 'grass_dry', 'leaf_light')), (d * math.cos(a), d * math.sin(a), 0.0), (math.cos(a), math.sin(a), rr.uniform(1.4, 3.0)), r * rr.uniform(1.0, 1.6), 0.025, droop=0.9, rise=0.0, rows=4)
    elif kind == 'bougain':
        blob_cluster(it, 0, 0, 0.0, r, 16, ['leaf', 'leaf_dark'], rr, sz=0.8, size=(0.3, 0.5), seg=7)
        for k in range(30):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, r)
            it.sph('flower_pink', d * math.cos(a), d * math.sin(a), rr.uniform(0.2, 1.0) * r, 0.04, seg=5, rings=3)
    return it.finish()


def hedge(name, x0, y0, x1, y1, h=0.7, w=0.5, seed=1):
    rr = random.Random(seed)
    it = Item(name, (x0 + x1) / 2, (y0 + y1) / 2, 0.0, kind='prop')
    L = math.hypot(x1 - x0, y1 - y0)
    it.rot = math.atan2(y1 - y0, x1 - x0)
    it.box('hedge', -L / 2, L / 2, -w / 2 * 0.9, w / 2 * 0.9, 0.0, h * 0.8, bev=0.1, seg=2)
    n = int(L / 0.2)
    for k in range(n):
        xx = -L / 2 + (k + 0.5) * L / n
        for j in range(2):
            it.sph(rr.choice(('hedge', 'leaf_dark', 'hedge', 'leaf')), xx + rr.uniform(-0.05, 0.05), rr.uniform(-w * 0.25, w * 0.25), h * (0.72 + 0.1 * j) + rr.uniform(-0.03, 0.03),
                   0.17 + rr.uniform(0, 0.07), sy=w / 0.5 * 1.1, sz=0.6, seg=6, rings=4)
    return it.finish()


def boulder(name, x, y, r=0.4, seed=1):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    b = it._b('stone_grey')
    it.sph('stone_grey', 0, 0, r * 0.45, r, sx=1.0, sy=rr.uniform(0.7, 1.0), sz=0.65, seg=9, rings=6)
    for v in list(b.verts):
        v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * r * 0.08
    return it.finish()


def stepping_stone(name, x, y, rot=0.0, w=0.6, seed=1):
    rr = random.Random(seed)
    it = Item(name, x, y, 0.0, kind='prop')
    it.rot = math.radians(rot)
    it.box('stone_grey', -w / 2, w / 2, -w / 2 * rr.uniform(0.8, 1.0), w / 2 * rr.uniform(0.8, 1.0), 0.0, 0.05, bev=0.03, seg=2, spin=(rr.uniform(-15, 15), 0, 0))
    return it.finish()


# ------------------------------------------------------------------ lighting hardware
def lamp_post(name, x, y, h=3.4, face=0.0):
    it = Item(name, x, y, 0.0, kind='prop')
    it.lathe('black_metal', [(0.0, 0.0), (0.2, 0.0), (0.2, 0.08), (0.14, 0.14), (0.1, 0.35), (0.12, 0.4), (0.07, 0.45), (0.06, 0.5)], seg=10)
    it.rod('black_metal', (0, 0, 0.45), (0, 0, h - 0.5), 0.055, 0.04, seg=10)
    for zz in (1.1, 2.0):
        it.lathe('black_metal', [(0.045, zz), (0.075, zz + 0.02), (0.075, zz + 0.05), (0.045, zz + 0.07)], seg=10)
    zt = h - 0.5
    it.lathe('black_metal', [(0.04, zt), (0.09, zt + 0.04), (0.07, zt + 0.1), (0.06, zt + 0.12)], seg=10)
    # scroll arm
    it.loft('black_metal', [(0, 0, 1.6), (0.14, 0, 1.75), (0.25, 0, 1.7), (0.3, 0, 1.58)], 0.011, seg=6, cap=False)
    it.loft('black_metal', [(0, 0, h - 0.7), (-0.14, 0, h - 0.55), (-0.25, 0, h - 0.6), (-0.3, 0, h - 0.72)], 0.011, seg=6, cap=False)
    # lantern
    zb = h - 0.4
    it.lathe('black_metal', [(0.06, zb), (0.1, zb + 0.03), (0.0, zb + 0.03)], seg=6)
    it.lathe('emit_warm', [(0.1, zb + 0.03), (0.14, zb + 0.34)], seg=6)
    for k in range(6):
        a = math.pi / 6 + k * math.pi / 3
        it.rod('black_metal', (0.1 * math.cos(a), 0.1 * math.sin(a), zb + 0.03), (0.143 * math.cos(a), 0.143 * math.sin(a), zb + 0.34), 0.007, seg=4)
    it.lathe('black_metal', [(0.17, zb + 0.34), (0.07, zb + 0.45), (0.02, zb + 0.48)], seg=6)
    it.sph('black_metal', 0, 0, zb + 0.5, 0.025, seg=8, rings=5)
    return it.finish()


def bollard(name, x, y, h=0.65):
    it = Item(name, x, y, 0.0, kind='prop')
    it.lathe('black_metal', [(0.0, 0.0), (0.07, 0.0), (0.07, h - 0.14), (0.065, h - 0.12)], seg=12)
    it.lathe('emit_warm', [(0.068, h - 0.14), (0.068, h - 0.04)], seg=12)
    it.lathe('black_metal', [(0.08, h - 0.04), (0.07, h), (0.0, h)], seg=12)
    return it.finish()


def uplight(name, x, y, rot=0.0):
    it = Item(name, x, y, 0.0, kind='prop')
    it.cyl('black_metal', 0, 0, 0, 0.06, 0.07, seg=12)
    it.lathe('emit_warm', [(0.055, 0.061), (0.0, 0.061)], seg=12)
    return it.finish()


def planter_tub(name, x, y, r=0.38, h=0.6, plant='areca', seed=3):
    it = Item(name, x, y, 0.0, kind='prop')
    it.lathe('concrete', [(r * 0.8, 0.0), (r, 0.04), (r, h * 0.9), (r * 1.1, h * 0.92), (r * 1.1, h), (r * 0.95, h)], seg=20)
    it.lathe('soil', [(r * 0.94, h - 0.03), (0, h - 0.03)], seg=16)
    it.finish()


# ------------------------------------------------------------------ gate + boundary
def gate_and_wall():
    setl('15_Hardscape')
    yg = 42.0
    # pillars
    for i, xx in enumerate((7.35, 16.65)):
        it = Item(f'SITE_Gate_Pillar_{i + 1}', xx, yg, 0.0, kind='prop')
        it.box('brick_red', -0.33, 0.33, -0.33, 0.33, 0.0, 0.3, bev=0.01, seg=1)
        it.box('paint_white', -0.29, 0.29, -0.29, 0.29, 0.3, 2.35, bev=0.01, seg=1)
        for zz in (0.9, 1.6, 2.2):
            it.box('paint_white', -0.33, 0.33, -0.33, 0.33, zz, zz + 0.07, bev=0.01, seg=1)
        it.box('paint_white', -0.37, 0.37, -0.37, 0.37, 2.35, 2.45, bev=0.01, seg=1)
        it.box('concrete', -0.3, 0.3, -0.3, 0.3, 2.45, 2.52, bev=0.01, seg=1)
        it.lathe('emit_warm', [(0.12, 2.52), (0.16, 2.78)], seg=6)
        it.lathe('black_metal', [(0.12, 2.52), (0.17, 2.52)], seg=6)
        it.lathe('black_metal', [(0.2, 2.78), (0.08, 2.9), (0.02, 2.95)], seg=6)
        it.finish()
    # gate leaves (dark green steel, spear tops, fan bars)
    for i, (x0, x1) in enumerate(((8.0, 11.95), (12.05, 16.0))):
        it = Item(f'SITE_Gate_Leaf_{i + 1}', (x0 + x1) / 2, yg, 0.0, kind='prop')
        hw = (x1 - x0) / 2
        it.box('green_rail', -hw, hw, -0.03, 0.03, 0.15, 0.2)
        it.box('green_rail', -hw, hw, -0.03, 0.03, 1.55, 1.6)
        it.box('green_rail', -hw, hw, -0.025, 0.025, 0.7, 0.74)
        for sx in (-hw, hw - 0.05):
            it.box('green_rail', sx, sx + 0.05, -0.03, 0.03, 0.12, 1.7)
        nb = int(hw * 2 / 0.14)
        for k in range(1, nb):
            xx = -hw + k * hw * 2 / nb
            it.rod('green_rail', (xx, 0, 0.2), (xx, 0, 1.55), 0.01, seg=4)
            it.rod('green_rail', (xx, 0, 1.6), (xx, 0, 1.72), 0.008, 0.001, seg=4)
        it.finish()
    # boundary wall segments
    wall_runs = [(-24.0, 7.02), (16.98, 48.0)]
    for i, (xa, xb) in enumerate(wall_runs):
        it = Item(f'SITE_BoundaryWall_{i + 1}', (xa + xb) / 2, yg, 0.0, kind='prop')
        hw = (xb - xa) / 2
        it.box('paint_white', -hw, hw, -0.115, 0.115, 0.0, 1.5, bev=0.005, seg=1)
        it.box('brick_red', -hw, hw, -0.125, 0.125, 0.0, 0.25, bev=0.005, seg=1)
        it.box('concrete', -hw, hw, -0.16, 0.16, 1.5, 1.58, bev=0.01, seg=1)
        n = int((xb - xa) / 3.0)
        for k in range(n + 1):
            xx = -hw + k * (xb - xa) / n
            it.box('paint_white', xx - 0.2, xx + 0.2, -0.17, 0.17, 0.0, 1.7, bev=0.01, seg=1)
            it.box('concrete', xx - 0.24, xx + 0.24, -0.21, 0.21, 1.7, 1.78, bev=0.01, seg=1)
        it.finish()
    # kerbs along drive
    it = Item('SITE_Drive_Kerbs', 12.0, 29.5, 0.0, kind='prop')
    for xx in (-4.1, 4.1):
        it.box('granite_grey', xx - 0.1, xx + 0.1, -12.4, 12.5, 0.0, 0.12, bev=0.01, seg=1)
    it.finish()
    # paving joints
    it = Item('SITE_Drive_PaverJoints', 12.0, 29.5, 0.04, kind='prop')
    for k in range(0, 26):
        yy = -12.4 + k * 1.0
        it.box('concrete', -3.95, 3.95, yy - 0.012, yy + 0.012, 0.0, 0.004)
    for xx in (-1.3, 1.3):
        it.box('concrete', xx - 0.012, xx + 0.012, -12.4, 12.5, 0.0, 0.004)
    it.finish()
    return 'ok'


def site_lighting():
    setl('15_Site_Lighting')
    n = 0
    for i, yy in enumerate((20.0, 27.0, 34.0)):
        lamp_post(f'SITE_LampPost_Drive_W{i + 1}', 7.35, yy); lamp_post(f'SITE_LampPost_Drive_E{i + 1}', 16.65, yy); n += 2
    for i, xx in enumerate((-8.0, -1.0, 6.0)):
        lamp_post(f'SITE_LampPost_Garden_{i + 1}', xx, -3.9, h=3.2); n += 1
    lamp_post('SITE_LampPost_Garden_4', 16.5, -3.9, h=3.2)
    lamp_post('SITE_LampPost_PoolLink', 10.4, -8.0, h=3.2)
    lamp_post('SITE_LampPost_PoolLink2', 13.6, -8.0, h=3.2)
    for i, yy in enumerate((19.0, 22.5, 26.0, 29.5, 33.0, 36.5)):
        bollard(f'SITE_Bollard_Drive_W{i + 1}', 8.35, yy); bollard(f'SITE_Bollard_Drive_E{i + 1}', 15.65, yy)
    for i, (xx, yy) in enumerate(((9.1, -3.5), (14.9, -3.5), (-3.0, -3.3), (27.0, -3.3))):
        uplight(f'SITE_Uplight_Palm_{i + 1}', xx, yy)
    return n


def landscaping():
    rr = random.Random(5)
    setl('15_Palms')
    palms = [(-1.8, -3.4, 6.5, 1), (25.8, -3.4, 6.0, 2), (3.0, -6.8, 5.2, 3), (21.5, -7.0, 5.8, 4), (-7.0, 14.5, 5.5, 5), (31.0, 17.0, 6.2, 6), (4.5, 18.5, 4.5, 7), (19.5, 18.8, 4.8, 8),
             (-12.0, -9.0, 5.6, 9), (29.0, -4.0, 5.4, 10)]
    for i, (x, y, h, s) in enumerate(palms):
        palm(f'LAND_Palm_Veitchia_{i + 1:02d}', x, y, h, seed=s)
    setl('15_Trees')
    tree_round('LAND_Tree_Shade_01', -11.0, 5.0, 7.5, 3.4, seed=1)
    tree_round('LAND_Tree_Shade_02', 32.0, 1.0, 8.0, 3.6, seed=2)
    tree_round('LAND_Tree_Shade_03', -9.0, 30.0, 8.5, 3.8, seed=3)
    tree_round('LAND_Tree_Shade_04', 28.0, 28.0, 7.0, 3.3, seed=4)
    tree_round('LAND_Tree_Shade_05', -9.0, -16.0, 6.0, 2.8, seed=5)
    tree_column('LAND_Tree_Slender_01', -5.0, 10.0, 10.0, 1.1, seed=1)
    tree_column('LAND_Tree_Slender_02', 28.5, 12.5, 11.0, 1.2, seed=2)
    tree_column('LAND_Tree_Slender_03', 20.0, 22.0, 9.0, 1.0, seed=3)
    tree_column('LAND_Tree_Slender_04', 4.0, 22.0, 9.5, 1.05, seed=4)
    tree_column('LAND_Tree_Slender_05', 36.0, -4.0, 10.5, 1.15, seed=5)
    setl('15_Shrubs_Beds')
    kinds = ['bush', 'flower', 'croton', 'agave', 'grass', 'bougain']
    beds = {'A': (-21, -3, -19.8, -12.2), 'B': (-17, -3, 18.8, 25.2), 'C': (24, 36, 5, 11)}
    cnt = 0
    for tag, (x0, x1, y0, y1) in beds.items():
        for i in range(26):
            x = rr.uniform(x0 + 1.0, x1 - 1.0); y = rr.uniform(y0 + 0.8, y1 - 0.8)
            kd = kinds[(i + ord(tag)) % len(kinds)]
            shrub(f'LAND_Bed{tag}_{kd.capitalize()}_{i + 1:02d}', x, y, rr.uniform(0.45, 0.9), kd, seed=i + 7 * ord(tag))
            cnt += 1
        for i in range(4):
            boulder(f'LAND_Bed{tag}_Boulder_{i + 1}', rr.uniform(x0 + 1.0, x1 - 1.0), rr.uniform(y0 + 0.8, y1 - 0.8), rr.uniform(0.3, 0.6), seed=i + 3)
    # foundation planting along the house (south + north)
    for i, xx in enumerate((1.5, 5.0, 7.0, 14.0, 17.0, 20.0, 23.0)):
        shrub(f'LAND_Foundation_S_{i + 1}', xx, -2.55, rr.uniform(0.4, 0.55), ('flower', 'croton', 'bush')[i % 3], seed=50 + i)
    for i, xx in enumerate((1.5, 4.5, 7.0, 17.0, 19.5, 22.5)):
        shrub(f'LAND_Foundation_N_{i + 1}', xx, 15.0, rr.uniform(0.4, 0.55), ('bougain', 'bush', 'croton')[i % 3], seed=60 + i)
    setl('15_Hedges')
    hedge('LAND_Hedge_Drive_W', 6.7, 17.3, 6.7, 41.2, h=0.8, seed=1)
    hedge('LAND_Hedge_Drive_E', 17.3, 17.3, 17.3, 41.2, h=0.8, seed=2)
    hedge('LAND_Hedge_Porch_W', 2.0, 16.4, 9.0, 16.4, h=0.6, seed=3)
    hedge('LAND_Hedge_Porch_E', 15.0, 16.4, 22.0, 16.4, h=0.6, seed=4)
    hedge('LAND_Hedge_Boundary_W', -24.0, 40.9, 6.2, 40.9, h=1.2, w=0.8, seed=5)
    hedge('LAND_Hedge_Boundary_E', 17.8, 40.9, 48.0, 40.9, h=1.2, w=0.8, seed=6)
    hedge('LAND_Hedge_South_Lawn', 14.0, -3.2, 22.5, -3.2, h=0.5, seed=7)
    setl('15_Hardscape')
    for i in range(9):
        t = i / 8
        stepping_stone(f'LAND_SteppingStone_{i + 1:02d}', 15.8 + 7.5 * t + rr.uniform(-0.15, 0.15), -3.7 - 3.2 * t * (1 - t) * 2 + rr.uniform(-0.1, 0.1), rr.uniform(-25, 25), 0.55, seed=i)
    planter_tub('GF_Porch_Planter_W', 9.1, 15.8, 0.34, 0.6)
    planter_tub('GF_Porch_Planter_E', 14.9, 15.8, 0.34, 0.6)
    F.pot_plant('GF_Porch_Planter_W_Plant', 9.1, 15.8, 0.34, 'areca', 'terracotta', 1.5, 0.01, 0.25, seed=81)
    F.pot_plant('GF_Porch_Planter_E_Plant', 14.9, 15.8, 0.34, 'areca', 'terracotta', 1.5, 0.01, 0.25, seed=82)
    return cnt


def run_site():
    r1._colls()
    o = {}
    o['gate'] = gate_and_wall()
    o['lights'] = site_lighting()
    o['land'] = landscaping()
    return o
