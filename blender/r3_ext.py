"""Round 3 - exterior details, balcony railing (reference copy), veranda/balcony dressing, roof equipment  [module r3e]."""
import bpy, bmesh, math, sys, random
from mathutils import Vector, Matrix
c = sys.modules['r3c']; F = sys.modules['r3f']; K = sys.modules['r3k']; r1 = sys.modules['r1']; A = sys.modules['r3a']
Item = c.Item
WB, WR = A.WB, A.WR
rnd = random.Random(21)


def RES():
    return r1.BLD['RES']


def setx(coll, room='EXT', fl=''):
    c.ctx(coll, RES(), room, fl, 'r3')


def archive(objs):
    root = bpy.data.collections.get('PROJECT_5BHK_RA-1-RW')
    arc = bpy.data.collections.get('99_Archive_Superseded')
    if not arc:
        arc = bpy.data.collections.new('99_Archive_Superseded')
        (root or bpy.context.scene.collection).children.link(arc)
    for o in objs:
        for col in list(o.users_collection):
            col.objects.unlink(o)
        arc.objects.link(o)
        o.hide_render = True; o.hide_viewport = True
        o['archived_by'] = 'round3'
    lc = bpy.context.view_layer.layer_collection
    def find(l, n):
        if l.name == n: return l
        for ch in l.children:
            r = find(ch, n)
            if r: return r
    l = find(lc, arc.name)
    if l: l.exclude = True
    return arc


# --------------------------------------------------------------------------- small props
def wall_lantern(name, x, y, z, face='N', lit=True):
    it = Item(name, x, y, z, face, kind='wall')
    it.box('black_metal', -0.045, 0.045, 0, 0.014, 0.0, 0.26, bev=0.004, seg=1)
    it.loft('black_metal', [(0, 0.014, 0.18), (0, 0.1, 0.2), (0, 0.17, 0.17), (0, 0.17, 0.12)], 0.007, seg=6, cap=False)
    cy, zb = 0.17, 0.0
    it.lathe('black_metal', [(0.06, zb), (0.075, zb + 0.03), (0.0, zb + 0.03)], cx=0, cy=cy, seg=6)
    it.lathe('emit_warm' if lit else 'glass', [(0.07, zb + 0.03), (0.095, zb + 0.24)], cx=0, cy=cy, seg=6)
    for k in range(6):
        a = math.pi / 6 + k * math.pi / 3
        it.rod('black_metal', (0.07 * math.cos(a), cy + 0.07 * math.sin(a), zb + 0.03), (0.098 * math.cos(a), cy + 0.098 * math.sin(a), zb + 0.24), 0.0055, seg=4)
    it.lathe('black_metal', [(0.115, zb + 0.24), (0.04, zb + 0.34), (0.012, zb + 0.36)], cx=0, cy=cy, seg=6)
    it.sph('black_metal', 0, cy, zb + 0.375, 0.016, seg=8, rings=5)
    return it.finish()


def hanging_basket(name, x, y, ztop, drop=0.85, seed=1, r=0.17, mat='fern'):
    rr = random.Random(seed)
    it = Item(name, x, y, ztop, kind='ceil')
    zb = -drop
    it.lathe('black_metal', [(0.05, 0.0), (0.0, 0.0)], seg=8)
    it.sph('black_metal', 0, 0, 0.0, 0.02, seg=8, rings=5)
    for k in range(3):
        a = 2 * math.pi * k / 3
        it.rod('black_metal', (0, 0, -0.01), (r * 0.9 * math.cos(a), r * 0.9 * math.sin(a), zb + 0.16), 0.0025, seg=4)
    it.lathe('cane', [(0.0, zb), (r * 0.5, zb + 0.015), (r * 0.9, zb + 0.07), (r, zb + 0.16), (r * 0.96, zb + 0.17), (r * 0.9, zb + 0.15)], seg=18)
    it.lathe('soil', [(r * 0.92, zb + 0.15), (0, zb + 0.15)], seg=14)
    for k in range(26):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(0.0, r * 0.7)
        it.leaf('leaf_light' if k % 2 else 'leaf', (d * math.cos(a), d * math.sin(a), zb + 0.14), (math.cos(a), math.sin(a), rr.uniform(0.2, 1.1)), rr.uniform(0.18, 0.38), 0.05, droop=0.9, rise=0.3, rows=4)
    return it.finish()


