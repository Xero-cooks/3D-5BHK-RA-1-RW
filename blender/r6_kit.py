"""Round 6 kit: collections, material helper, multi-material Piece builder (bmesh)."""
import bpy, bmesh, math
from mathutils import Matrix, Vector, Euler

def coll(name, parent='PROJECT_5BHK_RA-1-RW'):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        p = bpy.data.collections.get(parent) or bpy.context.scene.collection
        p.children.link(c)
    return c

def pm(name, color, rough=0.5, metal=0.0, spec=0.5, coat=0.0, emit=None, strength=1.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    for k in ('Specular IOR Level',):
        if k in b.inputs: b.inputs[k].default_value = spec
    if coat and 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = coat
    if emit is not None:
        b.inputs['Emission Color'].default_value = emit; b.inputs['Emission Strength'].default_value = strength
    return m

def mat(name):
    m = bpy.data.materials.get(name)
    if not m: raise KeyError(name)
    return m

class Piece:
    def __init__(s, name):
        s.name = name; s.bm = bmesh.new(); s.mats = []
    def _mi(s, m):
        n = m if isinstance(m, str) else m.name
        if n not in s.mats: s.mats.append(n)
        return s.mats.index(n)
    def _place(s, verts, c, rot, mi):
        M = Matrix.Translation(c) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
        bmesh.ops.transform(s.bm, matrix=M, verts=verts)
        fs = {f for v in verts for f in v.link_faces}
        for f in fs: f.material_index = mi
    def box(s, c, size, m, rot=(0, 0, 0)):
        r = bmesh.ops.create_cube(s.bm, size=1.0)
        v = r['verts']
        bmesh.ops.transform(s.bm, matrix=Matrix.Diagonal((size[0], size[1], size[2], 1.0)), verts=v)
        s._place(v, Vector(c), rot, s._mi(m)); return s
    def cyl(s, c, r, d, m, axis='Z', seg=16, r2=None, rot=None):
        r2 = r if r2 is None else r2
        res = bmesh.ops.create_cone(s.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r2, depth=d)
        v = res['verts']
        base = {'Z': (0, 0, 0), 'X': (0, math.pi / 2, 0), 'Y': (-math.pi / 2, 0, 0)}[axis]
        bmesh.ops.transform(s.bm, matrix=Euler(base, 'XYZ').to_matrix().to_4x4(), verts=v)
        s._place(v, Vector(c), rot or (0, 0, 0), s._mi(m)); return s
    def sph(s, c, r, m, seg=12, sc=(1, 1, 1)):
        res = bmesh.ops.create_uvsphere(s.bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
        v = res['verts']
        bmesh.ops.transform(s.bm, matrix=Matrix.Diagonal((sc[0], sc[1], sc[2], 1.0)), verts=v)
        s._place(v, Vector(c), (0, 0, 0), s._mi(m)); return s
    def build(s, loc=(0, 0, 0), rz=0.0, col=None, parent=None, bevel=0.004, smooth=True, mesh=None):
        me = mesh or bpy.data.meshes.new(s.name)
        if not mesh:
            if smooth is not False:
                for f in s.bm.faces: f.smooth = True
                for e in s.bm.edges:
                    if len(e.link_faces) == 2:
                        try: e.smooth = e.calc_face_angle(0.0) < 1.0
                        except Exception: pass
                    else: e.smooth = False
            s.bm.to_mesh(me)
            for n in s.mats: me.materials.append(bpy.data.materials[n])
        s.bm.free()
        ob = bpy.data.objects.new(s.name, me)
        ob.location = loc; ob.rotation_euler = (0, 0, rz)
        (col or bpy.context.scene.collection).objects.link(ob)
        if parent: ob.parent = bpy.data.objects[parent] if isinstance(parent, str) else parent
        if bevel:
            md = ob.modifiers.new('Bevel', 'BEVEL'); md.width = bevel; md.segments = 2; md.limit_method = 'ANGLE'
        return ob

def place(src, name, loc, rz=0.0, col=None, parent=None):
    """linked-data duplicate of an existing piece object (independent object, shared mesh)."""
    ob = bpy.data.objects.new(name, src.data)
    ob.location = loc; ob.rotation_euler = (0, 0, rz)
    (col or bpy.context.scene.collection).objects.link(ob)
    if parent: ob.parent = bpy.data.objects[parent] if isinstance(parent, str) else parent
    for m in src.modifiers:
        n = ob.modifiers.new(m.name, m.type)
        if m.type == 'BEVEL': n.width = m.width; n.segments = m.segments; n.limit_method = m.limit_method
    return ob

def _bar(s, p, q, r, m, seg=8):
    p=Vector(p); q=Vector(q); d=q-p; L=d.length
    if L<1e-6: return s
    res = bmesh.ops.create_cone(s.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=L)
    v = res['verts']
    R = Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(s.bm, matrix=Matrix.Translation((p+q)/2) @ R, verts=v)
    mi = s._mi(m)
    for f in {f for x in v for f in x.link_faces}: f.material_index = mi
    return s
Piece.bar = _bar

def purge(*prefixes):
    n=0
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):
            me=o.data if o.type=='MESH' else None
            bpy.data.objects.remove(o, do_unlink=True); n+=1
            if me is not None and me.users==0: bpy.data.meshes.remove(me)
    return n
