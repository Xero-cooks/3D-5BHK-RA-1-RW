"""Round 3 - room-by-room furnishing of the main residence (module r3r)."""
import bpy, sys, math
c = sys.modules['r3c']; F = sys.modules['r3f']; K = sys.modules['r3k']; r1 = sys.modules['r1']
Z = {'GF': 0.6, 'FF': 3.8}
CE = {'GF': 3.57, 'FF': 6.77}
ROOMRECT = {}


def inner(b):
    xa = b[0] + (0.115 if abs(b[0]) < 1e-6 else 0.0575)
    xb = b[1] - (0.115 if abs(b[1] - 24) < 1e-6 else 0.0575)
    ya = b[2] + (0.115 if abs(b[2]) < 1e-6 else 0.0575)
    yb = b[3] - (0.115 if abs(b[3] - 14) < 1e-6 else 0.0575)
    return (xa, xb, ya, yb)


def at(R, wall, u, off=0.0):
    xa, xb, ya, yb = R
    if wall == 'S': return (u, ya + off, 'N')
    if wall == 'N': return (u, yb - off, 'S')
    if wall == 'W': return (xa + off, u, 'E')
    return (xb - off, u, 'W')


class Ctx:
    def __init__(s):
        s.par = r1.BLD['RES']; s.C = r1.C
        s.fl = 'GF'; s.room = ''; s.R = None

    def set(s, cat, fl, room, rect=None):
        C = s.C
        s.fl = fl; s.room = f'{fl}_{room}'
        if rect:
            s.R = inner(rect); ROOMRECT[s.room] = s.R
        coll = {'furn': lambda: c.sub_coll(C['FURN'], f'12_{fl}_Furniture'), 'decor': lambda: c.sub_coll(C['DECOR'], f'13_{fl}_Decor'),
                'light': lambda: c.sub_coll(C['LIGHT'], f'17_{fl}_Fixtures'), 'kit': lambda: C['KIT'], 'bath': lambda: C['BATH'],
                'bed': lambda: c.sub_coll(C['BED'], f'11d_{fl}_Bedroom_Furniture'), 'liv': lambda: C['LIV'],
                'plant': lambda: c.sub_coll(C['DECOR'], f'13_{fl}_Plants')}[cat]()
        c.ctx(coll, s.par, s.room, fl, 'r3')


X = Ctx()


def P(fn, name, wall, u, off=0.0, z=0.0, **kw):
    x, y, face = at(X.R, wall, u, off)
    return fn(f'{X.room}_{name}', x, y, z, face, **kw)


def ROOM(name, fl, cat='furn'):
    pass


def curt(name, wall, u, W, fl, scheme='A', head=2.4):
    if scheme == 'A':     # ref hall: grey / ochre / mustard triplets
        L = [(-W / 2 - 0.0, -W / 2 + 0.2, 'fab_grey'), (-W / 2 + 0.2, -W / 2 + 0.42, 'fab_ochre'), (-W / 2 + 0.42, -W / 2 + 0.66, 'fab_grey')]
        Rr = [(W / 2 - 0.66, W / 2 - 0.42, 'fab_mustard'), (W / 2 - 0.42, W / 2 - 0.2, 'fab_ochre'), (W / 2 - 0.2, W / 2, 'fab_grey')]
        pan = L + Rr
    elif scheme == 'B':   # bedroom: cream + brown print (ref bedroom)
        pan = [(-W / 2, -W / 2 + 0.38, 'fab_cream'), (-W / 2 + 0.38, -W / 2 + 0.7, 'fab_brown'), (W / 2 - 0.7, W / 2 - 0.38, 'fab_brown'), (W / 2 - 0.38, W / 2, 'fab_cream')]
    else:                 # simple pair
        pan = [(-W / 2, -W / 2 + 0.5, 'fab_taupe'), (W / 2 - 0.5, W / 2, 'fab_taupe')]
    x, y, face = at(X.R, wall, u, 0.0)
    return F.curtains(f'{X.room}_{name}', x, y, Z[fl], face, W, head, pan, floor_z=0.0)


def bath_room(tag, fl, rect, shower='E', vanity=False, ywall=None):
    X.set('bath', fl, tag, rect)
    xa, xb, ya, yb = X.R; z = Z[fl]
    n = f'{X.room}'
    sw = 1.0
    if shower == 'E':
        s0, s1 = xb - sw, xb; wc_x = xb - 1.3; b_x = xb - (2.1 if vanity else 1.9)
    else:
        s0, s1 = xa, xa + sw; wc_x = xa + 1.3; b_x = xa + (2.1 if vanity else 1.9)
    K.wc(f'{n}_WC', wc_x, yb, z, 'S')
    if vanity:
        K.vanity(f'{n}_Vanity', b_x, yb, z, 'S')
        K.bath_mirror(f'{n}_Mirror', b_x, yb, z, 'S', w=0.8, h=0.9, zb=1.25, shelf=False)
        K.soap_dispenser(f'{n}_Soap', b_x - 0.25, yb - 0.25, z + 0.85)
    else:
        K.basin_wall(f'{n}_Basin', b_x, yb, z, 'S')
        K.bath_mirror(f'{n}_Mirror', b_x, yb, z, 'S')
        K.soap_dispenser(f'{n}_Soap', b_x + 0.18, yb - 0.1, z + 0.82)
    K.exhaust_fan(f'{n}_ExhaustFan', wc_x, yb, z + 2.15, 'S')
    if shower == 'E':
        K.shower(f'{n}_ShowerSet', xb, (yb + (yb - 0.95)) / 2, z, 'W')
        K.glass_panel(f'{n}_ShowerGlass_W', s0, yb - 0.95, s0, yb, z + 0.04, z + 2.0)
        K.glass_panel(f'{n}_ShowerGlass_S', s0, yb - 0.95, s1, yb - 0.95, z + 0.04, z + 2.0)
        K.floor_drain(f'{n}_Drain', (s0 + s1) / 2, yb - 0.47, z)
        K.bucket_mug(f'{n}_Bucket', s1 - 0.45, yb - 0.45, z)
        K.towel_ring(f'{n}_TowelRing', xa, ya + 0.9, z + 1.2, 'E')
        K.geyser(f'{n}_Geyser', xa, yb - 0.4, z + 1.85, 'E')
    else:
        K.shower(f'{n}_ShowerSet', xa, (yb + (yb - 0.95)) / 2, z, 'E')
        K.glass_panel(f'{n}_ShowerGlass_E', s1, yb - 0.95, s1, yb, z + 0.04, z + 2.0)
        K.glass_panel(f'{n}_ShowerGlass_S', s0, yb - 0.95, s1, yb - 0.95, z + 0.04, z + 2.0)
        K.floor_drain(f'{n}_Drain', (s0 + s1) / 2, yb - 0.47, z)
        K.bucket_mug(f'{n}_Bucket', s0 + 0.45, yb - 0.45, z)
        K.towel_ring(f'{n}_TowelRing', xb, ya + 0.9, z + 1.2, 'W')
        K.geyser(f'{n}_Geyser', xb, yb - 0.4, z + 1.85, 'W')
    K.floor_drain(f'{n}_Drain2', (xa + xb) / 2, (ya + yb) / 2 - 0.2, z)
    c.ctx(X.C['LIGHT'], X.par, X.room, fl, 'r3')
    F.downlight(f'{n}_Downlight_1', (xa + xb) / 2 - 0.5, (ya + yb) / 2, CE[fl])
    F.downlight(f'{n}_Downlight_2', (xa + xb) / 2 + 0.5, (ya + yb) / 2, CE[fl])