def teak_bench(name, x, y, z, face='S', w=1.7, d=0.5, h=0.44):
    it = Item(name, x, y, z, face)
    hw = w / 2
    for k in range(5):
        y0 = 0.08 + k * 0.085
        it.box('wood_teak', -hw, hw, y0, y0 + 0.07, h - 0.035, h, bev=0.004, seg=1)
    for sx in (-hw + 0.06, hw - 0.06):
        it.box('wood_teak', sx - 0.03, sx + 0.03, 0.06, d - 0.04, 0.0, h - 0.035, bev=0.004, seg=1)
        it.box('wood_teak', sx - 0.03, sx + 0.03, 0.0, 0.07, 0.0, 0.85, bev=0.004, seg=1)
        it.box('wood_teak', sx - 0.03, sx + 0.03, 0.0, 0.07, 0.62, 0.66, bev=0.004, seg=1)
    for zz in (0.55, 0.66, 0.77):
        it.box('wood_teak', -hw, hw, 0.02, 0.05, zz, zz + 0.07, bev=0.004, seg=1)
    it.box('fab_mustard', -hw + 0.12, hw - 0.12, 0.1, d - 0.02, h, h + 0.07, bev=0.025, seg=3)
    it.box('fab_cream', -0.45, -0.1, 0.04, 0.17, h + 0.05, h + 0.4, bev=0.035, seg=3, rot=(-10, 0, 0))
    it.box('fab_ochre', 0.1, 0.45, 0.04, 0.17, h + 0.05, h + 0.4, bev=0.035, seg=3, rot=(-10, 0, 0))
    return it.finish()


def monobloc(name, x, y, z, face='N'):
    it = Item(name, x, y, z, face)
    it.box('plastic_white', -0.22, 0.22, 0.2, 0.62, 0.40, 0.44, bev=0.012, seg=2)
    it.box('plastic_white', -0.21, 0.21, 0.55, 0.6, 0.42, 0.9, bev=0.012, seg=2, rot=(-14, 0, 0))
    for sx in (-0.24, 0.24):
        it.box('plastic_white', sx - 0.02, sx + 0.02, 0.22, 0.6, 0.6, 0.64, bev=0.01, seg=2)
        it.box('plastic_white', sx - 0.02, sx + 0.02, 0.56, 0.6, 0.44, 0.64, bev=0.01, seg=2)
    for sx in (-0.19, 0.19):
        for sy in (0.25, 0.57):
            it.rod('plastic_white', (sx, sy, 0), (sx, sy, 0.41), 0.017, 0.022, seg=8)
    return it.finish()


def water_tank(name, x, y, z, r=0.56, h=1.15):
    it = Item(name, x, y, z, kind='prop')
    prof = [(0, 0), (r * 0.9, 0), (r, 0.03), (r, 0.12), (r * 1.025, 0.15), (r * 1.025, 0.2), (r, 0.23)]
    for k in range(3):
        zz = 0.12 + (k + 1) * 0.26
        prof += [(r, zz - 0.03), (r * 1.03, zz), (r * 1.03, zz + 0.04), (r, zz + 0.07)]
    prof += [(r, h - 0.08), (r * 0.8, h - 0.02), (r * 0.5, h + 0.04), (r * 0.3, h + 0.07), (r * 0.28, h + 0.07)]
    it.lathe('tank_black', prof, seg=28)
    it.lathe('tank_black', [(0.2, h + 0.06), (0.21, h + 0.1), (0.18, h + 0.13), (0.0, h + 0.13)], cx=0.0, cy=0.0, seg=16)
    it.rod('pvc_grey', (r + 0.0, 0.0, 0.3), (r + 0.18, 0.0, 0.3), 0.025, seg=8)
    it.rod('pvc_grey', (r + 0.18, 0.0, 0.3), (r + 0.18, 0.0, -0.1), 0.025, seg=8)
    it.rod('pvc_grey', (-r + 0.1, 0.0, h * 0.82), (-r - 0.25, 0.0, h * 0.82), 0.022, seg=8)
    return it.finish()


