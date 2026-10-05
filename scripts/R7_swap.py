# R7_swap.py - replace placeholder furniture groups with imported hi-res models
import bpy, math
from mathutils import Vector, Matrix

def wbbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx

def group_objs(base):
    return [o for o in bpy.data.objects if o.type == 'MESH' and (o.name == base or o.name.startswith(base + '.'))]

def old_info(base):
    L = group_objs(base)
    mn, mx = wbbox(L)
    d = mx - mn; cen = (mn + mx) / 2
    # long axis / depth axis
    ax_long = 0 if d.x >= d.y else 1
    ax_short = 1 - ax_long
    # back detection: centroid of the highest vertices
    zt = mx.z - 0.12
    acc = 0.0; n = 0
    for o in L:
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            if w.z >= zt:
                acc += w[ax_short] - cen[ax_short]; n += 1
    off = acc / n if n else 0.0
    return dict(objs=L, mn=mn, mx=mx, d=d, cen=cen, ax_long=ax_long, ax_short=ax_short, off=off)

def place(template_names, base, coll, fit='width', front=None, kill_old=True, yaw_extra=0.0, scale_mul=1.0, tag=None, clamp=(0.8, 1.3), face_pt=None, yaw=None, wdim='x', wold=None):
    """duplicate imported template objects (names) onto the footprint of old group `base`.
       model convention: width along +X, front faces -Y, floor at z=0 (bbox min)."""
    info = old_info(base)
    T = [bpy.data.objects[n] for n in template_names]
    tmn, tmx = wbbox(T); tc = (tmn + tmx) / 2; td = tmx - tmn
    al, a_s = info['ax_long'], info['ax_short']
    # front direction
    fv = Vector((0, 0, 0))
    if front is not None: fv = Vector(front)
    elif face_pt is not None:
        fv = Vector((face_pt[0] - info['cen'].x, face_pt[1] - info['cen'].y, 0))
        if abs(fv.x) > abs(fv.y): fv = Vector((math.copysign(1, fv.x), 0, 0))
        else: fv = Vector((0, math.copysign(1, fv.y), 0))
    else:
        s = -1.0 if info['off'] > 0 else 1.0
        fv = Vector((s, 0, 0)) if a_s == 0 else Vector((0, s, 0))
    if yaw is None: yaw = math.atan2(fv.y, fv.x) + math.pi / 2 + yaw_extra
    # model width aligned to the old long axis
    width_old = info['d'][al] if (fv.x == 0) == (al == 0) else info['d'][a_s]
    # width axis in world: perpendicular to front
    width_old = info['d'][0] if abs(fv.y) > 0.5 else info['d'][1]
    if wold is not None: width_old = wold
    s = width_old / (td.x if wdim == 'x' else td.y) * scale_mul
    s = max(clamp[0], min(clamp[1], s))
    E = bpy.data.objects.new('SW_' + (tag or base), None); coll.objects.link(E)
    R = Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Scale(s, 4)
    # position so bbox centre xy and floor z match
    off_local = Vector((-tc.x, -tc.y, -tmn.z))
    pos = Vector((info['cen'].x, info['cen'].y, info['mn'].z)) + R.to_3x3() @ off_local * 1.0
    pos.x = info['cen'].x + (R.to_3x3() @ Vector((-tc.x, -tc.y, 0))).x
    pos.y = info['cen'].y + (R.to_3x3() @ Vector((-tc.x, -tc.y, 0))).y
    pos.z = info['mn'].z - tmn.z * s
    E.matrix_world = Matrix.Translation(pos) @ R
    for t in T:
        c = bpy.data.objects.new(t.name.split('.')[0] + '_' + (tag or base), t.data)
        coll.objects.link(c)
        c.parent = E
        c.matrix_parent_inverse = Matrix.Identity(4)
        c.matrix_local = t.matrix_world.copy()
        for slot, ms in zip(c.material_slots, t.material_slots):
            pass
        c.hide_render = False; c.hide_viewport = False
    if kill_old:
        for o in info['objs']:
            o.hide_render = True; o.hide_viewport = True
    return E, s, fv


def place_table(tn, base, coll, tag=None):
    info = old_info(base)
    yaw = 0.0 if info['d'].y >= info['d'].x else math.pi / 2
    return place([tn], base, coll, yaw=yaw, wdim='y', wold=max(info['d'].x, info['d'].y), tag=tag, clamp=(0.75, 1.4))

def batch(jobs, doneflag):
    import bpy
    Q = list(jobs); LOG = []
    def tick():
        if not Q:
            open(bpy.app.tempdir + doneflag, 'w').write(repr(LOG)); return None
        kind, base, arg = Q.pop(0)
        try:
            L = group_objs(base)
            if not L: LOG.append((base, 'nogroup')); return 0.3
            coll = L[0].users_collection[0]
            if kind == 'sofa':
                E, s, fv = place(arg, base, coll, tag=base)
            elif kind == 'chair':
                E, s, fv = place(arg[0], base, coll, front=arg[1], tag=base, clamp=(0.8, 1.3))
            elif kind == 'table':
                E, s, fv = place_table(arg, base, coll, tag=base)
            LOG.append((base, round(s, 2), tuple(fv)))
        except Exception as e:
            LOG.append((base, repr(e)))
        return 0.4
    bpy.app.timers.register(tick, first_interval=0.5)
