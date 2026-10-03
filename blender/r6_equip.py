# ---- Round 6 equipment / furniture constructors (return un-built Piece; local origin = footprint centre on floor, user faces +Y)
MB='R6_Machine_Black'; MG='R6_Machine_Grey'; RB='R6_Rubber_Black'; ST='R6_Steel_Brushed'; WS='R6_Weight_Stack'
def treadmill(n):
    p=Piece(n)
    p.box((0,0,0.16),(0.86,1.85,0.2),MB).box((0,-0.02,0.275),(0.62,1.55,0.03),RB)
    for sx in (-1,1):
        p.box((sx*0.38,-0.02,0.2),(0.1,1.7,0.1),MG)
        p.bar((sx*0.4,0.78,0.2),(sx*0.4,0.82,1.28),0.025,MB)
        p.bar((sx*0.4,0.82,1.0),(sx*0.4,0.1,0.98),0.02,MB)
    p.box((0,0.8,1.3),(0.82,0.16,0.3),MG,rot=(-0.35,0,0)).box((0,0.715,1.3),(0.5,0.02,0.2),'R4_Glass_Black_TV',rot=(-0.35,0,0))
    p.box((0,0.82,0.5),(0.7,0.12,0.5),MB)
    return p
def elliptical(n):
    p=Piece(n)
    p.box((0,0,0.1),(0.62,1.65,0.12),MB)
    p.cyl((0,-0.6,0.42),0.3,0.2,MG,axis='X',seg=20).box((0,-0.62,0.3),(0.4,0.5,0.5),MG)
    p.bar((0,0.45,0.1),(0,0.7,1.45),0.035,MB)
    p.box((0,0.72,1.5),(0.5,0.12,0.26),MG,rot=(-0.3,0,0)).box((0,0.655,1.5),(0.34,0.02,0.16),'R4_Glass_Black_TV',rot=(-0.3,0,0))
    for sx in (-1,1):
        p.bar((sx*0.25,-0.6,0.3),(sx*0.25,0.3,0.3),0.02,MG).box((sx*0.25,-0.3,0.3),(0.16,0.4,0.05),RB)
        p.bar((sx*0.25,0.62,1.4),(sx*0.28,-0.2,0.5),0.022,MB)
        p.bar((sx*0.22,0.7,1.35),(sx*0.22,0.62,1.0),0.02,RB)
    return p
def spinbike(n):
    p=Piece(n)
    for yy in (-0.45,0.45): p.box((0,yy,0.03),(0.5,0.08,0.05),MB)
    p.bar((0,-0.4,0.06),(0,0.4,0.06),0.03,MB)
    p.bar((0,-0.3,0.1),(0.0,-0.36,1.02),0.025,MG).box((0,-0.38,1.06),(0.24,0.28,0.07),RB)
    p.bar((0,0.36,0.1),(0,0.46,1.12),0.025,MG).bar((-0.18,0.46,1.12),(0.18,0.46,1.12),0.016,ST)
    p.cyl((0,0.28,0.42),0.26,0.07,'R4_Plastic_Red',axis='X',seg=20).bar((0,0.28,0.42),(0,-0.05,0.42),0.02,MB)
    p.bar((0,0.0,0.3),(0,-0.05,0.3),0.02,MB)
    return p