def tank_stand(name, x0, x1, y0, y1, z):
    it = Item(name, (x0 + x1) / 2, (y0 + y1) / 2, z, kind='prop')
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    for sx in (-hw + 0.17, 0, hw - 0.17):
        for sy in (-hd + 0.17, hd - 0.17):
            it.box('brick_red', sx - 0.17, sx + 0.17, sy - 0.17, sy + 0.17, 0, 0.5, bev=0.004, seg=1)
    it.box('concrete', -hw, hw, -hd, hd, 0.5, 0.64, bev=0.006, seg=1)
    return it.finish()


def solar_heater(name, x, y, z, ntubes=16):
    it = Item(name, x, y, z, kind='prop')
    ang = math.radians(32)
    L = 1.9
    dy, dz = -L * math.cos(ang), L * math.sin(ang)
    hw = 0.1 * ntubes / 2
    zt = 1.12
    for k in range(ntubes):
        xx = -hw + 0.05 + k * 0.1
        it.rod('graphite', (xx, 0.42, zt), (xx, 0.42 + dy, zt - dz), 0.024, seg=8)
        it.rod('mirror', (xx, 0.42, zt), (xx, 0.42 + dy * 0.97, zt - dz * 0.97), 0.012, seg=6)
    it.rod('plastic_white', (-hw - 0.05, 0.42, zt + 0.1), (hw + 0.05, 0.42, zt + 0.1), 0.2, seg=20)
    for sx in (-hw + 0.1, hw - 0.1):
        it.rod('steel', (sx, 0.42, zt), (sx, 0.42 + dy, zt - dz), 0.016, seg=6)
        it.rod('steel', (sx, 0.42, zt), (sx, 0.5, 0.0), 0.015, seg=6)
        it.rod('steel', (sx, 0.42 + dy, zt - dz), (sx, 0.42 + dy, 0.0), 0.015, seg=6)
    return it.finish()


def dish(name, x, y, z, h=1.3):
    it = Item(name, x, y, z, kind='prop')
    it.rod('steel', (0, 0, 0), (0, 0, h), 0.03, seg=10)
    it.lathe('concrete', [(0.2, 0.0), (0.2, 0.08), (0.0, 0.08)], seg=14)
    b = it._b('plastic_white'); n0 = len(b.verts)
    it.lathe('plastic_white', [(0.0, 0.0), (0.12, 0.012), (0.24, 0.045), (0.36, 0.1), (0.36, 0.11), (0.24, 0.056), (0.12, 0.022), (0.0, 0.01)], cx=0.0, cy=0.0, z=0.0, seg=26)
    vs = list(b.verts)[n0:]
    bmesh.ops.rotate(b, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(58), 3, 'X'), verts=vs)
    bmesh.ops.translate(b, vec=(0, 0, h + 0.1), verts=vs)
    it.rod('graphite', (0, 0.0, h + 0.1), (0, -0.42, h + 0.38), 0.008, seg=5)
    it.sph('graphite', 0, -0.42, h + 0.38, 0.03, seg=8, rings=5)
    return it.finish()


def vent_stack(name, x, y, z, h=1.0):
    it = Item(name, x, y, z, kind='prop')
    it.rod('pvc_grey', (0, 0, 0), (0, 0, h), 0.04, seg=10)
    it.lathe('pvc_grey', [(0.042, h - 0.02), (0.06, h), (0.04, h + 0.08), (0.0, h + 0.1)], seg=10)
    it.lathe('concrete', [(0.14, 0.0), (0.12, 0.08), (0.05, 0.12)], seg=10)
    return it.finish()


def lightning_rod(name, x, y, z, h=1.6):
    it = Item(name, x, y, z, kind='prop')
    it.rod('steel', (0, 0, 0), (0, 0, h), 0.012, 0.005, seg=6)
    for k in range(4):
        a = k * math.pi / 2
        it.rod('steel', (0, 0, h - 0.25), (0.12 * math.cos(a), 0.12 * math.sin(a), h - 0.12), 0.004, seg=4)
    it.lathe('concrete', [(0.16, 0.0), (0.12, 0.1), (0.03, 0.14)], seg=10)
    return it.finish()