def bedroom_set(tag, fl, rect, head_wall, head_u, head_off=0.0, w=1.6, l=2.05, cover='fab_floral', pill='fab_white', throw='fab_mustard', ward=None, bs_gap=0.4, rugd=None):
    X.set('bed', fl, tag, rect)
    z = Z[fl]
    P(F.bed, 'Bed', head_wall, head_u, head_off, z, w=w, l=l, cover=cover, pill=pill, throw=throw)
    for sgn, nm in ((-1, 'BedsideA'), (1, 'BedsideB')):
        P(F.bedside, nm, head_wall, head_u + sgn * (w / 2 + bs_gap / 2 + 0.07 + 0.02), head_off, z)


def lights_bundle(tag, fl, pts, fan=None, tube=None):
    X.set('light', fl, tag)
    for i, (x, y) in enumerate(pts):
        F.downlight(f'{X.room}_Downlight_{i + 1}', x, y, CE[fl])
    if fan:
        F.ceiling_fan(f'{X.room}_CeilingFan', fan[0], fan[1], CE[fl])


# ===================================================================== GROUND FLOOR
def ground_floor(rooms):
    z = Z['GF']; fl = 'GF'
    # -------------------------------------------------- LIVING HALL
    X.set('liv', fl, 'Hall', rooms['GF_Living Hall'])
    R = X.R
    F.coffee_table_rect('GF_Hall_CoffeeTable', 3.3, 3.95, z)
    P(F.sofa, 'Sofa3', 'S', 3.3, 1.9 - R[2], z, w=2.2, fab='fab_grey')
    x, y, f = 1.0, 3.95, 'E'
    F.armchair_wicker('GF_Hall_ArmchairW', 1.05, 3.95, z, 'E')
    F.armchair_wicker('GF_Hall_ArmchairE', 5.55, 3.95, z, 'W')
    F.rug('GF_Hall_Rug_Main', 3.3, 3.2, z, 3.4, 2.5, base='rug_cream', stripe='rug_pink', n=0)
    F.rug('GF_Hall_Rug_Striped', 4.0, 0.9, z, 1.4, 0.7, base='rug_red', stripe='rug_pink', n=4)
    # TV wall (niche panel from R2)
    F.tv_unit('GF_Hall_TVUnit', 6.45, 6.82, z, 'S', w=2.0, d=0.4)
    F.tv('GF_Hall_TV', 6.45, 6.92, z + 0.9, 'S')
    F.table_lamp('GF_Hall_TVUnit_Lamp', 5.65, 6.62, z + 0.5)
    F.pot_plant('GF_Hall_TVUnit_Plant', 7.3, 6.6, z + 0.5, 'money', 'ceramic', h=0.3, pot_r=0.07, pot_h=0.14, kindtag='prop')
    # reading corner (ref hall: wicker chairs, glass table, terracotta vase, plant stand)
    F.side_table('GF_Hall_GlassTable', 7.3, 1.0, z, r=0.3, h=0.5, top='wicker')
    F.armchair_wicker('GF_Hall_CornerChair1', 6.1, 1.0, z, 'E', cush='fab_brown', pillow='fab_cream')
    F.armchair_wicker('GF_Hall_CornerChair2', 7.35, 2.05, z, 'S', cush='fab_brown', pillow='fab_black_floral')
    F.vase_tall('GF_Hall_VaseTall', 7.78, 0.4, z, h=1.0, r=0.16)
    F.pot_plant('GF_Hall_Areca', 0.8, 6.4, z, 'areca', 'terracotta', h=1.1, pot_r=0.2, pot_h=0.4, kindtag='floor')
    F.pot_plant('GF_Hall_Snake', 0.45, 0.45, z, 'snake', 'black', h=0.75, pot_r=0.16, pot_h=0.34, kindtag='floor')
    X.set('decor', fl, 'Hall')
    curt('Curtain_Slider', 'S', 4.0, 4.6, fl, 'A', 2.4)
    curt('Curtain_Window', 'W', 3.5, 4.4, fl, 'A', 2.3)
    for i, (px, pz) in enumerate(((0.55, 2.35), (0.98, 2.0), (0.55, 1.65))):
        F.wall_plate(f'GF_Hall_WallPlate_{i + 1}', px, 0.115, z + pz, 'N', r=0.12)
    F.framed_art('GF_Hall_Art_1', 1.9, 6.9425, z + 1.5, 'S', 1.1, 0.75, 'art_ochre', 'art_blue', seed=3)
    F.sconce('GF_Hall_Sconce_1', 4.85, 6.9425, z + 1.8, 'S')
    F.sconce('GF_Hall_Sconce_2', 7.9, 0.115, z + 1.8, 'N')
    X.set('light', fl, 'Hall')
    F.ceiling_fan('GF_Hall_CeilingFan', 3.3, 3.6, CE[fl])
    F.split_ac('GF_Hall_SplitAC', 0.115, 3.5, z + 2.5, 'E')
    F.tube_light('GF_Hall_TubeLight', 1.7, 6.9425, z + 1.75, 'S')
    for i, (px, py) in enumerate(((1.5, 1.6), (3.3, 1.6), (5.1, 1.6), (1.5, 5.4), (5.1, 5.4), (7.0, 3.4))):
        F.downlight(f'GF_Hall_Downlight_{i + 1}', px, py, CE[fl])
    for i, (px, py, fc) in enumerate(((2.9, 6.9425, 'S'), (0.115, 6.2, 'E'))):
        F.switchplate(f'GF_Hall_Switch_{i + 1}', px, py, z + 1.2, fc, n=4)
    # -------------------------------------------------- DINING
    X.set('furn', fl, 'Dining', rooms['GF_Dining'])
    R = X.R
    F.dining_table('GF_Dining_Table', 10.4, 3.4, z, 'E')
    for i, (cx, cy, fc) in enumerate(((9.5, 2.95, 'E'), (9.5, 3.85, 'E'), (11.3, 2.95, 'W'), (11.3, 3.85, 'W'), (10.4, 2.1, 'N'), (10.4, 4.7, 'S'))):
        F.dining_chair(f'GF_Dining_Chair_{i + 1}', cx, cy, z, fc)
    F.console('GF_Dining_CrockeryConsole', 12.82, 5.1, z, 'W', w=1.7, d=0.42, h=0.85)
    F.rug('GF_Dining_Rug', 10.4, 3.4, z, 3.0, 2.4, base='rug_cream', stripe='rug_pink', n=0)
    X.set('decor', fl, 'Dining')
    F.vase_tall('GF_Dining_Console_Vase', 12.6, 4.45, z + 0.85, h=0.45, r=0.09, mat='ceramic', branches=False)
    F.table_lamp('GF_Dining_Console_Lamp', 12.6, 5.8, z + 0.85)
    curt('Curtain_Slider', 'S', 10.75, 3.4, fl, 'A', 2.4)
    F.framed_art('GF_Dining_Art', 10.4, 6.9425, z + 1.4, 'S', 1.3, 0.8, 'art_red', 'art_ochre', seed=8)
    F.pot_plant('GF_Dining_Fern', 12.5, 0.75, z, 'fern', 'terracotta', h=0.8, pot_r=0.2, pot_h=0.34, kindtag='floor')
    F.pot_plant('GF_Dining_Bowl_Plant', 10.4, 3.4, z + 0.76, 'money', 'ceramic', h=0.25, pot_r=0.07, pot_h=0.12, kindtag='prop')
    X.set('light', fl, 'Dining')
    for i in range(3):
        F.pendant(f'GF_Dining_Pendant_{i + 1}', 10.4, 2.75 + 0.65 * i, CE[fl], drop=0.85)
    F.ceiling_fan('GF_Dining_CeilingFan', 10.4, 5.9, CE[fl])
    F.split_ac('GF_Dining_SplitAC', 10.75, 0.115, z + 2.5, 'N')
    for i, (px, py) in enumerate(((9.0, 1.5), (11.8, 1.5), (9.0, 5.3), (11.8, 5.3))):
        F.downlight(f'GF_Dining_Downlight_{i + 1}', px, py, CE[fl])
    # -------------------------------------------------- KITCHEN
    X.set('kit', fl, 'Kitchen', rooms['GF_Kitchen'])
    R = X.R; ya = R[2]; xb = R[1]
    K.fridge('GF_Kitchen_Fridge', 13.4, ya, z, 'N')
    K.base_run('GF_Kitchen_BaseRun_South', 15.895, ya, z, 'N', [(0.6, 'drawers'), (0.9, 'sink'), (0.75, 'door2'), (0.6, 'drawers'), (0.6, 'door2'), (0.44, 'door1')])
    K.base_run('GF_Kitchen_BaseRun_East', xb, 2.0575, z, 'W', [(0.6, 'door1'), (0.6, 'drawers'), (0.9, 'drawers'), (0.6, 'door2'), (0.6, 'drawers'), (0.585, 'door1')])
    # fix: east run centred on y = .115 + L/2
    X.set('kit', fl, 'Kitchen')
    K.wall_run('GF_Kitchen_WallRun_East', xb, 2.395, z, 'W', [(0.45, 'door'), (0.44, 'glass'), (0.66, 'gap'), (0.55, 'door'), (0.55, 'door'), (0.55, 'glass'), (0.5, 'door')])
    K.wall_run('GF_Kitchen_WallRun_South', 17.6, ya, z, 'N', [(1.0, 'door')])
    K.chimney('GF_Kitchen_Chimney', xb, 1.765, z, 'W', w=0.62, zb=1.55)
    K.hob('GF_Kitchen_Hob', xb - 0.05, 1.765, z + 0.9, 'W', 3)
    # mosaic backsplash (material refined in R4)
    it = c.Item('GF_Kitchen_Backsplash', 0, 0, 0, 'N', kind='wall')
    it.box('mosaic', 13.95, 17.84, ya, ya + 0.01, z + 0.9, z + 1.45)
    it.box('mosaic', xb - 0.01, xb, 0.115, 4.0, z + 0.9, z + 1.45)
    it.finish()
    X.set('kit', fl, 'Kitchen')
    for i, mt in enumerate(('teal', 'purple', 'plain', 'blue', 'blue')):
        K.bottle(f'GF_Kitchen_Bottle_{i + 1}', 16.15 + i * 0.09, 0.3, z + 0.9, {'teal': 'fab_teal', 'purple': 'purple_plastic', 'plain': 'glass', 'blue': 'blue_plastic'}[mt], h=0.24 + 0.02 * (i % 3))
    K.kettle('GF_Kitchen_Kettle', 17.3, 0.32, z + 0.9)
    K.bowl('GF_Kitchen_Bowl', 17.5, 0.3, z + 0.9, mat='pink_plastic')
    K.mixer_jar('GF_Kitchen_Mixer', 18.1, 3.4, z + 0.9)
    K.rice_cooker('GF_Kitchen_RiceCooker', 18.1, 3.8, z + 0.9)
    K.knife_block('GF_Kitchen_KnifeBlock', 18.2, 0.5, z + 0.9)
    K.bowl('GF_Kitchen_BowlSink', 14.35, 0.3, z + 0.9, r=0.06, mat='yellow_plastic')
    K.exhaust_fan('GF_Kitchen_ExhaustFan', 13.5, ya, z + 2.2, 'N')
    for i, (py) in enumerate((0.95, 3.0)):
        F.switchplate(f'GF_Kitchen_Switch_{i + 1}', xb, py, z + 1.15, 'W', n=4)
    F.tube_light('GF_Kitchen_TubeLight', 15.6, 4.9425, z + 1.75, 'S')
    F.doormat('GF_Kitchen_Mat', 14.0, 1.6, z, 'N', 0.5, 0.8, 'rug_blue')
    X.set('light', fl, 'Kitchen')
    for i, (px, py) in enumerate(((14.4, 1.5), (16.4, 1.5), (14.4, 3.6), (16.4, 3.6))):
        F.downlight(f'GF_Kitchen_Downlight_{i + 1}', px, py, CE[fl])
    # -------------------------------------------------- UTILITY
    X.set('furn', fl, 'Utility', rooms['GF_Utility'])
    R = X.R
    K.washing_machine('GF_Utility_WashingMachine', 17.0, R[3], z, 'S', cover=True)
    K.base_run('GF_Utility_SinkRun', R[1], 6.0, z, 'W', [(0.9, 'sink'), (0.9, 'door2')], depth=0.55)
    K.wall_run('GF_Utility_WallRun', R[1], 6.0, z, 'W', [(0.9, 'door'), (0.9, 'door')], loft=0.0)
    F.bookshelf('GF_Utility_Shelf', 13.5, R[3], z, 'S', w=1.0, h=1.9, d=0.35, rows=4, seed=11, fill=0.5, mat='lam_white')
    X.set('light', fl, 'Utility')
    F.downlight('GF_Utility_Downlight_1', 15.7, 6.0, CE[fl]); F.downlight('GF_Utility_Downlight_2', 17.3, 5.6, CE[fl])
    F.tube_light('GF_Utility_TubeLight', 14.2, R[3], z + 2.0, 'S')
    K.exhaust_fan('GF_Utility_ExhaustFan', 18.0, R[3], z + 2.2, 'S')
    # -------------------------------------------------- BEDROOM G1 (guest)
    rg1 = rooms['GF_Bedroom G1 (Guest)']
    bedroom_set('BedG1', fl, rg1, 'W', 2.5, 0.0, w=1.6, cover='fab_mandala', throw='fab_cream')
    X.set('bed', fl, 'BedG1', rg1)
    P(F.dresser, 'Dresser', 'S', 19.05, 0.0, z, w=0.9)
    F.armchair_wicker('GF_BedG1_Armchair', 23.3, 0.95, z, 'N', cush='fab_taupe', pillow='fab_cream')
    F.rug('GF_BedG1_Rug', 20.3, 2.5, z, 2.8, 2.0, base='rug_cream', stripe='rug_pink')
    X.set('decor', fl, 'BedG1')
    curt('Curtain_Slider', 'S', 21.0, 3.3, fl, 'B', 2.4)
    curt('Curtain_Window', 'E', 2.5, 2.4, fl, 'B', 2.3)
    F.framed_art('GF_BedG1_Art', 18.5575, 2.5, z + 1.55, 'E', 1.0, 0.65, 'art_blue', 'art_ochre', seed=21)
    X.set('light', fl, 'BedG1')
    F.ceiling_fan('GF_BedG1_CeilingFan', 21.2, 2.6, CE[fl])
    F.split_ac('GF_BedG1_SplitAC', 21.0, 0.115, z + 2.5, 'N')
    F.tube_light('GF_BedG1_TubeLight', 21.2, 4.9425, z + 1.75, 'S')
    for i, (px, py) in enumerate(((20.0, 1.2), (22.4, 1.2), (20.0, 3.8), (22.4, 3.8))):
        F.downlight(f'GF_BedG1_Downlight_{i + 1}', px, py, CE[fl])
    F.switchplate('GF_BedG1_Switch', 19.0, 4.9425, z + 1.2, 'S', n=4)
    # bath G1
    bath_room('BathG1', fl, rooms['GF_Bath G1'], 'E')
    # dress lobby G1
    X.set('bed', fl, 'LobbyG1', rooms['GF_Dress Lobby G1'])
    R = X.R
    F.wardrobe('GF_LobbyG1_WardrobeE', R[1], 6.0, z, 'W', w=1.8, h=2.8, cols=3)
    F.wardrobe('GF_LobbyG1_WardrobeW', R[0], 6.25, z, 'E', w=1.2, h=2.8, cols=2)
    X.set('light', fl, 'LobbyG1')
    F.downlight('GF_LobbyG1_Downlight_1', 22.7, 6.0, CE[fl])
    # -------------------------------------------------- BEDROOM G2
    rg2 = rooms['GF_Bedroom G2']
    bedroom_set('BedG2', fl, rg2, 'E', 10.7, 0.0, w=1.6, cover='fab_floral', throw='fab_mustard', bs_gap=0.4)
    X.set('bed', fl, 'BedG2', rg2)
    x, y, f = 4.6, 8.5575, 'N'
    F.wardrobe('GF_BedG2_Wardrobe', 4.55, 8.5575, z, 'N', w=1.8, h=2.8, cols=3)
    F.desk('GF_BedG2_Desk', 3.0, 13.885, z, 'S', w=1.4, d=0.6)
    F.office_chair('GF_BedG2_Chair', 3.0, 12.85, z, 'N')
    F.dresser('GF_BedG2_Dresser', 0.115, 9.6, z, 'E', w=0.9)
    F.rug('GF_BedG2_Rug', 4.5, 10.7, z, 2.6, 2.0, base='rug_cream', stripe='rug_pink')
    F.laptop('GF_BedG2_Laptop', 3.0, 13.55, z + 0.75, 'S')
    X.set('decor', fl, 'BedG2')
    curt('Curtain_Window_W', 'W', 11.25, 3.2, fl, 'B', 2.4)
    curt('Curtain_Window_N', 'N', 3.0, 2.6, fl, 'B', 2.4)
    X.set('light', fl, 'BedG2')
    F.ceiling_fan('GF_BedG2_CeilingFan', 2.9, 11.2, CE[fl])
    F.split_ac('GF_BedG2_SplitAC', 0.115, 11.25, z + 2.5, 'E')
    F.tube_light('GF_BedG2_TubeLight', 1.1, 8.5575, z + 1.75, 'N')
    for i, (px, py) in enumerate(((1.5, 9.8), (4.4, 9.2), (1.5, 12.8), (4.4, 12.8))):
        F.downlight(f'GF_BedG2_Downlight_{i + 1}', px, py, CE[fl])
    bath_room('BathG2', fl, rooms['GF_Bath G2'], 'E', vanity=False)
    # store
    X.set('furn', fl, 'Store', rooms['GF_Store'])
    R = X.R
    F.bookshelf('GF_Store_ShelfE', R[1], 10.0, z, 'W', w=2.0, h=2.2, d=0.4, rows=5, seed=5, fill=0.35, mat='steel')
    F.bookshelf('GF_Store_ShelfW', R[0], 10.0, z, 'E', w=2.0, h=2.2, d=0.4, rows=5, seed=6, fill=0.35, mat='steel')
    X.set('light', fl, 'Store')
    F.tube_light('GF_Store_TubeLight', 7.5, 11.4425, z + 2.4, 'S')
    # -------------------------------------------------- FOYER
    X.set('furn', fl, 'Foyer', rooms['GF_Entrance Foyer'])
    R = X.R
    F.console('GF_Foyer_Console', R[0], 11.2, z, 'E', w=1.3, d=0.38, h=0.85, mat='wood_dark')
    F.ottoman_bench('GF_Foyer_Bench', R[1], 12.3, z, 'W', w=1.2, d=0.42)
    F.bookshelf('GF_Foyer_ShoeRack', R[1], 10.3, z, 'W', w=1.2, h=1.0, d=0.35, rows=3, seed=2, fill=0.5, mat='wood_med')
    F.doormat('GF_Foyer_Doormat', 12.0, 13.4, z, 'N', 1.1, 0.7, 'rug_red')
    F.rug('GF_Foyer_Rug', 12.0, 10.9, z, 2.8, 2.0, base='rug_cream', stripe='rug_pink')
    F.pot_plant('GF_Foyer_PlantW', 10.15, 13.25, z, 'areca', 'terracotta', h=1.2, pot_r=0.2, pot_h=0.4, kindtag='floor')
    F.pot_plant('GF_Foyer_PlantE', 13.85, 13.5, z, 'ficus', 'ceramic', h=1.1, pot_r=0.2, pot_h=0.4, kindtag='floor')
    X.set('decor', fl, 'Foyer')
    F.wall_mirror('GF_Foyer_Mirror', R[0], 11.2, z + 1.3, 'E', 0.8, 1.1, frame='brass')
    F.table_lamp('GF_Foyer_ConsoleLamp', R[0] + 0.15, 10.8, z + 0.85)
    F.vase_tall('GF_Foyer_ConsoleVase', R[0] + 0.18, 11.65, z + 0.85, h=0.5, r=0.09, mat='ceramic', branches=False)
    F.framed_art('GF_Foyer_Art', R[1], 11.3, z + 1.5, 'W', 1.0, 0.7, 'art_ochre', 'art_red', seed=30)
    X.set('light', fl, 'Foyer')
    F.chandelier('GF_Foyer_Chandelier', 12.0, 11.2, CE[fl], drop=0.45, r=0.36)
    F.sconce('GF_Foyer_Sconce_1', 10.6, 13.885, z + 1.9, 'S')
    F.sconce('GF_Foyer_Sconce_2', 13.4, 13.885, z + 1.9, 'S')
    F.switchplate('GF_Foyer_Switch', 10.5, 13.885, z + 1.2, 'S', n=4)
    # -------------------------------------------------- STAIR HALL / STUDY / CORRIDOR
    X.set('furn', fl, 'StairHall', rooms['GF_Stair Hall'])
    F.pot_plant('GF_StairHall_Palm', 19.15, 13.6, z, 'areca', 'black', h=1.2, pot_r=0.17, pot_h=0.38, kindtag='floor')
    X.set('decor', fl, 'StairHall')
    F.framed_art('GF_StairHall_Art', 19.4425, 11.5, z + 1.6, 'W', 0.9, 0.65, 'art_blue', 'art_red', seed=33)
    X.set('light', fl, 'StairHall')
    F.pendant('GF_StairHall_Pendant', 17.2, 11.5, CE[fl], drop=0.7, kind='lamp')
    F.tube_light('GF_StairHall_TubeLight', 16.0, 8.5575, z + 2.2, 'N')
    st = rooms['GF_Study']
    X.set('furn', fl, 'Study', st)
    R = X.R
    F.bookshelf('GF_Study_Shelf_1', R[0], 9.6, z, 'E', w=1.0, h=2.4, d=0.35, rows=6, seed=41)
    F.bookshelf('GF_Study_Shelf_2', R[0], 10.7, z, 'E', w=1.0, h=2.4, d=0.35, rows=6, seed=42)
    F.bookshelf('GF_Study_Shelf_3', R[0], 11.8, z, 'E', w=1.0, h=2.4, d=0.35, rows=6, seed=43)
    F.desk('GF_Study_Desk', 22.0, R[3], z, 'S', w=1.6, d=0.7)
    F.office_chair('GF_Study_Chair', 22.0, 12.75, z, 'N')
    F.sofa('GF_Study_Sofa', R[1], 11.5, z, 'W', w=1.7, d=0.85, fab='fab_taupe', pill=('fab_cream', 'fab_mustard'))
    F.side_table('GF_Study_SideTable', 23.4, 9.6, z, r=0.25, h=0.55)
    F.rug('GF_Study_Rug', 22.2, 11.2, z, 2.4, 1.8, base='rug_blue', stripe='rug_cream')
    F.monitor('GF_Study_Monitor', 22.0, R[3] - 0.25, z + 0.75, 'S')
    F.table_lamp('GF_Study_DeskLamp', 21.3, R[3] - 0.2, z + 0.75, h=0.3)
    X.set('decor', fl, 'Study')
    curt('Curtain_Window_N', 'N', 21.75, 2.9, fl, 'C', 2.3)
    curt('Curtain_Window_E', 'E', 11.5, 2.4, fl, 'C', 2.3)
    X.set('light', fl, 'Study')
    F.ceiling_fan('GF_Study_CeilingFan', 21.7, 11.2, CE[fl])
    F.split_ac('GF_Study_SplitAC', R[1], 11.5, z + 2.5, 'W')
    F.tube_light('GF_Study_TubeLight', 22.8, 8.5575, z + 1.75, 'N')
    for i, (px, py) in enumerate(((21.0, 9.6), (23.0, 9.6), (21.0, 12.8))):
        F.downlight(f'GF_Study_Downlight_{i + 1}', px, py, CE[fl])
    # corridor
    X.set('furn', fl, 'Corridor', rooms['GF_Corridor'])
    R = X.R
    F.console('GF_Corridor_Console_1', 7.0, R[2], z, 'N', w=1.4, d=0.35, h=0.8)
    F.console('GF_Corridor_Console_2', 19.0, R[2], z, 'N', w=1.4, d=0.35, h=0.8)
    F.pot_plant('GF_Corridor_PlantW', 0.6, 7.75, z, 'snake', 'ceramic', h=0.8, pot_r=0.15, pot_h=0.34, kindtag='floor')
    F.pot_plant('GF_Corridor_PlantE', 23.5, 7.75, z, 'aloe', 'terracotta', h=0.6, pot_r=0.17, pot_h=0.3, kindtag='floor')
    X.set('decor', fl, 'Corridor')
    F.wall_mirror('GF_Corridor_Mirror', 7.0, R[2], z + 1.25, 'N', 0.8, 1.0, frame='wood_dark')
    for i, ax in enumerate((5.4, 8.7)):
        F.framed_art(f'GF_Corridor_Art_{i + 1}', ax, R[3], z + 1.4, 'S', 1.0, 0.7, 'art_blue' if i else 'art_ochre', 'art_red', seed=50 + i)
    F.framed_art('GF_Corridor_Art_3', 19.5, R[3], z + 1.4, 'S', 1.4, 0.7, 'art_ochre', 'art_blue', seed=55)
    F.table_lamp('GF_Corridor_Lamp_1', 6.6, R[2] + 0.15, z + 0.8, h=0.3); F.table_lamp('GF_Corridor_Lamp_2', 19.4, R[2] + 0.15, z + 0.8, h=0.3)
    X.set('light', fl, 'Corridor')
    for i, px in enumerate((2.0, 6.0, 10.0, 14.0, 18.0, 22.0)):
        F.downlight(f'GF_Corridor_Downlight_{i + 1}', px, 7.75, CE[fl])
    F.tube_light('GF_Corridor_TubeLight_1', 9.0, R[3], z + 2.3, 'S'); F.tube_light('GF_Corridor_TubeLight_2', 21.0, R[3], z + 2.3, 'S')
    return 'GF furnished'