def multistation(n):
    p=Piece(n); W,D,H=2.5,1.7,2.35
    for sx in (-1,1):
        for sy in (-1,1): p.box((sx*W/2,sy*D/2,H/2),(0.09,0.09,H),MB)
    for sy in (-1,1): p.box((0,sy*D/2,H-0.05),(W,0.09,0.09),MB); p.box((0,sy*D/2,0.1),(W,0.09,0.12),MB)
    for sx in (-1,1): p.box((sx*W/2,0,H-0.05),(0.09,D,0.09),MB); p.box((sx*W/2,0,0.1),(0.09,D,0.12),MB)
    # weight stacks (rear)
    for sx in (-0.75,0.75):
        p.box((sx,-D/2+0.2,1.0),(0.38,0.34,1.7),MB)
        for k in range(14): p.box((sx,-D/2+0.2,0.28+k*0.1),(0.3,0.26,0.075),WS)
        p.bar((sx,-D/2+0.2,0.2),(sx,-D/2+0.2,2.1),0.012,ST)
    p.box((0,-D/2+0.06,1.5),(W-0.2,0.05,0.9),MG)
    # seats
    p.box((-0.75,0.15,0.46),(0.4,0.4,0.12),'R4_Leather_Charcoal');p.box((-0.75,-0.2,1.0),(0.4,0.1,0.7),'R4_Leather_Charcoal')
    p.box((0.75,0.15,0.46),(0.4,0.4,0.12),'R4_Leather_Charcoal');p.box((0.75,-0.2,1.0),(0.4,0.1,0.7),'R4_Leather_Charcoal')
    p.bar((-W/2,0.4,2.2),(-0.9,-0.2,2.2),0.012,ST);p.bar((W/2,0.4,2.2),(0.9,-0.2,2.2),0.012,ST)
    return p
def bench(n):
    p=Piece(n)
    p.box((0,0,0.45),(0.32,1.25,0.1),'R4_Leather_Charcoal').box((0,0,0.38),(0.12,1.1,0.05),MB)
    for yy in (-0.5,0.5): p.box((0,yy,0.18),(0.5,0.06,0.04),MB).box((0,yy,0.28),(0.05,0.05,0.22),MB)
    return p
def squat_rack(n):
    p=Piece(n)
    for sx in (-0.65,0.65):
        p.box((sx,0,1.1),(0.07,0.07,2.2),MB);p.box((sx,0.5,0.03),(0.07,1.2,0.06),MB);p.box((sx,-0.5,0.03),(0.07,1.2,0.06),MB)
        p.box((sx,0,1.0),(0.12,0.12,0.04),ST)
    p.box((0,0,2.15),(1.4,0.07,0.07),MB)
    p.bar((-1.1,0,1.1),(1.1,0,1.1),0.014,ST)
    for sx in (-0.95,0.95):
        for k,(rr,wd) in enumerate(((0.22,0.04),(0.2,0.035),(0.17,0.03))): p.cyl((sx+(k*0.045*(1 if sx>0 else -1)),0,1.1),rr,wd,MB,axis='X',seg=20)
    return p
def dumbbell_rack(n):
    p=Piece(n)
    for k in range(2): p.box((0,0,0.45+k*0.42),(2.3,0.5,0.04),MB)
    for sx in (-1.1,1.1): p.box((sx,0,0.4),(0.05,0.5,0.8),MB)
    p.box((0,-0.24,0.4),(2.3,0.02,0.7),MB)
    for k in range(2):
        for i in range(9):
            x=-1.0+i*0.25;rr=0.045+i*0.004
            p.bar((x,0.05,0.52+k*0.42),(x,-0.05,0.52+k*0.42),0.012,ST)
            p.bar((x,0.12,0.52+k*0.42),(x,0.07,0.52+k*0.42),0.045+i*0.003,MB,seg=10).bar((x,-0.07,0.52+k*0.42),(x,-0.12,0.52+k*0.42),0.045+i*0.003,MB,seg=10)
    return p
def kettlebells(n):
    p=Piece(n)
    for i in range(6):
        r=0.07+i*0.012; x=i*0.3
        p.sph((x,0,r+0.02),r,MB,seg=12);p.bar((x-0.05,0,2*r+0.0),(x+0.05,0,2*r+0.0),0.012,MB)
    return p
def mat_yoga(n,m='R6_Yoga_Mat_Teal'):
    p=Piece(n); p.box((0,0,0.01),(0.62,1.8,0.02),m); return p
def sofa(n,w=2.1,fab='R4_Fabric_charcoal'):
    p=Piece(n)
    p.box((0,0,0.2),(w,0.9,0.28),'R4_Wood_Dark').box((0,0.02,0.4),(w-0.4,0.8,0.16),fab).box((0,-0.38,0.65),(w,0.18,0.55),fab)
    for sx in (-1,1): p.box((sx*(w/2-0.1),0,0.45),(0.2,0.9,0.5),fab)
    for sx in (-0.5,0.5): p.box((sx*(w-0.5)/1.0*0.5,-0.25,0.66),((w-0.5)/2-0.02,0.2,0.4),fab,rot=(-0.12,0,0))
    return p
