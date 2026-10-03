purge('Club_WIN_','Club_DOOR_','Club_CANOPY')
# ---- Round 6: Clubhouse glazing, doors, canopy (non-destructive: cutters untouched)
def R6_mats():
    pm('R6_Alu_Graphite',(0.035,0.037,0.042,1),0.38,0.85)
    pm('R6_Steel_Brushed',(0.55,0.56,0.58,1),0.3,1.0)
    pm('R6_Rubber_Black',(0.012,0.012,0.012,1),0.7)
    pm('R6_Pipe_Red',(0.55,0.03,0.02,1),0.35,0.2)
    pm('R6_Machine_Black',(0.02,0.02,0.022,1),0.45,0.5)
    pm('R6_Machine_Grey',(0.35,0.36,0.38,1),0.4,0.7)
    pm('R6_Weight_Stack',(0.5,0.5,0.52,1),0.3,1.0)
    pm('R6_Baize_Green',(0.02,0.22,0.08,1),0.95)
    pm('R6_Mahogany',(0.12,0.035,0.02,1),0.3,0,0.5,0.3)
    pm('R6_Concrete_Soffit',(0.42,0.42,0.40,1),0.9)
    pm('R6_Band_Yellow',(0.78,0.58,0.12,1),0.7)
    pm('R6_Band_Green',(0.10,0.35,0.15,1),0.7)
    pm('R6_Band_Dark',(0.07,0.08,0.09,1),0.6)
    pm('R6_Cushion_Grey',(0.22,0.23,0.25,1),0.9)
    pm('R6_Yoga_Mat_Teal',(0.04,0.35,0.34,1),0.8)
    pm('R6_Yoga_Mat_Plum',(0.30,0.08,0.22,1),0.8)
    pm('R6_AC_White',(0.9,0.9,0.88,1),0.4)
    pm('R6_Downlight',(1,0.9,0.75,1),0.5,0,0.5,0,(1,0.85,0.6,1),12.0)
    pm('R6_Panel_Light',(1,0.95,0.85,1),0.5,0,0.5,0,(1,0.93,0.82,1),9.0)
R6_mats()

def bbox_of(o):
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[i] for w in ws) for i in range(3)],[max(w[i] for w in ws) for i in range(3)]