# ===================================================================== FIRST FLOOR
def first_floor(rooms):
    fl = 'FF'; z = Z[fl]
    # ---------------------------------------------- MASTER
    rm = rooms['FF_Master Bedroom']
    X.set('bed', fl, 'Master', rm)
    F.bed('FF_Master_Bed', 3.35, 4.82, z, 'S', w=1.8, l=2.1, cover='fab_mandala', pill='fab_white', throw='fab_cream')
    F.bedside('FF_Master_BedsideA', 2.14, 4.82, z, 'S', w=0.46)
    F.bedside('FF_Master_BedsideB', 4.56, 4.82, z, 'S', w=0.46)
    F.ottoman_bench('FF_Master_Bench', 3.35, 2.55, z, 'S', w=1.5)
    F.tv_unit('FF_Master_TVUnit', 6.9425, 2.5, z, 'W', w=1.6, d=0.4, h=0.45)
    F.sofa('FF_Master_Sofa', 0.115, 2.5, z, 'E', w=1.5, d=0.8, fab='fab_taupe', pill=('fab_cream', 'fab_mustard'))
    F.rug('FF_Master_Rug', 3.35, 3.3, z, 2.9, 2.2, base='rug_cream', stripe='rug_pink')
    F.pot_plant('FF_Master_Plant', 6.4, 0.5, z, 'ficus', 'ceramic', h=1.1, pot_r=0.2, pot_h=0.4, kindtag='floor')
    F.side_table('FF_Master_SideTable', 0.5, 4.2, z, r=0.22, h=0.5)
    F.tv('FF_Master_TV', 6.92, 2.5, z + 1.15, 'W', w=1.1, hgt=0.65)
    X.set('decor', fl, 'Master')
    for sx, u in ((2.6, 1), (4.1, 2)):
        F.vase_tall(f'FF_Master_NicheVase_{u}', sx, 4.86, z + 1.5, h=0.45, r=0.08, mat='ceramic', branches=False)
    curt('Curtain_Slider', 'S', 3.5, 3.8, fl, 'B', 2.4)
    curt('Curtain_Window', 'W', 2.5, 2.4, fl, 'B', 2.3)
    X.set('light', fl, 'Master')
    F.ceiling_fan('FF_Master_CeilingFan', 3.5, 2.8, CE[fl])
    F.split_ac('FF_Master_SplitAC', 3.5, 0.115, z + 2.52, 'N')
    for i, (px, py) in enumerate(((1.4, 1.2), (5.6, 1.2), (1.2, 3.6), (5.8, 3.6))):
        F.downlight(f'FF_Master_Downlight_{i + 1}', px, py, CE[fl])
    F.switchplate('FF_Master_Switch', 1.0, 4.9425, z + 1.2, 'S', n=4)
    bath_room('MasterBath', fl, rooms['FF_Master Bath'], 'E', vanity=True)
    # dressing
    X.set('bed', fl, 'Dressing', rooms['FF_Master Dressing'])
    R = X.R
    F.wardrobe('FF_Dressing_WardrobeW', R[0], 6.0, z, 'E', w=1.8, h=2.8, cols=3)
    F.wardrobe('FF_Dressing_WardrobeE', R[1], 6.0, z, 'W', w=1.8, h=2.8, cols=3)
    F.pouf('FF_Dressing_Pouf', 5.25, 6.2, z, r=0.22, h=0.42)
    X.set('light', fl, 'Dressing')
    F.downlight('FF_Dressing_Downlight_1', 5.25, 5.5, CE[fl]); F.downlight('FF_Dressing_Downlight_2', 5.25, 6.5, CE[fl])
    # ---------------------------------------------- BED 3 & BED 4
    for tag, key, headu, hx, sl_u, ward_x in (('Bed3', 'FF_Bedroom F3', 2.5, 'E', 10.0, 7.0575), ('Bed4', 'FF_Bedroom F4', 2.5, 'E', 15.7, 13.0575)):
        rect = rooms[key]
        bedroom_set(tag, fl, rect, 'E', 2.5, 0.0, w=1.6, cover='fab_floral' if tag == 'Bed3' else 'fab_mandala', throw='fab_mustard' if tag == 'Bed3' else 'fab_cream')
        X.set('bed', fl, tag, rect)
        R = X.R
        F.wardrobe(f'FF_{tag}_Wardrobe', ward_x, 2.6, z, 'E', w=2.6, h=2.8, cols=4)
        F.armchair_wicker(f'FF_{tag}_Armchair', R[0] + 0.55, R[2], z, 'N', cush='fab_taupe', pillow='fab_cream')
        F.rug(f'FF_{tag}_Rug', (R[0] + R[1]) / 2 + 0.9, 2.5, z, 2.8, 2.0, base='rug_cream', stripe='rug_pink')
        F.framed_art(f'FF_{tag}_Art', (R[0] + R[1]) / 2 + 0.3, R[3], z + 1.6, 'S', 1.0, 0.65, 'art_blue', 'art_ochre', seed=60 + len(tag))
        X.set('decor', fl, tag)
        curt('Curtain_Slider', 'S', sl_u, 3.6, fl, 'B', 2.4)
        X.set('light', fl, tag)
        F.ceiling_fan(f'FF_{tag}_CeilingFan', sl_u + 0.2, 2.5, CE[fl])
        F.split_ac(f'FF_{tag}_SplitAC', sl_u, 0.115, z + 2.52, 'N')
        F.tube_light(f'FF_{tag}_TubeLight', sl_u + 0.2, R[3], z + 1.75, 'S')
        for i, (px, py) in enumerate(((sl_u - 1.5, 1.2), (sl_u + 1.5, 1.2), (sl_u - 1.5, 3.8), (sl_u + 1.5, 3.8))):
            F.downlight(f'FF_{tag}_Downlight_{i + 1}', px, py, CE[fl])
    bath_room('BathF3', fl, rooms['FF_Bath F3'], 'E')
    bath_room('BathF4', fl, rooms['FF_Bath F4'], 'E')
    X.set('bed', fl, 'LobbyF3', rooms['FF_Lobby F3']); R = X.R
    F.wardrobe('FF_LobbyF3_WardrobeW', R[0], 6.0, z, 'E', w=1.6, h=2.8, cols=3)
    F.wardrobe('FF_LobbyF3_WardrobeE', R[1], 6.0, z, 'W', w=1.6, h=2.8, cols=3)
    X.set('bed', fl, 'LobbyF4', rooms['FF_Lobby F4']); R = X.R
    F.wardrobe('FF_LobbyF4_WardrobeE', R[1], 6.0, z, 'W', w=1.6, h=2.8, cols=3)
    for t in ('LobbyF3', 'LobbyF4'):
        X.set('light', fl, t)
        F.downlight(f'FF_{t}_Downlight', 11.5 if t == 'LobbyF3' else 17.2, 6.0, CE[fl])
    # ---------------------------------------------- FAMILY LOUNGE
    X.set('furn', fl, 'Lounge', rooms['FF_Family Lounge']); R = X.R
    F.tv_unit('FF_Lounge_TVUnit', R[0], 3.5, z, 'E', w=1.9, d=0.42)
    F.tv('FF_Lounge_TV', R[0] + 0.03, 3.5, z + 0.95, 'E', w=1.4, hgt=0.8)
    F.sofa('FF_Lounge_Sofa', R[1], 3.5, z, 'W', w=2.3, d=0.9, fab='fab_taupe', pill=('fab_mustard', 'fab_cream'))
    F.coffee_table_round('FF_Lounge_CoffeeTable', 21.4, 3.5, z, r=0.5, h=0.42)
    F.armchair_wicker('FF_Lounge_ArmchairA', 20.5, 1.9, z, 'N', cush='fab_brown', pillow='fab_cream')
    F.armchair_wicker('FF_Lounge_ArmchairB', 20.5, 5.1, z, 'S', cush='fab_brown', pillow='fab_black_floral')
    F.rug('FF_Lounge_Rug', 21.2, 3.5, z, 3.2, 2.6, base='rug_blue', stripe='rug_cream')
    F.pot_plant('FF_Lounge_Palm', 23.4, 6.4, z, 'areca', 'terracotta', h=1.3, pot_r=0.22, pot_h=0.42, kindtag='floor')
    F.pot_plant('FF_Lounge_Fern', 19.0, 6.4, z, 'fern', 'ceramic', h=0.8, pot_r=0.2, pot_h=0.34, kindtag='floor')
    X.set('decor', fl, 'Lounge')
    curt('Curtain_Slider', 'S', 21.25, 4.0, fl, 'A', 2.4)
    curt('Curtain_Window', 'E', 3.5, 3.4, fl, 'A', 2.3)
    F.framed_art('FF_Lounge_Art', 21.5, 6.9425, z + 1.4, 'S', 1.5, 0.9, 'art_ochre', 'art_blue', seed=71)
    X.set('light', fl, 'Lounge')
    F.ceiling_fan('FF_Lounge_CeilingFan', 21.2, 3.5, CE[fl])
    F.split_ac('FF_Lounge_SplitAC', R[0], 3.5, z + 2.52, 'E')
    for i, (px, py) in enumerate(((19.6, 1.2), (22.8, 1.2), (19.6, 5.8), (22.8, 5.8), (21.2, 6.0))):
        F.downlight(f'FF_Lounge_Downlight_{i + 1}', px, py, CE[fl])
    F.tube_light('FF_Lounge_TubeLight', 19.6, 6.9425, z + 1.75, 'S')
    # ---------------------------------------------- HOME OFFICE
    X.set('furn', fl, 'Office', rooms['FF_Home Office']); R = X.R
    for i, ux in enumerate((3.0, 5.0)):
        F.desk(f'FF_Office_Desk_{i + 1}', ux, R[3], z, 'S', w=1.5, d=0.65)
        F.office_chair(f'FF_Office_Chair_{i + 1}', ux, 12.95, z, 'N')
        F.monitor(f'FF_Office_Monitor_{i + 1}', ux, R[3] - 0.22, z + 0.75, 'S')
    for i, uy in enumerate((9.6, 10.7, 11.8, 12.9)):
        F.bookshelf(f'FF_Office_Shelf_{i + 1}', R[1], uy, z, 'W', w=1.05, h=2.4, d=0.35, rows=6, seed=80 + i)
    F.sofa('FF_Office_Sofa', 7.0, R[2], z, 'N', w=1.9, d=0.85, fab='fab_charcoal', pill=('fab_mustard', 'fab_cream'))
    F.coffee_table_rect('FF_Office_CoffeeTable', 7.0, 10.1, z, 'N', w=0.9, d=0.5)
    F.side_table('FF_Office_MeetTable', 3.0, 10.2, z, r=0.55, h=0.74, top='wood_med')
    for i, a in enumerate((200, 320, 80)):
        px = 3.0 + 1.0 * math.cos(math.radians(a)); py = 10.2 + 1.0 * math.sin(math.radians(a))
        F.dining_chair(f'FF_Office_MeetChair_{i + 1}', px, py, z, 'N' if py < 10.2 else 'S')
    F.rug('FF_Office_Rug', 5.5, 10.4, z, 3.6, 2.4, base='rug_blue', stripe='rug_cream')
    F.pot_plant('FF_Office_Plant', 0.5, 13.5, z, 'rubber', 'black', h=1.2, pot_r=0.2, pot_h=0.4, kindtag='floor')
    X.set('decor', fl, 'Office')
    curt('Curtain_Window_N', 'N', 4.0, 4.6, fl, 'C', 2.3)
    curt('Curtain_Window_W', 'W', 11.25, 3.2, fl, 'C', 2.3)
    F.framed_art('FF_Office_Art', 7.0, R[2], z + 1.7, 'N', 1.2, 0.8, 'art_blue', 'art_ochre', seed=90)
    X.set('light', fl, 'Office')
    F.ceiling_fan('FF_Office_CeilingFan', 4.4, 11.0, CE[fl])
    F.split_ac('FF_Office_SplitAC', R[0], 11.25, z + 2.52, 'E')
    F.tube_light('FF_Office_TubeLight', 7.5, 13.885, z + 1.75, 'S')
    for i, (px, py) in enumerate(((1.5, 9.5), (4.4, 9.5), (7.4, 9.5), (1.5, 12.6), (7.4, 12.6), (4.4, 12.0))):
        F.downlight(f'FF_Office_Downlight_{i + 1}', px, py, CE[fl])
    # landing / stair hall / corridor
    X.set('furn', fl, 'Landing', rooms['FF_Landing']); R = X.R
    F.ottoman_bench('FF_Landing_Bench', 12.0, R[3], z, 'S', w=1.7, d=0.45)
    F.console('FF_Landing_Console', R[0], 11.2, z, 'E', w=1.2, d=0.35, h=0.85)
    F.pot_plant('FF_Landing_PlantA', 10.0, 13.25, z, 'areca', 'terracotta', h=1.1, pot_r=0.2, pot_h=0.4, kindtag='floor')
    F.pot_plant('FF_Landing_PlantB', 14.0, 13.5, z, 'ficus', 'ceramic', h=1.0, pot_r=0.2, pot_h=0.4, kindtag='floor')
    X.set('decor', fl, 'Landing')
    F.wall_mirror('FF_Landing_Mirror', R[0], 11.2, z + 1.3, 'E', 0.8, 1.0, frame='wood_dark')
    F.framed_art('FF_Landing_Art', R[1], 11.2, z + 1.5, 'W', 1.2, 0.8, 'art_ochre', 'art_blue', seed=95)
    curt('Curtain_Window', 'N', 12.0, 2.8, fl, 'C', 2.45)
    X.set('light', fl, 'Landing')
    F.chandelier('FF_Landing_Chandelier', 12.0, 11.0, CE[fl], drop=0.4, r=0.32)
    X.set('furn', fl, 'StairHall', rooms['FF_Stair Hall'])
    F.pot_plant('FF_StairHall_Palm', 19.15, 13.6, z, 'areca', 'black', h=1.2, pot_r=0.17, pot_h=0.38, kindtag='floor')
    X.set('furn', fl, 'Corridor', rooms['FF_Corridor']); R = X.R
    F.console('FF_Corridor_Console_1', 8.3, R[2], z, 'N', w=1.2, d=0.35, h=0.8)
    F.console('FF_Corridor_Console_2', 19.2, R[2], z, 'N', w=1.2, d=0.35, h=0.8)
    F.pot_plant('FF_Corridor_PlantW', 0.6, 7.75, z, 'snake', 'ceramic', h=0.8, pot_r=0.15, pot_h=0.34, kindtag='floor')
    F.pot_plant('FF_Corridor_PlantE', 23.5, 7.75, z, 'aloe', 'terracotta', h=0.6, pot_r=0.17, pot_h=0.3, kindtag='floor')
    X.set('decor', fl, 'Corridor')
    F.framed_art('FF_Corridor_Art_1', 5.5, R[3], z + 1.4, 'S', 1.0, 0.7, 'art_blue', 'art_ochre', seed=101)
    F.framed_art('FF_Corridor_Art_2', 19.5, R[3], z + 1.4, 'S', 1.3, 0.7, 'art_ochre', 'art_red', seed=102)
    X.set('light', fl, 'Corridor')
    for i, px in enumerate((2.0, 6.0, 10.0, 14.0, 18.0, 22.0)):
        F.downlight(f'FF_Corridor_Downlight_{i + 1}', px, 7.75, CE[fl])
    F.tube_light('FF_Corridor_TubeLight', 12.0, R[3], z + 2.3, 'S')
    # roof stair hall (service lobby below the terrace stair mumty)
    X.set('furn', fl, 'RoofStairHall', rooms['FF_Roof Stair Hall']); R = X.R
    F.console('FF_RoofHall_ShoeCabinet', R[1], 11.2, z, 'W', w=1.5, d=0.38, h=0.9)
    F.stool('FF_RoofHall_Stool', R[1] - 0.8, 12.6, z, r=0.2, h=0.45)
    F.pot_plant('FF_RoofHall_Plant', R[1] - 0.45, R[3] - 0.45, z, 'snake', 'ceramic', h=0.9, pot_r=0.16, pot_h=0.34, kindtag='floor')
    F.pot_plant('FF_RoofHall_PlantB', R[0] + 0.5, R[3] - 0.45, z, 'areca', 'terracotta', h=1.0, pot_r=0.2, pot_h=0.4, kindtag='floor')
    F.doormat('FF_RoofHall_Mat', R[0] + 1.2, 11.2, z, 'E', 0.9, 0.6)
    X.set('decor', fl, 'RoofStairHall')
    F.framed_art('FF_RoofHall_Art', R[1], 11.2, z + 1.55, 'W', 0.9, 0.65, 'art_red', 'art_ochre', seed=111)
    F.wall_mirror('FF_RoofHall_Mirror', R[1], 9.7, z + 1.2, 'W', 0.6, 0.9, frame='wood_dark')
    X.set('light', fl, 'RoofStairHall')
    F.ceiling_fan('FF_RoofHall_CeilingFan', (R[0] + R[1]) / 2, 11.2, CE[fl])
    for i, (px, py) in enumerate(((20.8, 9.6), (22.9, 9.6), (20.8, 12.8), (22.9, 12.8))):
        F.downlight(f'FF_RoofHall_Downlight_{i + 1}', px, py, CE[fl])
    F.switchplate('FF_RoofHall_Switch', R[0], 10.3, z + 1.2, 'E', 2)
    return 'FF furnished'


def run():
    rooms = {}
    for o in bpy.data.objects:
        if o.get('room_type') and o.parent == r1.BLD['RES']:
            rooms[f"{o['floor']}_{o['room_name']}"] = tuple(o['bbox'][:4])
    out = ground_floor(rooms)
    out += ' | ' + first_floor(rooms)
    return out