def downpipe(name, x, y, z0, z1, side='N', out=0.0):
    """vertical PVC pipe with brackets, shoe and rainwater head. side: N/E/W = which wall."""
    it = Item(name, x, y, z0, kind='prop')
    H = z1 - z0
    it.rod('pvc_grey', (0, 0, 0.0), (0, 0, H - 0.2), 0.045, seg=14)
    it.lathe('pvc_grey', [(0.045, 0.0), (0.045, 0.04), (0.055, 0.045), (0.055, 0.1), (0.045, 0.105)], seg=14, z=0.0)
    # shoe
    it.loft('pvc_grey', [(0, 0, 0.0), (0, 0, -0.04), (0, 0.04, -0.07), (0, 0.18, -0.07), (0, 0.3, -0.07)], 0.045, seg=12, cap=True)
    # rainwater head
    it.box('pvc_grey', -0.1, 0.1, -0.12, 0.12, H - 0.42, H - 0.12, bev=0.02, seg=2)
    it.lathe('pvc_grey', [(0.06, H - 0.12), (0.045, H - 0.2)], seg=12)
    n = int(H // 1.5) + 1
    for k in range(1, n + 1):
        zz = k * H / (n + 1)
        it.lathe('steel', [(0.047, zz - 0.012), (0.056, zz - 0.01), (0.056, zz + 0.01), (0.047, zz + 0.012)], seg=14)
    return it.finish()


# --------------------------------------------------------------------------- balcony railing (copy of reference geometry)
def rail_bay(it, pos, a0, a1, zb, zt, mat='green_rail'):
    """pos(a)->(x,y); bay from a0..a1 (clear span between posts)."""
    L = a1 - a0; ac = (a0 + a1) / 2
    def P(a, z):
        x, y = pos(a); return (x, y, z)
    # rails
    def bar(aa, za, ab, zbb, r=0.007):
        WR(it, mat, P(aa, za), P(ab, zbb), r, seg=4, cap=True)
    def flat(aa, ab, z0, z1, wd):
        x0, y0, _ = P(aa, 0); x1, y1, _ = P(ab, 0)
        WB(it, mat, min(x0, x1) - wd / 2 * (abs(y1 - y0) > abs(x1 - x0)), max(x0, x1) + wd / 2 * (abs(y1 - y0) > abs(x1 - x0)),
           min(y0, y1) - wd / 2 * (abs(x1 - x0) >= abs(y1 - y0)), max(y0, y1) + wd / 2 * (abs(x1 - x0) >= abs(y1 - y0)), z0, z1)
    flat(a0, a1, zt - 0.03, zt, 0.07)           # flat top rail (ref)
    flat(a0, a1, zb, zb + 0.035, 0.05)          # bottom rail
    flat(a0, a1, zb + 0.28, zb + 0.30, 0.03)    # lower intermediate rail
    # central spine + herringbone feathers
    bar(ac, zb, ac, zt - 0.03, 0.009)
    H = zt - 0.03 - (zb + 0.035)
    n = 7
    for i in range(1, n + 1):
        zi = zb + 0.035 + i * H / (n + 1)
        reach = min((zi - zb - 0.035) * 1.9, L / 2 - 0.02)
        zend = zi - reach / 1.9
        for sg in (-1, 1):
            bar(ac, zi, ac + sg * reach, zend, 0.0055)
    # long fan diagonals from the lower corners toward the top rail centre
    for sg in (-1, 1):
        a_start = ac + sg * (L / 2 - 0.02)
        bar(a_start, zb + 0.035, ac + sg * 0.55, zt - 0.03, 0.0055)
        bar(a_start, zb + 0.035, ac + sg * 1.1, zt - 0.03, 0.0055)
        bar(ac + sg * 0.6, zb + 0.035, ac + sg * (L / 2 - 0.02), zt - 0.03, 0.0055)


def balcony_railing():
    old = [bpy.data.objects.get(n) for n in ('Res_RAILING_FF_Balcony_Frame', 'Res_RAILING_FF_Balcony_Diagonals')]
    old = [o for o in old if o]
    setx(r1.C['RAIL'], 'BALCONY_RAIL', 'FF')
    zk = 3.8; zk1 = 3.95; zb = zk1; zt = 4.9
    yf = -1.89
    xs = [-0.02, 4.0, 8.0, 12.0, 16.0, 20.0, 24.02]
    out = 0
    # kerb (granite) - front + sides
    k = Item('Rail_FF_Balcony_GraniteKerb', 12.0, -1.89, zk, kind='wall')
    WB(k, 'granite_grey', -0.11, 24.11, -1.99, -1.79, zk, zk1, bev=0.012, seg=2)
    WB(k, 'granite_grey', -0.11, 0.09, -1.79, -0.12, zk, zk1, bev=0.012, seg=2)
    WB(k, 'granite_grey', 23.91, 24.11, -1.79, -0.12, zk, zk1, bev=0.012, seg=2)
    k.finish()
    it = Item('Rail_FF_Balcony_GreenSteel', 12.0, yf, zk1, kind='wall')
    # front bays
    for a, b in zip(xs, xs[1:]):
        rail_bay(it, lambda aa: (aa, yf), a + 0.03, b - 0.03, zb, zt)
    # posts
    for xx in xs:
        WB(it, 'green_rail', xx - 0.0275, xx + 0.0275, yf - 0.0275, yf + 0.0275, zk1, zt + 0.02, bev=0.004, seg=1)
        WB(it, 'green_rail', xx - 0.04, xx + 0.04, yf - 0.04, yf + 0.04, zt + 0.02, zt + 0.045, bev=0.006, seg=2)
        WB(it, 'green_rail', xx - 0.045, xx + 0.045, yf - 0.045, yf + 0.045, zk1, zk1 + 0.04, bev=0.004, seg=1)
    # side returns
    for xx in (-0.02, 24.02):
        rail_bay(it, lambda aa, xx=xx: (xx, aa), yf + 0.03, -0.2 - 0.03, zb, zt)
        WB(it, 'green_rail', xx - 0.0275, xx + 0.0275, -0.2 - 0.0275, -0.2 + 0.0275, zk1, zt + 0.02, bev=0.004, seg=1)
        WB(it, 'green_rail', xx - 0.04, xx + 0.04, -0.2 - 0.04, -0.2 + 0.04, zt + 0.02, zt + 0.045, bev=0.006, seg=2)
    it.finish()
    arc = archive(old)
    return len(old)


def tile_floor(name, x0, x1, y0, y1, z, nx, ny, mat='tile_cream', t=0.012, gap=0.006, coll=None):
    it = Item(name, (x0 + x1) / 2, (y0 + y1) / 2, z, kind='wall')
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            WB(it, mat, x0 + i * dx + gap / 2, x0 + (i + 1) * dx - gap / 2, y0 + j * dy + gap / 2, y0 + (j + 1) * dy - gap / 2, z, z + t)
    return it.finish()


def run_balcony_floor_and_rail():
    out = {}
    setx(r1.C['FLOOR'], 'TILES', 'GF')
    tile_floor('Floor_GF_Veranda_Tiles', -0.11, 24.11, -2.0, -0.12, 0.6, 40, 3)
    setx(r1.C['FLOOR'], 'TILES', 'FF')
    tile_floor('Floor_FF_Balcony_Tiles', -0.11, 24.11, -2.0, -0.12, 3.8, 40, 3)
    out['archived'] = balcony_railing()
    return out


# --------------------------------------------------------------------------- dressing
def dress_veranda():
    P = F.pot_plant
    coll = c.sub_coll(r1.C['FURN'], '12_Outdoor_Furniture')
    pcoll = c.sub_coll(r1.C['DECOR'], '13_Outdoor_Plants_Decor')
    lcoll = c.sub_coll(r1.C['LIGHT'], '17_Exterior_Lights')
    z = 0.6 + 0.012
    setx(coll, 'VERANDA', 'GF')
    F.armchair_wicker('GF_Veranda_ChairW', 6.25, -0.95, z, 'E', cush='fab_brown', pillow='fab_cream')
    F.armchair_wicker('GF_Veranda_ChairE', 8.85, -0.95, z, 'W', cush='fab_brown', pillow='fab_black_floral')
    F.coffee_table_round('GF_Veranda_RoundTable', 7.55, -0.95, z, r=0.38, h=0.5)
    teak_bench('GF_Veranda_TeakBench', 15.4, -0.12, z, 'S', 1.8)
    F.side_table('GF_Veranda_SideTable', 17.15, -0.5, z, r=0.2, h=0.5)
    F.doormat('GF_Veranda_Mat_Hall', 4.0, -0.5, z, 'N', 1.0, 0.6)
    F.doormat('GF_Veranda_Mat_Dining', 10.75, -0.5, z, 'N', 1.0, 0.6, mat='rug_blue')
    F.doormat('GF_Veranda_Mat_Bed', 21.0, -0.5, z, 'N', 1.0, 0.6)
    setx(pcoll, 'VERANDA', 'GF')
    P('GF_Veranda_Areca_W', 0.85, -0.55, z, 'areca', 'terracotta', 1.35, 0.24, 0.46, seed=11)
    P('GF_Veranda_Areca_E', 23.35, -0.55, z, 'areca', 'terracotta', 1.35, 0.24, 0.46, seed=12)
    P('GF_Veranda_Rubber_Mid', 13.1, -0.5, z, 'rubber', 'ceramic', 1.2, 0.2, 0.4, seed=13)
    P('GF_Veranda_Snake_A', 18.4, -1.45, z, 'snake', 'black', 0.7, 0.16, 0.3, seed=14)
    P('GF_Veranda_Aloe_A', 6.6, -1.45, z, 'aloe', 'terracotta', 0.5, 0.16, 0.26, seed=15)
    P('GF_Veranda_Money_A', 12.55, -1.45, z, 'money', 'clay_dark', 0.5, 0.15, 0.26, seed=16)
    for i, xx in enumerate((2.0, 6.0, 10.0, 14.0, 18.0, 22.0)):
        hanging_basket(f'GF_Veranda_HangBasket_{i + 1}', xx, -1.45, 3.6, 0.9, seed=30 + i)
    setx(lcoll, 'VERANDA', 'GF')
    for i, xx in enumerate((1.0, 7.0, 13.4, 17.6, 23.4)):
        wall_lantern(f'GF_Veranda_WallLantern_{i + 1}', xx, -0.12, 2.15, 'S')
    for i, xx in enumerate((1.5, 3.9, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.5)):
        F.downlight(f'GF_Veranda_Downlight_{i + 1}', xx, -1.0, 3.6)
    # ---------------- FF balcony
    zf = 3.8 + 0.012
    setx(coll, 'BALCONY', 'FF')
    for i, xx in enumerate((6.8, 12.85, 18.35)):
        F.ac_outdoor(f'FF_Balcony_ACOutdoor_{i + 1}', xx, -0.12, zf, 'S')
        # refrigerant lines up into wall
        it = Item(f'FF_Balcony_ACPipes_{i + 1}', xx, -0.12, zf, 'S', kind='prop')
        for sx in (-0.03, 0.03):
            it.loft('black_plastic', [(sx, 0.02, 0.5), (sx, 0.1, 0.62), (sx, 0.1, 1.5), (sx, 0.02, 1.9), (sx, -0.1, 1.9)], 0.014, seg=6, cap=True)
        it.finish()
    K.washing_machine('FF_Balcony_WashingMachine', 23.55, -0.12, zf, 'S', cover=True)
    monobloc('FF_Balcony_PlasticChair', 1.3, -1.05, zf, 'E')
    setx(pcoll, 'BALCONY', 'FF')
    row = [(5.35, 'aloe', 'ceramic', 0.55), (5.8, 'snake', 'terracotta', 0.75), (6.35, 'aloe', 'clay_dark', 0.5), (7.05, 'aloe', 'ceramic', 0.65), (7.7, 'snake', 'black', 0.6),
           (11.7, 'snake', 'terracotta', 0.8), (12.3, 'aloe', 'ceramic', 0.55), (13.0, 'money', 'clay_dark', 0.5), (13.65, 'aloe', 'terracotta', 0.6),
           (0.6, 'areca', 'terracotta', 1.0), (17.4, 'aloe', 'ceramic', 0.55), (18.0, 'snake', 'clay_dark', 0.7), (23.5, 'snake', 'black', 0.65)]
    for i, (xx, kd, pt, hh) in enumerate(row):
        P(f'FF_Balcony_Plant_{i + 1:02d}_{kd}', xx, -1.58 + rnd.uniform(-0.03, 0.03), zf + 0.0, kd, pt, hh, 0.15 + rnd.uniform(0, 0.04), 0.27, seed=40 + i)
    P('FF_Balcony_BlueTub_1', 19.0, -1.55, zf, 'aloe', 'blue', 0.55, 0.23, 0.22, seed=70)
    P('FF_Balcony_BlueTub_2', 19.55, -1.62, zf, 'fern', 'blue', 0.5, 0.2, 0.2, seed=71)
    setx(lcoll, 'BALCONY', 'FF')
    for i, xx in enumerate((1.0, 5.5, 7.9, 12.8, 17.7, 23.5)):
        wall_lantern(f'FF_Balcony_WallLantern_{i + 1}', xx, -0.12, 3.8 + 2.15, 'S')
    return 'ok'


def porch_and_facade():
    lcoll = c.sub_coll(r1.C['LIGHT'], '17_Exterior_Lights')
    dcoll = c.sub_coll(r1.C['DECOR'], '13_Outdoor_Plants_Decor')
    ecoll = c.sub_coll(r1.C['EXT'], '02_Exterior_Details')
    setx(lcoll, 'PORCH', 'GF')
    wall_lantern('GF_Porch_WallLantern_W', 10.5, 14.115, 2.1, 'N')
    wall_lantern('GF_Porch_WallLantern_E', 13.5, 14.115, 2.1, 'N')
    wall_lantern('GF_Porch_ColumnLantern_W', 10.2, 16.3, 2.0, 'S')
    wall_lantern('GF_Porch_ColumnLantern_E', 13.8, 16.3, 2.0, 'S')
    for i, (xx, yy) in enumerate(((10.6, 15.0), (13.4, 15.0), (10.6, 16.0), (13.4, 16.0), (12.0, 15.5))):
        F.downlight(f'GF_Porch_Downlight_{i + 1}', xx, yy, 3.4)
    setx(ecoll, 'PORCH', 'GF')
    # nameplate (black granite + brass border) beside entrance
    it = Item('GF_Porch_NamePlate', 14.9, 14.115, 1.55, 'N', kind='wall')
    it.box('brass', -0.27, 0.27, 0, 0.018, 0, 0.34, bev=0.004, seg=1)
    it.box('black_glass', -0.25, 0.25, 0.018, 0.026, 0.02, 0.32, bev=0.002, seg=1)
    it.box('brass', -0.17, 0.17, 0.026, 0.03, 0.15, 0.19)
    it.box('brass', -0.12, 0.12, 0.026, 0.03, 0.22, 0.25)
    it.finish()
    # doorbell + outdoor switch
    it = Item('GF_Porch_DoorBell', 13.3, 14.115, 1.3, 'N', kind='wall')
    it.box('plastic_white', -0.03, 0.03, 0, 0.015, 0, 0.09, bev=0.004, seg=1)
    it.rod('brass', (0, 0.015, 0.045), (0, 0.025, 0.045), 0.011, seg=10)
    it.finish()
    # downpipes
    for i, xx in enumerate((0.75, 23.25)):
        downpipe(f'EXT_Downpipe_N{i + 1}', xx, 14.3, 0.35, 7.0)
        s = Item(f'EXT_Scupper_N{i + 1}', xx, 14.3, 7.0, kind='prop')
        s.box('concrete', -0.12, 0.12, -0.22, 0.25, 0.0, 0.05, bev=0.004, seg=1)
        s.box('concrete', -0.12, -0.09, -0.22, 0.25, 0.05, 0.12)
        s.box('concrete', 0.09, 0.12, -0.22, 0.25, 0.05, 0.12)
        s.finish()
    for i, yy in enumerate((13.0, 13.0)):
        pass
    return 'ok'


def roof_equipment():
    coll = c.sub_coll(r1.C['ROOF'], '06_Roof_Equipment')
    setx(coll, 'ROOF', 'RF')
    z = 7.0
    tank_stand('RF_TankStand', 2.7, 6.1, 10.3, 11.7, z)
    water_tank('RF_WaterTank_1', 3.6, 11.0, z + 0.64)
    water_tank('RF_WaterTank_2', 5.2, 11.0, z + 0.64)
    solar_heater('RF_SolarHeater', 9.6, 11.4, z)
    dish('RF_SatelliteDish', 15.0, 12.2, z)
    for i, (xx, yy) in enumerate(((7.6, 12.8), (13.0, 12.7), (16.8, 12.9))):
        vent_stack(f'RF_VentStack_{i + 1}', xx, yy, z, 1.0)
    lightning_rod('RF_LightningRod', 21.7, 11.3, 9.5)
    # roof drain outlets
    for i, xx in enumerate((0.75, 23.25)):
        pass
    return 'ok'


def run_ext():
    r1._colls()
    o = {}
    o['balcony'] = run_balcony_floor_and_rail()
    o['dress'] = dress_veranda()
    o['facade'] = porch_and_facade()
    o['roof'] = roof_equipment()
    return o
