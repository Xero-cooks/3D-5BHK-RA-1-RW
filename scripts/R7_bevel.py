import bpy,math
SOFT=('fabric','rug','cushion','leather','wicker')
SKIP=('led','glass','leaf','paper','sheer','mirror','soil','bark','water','art_')
def add_bevel(o):
    if o.type!='MESH' or any(m.type=='BEVEL' for m in o.modifiers): return 0
    me=o.data
    if len(me.polygons)<6 or len(me.polygons)>30000: return 0
    ms=[s.material.name.lower() for s in o.material_slots if s.material]
    if ms and all(any(k in n for k in SKIP) for n in ms): return 0
    d=sorted([v for v in o.dimensions if v>1e-4])
    if not d: return 0
    md=d[0]
    if md<0.012: return 0
    soft=any(any(k in n for k in SOFT) for n in ms)
    w=0.018 if soft else 0.004
    if 'wall' in o.name.lower() or 'ceil' in o.name.lower(): w=0.006
    w=min(w,md*0.3)
    m=o.modifiers.new('R7_Bevel','BEVEL')
    m.width=w; m.segments=3 if soft else 2; m.limit_method='ANGLE'; m.angle_limit=math.radians(40)
    m.use_clamp_overlap=True; m.harden_normals=False
    return 1
# Shading: select meshes then bpy.ops.object.shade_smooth_by_angle(angle=math.radians(32)) under temp_override
