"""Round 1 foundation/blockout builder - 3D-5BHK-RA-1-RW.
Units: metres. X east, Y north, Z up. Origin = SW corner of residence.
All geometry is non-destructive: walls carry Boolean modifiers fed by cutter objects.
"""
import bpy, math, json
from mathutils import Vector

ROOT = "PROJECT_5BHK_RA-1-RW"
C = {}
PX = {"RES": "Res", "CLUB": "Club", "PAV": "Pav"}
BLD = {}

BLOCK_MATS = {
    "BLK_Wall_Exterior": (0.86, 0.82, 0.72), "BLK_Wall_Interior": (0.93, 0.92, 0.88),
    "BLK_Slab_Concrete": (0.55, 0.55, 0.55), "BLK_Floor_Finish": (0.80, 0.74, 0.62),
    "BLK_Stair": (0.85, 0.50, 0.20), "BLK_Roof": (0.25, 0.22, 0.22),
    "BLK_Column": (0.70, 0.68, 0.64), "BLK_Ground_Lawn": (0.28, 0.50, 0.20),
    "BLK_Pool_Deck": (0.62, 0.62, 0.60), "BLK_Pool_Water": (0.10, 0.35, 0.80),
    "BLK_Path": (0.72, 0.65, 0.55), "BLK_Laterite": (0.60, 0.25, 0.15),
    "BLK_Cutter": (1.0, 0.0, 0.0), "BLK_Room": (0.2, 0.5, 0.9),
}


