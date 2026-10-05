# R7_gym.py - place imported gym equipment templates at explicit world positions
import bpy, math
from mathutils import Vector, Matrix

def tbbox(names):
    pts = [bpy.data.objects[n].matrix_world @ Vector(c) for n in names for c in bpy.data.objects[n].bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx

def tmpl_names(prefix_objs):
    return [o.name for o in prefix_objs]

def put(names, cx, cy, z, yaw, s, tag, coll):
    """copy template objects (linked data) under an empty; centre of bbox xy -> (cx,cy), bbox min z -> z, rotate yaw (rad) about Z, uniform scale s"""
    mn, mx = tbbox(names); tc = (mn + mx) / 2
    R = Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Scale(s, 4)
    off = R.to_3x3() @ Vector((-tc.x, -tc.y, 0))
    pos = Vector((cx + off.x, cy + off.y, z - mn.z * s))
    E = bpy.data.objects.new('GYM_' + tag, None); coll.objects.link(E)
    E.matrix_world = Matrix.Translation(pos) @ R
    for n in names:
        t = bpy.data.objects[n]
        c = bpy.data.objects.new(n.split('.')[0] + '_' + tag, t.data)
        coll.objects.link(c); c.parent = E
        c.matrix_parent_inverse = Matrix.Identity(4)
        c.matrix_local = t.matrix_world.copy()
        c.hide_render = False; c.hide_viewport = False
    return E

def hide(bases):
    for b in bases:
        for o in bpy.data.objects:
            if o.name == b or o.name.startswith(b + '.'):
                o.hide_render = True; o.hide_viewport = True