def armchair(n,fab='R4_Fabric_grey'):
    p=sofa(n,0.85,fab); return p
def coffee_table(n,w=1.1,d=0.6):
    p=Piece(n); p.box((0,0,0.38),(w,d,0.04),'R4_Wood_Dark').box((0,0,0.2),(w-0.1,d-0.1,0.02),'R4_Wood_Dark')
    for sx in (-1,1):
        for sy in (-1,1): p.box((sx*(w/2-0.04),sy*(d/2-0.04),0.19),(0.04,0.04,0.38),'R6_Steel_Brushed')
    return p
def ac_cassette(n):
    p=Piece(n); p.box((0,0,0),(0.7,0.7,0.06),'R6_AC_White').box((0,0,-0.035),(0.56,0.56,0.02),'R4_Paper')
    for sx in (-1,1): p.box((sx*0.2,0,-0.05),(0.06,0.5,0.01),'R6_Machine_Grey')
    return p
def downlight(n):
    p=Piece(n); p.cyl((0,0,0),0.09,0.02,'R6_Downlight',seg=16); return p
def potted_plant(n,h=1.3):
    p=Piece(n); p.cyl((0,0,0.2),0.22,0.4,'R4_Terracotta',seg=16,r2=0.17)
    p.cyl((0,0,0.42),0.2,0.04,'R4_Soil',seg=12)
    for i in range(9):
        a=i*0.7; p.bar((0.04*math.cos(a),0.04*math.sin(a),0.42),(0.30*math.cos(a),0.30*math.sin(a),0.42+h*(0.55+0.05*(i%3))),0.012,'R4_Leaf_Dark',seg=5)
        p.sph((0.30*math.cos(a),0.30*math.sin(a),0.42+h*(0.55+0.05*(i%3))),0.14,'R4_Leaf',seg=8,sc=(1,1,0.45))
    return p
def chair(n,fab='R4_Fabric_cream',wood='R4_Wood_Teak'):
    p=Piece(n); p.box((0,0,0.46),(0.46,0.46,0.05),wood).box((0,0.01,0.5),(0.42,0.42,0.05),fab).box((0,-0.21,0.8),(0.44,0.04,0.5),wood)
    for sx in (-1,1):
        for sy in (-1,1): p.box((sx*0.2,sy*0.2,0.22),(0.04,0.04,0.44),wood)
    return p
def dining_table(n,w=2.0,d=1.0,top='R4_Wood_Teak'):
    p=Piece(n); p.box((0,0,0.74),(w,d,0.05),top).box((0,0,0.69),(w-0.2,d-0.2,0.05),'R4_Wood_Dark')
    for sx in (-1,1):
        for sy in (-1,1): p.box((sx*(w/2-0.1),sy*(d/2-0.1),0.36),(0.07,0.07,0.72),'R4_Wood_Dark')
    return p
def fridge(n):
    p=Piece(n); p.box((0,0,0.9),(0.75,0.72,1.8),'R4_Steel_Stainless').box((0,0.37,1.25),(0.01,0.7,0.02),'R6_Machine_Black')
    p.bar((-0.3,0.38,1.1),(-0.3,0.38,1.5),0.012,'R6_Steel_Brushed'); p.bar((-0.3,0.38,0.7),(-0.3,0.38,1.0),0.012,'R6_Steel_Brushed')
    return p
def roof_prism(p,pts,th,mat,up=0.0):
    """thick plank from 4 coplanar pts (counter-clockwise seen from above); offset 'up' along normal"""
    P=[Vector(x) for x in pts]; nrm=((P[1]-P[0]).cross(P[3]-P[0])).normalized()
    top=[x+nrm*up for x in P]; bot=[x+nrm*(up-th) for x in P]
    vs=[p.bm.verts.new(v) for v in top+bot]
    mi=p._mi(mat)
    for f in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        try: fc=p.bm.faces.new([vs[i] for i in f]); fc.material_index=mi
        except ValueError: pass
