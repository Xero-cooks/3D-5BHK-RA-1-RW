"""Round 4 - material assignment (module r4a): remap R3 palette, per-room floors, per-face wall paint, BLK_* upgrade."""
import bpy, sys, re
from mathutils import Vector
b = sys.modules['r4b']

def get(n): return bpy.data.materials.get(n)

def _setmat(o, old, new):
    mt = get(new)
    if not mt: return 0
    k = 0
    for s in o.material_slots:
        if s.material and s.material.name == old:
            s.material = mt; k += 1
    return k

def remap_r3():
    n = 0
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        for s in o.material_slots:
            if s.material and s.material.name in b.MAP_R3:
                mt = get(b.MAP_R3[s.material.name])
                if mt: s.material = mt; n += 1
    return n

FLOOR = {  # room suffix regex -> material
 r'Gym': 'R4_Rubber_Gym', r'Changing': 'R4_Floor_Tile_Bath', r'Studio|Games|Multi': 'R4_Floor_Laminate_Oak_Honey', r'Annex': 'R4_Floor_Vitrified_Ivory',
 r'Hall|Dining|Foyer': 'R4_Floor_Vitrified_Cream',
 r'Corridor|Lobby|Stair|Landing|Lounge': 'R4_Floor_Vitrified_Ivory',
 r'Kitchen': 'R4_Floor_Tile_Kitchen',
 r'Bath': 'R4_Floor_Tile_Bath',
 r'Utility|Store': 'R4_Floor_Tile_Utility',
 r'Study|Office': 'R4_Floor_Laminate_Oak_Honey',
 r'Bed|Master|Dress': 'R4_Floor_Laminate_Oak_Grey',
}

def floors():
    n = 0
    for o in bpy.data.objects:
        if o.type == 'MESH' and 'FLOORFIN_' in o.name:
            room = o.name.split('_', 3)[-1]
            for pat, mat in FLOOR.items():
                if re.search(pat, room):
                    n += _setmat(o, 'BLK_Floor_Finish', mat); break
    return n

def blk():
    rules = []
    def R(old, test, new): rules.append((old, test, new))
    R('BLK_Ceiling', lambda n: True, 'R4_Paint_Ceiling'); R('BLK_Cove', lambda n: True, 'R4_Paint_Ceiling')
    R('BLK_Column', lambda n: any(k in n for k in ('BAND', 'CORNICE', 'COLBASE', 'COLCAP', 'Fascia')), 'R4_Plaster_Trim_White')
    R('BLK_Column', lambda n: True, 'R4_Plaster_Exterior')
    R('BLK_Stone_Sill', lambda n: 'Plinth' in n, 'R4_Stone_Plinth'); R('BLK_Stone_Sill', lambda n: True, 'R4_Stone_Sill')
    R('BLK_Slab_Concrete', lambda n: 'ROOF_Slab' in n, 'R4_Terrace_Tile_Grey')
    R('BLK_Slab_Concrete', lambda n: any(k in n for k in ('Coping', 'Canopy', 'BEAM', 'Mumty')), 'R4_Plaster_Trim_White')
    R('BLK_Slab_Concrete', lambda n: 'FOUNDATION' in n, 'R4_Plaster_Plinth')
    R('BLK_Slab_Concrete', lambda n: True, 'R4_Plaster_Exterior')
    R('BLK_Door_Wood', lambda n: 'MainEntrance' in n and 'Leaf' in n, 'R4_Door_Teak_Main'); R('BLK_Door_Wood', lambda n: True, 'R4_Door_Walnut')
    R('BLK_Frame', lambda n: True, 'R4_Frame_Aluminium_White'); R('BLK_Glass', lambda n: True, 'R4_Glass_Clear')
    R('BLK_Railing', lambda n: 'Balusters' in n or 'Guard' in n, 'R4_Metal_Black_Powder'); R('BLK_Railing', lambda n: True, 'R4_Wood_Handrail')
    R('BLK_Stair', lambda n: 'STEP_' in n, 'R4_Granite_Grey'); R('BLK_Stair', lambda n: True, 'R4_Stair_Marble_Beige')
    R('BLK_Path', lambda n: 'Drive' in n, 'R4_Paving_Interlock_Grey'); R('BLK_Path', lambda n: True, 'R4_Paving_Sandstone')
    R('BLK_Niche_Panel', lambda n: 'TVPanel' in n, 'R4_Panel_Stone_Cladding'); R('BLK_Niche_Panel', lambda n: 'Headboard' in n, 'R4_Fabric_Headboard')
    R('BLK_Niche_Panel', lambda n: True, 'R4_Laminate_Cream')
    R('BLK_Ground_Lawn', lambda n: True, 'R4_Grass_Lawn'); R('BLK_Laterite', lambda n: True, 'R4_Soil_Laterite')
    R('BLK_Wall_Exterior', lambda n: 'ROOF_Parapet' in n, 'R4_Plaster_Exterior')
    R('BLK_Pool_Deck', lambda n: True, 'R4_Pool_Deck_Travertine'); R('BLK_Pool_Water', lambda n: 'Water' in n, 'R4_Water_Pool')
    R('BLK_Roof', lambda n: True, 'R4_Roof_Tile_Terracotta')
    cnt = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.name.startswith(('Res_', 'SITE_', 'LAND_', 'Club_', 'Pav_', 'POOL_')): continue
        for s in o.material_slots:
            if not s.material or not s.material.name.startswith('BLK_'): continue
            for old, test, new in rules:
                if old == s.material.name and test(o.name):
                    mt = get(new)
                    if mt: s.material = mt; cnt += 1
                    break
    return cnt