def orient(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    if dx<dy: return (a[0]+b[0])/2,(a[1]+b[1])/2,dy,math.pi/2
    return (a[0]+b[0])/2,(a[1]+b[1])/2,dx,0.0

def window(name,cutter,nv,nh,col,parent,frame='R6_Alu_Graphite',glass='R4_Glass_Clear',z0=None,sill=False):
    a,b=bbox_of(bpy.data.objects[cutter]); cx,cy,L,rz=orient(a,b)
    z0=a[2] if z0 is None else z0; H=b[2]-z0
    bd=0.07; d=0.12; p=Piece(name)
    p.box((-(L/2-bd/2),0,H/2),(bd,d,H),frame).box(((L/2-bd/2),0,H/2),(bd,d,H),frame)
    p.box((0,0,H-bd/2),(L-2*bd,d,bd),frame).box((0,0,bd/2),(L-2*bd,d,bd),frame)
    iw=L-2*bd; ih=H-2*bd
    for i in range(1,nv): p.box((-iw/2+iw*i/nv,0,H/2),(0.05,0.09,ih),frame)
    for j in range(1,nh): p.box((0,0,bd+ih*j/nh),(iw,0.09,0.05),frame)
    p.box((0,0,H/2),(iw,0.012,ih),glass)
    if sill: p.box((0,0.1,-0.03),(L+0.2,0.3,0.06),'R4_Stone_Sill')
    return p.build((cx,cy,z0),rz,col,parent,bevel=0.003)

def door_glass(name,cutter,z0,col,parent,frosted=True,hl=2.1):
    a,b=bbox_of(cutter if not isinstance(cutter,str) else bpy.data.objects[cutter]); cx,cy,L,rz=orient(a,b)
    H=b[2]-z0; hl=min(hl,H); p=Piece(name); d=0.1; bd=0.07
    # outer frame/architrave
    p.box((-(L/2-bd/2),0,H/2),(bd,0.16,H),'R6_Alu_Graphite').box(((L/2-bd/2),0,H/2),(bd,0.16,H),'R6_Alu_Graphite')
    p.box((0,0,H-bd/2),(L-2*bd,0.16,bd),'R6_Alu_Graphite')
    n=2 if L>1.6 else 1; w=(L-2*bd)/n
    for k in range(n):
        x0=-L/2+bd+k*w; xc=x0+w/2
        p.box((x0+0.04,0,hl/2),(0.08,d,hl),'R6_Alu_Graphite').box((x0+w-0.04,0,hl/2),(0.08,d,hl),'R6_Alu_Graphite')
        p.box((xc,0,hl-0.05),(w,d,0.1),'R6_Alu_Graphite').box((xc,0,0.12),(w,d,0.24),'R6_Alu_Graphite')
        p.box((xc,0,(hl+0.24-0.1)/2),(w-0.16,0.012,hl-0.34),'R4_Glass_Clear')
        if frosted: p.box((xc,0.0,1.05),(w-0.16,0.016,0.30),'R4_Glass_Frosted')
        hx=x0+(w-0.12 if k%2==0 or n==1 else 0.12)
        p.bar((hx,0.07,0.85),(hx,0.07,1.45),0.014,'R6_Steel_Brushed').bar((hx,-0.07,0.85),(hx,-0.07,1.45),0.014,'R6_Steel_Brushed')
    if H>hl+0.1:
        p.box((0,0,hl+0.02),(L-2*bd,0.1,0.04),'R6_Alu_Graphite')
        p.box((0,0,(hl+H-bd)/2+0.02),(L-2*bd,0.012,H-bd-hl-0.04),'R4_Glass_Clear')
    return p.build((cx,cy,z0),rz,col,parent,bevel=0.003)

def door_wood(name,cutter,z0,col,parent):
    a,b=bbox_of(bpy.data.objects[cutter]); cx,cy,L,rz=orient(a,b); H=b[2]-z0; p=Piece(name)
    bd=0.06
    p.box((-(L/2-bd/2),0,H/2),(bd,0.2,H),'R4_Paint_White').box(((L/2-bd/2),0,H/2),(bd,0.2,H),'R4_Paint_White').box((0,0,H-bd/2),(L-2*bd,0.2,bd),'R4_Paint_White')
    p.box((0,0,(H-bd)/2),(L-2*bd,0.04,H-bd),'R4_Door_Walnut')
    hx=L/2-bd-0.12
    p.bar((hx-0.1,0.07,1.0),(hx+0.02,0.07,1.0),0.014,'R6_Steel_Brushed').bar((hx-0.1,-0.07,1.0),(hx+0.02,-0.07,1.0),0.014,'R6_Steel_Brushed')
    return p.build((cx,cy,z0),rz,col,parent,bevel=0.003)

cg=coll('08_Club_Glazing'); cd=coll('07_Club_Doors')
W=[('Club_WIN_FF_GamesGlazing','Club_CUT_Window_FF_GamesGlazing',3,2),('Club_WIN_FF_GamesNorth','Club_CUT_Window_FF_GamesNorth',4,1),
   ('Club_WIN_FF_StudioGlazing','Club_CUT_Window_FF_StudioGlazing',6,2),('Club_WIN_FF_StudioRibbon','Club_CUT_Window_FF_StudioRibbon',8,1),
   ('Club_WIN_GF_Changing','Club_CUT_Window_GF_Changing',2,1),('Club_WIN_GF_GymEast','Club_CUT_Window_GF_GymEast',4,1),
   ('Club_WIN_GF_GymGlazing','Club_CUT_Window_GF_GymGlazing',6,2),('Club_WIN_GF_GymRibbon','Club_CUT_Window_GF_GymRibbon',8,1),
   ('Club_WIN_GF_Lobby','Club_CUT_Window_GF_Lobby',2,1)]
for n,c,nv,nh in W: window(n,c,nv,nh,cg,'BLD_Clubhouse')
door_glass('Club_DOOR_GF_MainEntrance','Club_CUT_Door_GF_MainEntrance',0.62,cd,'BLD_Clubhouse',frosted=False)
door_glass('Club_DOOR_GF_LobbyGym','Club_CUT_Door_GF_LobbyGym',0.62,cd,'BLD_Clubhouse')
door_wood('Club_DOOR_GF_LobbyChanging','Club_CUT_Door_GF_LobbyChanging',0.62,cd,'BLD_Clubhouse')
door_glass('Club_DOOR_FF_StudioGames','Club_CUT_Door_FF_StudioGames',4.52,cd,'BLD_Clubhouse')
door_glass('Club_DOOR_FF_StudioMulti','Club_CUT_Door_FF_StudioMulti',4.52,cd,'BLD_Clubhouse')
# entrance canopy (west facade)
p=Piece('Club_CANOPY_Entrance'); p.box((0,0,0),(1.8,4.4,0.14),'R6_Alu_Graphite').box((0.0,0,0.11),(1.7,4.3,0.04),'R4_Plaster_Trim_White')
for yy in (-2.0,2.0): p.cyl((-0.75,yy,-1.6),0.05,3.2,'R6_Alu_Graphite')
p.build((31.1,-13.25,3.55),0,cg,'BLD_Clubhouse',bevel=0.004)
print('glazing done', len(cg.objects), len(cd.objects))