def _mat(name, col, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (col[0], col[1], col[2], 1.0)
    try:
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if b:
            b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
            b.inputs["Roughness"].default_value = rough
    except Exception:
        pass
    return m


def _colls():
    """Re-bind collection handles (stateless between executions)."""
    for c in bpy.data.collections:
        if c.name[:2].isdigit() or c.name == ROOT:
            C[c.name] = c
    keys = {"REF": "00_Reference_Guides", "SITE": "01_Site_Ground", "EXT": "02_Exterior_Architecture",
            "FLOOR": "03_Floors", "WALL": "04_Walls", "CEIL": "05_Ceilings", "ROOF": "06_Roof",
            "DOOR": "07_Doors", "WIN": "08_Windows", "STAIR": "09_Stairs", "RAIL": "10_Railings",
            "ROOMS": "11_Rooms", "LIV": "11a_Living_Hall", "KIT": "11b_Kitchen", "BATH": "11c_Bathrooms",
            "BED": "11d_Bedrooms", "FURN": "12_Furniture", "DECOR": "13_Decorative_Elements",
            "POOL": "14_Pool_Water", "LAND": "15_Landscaping", "MAT": "16_Materials",
            "LIGHT": "17_Lighting", "CAM": "18_Cameras"}
    for k, n in keys.items():
        C[k] = bpy.data.collections[n]
    for k, n in ("RES", "BLD_Residence"), ("CLUB", "BLD_Clubhouse"), ("PAV", "BLD_Pavilion"):
        BLD[k] = bpy.data.objects.get(n)


def setup():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    for n in ("Cube", "Light", "Camera"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    root = bpy.data.collections.new(ROOT)
    sc.collection.children.link(root)
    top = ["00_Reference_Guides", "01_Site_Ground", "02_Exterior_Architecture", "03_Floors", "04_Walls",
           "05_Ceilings", "06_Roof", "07_Doors", "08_Windows", "09_Stairs", "10_Railings", "11_Rooms",
           "12_Furniture", "13_Decorative_Elements", "14_Pool_Water", "15_Landscaping", "16_Materials",
           "17_Lighting", "18_Cameras"]
    for n in top:
        c = bpy.data.collections.new(n)
        root.children.link(c)
    rooms = bpy.data.collections["11_Rooms"]
    for n in ["11a_Living_Hall", "11b_Kitchen", "11c_Bathrooms", "11d_Bedrooms"]:
        c = bpy.data.collections.new(n)
        rooms.children.link(c)
    for n, c in BLOCK_MATS.items():
        _mat(n, c)
    for n in ("BLD_Residence", "BLD_Clubhouse", "BLD_Pavilion"):
        e = bpy.data.objects.new(n, None)
        e.empty_display_type = "PLAIN_AXES"
        e.empty_display_size = 1.5
        bpy.data.collections["02_Exterior_Architecture"].objects.link(e)
    _colls()
    return "setup ok"


def link(ob, coll, parent=None, mat=None, props=None):
    coll.objects.link(ob)
    if parent:
        ob.parent = parent
    if mat:
        ob.data.materials.append(bpy.data.materials[mat])
    for k, v in (props or {}).items():
        ob[k] = v
    return ob


def _boxmesh(name, x0, x1, y0, y1, z0, z1):
    hx, hy, hz = (x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    return me


def box(name, x0, x1, y0, y1, z0, z1, coll, parent=None, mat=None, **props):
    me = _boxmesh(name, x0, x1, y0, y1, z0, z1)
    ob = bpy.data.objects.new(name, me)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    return link(ob, coll, parent, mat, props)


def multibox(name, boxes, coll, parent=None, mat=None, **props):
    ox = min(b[0] for b in boxes); oy = min(b[2] for b in boxes); oz = min(b[4] for b in boxes)
    v, f = [], []
    for (x0, x1, y0, y1, z0, z1) in boxes:
        i = len(v)
        v += [(x0 - ox, y0 - oy, z0 - oz), (x1 - ox, y0 - oy, z0 - oz), (x1 - ox, y1 - oy, z0 - oz), (x0 - ox, y1 - oy, z0 - oz),
              (x0 - ox, y0 - oy, z1 - oz), (x1 - ox, y0 - oy, z1 - oz), (x1 - ox, y1 - oy, z1 - oz), (x0 - ox, y1 - oy, z1 - oz)]
        f += [tuple(i + k for k in q) for q in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = (ox, oy, oz)
    return link(ob, coll, parent, mat, props)


def prism(name, pts, z0, z1, coll, parent=None, mat=None, **props):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) / 2
    if area < 0:
        pts = pts[::-1]
    cx = sum(p[0] for p in pts) / n; cy = sum(p[1] for p in pts) / n
    h = (z1 - z0) / 2
    v = [(x - cx, y - cy, -h) for x, y in pts] + [(x - cx, y - cy, h) for x, y in pts]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = (cx, cy, (z0 + z1) / 2)
    return link(ob, coll, parent, mat, props)


def hip_roof(name, x0, x1, y0, y1, zb, rise, coll, parent=None, mat=None):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = (y1 - y0) / 2
    ym = cy
    P = [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0), (x0 + d, ym, rise), (x1 - d, ym, rise)]
    v = [(x - cx, y - cy, z) for x, y, z in P]
    f = [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4), (0, 3, 2, 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = (cx, cy, zb)
    return link(ob, coll, parent, mat)


def _merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _subtract(ivs, ex):
    out = []
    for a, b in ivs:
        segs = [[a, b]]
        for ea, eb in ex:
            new = []
            for s0, s1 in segs:
                if eb <= s0 or ea >= s1:
                    new.append([s0, s1])
                else:
                    if ea > s0: new.append([s0, ea])
                    if eb < s1: new.append([eb, s1])
            segs = new
        out += segs
    return out


def build_walls(b, fl, rooms, foot, ffl, clear, te, ti, exclude=()):
    px, par = PX[b], BLD[b]
    fx0, fx1, fy0, fy1 = foot
    lines = {}
    for k, nm, tp, x0, x1, y0, y1 in rooms:
        for c in (y0, y1): lines.setdefault(("H", round(c, 3)), []).append([x0, x1])
        for c in (x0, x1): lines.setdefault(("V", round(c, 3)), []).append([y0, y1])
    n = 0
    for (o, c), iv in lines.items():
        iv = _merge(iv)
        iv = _subtract(iv, [(e[2], e[3]) for e in exclude if e[0] == o and abs(e[1] - c) < 1e-6])
        ext = (o == "H" and c in (fy0, fy1)) or (o == "V" and c in (fx0, fx1))
        t = te if ext else ti
        for a, bb in iv:
            if o == "H":
                bx = (a - t / 2, bb + t / 2, c - t / 2, c + t / 2)
                d = "South" if c == fy0 else "North"
            else:
                bx = (c - t / 2, c + t / 2, a - t / 2, bb + t / 2)
                d = "West" if c == fx0 else "East"
            nm = f"{px}_WALL_{fl}_EXT_{d}" if ext else f"{px}_WALL_{fl}_INT_{o}{c:+.2f}_{a:.1f}to{bb:.1f}"
            box(nm, bx[0], bx[1], bx[2], bx[3], ffl, ffl + clear, C["WALL"], par,
                "BLK_Wall_Exterior" if ext else "BLK_Wall_Interior",
                is_wall=1, bld=b, floor=fl, bbox=[bx[0], bx[1], bx[2], bx[3], ffl, ffl + clear])
            n += 1
    return n


def floor_plates(b, fl, rooms, ffl):
    px, par = PX[b], BLD[b]
    for k, nm, tp, x0, x1, y0, y1 in rooms:
        box(f"{px}_FLOORFIN_{fl}_{k}", x0, x1, y0, y1, ffl, ffl + 0.02, C["FLOOR"], par, "BLK_Floor_Finish")


def room_volumes(b, fl, rooms, ffl, clear):
    px, par = PX[b], BLD[b]
    tmap = {"living": "LIV", "kitchen": "KIT", "bath": "BATH", "bed": "BED", "other": "ROOMS"}
    for k, nm, tp, x0, x1, y0, y1 in rooms:
        ob = box(f"{px}_ROOM_{fl}_{k}", x0, x1, y0, y1, ffl, ffl + clear, C[tmap[tp]], par, None,
                 room_name=nm, room_type=tp, floor=fl, area_m2=round((x1 - x0) * (y1 - y0), 1),
                 bbox=[x0, x1, y0, y1, ffl, ffl + clear])
        ob.display_type = "WIRE"
        ob.hide_render = True
        ob.show_name = True


def cutter(b, fl, o, c, a, bb, zlo, zhi, name, ffl, depth=0.6):
    px, par = PX[b], BLD[b]
    z0 = ffl + zlo - (0.05 if zlo == 0 else 0)
    z1 = ffl + zhi
    bx = (a, bb, c - depth / 2, c + depth / 2) if o == "H" else (c - depth / 2, c + depth / 2, a, bb)
    kind = "DOOR" if zlo == 0 else "WIN"
    ob = box(f"{px}_CUT_{'Door' if zlo == 0 else 'Window'}_{fl}_{name}", bx[0], bx[1], bx[2], bx[3], z0, z1,
             C[kind], par, None, cutter=1, bld=b, floor=fl, bbox=[bx[0], bx[1], bx[2], bx[3], z0, z1])
    ob.display_type = "WIRE"
    ob.hide_render = True
    return ob


def apply_openings(b):
    walls = [o for o in bpy.data.objects if o.get("is_wall") and o.get("bld") == b]
    cuts = [o for o in bpy.data.objects if o.get("cutter") and o.get("bld") == b]
    cnt = 0
    for cu in cuts:
        cb = list(cu["bbox"])
        for w in walls:
            wb = list(w["bbox"])
            if all(min(cb[2 * i + 1], wb[2 * i + 1]) - max(cb[2 * i], wb[2 * i]) > 0.02 for i in range(3)):
                m = w.modifiers.new("Open_" + cu.name[len(PX[b]) + 5:], "BOOLEAN")
                m.operation = "DIFFERENCE"
                m.operand_type = "OBJECT"
                m.object = cu
                m.solver = "EXACT"
                cnt += 1
    for cu in cuts:
        cu.hide_set(True)
    return cnt


def stair_u(b, name, xa0, xa1, xb0, xb1, ys, ydir, zf, zl, ztop, n, tread, ld0, ld1, lx0, lx1):
    """U-stair: flight A (x xa0..xa1) from ys heading ydir up to landing zl; landing; flight B (xb0..xb1) back to ztop."""
    par = BLD[b]
    rise = (zl - zf) / n
    A, B = [], []
    for i in range(n):
        y0 = ys + ydir * i * tread; y1 = ys + ydir * (i + 1) * tread
        A.append((xa0, xa1, min(y0, y1), max(y0, y1), zf, zf + (i + 1) * rise))
        B.append((xb0, xb1, min(y0, y1), max(y0, y1), zl, zl + (i + 1) * rise))
    multibox(f"{PX[b]}_STAIR_FlightA_{name}", A, C["STAIR"], par, "BLK_Stair")
    multibox(f"{PX[b]}_STAIR_FlightB_{name}", B, C["STAIR"], par, "BLK_Stair")
    box(f"{PX[b]}_STAIR_Landing_{name}", lx0, lx1, min(ld0, ld1), max(ld0, ld1), zl - 0.2, zl, C["STAIR"], par, "BLK_Stair")


# ---------------------------------------------------------------- data
RES_GF = [
    ("Hall", "Living Hall", "living", 0, 8, 0, 7), ("Dining", "Dining", "living", 8, 13, 0, 7),
    ("Kitchen", "Kitchen", "kitchen", 13, 18.5, 0, 5), ("Utility", "Utility", "other", 13, 18.5, 5, 7),
    ("BedG1", "Bedroom G1 (Guest)", "bed", 18.5, 24, 0, 5), ("BathG1", "Bath G1", "bath", 18.5, 21.5, 5, 7),
    ("LobbyG1", "Dress Lobby G1", "other", 21.5, 24, 5, 7), ("Corridor", "Corridor", "other", 0, 24, 7, 8.5),
    ("BedG2", "Bedroom G2", "bed", 0, 6, 8.5, 14), ("StoreG", "Store", "other", 6, 9, 8.5, 11.5),
    ("BathG2", "Bath G2", "bath", 6, 9, 11.5, 14), ("Foyer", "Entrance Foyer", "living", 9, 15, 8.5, 14),
    ("Stair", "Stair Hall", "other", 15, 19.5, 8.5, 14), ("Study", "Study", "other", 19.5, 24, 8.5, 14),
]
RES_FF = [
    ("Master", "Master Bedroom", "bed", 0, 7, 0, 5), ("BathM", "Master Bath", "bath", 0, 3.5, 5, 7),
    ("DressM", "Master Dressing", "other", 3.5, 7, 5, 7), ("Bed3", "Bedroom F3", "bed", 7, 13, 0, 5),
    ("Bath3", "Bath F3", "bath", 7, 10, 5, 7), ("Lobby3", "Lobby F3", "other", 10, 13, 5, 7),
    ("Bed4", "Bedroom F4", "bed", 13, 18.5, 0, 5), ("Bath4", "Bath F4", "bath", 13, 16, 5, 7),
    ("Lobby4", "Lobby F4", "other", 16, 18.5, 5, 7), ("Lounge", "Family Lounge", "living", 18.5, 24, 0, 7),
    ("Corridor", "Corridor", "other", 0, 24, 7, 8.5), ("Office", "Home Office", "other", 0, 9, 8.5, 14),
    ("Landing", "Landing", "living", 9, 15, 8.5, 14), ("Stair", "Stair Hall", "other", 15, 19.5, 8.5, 14),
    ("Utility2", "Utility Room", "other", 19.5, 24, 8.5, 14),
]
# (orient, line coord, a, b, zlo, zhi, name)  z offsets are relative to finished floor level
RES_OPEN_GF = [
    ("H", 0, 2.2, 5.8, 0, 2.3, "SliderHall"), ("H", 0, 9.5, 12.0, 0, 2.3, "SliderDining"),
    ("H", 0, 14.2, 17.0, 1.0, 2.2, "Kitchen"), ("H", 0, 19.5, 22.5, 0, 2.3, "SliderBedG1"),
    ("H", 14, 11.1, 12.9, 0, 2.4, "MainEntrance"), ("H", 14, 2.0, 4.0, 1.0, 2.2, "BedG2"),
    ("H", 14, 7.2, 8.2, 1.5, 2.2, "BathG2"), ("H", 14, 20.5, 23.0, 1.0, 2.2, "Study"),
    ("H", 14, 16.2, 18.2, 0.9, 2.6, "Stair"),
    ("V", 0, 1.5, 5.5, 0.9, 2.3, "Hall"), ("V", 0, 10.0, 12.5, 1.0, 2.2, "BedG2"),
    ("V", 24, 1.5, 3.5, 1.0, 2.2, "BedG1"), ("V", 24, 10.5, 12.5, 1.0, 2.2, "Study"),
    ("H", 7, 3.2, 4.8, 0, 2.4, "HallCorr"), ("H", 7, 10.2, 11.2, 0, 2.1, "DiningCorr"),
    ("H", 7, 14.55, 15.45, 0, 2.1, "UtilCorr"), ("H", 7, 22.3, 23.2, 0, 2.1, "LobbyG1Corr"),
    ("H", 5, 14.5, 15.5, 0, 2.1, "KitchenUtil"), ("H", 5, 22.3, 23.2, 0, 2.1, "BedG1Lobby"),
    ("H", 5, 19.3, 20.1, 0, 2.1, "BedG1Bath"), ("V", 13, 2.0, 3.0, 0, 2.1, "KitchenDining"),
    ("H", 8.5, 2.55, 3.45, 0, 2.1, "BedG2"), ("H", 8.5, 7.05, 7.95, 0, 2.1, "Store"),
    ("H", 8.5, 10.75, 13.25, 0, 2.4, "FoyerOpen"), ("H", 8.5, 15.4, 16.6, 0, 2.4, "StairOpen"),
    ("H", 8.5, 21.3, 22.2, 0, 2.1, "Study"), ("V", 6, 12.35, 13.15, 0, 2.1, "BedG2Bath"),
]
RES_OPEN_FF = [
    ("H", 0, 2.0, 5.0, 0, 2.3, "SliderMaster"), ("H", 0, 8.5, 11.5, 0, 2.3, "SliderBed3"),
    ("H", 0, 14.2, 17.2, 0, 2.3, "SliderBed4"), ("H", 0, 19.5, 23.0, 0, 2.3, "SliderLounge"),
    ("H", 14, 2.0, 6.0, 1.0, 2.2, "Office"), ("H", 14, 11.0, 13.0, 1.0, 2.4, "Landing"),
    ("H", 14, 16.2, 18.2, 0.9, 2.6, "Stair"), ("H", 14, 20.5, 23.0, 1.0, 2.2, "Utility2"),
    ("V", 0, 1.5, 3.5, 1.0, 2.2, "Master"), ("V", 0, 10.0, 12.5, 1.0, 2.2, "Office"),
    ("V", 24, 2.0, 5.0, 1.0, 2.2, "Lounge"),
    ("H", 7, 4.8, 5.7, 0, 2.1, "DressMCorr"), ("H", 7, 11.05, 11.95, 0, 2.1, "Lobby3Corr"),
    ("H", 7, 16.8, 17.7, 0, 2.1, "Lobby4Corr"), ("H", 7, 20.7, 21.8, 0, 2.1, "LoungeCorr"),
    ("H", 5, 4.8, 5.7, 0, 2.1, "MasterDress"), ("H", 5, 1.0, 1.9, 0, 2.1, "MasterBath"),
    ("H", 5, 11.05, 11.95, 0, 2.1, "Bed3Lobby"), ("H", 5, 8.0, 8.9, 0, 2.1, "Bed3Bath"),
    ("H", 5, 16.8, 17.7, 0, 2.1, "Bed4Lobby"), ("H", 5, 14.0, 14.9, 0, 2.1, "Bed4Bath"),
    ("H", 8.5, 4.05, 4.95, 0, 2.1, "Office"), ("H", 8.5, 10.75, 13.25, 0, 2.4, "LandingOpen"),
    ("H", 8.5, 15.4, 16.6, 0, 2.4, "StairOpen"), ("H", 8.5, 21.3, 22.2, 0, 2.1, "Utility2"),
]

CLUB_GF = [("Gym", "Gymnasium", "other", 32, 48, -26, -16), ("Lobby", "Reception Lobby", "living", 32, 40, -16, -10),
           ("Changing", "Changing & Toilets", "bath", 40, 48, -16, -10)]
CLUB_FF = [("Studio", "Aerobics Studio", "other", 32, 42, -26, -16), ("Multi", "Multipurpose / Yoga", "other", 42, 48, -26, -16),
           ("Games", "Games Room (Snooker)", "living", 32, 48, -16, -10)]
CLUB_OPEN_GF = [
    ("V", 32, -25.2, -17.0, 0.3, 3.3, "GymGlazing"), ("V", 32, -14.5, -12.0, 0, 2.4, "MainEntrance"),
    ("H", -16, 38.0, 39.2, 0, 2.4, "LobbyGym"), ("V", 40, -13.9, -12.9, 0, 2.1, "LobbyChanging"),
    ("H", -26, 34.0, 46.0, 2.4, 3.4, "GymRibbon"), ("V", 48, -24.0, -18.0, 1.4, 3.0, "GymEast"),
    ("H", -10, 36.0, 38.0, 1.0, 2.4, "Lobby"), ("H", -10, 43.0, 45.0, 1.8, 2.4, "Changing"),
]
CLUB_OPEN_FF = [
    ("V", 32, -25.3, -16.8, 0.3, 3.4, "StudioGlazing"), ("V", 32, -15.2, -10.8, 0.3, 3.0, "GamesGlazing"),
    ("H", -16, 38.0, 39.2, 0, 2.3, "StudioGames"), ("V", 42, -20.9, -19.7, 0, 2.3, "StudioMulti"),
    ("H", -26, 34.0, 46.0, 1.2, 3.3, "StudioRibbon"), ("H", -10, 40.0, 46.0, 1.0, 2.6, "GamesNorth"),
]
PAV_GF = [("Hall", "Pavilion Main Hall", "living", -34, -26, -32, -24), ("Annex", "Pavilion Annex", "other", -26, -22, -32, -24)]
PAV_OPEN = [
    ("H", -24, -29.2, -27.6, 0, 2.3, "MainDoor"), ("H", -24, -33.3, -30.5, 0.9, 2.4, "HallWin"),
    ("H", -24, -25.3, -22.7, 0.9, 2.4, "AnnexWin"), ("V", -34, -29.5, -26.5, 0.9, 2.4, "HallWest"),
    ("H", -32, -31.0, -28.5, 0.9, 2.4, "HallSouth"), ("V", -26, -28.0, -27.1, 0, 2.1, "HallAnnex"),
]


def _open(b, fl, lst, ffl):
    for o, c, a, bb, zl, zh, nm in lst:
        cutter(b, fl, o, c, a, bb, zl, zh, nm, ffl)


def step_residence():
    _colls()
    par = BLD["RES"]
    foot = (0, 24, 0, 14)
    h = 0.115
    box("Res_FOUNDATION_Plinth", -h, 24 + h, -h, 14 + h, -0.6, 0.3, C["EXT"], par, "BLK_Slab_Concrete")
    box("Res_FLOOR_GF_StructuralSlab", -h, 24 + h, -h, 14 + h, 0.3, 0.6, C["FLOOR"], par, "BLK_Slab_Concrete")
    ff = box("Res_FLOOR_FF_StructuralSlab", -h, 24 + h, -h, 14 + h, 3.6, 3.8, C["FLOOR"], par, "BLK_Slab_Concrete")
    void = box("Res_CUT_StairVoid_FF", 15.2, 19.2, 9.05, 13.9, 3.5, 3.9, C["STAIR"], par)
    void.display_type = "WIRE"; void.hide_render = True
    m = ff.modifiers.new("StairVoid", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = void; m.solver = "EXACT"
    void.hide_set(True)
    box("Res_ROOF_Slab", -h, 24 + h, -h, 14 + h, 6.8, 7.0, C["ROOF"], par, "BLK_Slab_Concrete")
    p = 0.15; ph = 0.9
    box("Res_ROOF_Parapet_South", -0.23, 24.23, -0.23, -0.23 + p, 7.0, 7.0 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Res_ROOF_Parapet_North", -0.23, 24.23, 14.23 - p, 14.23, 7.0, 7.0 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Res_ROOF_Parapet_West", -0.23, -0.23 + p, -0.23, 14.23, 7.0, 7.0 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Res_ROOF_Parapet_East", 24.23 - p, 24.23, -0.23, 14.23, 7.0, 7.0 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    ex = [("V", 8.0, 0.0, 7.0)]
    n1 = build_walls("RES", "GF", RES_GF, foot, 0.6, 3.0, 0.23, 0.115, ex)
    n2 = build_walls("RES", "FF", RES_FF, foot, 3.8, 3.0, 0.23, 0.115)
    for fl, rooms, ffl in (("GF", RES_GF, 0.6), ("FF", RES_FF, 3.8)):
        floor_plates("RES", fl, rooms, ffl)
        room_volumes("RES", fl, rooms, ffl, 3.0)
    # open-plan hall/dining column pair
    for i, y in enumerate((2.0, 5.0)):
        box(f"Res_COLUMN_GF_HallDining_{i + 1}", 7.85, 8.15, y - 0.15, y + 0.15, 0.6, 3.6, C["EXT"], par, "BLK_Column")
    _open("RES", "GF", RES_OPEN_GF, 0.6)
    _open("RES", "FF", RES_OPEN_FF, 3.8)
    nc = apply_openings("RES")
    # stairs
    stair_u("RES", "GF_FF", 15.3, 16.5, 17.7, 18.9, 9.0, 1, 0.6, 2.2, 3.8, 9, 0.28, 11.52, 13.6, 15.3, 18.9)
    # GF veranda + FF balcony + columns + steps (garden / south side)
    box("Res_VERANDA_GF_Slab", -h, 24 + h, -2.0, -h, 0.3, 0.6, C["EXT"], par, "BLK_Slab_Concrete")
    box("Res_BALCONY_FF_Slab", -h, 24 + h, -2.0, -h, 3.6, 3.8, C["EXT"], par, "BLK_Slab_Concrete")
    for i, x in enumerate((0.15, 4, 8, 12, 16, 20, 23.85)):
        box(f"Res_COLUMN_Veranda_{i + 1}", x - 0.15, x + 0.15, -1.95, -1.65, 0.6, 3.6, C["EXT"], par, "BLK_Column")
    box("Res_STEP_Garden_1", 9, 15, -2.45, -2.0, 0.0, 0.4, C["EXT"], par, "BLK_Stair")
    box("Res_STEP_Garden_2", 9, 15, -2.9, -2.45, 0.0, 0.2, C["EXT"], par, "BLK_Stair")
    # north entrance porch
    box("Res_PORCH_Slab", 10, 14, 14.115, 16.5, 0.3, 0.6, C["EXT"], par, "BLK_Slab_Concrete")
    box("Res_PORCH_Canopy", 9.8, 14.2, 14.115, 16.7, 3.4, 3.6, C["EXT"], par, "BLK_Slab_Concrete")
    for i, x in enumerate((10.2, 13.8)):
        box(f"Res_COLUMN_Porch_{i + 1}", x - 0.15, x + 0.15, 16.3, 16.6, 0.6, 3.4, C["EXT"], par, "BLK_Column")
    box("Res_STEP_Porch_1", 10, 14, 16.5, 16.8, 0.0, 0.4, C["EXT"], par, "BLK_Stair")
    box("Res_STEP_Porch_2", 10, 14, 16.8, 17.1, 0.0, 0.2, C["EXT"], par, "BLK_Stair")
    return f"residence walls GF={n1} FF={n2} boolean links={nc}"


def step_clubhouse_pavilion():
    _colls()
    par = BLD["CLUB"]
    foot = (32, 48, -26, -10)
    h = 0.125
    box("Club_FOUNDATION_Plinth", 32 - h, 48 + h, -26 - h, -10 + h, -0.6, 0.3, C["EXT"], par, "BLK_Slab_Concrete")
    box("Club_FLOOR_GF_StructuralSlab", 32 - h, 48 + h, -26 - h, -10 + h, 0.3, 0.6, C["FLOOR"], par, "BLK_Slab_Concrete")
    ff = box("Club_FLOOR_FF_StructuralSlab", 32 - h, 48 + h, -26 - h, -10 + h, 4.2, 4.5, C["FLOOR"], par, "BLK_Slab_Concrete")
    void = box("Club_CUT_StairVoid_FF", 32.9, 36.5, -15.55, -10.3, 4.1, 4.6, C["STAIR"], par)
    void.display_type = "WIRE"; void.hide_render = True
    m = ff.modifiers.new("StairVoid", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = void; m.solver = "EXACT"
    void.hide_set(True)
    box("Club_ROOF_Slab", 32 - h, 48 + h, -26 - h, -10 + h, 8.1, 8.4, C["ROOF"], par, "BLK_Slab_Concrete")
    p = 0.2; ph = 0.8
    box("Club_ROOF_Parapet_South", 32 - h, 48 + h, -26 - h, -26 - h + p, 8.4, 8.4 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Club_ROOF_Parapet_North", 32 - h, 48 + h, -10 + h - p, -10 + h, 8.4, 8.4 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Club_ROOF_Parapet_West", 32 - h, 32 - h + p, -26 - h, -10 + h, 8.4, 8.4 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    box("Club_ROOF_Parapet_East", 48 + h - p, 48 + h, -26 - h, -10 + h, 8.4, 8.4 + ph, C["ROOF"], par, "BLK_Wall_Exterior")
    n1 = build_walls("CLUB", "GF", CLUB_GF, foot, 0.6, 3.6, 0.25, 0.115)
    n2 = build_walls("CLUB", "FF", CLUB_FF, foot, 4.5, 3.6, 0.25, 0.115)
    for fl, rooms, ffl in (("GF", CLUB_GF, 0.6), ("FF", CLUB_FF, 4.5)):
        floor_plates("CLUB", fl, rooms, ffl)
        room_volumes("CLUB", fl, rooms, ffl, 3.6)
    _open("CLUB", "GF", CLUB_OPEN_GF, 0.6)
    _open("CLUB", "FF", CLUB_OPEN_FF, 4.5)
    nc = apply_openings("CLUB")
    stair_u("CLUB", "GF_FF", 33.0, 34.4, 35.0, 36.4, -15.6, 1, 0.6, 2.55, 4.5, 11, 0.28, -12.52, -10.3, 33.0, 36.4)
    # pavilion (hip-roof bungalow)
    par = BLD["PAV"]
    box("Pav_FOUNDATION_Plinth", -34.2, -21.8, -32.2, -21.8, -0.6, 0.3, C["EXT"], par, "BLK_Slab_Concrete")
    box("Pav_FLOOR_GF_StructuralSlab", -34.2, -21.8, -32.2, -21.8, 0.3, 0.6, C["FLOOR"], par, "BLK_Slab_Concrete")
    n3 = build_walls("PAV", "GF", PAV_GF, (-34, -22, -32, -24), 0.6, 3.0, 0.23, 0.115)
    floor_plates("PAV", "GF", PAV_GF, 0.6)
    room_volumes("PAV", "GF", PAV_GF, 0.6, 3.0)
    _open("PAV", "GF", PAV_OPEN, 0.6)
    nc2 = apply_openings("PAV")
    for i, x in enumerate((-33.6, -30.0, -26.0, -22.4)):
        box(f"Pav_POST_Veranda_{i + 1}", x - 0.1, x + 0.1, -22.1, -21.9, 0.6, 3.6, C["EXT"], par, "BLK_Column")
    hip_roof("Pav_ROOF_HipMass", -35, -21, -33, -20.9, 3.6, 2.6, C["ROOF"], par, "BLK_Roof")
    return f"clubhouse walls {n1}+{n2} links {nc}; pavilion walls {n3} links {nc2}"


def step_site():
    _colls()
    ground = box("SITE_Ground_Lawn", -45, 75, -45, 55, -0.5, 0.0, C["SITE"], None, "BLK_Ground_Lawn")
    pool_pts = [(6, -26), (30, -26), (30, -19), (25, -14), (6, -14)]
    cut = prism("POOL_Basin_Cutter", pool_pts, -1.4, 0.5, C["POOL"], None, "BLK_Pool_Water")
    cut.display_type = "WIRE"; cut.hide_render = True
    deck = box("SITE_Pool_Deck", 2, 32, -29, -11, 0.0, 0.06, C["SITE"], None, "BLK_Pool_Deck")
    for ob in (ground, deck):
        m = ob.modifiers.new("PoolCut", "BOOLEAN")
        m.operation = "DIFFERENCE"; m.object = cut; m.solver = "EXACT"
        try:
            m.material_mode = "TRANSFER"
        except Exception:
            pass
    cut.hide_set(True)
    prism("POOL_Water_Surface", pool_pts, -0.14, -0.12, C["POOL"], None, "BLK_Pool_Water")
    box("SITE_Drive_Entrance", 8, 16, 17.1, 42, 0.0, 0.04, C["SITE"], None, "BLK_Path")
    box("SITE_Path_Garden_A", -28.3, -26.7, -21.8, -4.2, 0.0, 0.04, C["LAND"], None, "BLK_Path")
    box("SITE_Path_Garden_B", -28.3, 12.8, -5.8, -4.2, 0.0, 0.04, C["LAND"], None, "BLK_Path")
    box("SITE_Path_Garden_C", 11.2, 12.8, -5.8, -2.9, 0.0, 0.04, C["LAND"], None, "BLK_Path")
    box("SITE_Path_PoolLink", 11.2, 12.8, -11.0, -5.8, 0.0, 0.04, C["LAND"], None, "BLK_Path")
    def ell(cx, cy, rx, ry, n=28):
        return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    prism("LAND_Laterite_Bed_A", ell(-12, -16, 9, 3.8), 0.0, 0.12, C["LAND"], None, "BLK_Laterite")
    prism("LAND_Laterite_Bed_B", ell(-10, 22, 7, 3.2), 0.0, 0.12, C["LAND"], None, "BLK_Laterite")
    prism("LAND_Laterite_Bed_C", ell(30, 8, 6, 3.0), 0.0, 0.12, C["LAND"], None, "BLK_Laterite")
    return "site ok"


def _cam(name, loc, target, lens=24, ortho=False, scale=100):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens; cd.clip_end = 600
    if ortho:
        cd.type = "ORTHO"; cd.ortho_scale = scale
    ob = bpy.data.objects.new(name, cd)
    C["CAM"].objects.link(ob)
    ob.location = loc
    if not ortho:
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


def step_guides(meta_json):
    _colls()
    _cam("CAM_Aerial_SW", (-45, -90, 60), (14, -5, 3), 22)
    _cam("CAM_South_Garden", (12, -38, 6), (12, 0, 4), 20)
    _cam("CAM_North_Entrance", (12, 38, 4), (12, 14, 3.5), 20)
    _cam("CAM_Pool_Clubhouse", (8, -50, 9), (36, -18, 3.5), 22)
    _cam("CAM_Pavilion", (-10, -5, 4), (-28, -26, 2.5), 24)
    _cam("CAM_Plan_Top", (14, -4, 150), (14, -4, 0), 24, True, 125)
    ld = bpy.data.lights.new("LIGHT_Sun_Daylight", "SUN")
    ld.energy = 3.0
    so = bpy.data.objects.new("LIGHT_Sun_Daylight", ld)
    C["LIGHT"].objects.link(so)
    so.location = (0, 0, 60)
    so.rotation_euler = (math.radians(50), 0, math.radians(35))
    e = bpy.data.objects.new("GUIDE_North_Arrow", None)
    e.empty_display_type = "SINGLE_ARROW"; e.empty_display_size = 8
    e.location = (-40, 40, 0); e.rotation_euler = (-math.pi / 2, 0, 0)
    C["REF"].objects.link(e)
    o = bpy.data.objects.new("GUIDE_Origin_SW_Corner_Residence", None)
    o.empty_display_type = "ARROWS"; o.empty_display_size = 3
    C["REF"].objects.link(o)
    t = bpy.data.texts.new("PROJECT_METADATA.json")
    t.write(meta_json)
    sc = bpy.context.scene
    sc.camera = bpy.data.objects["CAM_Aerial_SW"]
    sc["project"] = "3D-5BHK-RA-1-RW"
    sc["round_completed"] = 1
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            sp = area.spaces.active
            sp.shading.type = "SOLID"
            sp.shading.color_type = "MATERIAL"
            sp.region_3d.view_perspective = "CAMERA"
            sp.clip_end = 600
    return "guides ok"


def view(cam_name):
    sc = bpy.context.scene
    sc.camera = bpy.data.objects[cam_name]
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            sp = area.spaces.active
            sp.region_3d.view_perspective = "CAMERA"
    return cam_name