def wallpaint(key):
    nm = key.split('_', 1)[1]
    if 'Bath' in nm or 'Changing' in nm: return 'R4_Wall_Tile_Bath'
    if re.search(r'Master|Dress|Bedroom G1', nm): return 'R4_Paint_Sand'
    if re.search(r'Bedroom G2|Bedroom F4', nm): return 'R4_Paint_Taupe'
    if re.search(r'Dining|Kitchen|Study|Lounge', nm): return 'R4_Paint_Cream'
    if re.search(r'Utility|Store|Office', nm): return 'R4_Paint_Stone'
    return 'R4_Paint_Ivory'

def room_rects():
    out = []
    for o in bpy.data.objects:
        if o.get('room_type') and o.parent and o.parent.name.startswith('BLD_'):
            bb = o['bbox']; out.append((f"{o['floor']}_{o['room_name']}", o['floor'], bb[0], bb[1], bb[2], bb[3]))
    return out

def split_walls():
    """Cut long wall faces at every room boundary so each segment can take its own room finish."""
    import bmesh
    from mathutils import Vector
    rects = room_rects(); n = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or '_WALL_' not in o.name or not o.name.startswith(('Res_', 'Club_', 'Pav_')): continue
        if 'Parapet' in o.name or o.get('r4_split'): continue
        fl = 'GF' if '_GF_' in o.name else 'FF' if ('_FF_' in o.name or 'Mumty' in o.name) else None
        if not fl: continue
        mw = o.matrix_world; inv = mw.inverted(); m3t = inv.to_3x3().transposed()
        bb = [mw @ Vector(c) for c in o.bound_box]
        x0, x1 = min(b.x for b in bb), max(b.x for b in bb); y0, y1 = min(b.y for b in bb), max(b.y for b in bb)
        cuts = []
        if x1 - x0 > 0.6:
            for c in sorted({v for k, f, a, b, c1, d in rects if f == fl for v in (a, b)}):
                if x0 + 0.02 < c < x1 - 0.02: cuts.append((Vector((c, 0, 0)), Vector((1, 0, 0))))
        if y1 - y0 > 0.6:
            for c in sorted({v for k, f, a, b, c1, d in rects if f == fl for v in (c1, d)}):
                if y0 + 0.02 < c < y1 - 0.02: cuts.append((Vector((0, c, 0)), Vector((0, 1, 0))))
        o['r4_split'] = 1
        if not cuts: continue
        bm = bmesh.new(); bm.from_mesh(o.data)
        for co, no in cuts:
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=inv @ co, plane_no=(m3t @ no).normalized())
        bm.to_mesh(o.data); bm.free(); o.data.update(); n += 1
    return n

def walls():
    rooms = room_rects(); touched = 0; unmatched = set()
    ext = get('R4_Plaster_Exterior')
    for o in bpy.data.objects:
        if o.type != 'MESH' or '_WALL_' not in o.name or not o.name.startswith(('Res_', 'Club_', 'Pav_')): continue
        if 'Parapet' in o.name: continue
        fl = 'GF' if '_GF_' in o.name else 'FF' if ('_FF_' in o.name or 'Mumty' in o.name) else None
        if not fl: continue
        me = o.data; mw = o.matrix_world; m3 = mw.to_3x3()
        slots = [ext]; idx = {ext.name: 0}; asg = []
        for p in me.polygons:
            n = (m3 @ p.normal).normalized()
            if abs(n.z) > 0.7: asg.append(0); continue
            q = mw @ p.center + n * 0.22
            hit = None
            for key, f, x0, x1, y0, y1 in rooms:
                if f == fl and x0 <= q.x <= x1 and y0 <= q.y <= y1:
                    hit = key; break
            if not hit: asg.append(0); continue
            mn = wallpaint(hit)
            if not mn: unmatched.add(hit); asg.append(0); continue
            if mn not in idx:
                idx[mn] = len(slots); slots.append(get(mn))
            asg.append(idx[mn])
        me.materials.clear()
        for mt in slots: me.materials.append(mt)
        me.polygons.foreach_set('material_index', asg)
        me.update(); touched += 1
    return touched, sorted(unmatched)

def specials():
    n = 0
    lea = {'Hall_Sofa': 'R4_Leather_Charcoal', 'Master_Sofa': 'R4_Leather_Tan', 'Lounge_Sofa': 'R4_Leather_Brown', 'Study_Sofa': 'R4_Leather_Tan', 'Office_Sofa': 'R4_Leather_Charcoal'}
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        for k, mn in lea.items():
            if k in o.name and 'Curtain' not in o.name:
                for sl in o.material_slots:
                    if sl.material and sl.material.name in ('R4_Fabric_grey', 'R4_Fabric_charcoal', 'R4_Fabric_taupe', 'R4_Fabric_brown'):
                        sl.material = get(mn); n += 1
        if 'CEILING' in o.name and 'Bath' in o.name and o.name.startswith('Res_'):
            for sl in o.material_slots:
                if sl.material: sl.material = get('R4_PVC_Panel_White'); n += 1
    return n

def purge_old():
    k = 0
    for mt in list(bpy.data.materials):
        if mt.name.startswith(('R3_', 'BLK_')) and mt.users == 0 and mt.name not in ('BLK_Cutter', 'BLK_Room'):
            bpy.data.materials.remove(mt); k += 1
    return k

def run():
    r = {'remap': remap_r3(), 'floors': floors(), 'blk': blk()}
    r['split'] = split_walls(); r['walls'] = walls(); r['special'] = specials(); r['purged'] = purge_old()
    left = {}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith(('Res_', 'SITE_', 'LAND_', 'Club_', 'Pav_', 'POOL_')):
            for s in o.material_slots:
                if s.material and s.material.name.startswith(('BLK_', 'R3_')): left[s.material.name] = left.get(s.material.name, 0) + 1
    r['left'] = left
    return r
