import bpy
from mathutils import Vector
# --- fix coplanar end-cap on H wall (z-fight with V wall face)
w=bpy.data.objects['Res_WALL_GF_INT_H+5.00_13.0to24.0']
n=0
M=w.matrix_world; Mi=M.inverted()
for v in w.data.vertices:
    wc=M@v.co
    if abs(wc.x-12.94)<0.01: v.co=Mi@Vector((13.0,wc.y,wc.z)); n+=1
w.data.update()
print('capfix verts',n)
print([ (o.name) for o in bpy.data.objects if 'NICHE' in o.name and 'CUT' not in o.name])
import bpy
from mathutils import Vector
objs=[o for o in bpy.data.objects if o.type=='MESH' and ('_WALL_' in o.name or 'Parapet' in o.name or 'Pav_WALL' in o.name)]
def wbb(o):
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[i] for w in ws) for i in range(3)],[max(w[i] for w in ws) for i in range(3)]
BB={o.name:wbb(o) for o in objs}
fixed=[]; tol=0.004
for o in objs:
    M=o.matrix_world; R=M.to_3x3(); Mi=M.inverted().to_3x3(); me=o.data; moved=set(); cnt=0
    for p in me.polygons:
        nw=(R@p.normal).normalized()
        if abs(nw.z)>0.1: continue
        ax=0 if abs(nw.x)>abs(nw.y) else 1
        if abs(nw[ax])<0.99: continue
        vs=[M@me.vertices[i].co for i in p.vertices]
        c=sum(vs,Vector())/len(vs)
        o_ax=1-ax
        width=max(v[o_ax] for v in vs)-min(v[o_ax] for v in vs)
        if width>0.4: continue
        for q in objs:
            if q is o: continue
            lo,hi=BB[q.name]
            face=hi[ax] if nw[ax]>0 else lo[ax]
            if abs(c[ax]-face)>tol: continue
            if not (lo[o_ax]-0.01<=c[o_ax]<=hi[o_ax]+0.01 and lo[2]-0.01<=c.z<=hi[2]+0.01): continue
            moved.update(p.vertices); cnt+=1; break
    if moved:
        d=Mi@(Vector((0,0,0)))  # placeholder
        # shift each moved vertex inward along its face normal(s)
        for p in me.polygons:
            pass
    if cnt:
        # apply shift: recompute per polygon normal
        for p in me.polygons:
            if not set(p.vertices)<=moved: continue
            nw=(R@p.normal).normalized()
            if abs(nw.z)>0.1: continue
            delta=Mi@(-nw*tol)
            for i in p.vertices: me.vertices[i].co+=delta/ max(1,1)
        me.update(); fixed.append((o.name,cnt))
print('fixed objects',len(fixed)); print(fixed[:40])
n=0; ms=[]
for m in bpy.data.materials:
    if not m.use_nodes or not m.node_tree: continue
    for nd in m.node_tree.nodes:
        if nd.bl_idname=='ShaderNodeAmbientOcclusion':
            if not nd.only_local: nd.only_local=True; n+=1; ms.append(m.name)
print('AO nodes set only_local:',n, ms[:12])
purge('CornerFill_')
objs=[o for o in bpy.data.objects if o.type=='MESH' and ('_WALL_' in o.name or 'Parapet' in o.name) and 'INT' not in o.name and not o.name.startswith('CornerFill')]
def wbb(o):
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[i] for w in ws) for i in range(3)],[max(w[i] for w in ws) for i in range(3)]
BB={o.name:wbb(o) for o in objs}
tol=0.012; made=0; seen=set()
for o in objs:
    lo,hi=BB[o.name]
    if (hi[0]-lo[0]) < (hi[1]-lo[1]): continue      # o = run along X (horizontal)
    for q in objs:
        if q is o: continue
        l2,h2=BB[q.name]
        if (h2[0]-l2[0]) > (h2[1]-l2[1]): continue   # q = run along Y (vertical)
        if abs(o.location.z-q.location.z)>3.5 and False: continue
        # intersection
        ix0,ix1=max(lo[0],l2[0]),min(hi[0],h2[0]); iy0,iy1=max(lo[1],l2[1]),min(hi[1],h2[1]); iz0,iz1=max(lo[2],l2[2]),min(hi[2],h2[2])
        if ix1-ix0<=0.02 or iy1-iy0<=0.02 or iz1-iz0<=0.2: continue
        if ix1-ix0>0.4 or iy1-iy0>0.4: continue
        # outer-corner test: o's x end flush with q's outer x side; q's y end flush with o's outer y side
        sx = 1 if abs(hi[0]-h2[0])<tol else (-1 if abs(lo[0]-l2[0])<tol else 0)
        sy = 1 if abs(h2[1]-hi[1])<tol else (-1 if abs(l2[1]-lo[1])<tol else 0)
        if sx==0 or sy==0: continue
        e=0.0015
        x0=ix0-(e if sx<0 else -e); x1=ix1+(e if sx>0 else -e); y0=iy0-(e if sy<0 else -e); y1=iy1+(e if sy>0 else -e)
        key=(round(x0,2),round(y0,2),round(iz0,1))
        if key in seen: continue
        seen.add(key)
        p=Piece(f'CornerFill_{o.name.split("_ROOF")[0].split("_WALL")[0]}_{made:02d}')
        mat0=o.data.materials[0].name if o.data.materials and o.data.materials[0] else 'R4_Plaster_Exterior'
        p.box(((x0+x1)/2,(y0+y1)/2,(iz0+iz1)/2),(x1-x0,y1-y0,iz1-iz0),mat0)
        col=o.users_collection[0]
        ob=p.build((0,0,0),0,col,o.parent,bevel=0); made+=1
print('corner fills',made)
