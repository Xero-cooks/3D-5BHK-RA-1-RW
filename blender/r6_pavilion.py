purge('Pav_WIN_','Pav_DOOR_','Pav_ROOFD','Pav_POSTCLAD','Pav_BEAM','Pav_VERANDA','Pav_STEP','Pav_FURN','Pav_FIX','Pav_CEIL','Pav_DECOR','LT_Room_GF_Pav','LT_Pav_')
pm('R6_Alu_GreyBlue',(0.17,0.23,0.30,1),0.4,0.8)
pm('R6_Roof_Tile_Charcoal',(0.055,0.057,0.062,1),0.5,0.1)
pm('R6_Roof_Ridge',(0.04,0.04,0.045,1),0.45,0.1)
PAR='BLD_Pavilion'; D=math.pi/2
cwin=coll('08_Pav_Glazing'); cdoor=coll('07_Pav_Doors'); croof=coll('06_Pav_Roof'); cf=coll('12_Pav_Furniture'); cdec=coll('13_Pav_Decor'); cfx=coll('17_Pav_Fixtures')
def put(p,loc,rz=0.0,col=cf,bevel=0.004): return p.build(loc,rz,col,PAR,bevel=bevel)
for n,c,nv,nh in (('Pav_WIN_HallSouth','Pav_CUT_Window_GF_HallSouth',2,1),('Pav_WIN_HallWest','Pav_CUT_Window_GF_HallWest',2,1),('Pav_WIN_HallNorth','Pav_CUT_Window_GF_HallWin',2,1),('Pav_WIN_AnnexNorth','Pav_CUT_Window_GF_AnnexWin',2,1)):
    window(n,c,nv,nh,cwin,PAR,frame='R6_Alu_GreyBlue',z0=1.5,sill=True)
# main double timber door w/ glazed upper panes
a,b=bbox_of(bpy.data.objects['Pav_CUT_Door_GF_MainDoor']); cx,cy,L,rz=orient(a,b); H=b[2]-0.62
p=Piece('Pav_DOOR_Main'); bd=0.08
p.box((-(L/2-bd/2),0,H/2),(bd,0.2,H),'R4_Wood_Teak').box(((L/2-bd/2),0,H/2),(bd,0.2,H),'R4_Wood_Teak').box((0,0,H-bd/2),(L-2*bd,0.2,bd),'R4_Wood_Teak')
w=(L-2*bd)/2
for k in (0,1):
    xc=-L/2+bd+w*(k+0.5)
    p.box((xc,0,0.5),(w-0.02,0.05,1.0),'R4_Door_Teak_Main')
    p.box((xc,0,1.0+0.5*(H-bd-1.0)),(w-0.02,0.05,H-bd-1.0),'R4_Door_Teak_Main')
    p.box((xc,0,1.0+0.5*(H-bd-1.0)),(w-0.3,0.014,H-bd-1.35),'R4_Glass_Clear')
    hx=xc+(-w/2+0.08 if k==1 else w/2-0.08)
    p.bar((hx,0.045,0.95),(hx,0.045,1.4),0.014,'R4_Brass_Satin').bar((hx,-0.045,0.95),(hx,-0.045,1.4),0.014,'R4_Brass_Satin')
p.build((cx,cy,0.62),rz,cdoor,PAR,bevel=0.003)
door_wood('Pav_DOOR_HallAnnex','Pav_CUT_Door_GF_HallAnnex',0.62,cdoor,PAR)
# ---------- Roof ----------
x0,x1,y0,y1=-35.2,-20.8,-33.2,-20.8; zE=3.6; zR=6.05; rl=(x1-x0)/2-(y1-y0)/2; cxm=(x0+x1)/2; cym=(y0+y1)/2
R0=(cxm-rl,cym); R1=(cxm+rl,cym)  # ridge ends, rl=1.0
V=Vector
A=V((x0,y0,zE));B=V((x1,y0,zE));C=V((x1,y1,zE));Dd=V((x0,y1,zE));r0=V((R0[0],R0[1],zR));r1=V((R1[0],R1[1],zR))
faces={'S':[A,B,r1,r0],'E':[B,C,r1,r1+V((0,0,0))],'N':[C,Dd,r0,r1],'W':[Dd,A,r0,r0+V((0,0,0))]}
p=Piece('Pav_ROOFD_Tiles')
def tri_or_quad(face):
    return face
# long faces as trapezoids, end faces as triangles (degenerate quad)
def face_pts(a,b,c,d): return [a,b,c,d]
S=[A,B,r1,r0]; N=[C,Dd,r0,r1]; E=[B,C,r1,r1]; W=[Dd,A,r0,r0]
def tile_face(p,pts,rows):
    a,b,c,d=pts
    roof_prism(p,[a,b,c,d] if (c-d).length>0.01 else [a,b,c,c+V((0.0001,0,0))],0.12,'R6_Roof_Tile_Charcoal')
    for k in range(1,rows):
        t0=k/rows; t1=t0+0.035
        l0=a+(d-a)*t0; r0_=b+(c-b)*t0; l1=a+(d-a)*t1; r1_=b+(c-b)*t1
        roof_prism(p,[l0,r0_,r1_,l1],0.02,'R6_Roof_Ridge',up=0.03)
for f_,rows in ((S,26),(N,26)): tile_face(p,f_,rows)
for f_,rows in ((E,22),(W,22)): tile_face(p,f_,rows)
p.build((0,0,0),0,croof,PAR,bevel=0)
# ridge + hip caps + fascia + soffit
p=Piece('Pav_ROOFD_RidgeHips')
p.bar(r0+V((0,0,0.1)),r1+V((0,0,0.1)),0.11,'R6_Roof_Ridge',seg=8)
for a_,r_ in ((A,r0),(Dd,r0),(B,r1),(C,r1)): p.bar(a_+V((0,0,0.06)),r_+V((0,0,0.1)),0.075,'R6_Roof_Ridge',seg=8)
p.build((0,0,0),0,croof,PAR,bevel=0)
p=Piece('Pav_ROOFD_FasciaSoffit')
for yy in (y0,y1): p.box((cxm,yy,zE-0.05),(x1-x0+0.1,0.1,0.28),'R4_Plaster_Trim_White')
for xx in (x0,x1): p.box((xx,cym,zE-0.05),(0.1,y1-y0+0.1,0.28),'R4_Plaster_Trim_White')
for (ax0,ax1,ay0,ay1) in ((x0,x1,y0,-32.1),(x0,-34.1,y0,y1),(-21.9,x1,y0,y1),(x0,x1,-21.9,y1)):
    p.box(((ax0+ax1)/2,(ay0+ay1)/2,zE-0.22),(ax1-ax0,ay1-ay0,0.04),'R4_Wood_Teak')
p.build((0,0,0),0,croof,PAR,bevel=0)
# ---------- Veranda ----------
p=Piece('Pav_VERANDA_Floor'); p.box((-28,-22.95,0.61),(12.2,2.1,0.02),'R4_Paving_Sandstone'); put(p,(0,0,0),0,cdec,0)
p=Piece('Pav_STEP_Veranda')
for i in range(2): p.box((0,-21.7+0.3*i,0.38-0.16*i),(3.4,0.3,0.16),'R4_Stone_Sill')
put(p,(-28.5,0,0.0),0,cdec,0.003)
for i,x in enumerate((-33.6,-30.0,-26.0,-22.4)):
    p=Piece(f'Pav_POSTCLAD_{i+1}'); p.box((0,0,1.5),(0.30,0.30,3.0),'R4_Wood_Teak').box((0,0,0.05),(0.38,0.38,0.1),'R4_Stone_Plinth').box((0,0,2.98),(0.38,0.38,0.08),'R4_Wood_Dark')
    put(p,(x,-22.0,0.6),0,cdec,0.004)
p=Piece('Pav_BEAM_Veranda'); p.box((-28,-22.0,3.38),(12.0,0.24,0.34),'R4_Wood_Teak'); put(p,(0,0,0),0,cdec,0.004)
p=Piece('Pav_BEAM_VerandaCeiling'); p.box((-28,-22.95,3.48),(12.2,2.0,0.04),'R4_Wood_Teak'); put(p,(0,0,0),0,cdec,0)
# ---------- Interior ----------
p=Piece('Pav_CEIL_Hall'); p.box((-30,-28,3.57),(7.8,7.8,0.03),'R4_Paint_Ceiling'); put(p,(0,0,0),0,cfx,0)
p=Piece('Pav_CEIL_Annex'); p.box((-24,-28,3.57),(3.8,7.8,0.03),'R4_Paint_Ceiling'); put(p,(0,0,0),0,cfx,0)
put(sofa('Pav_FURN_Hall_Sofa',2.2,'R4_Fabric_teal'),(-32.4,-26.2,0.62),-D)
put(sofa('Pav_FURN_Hall_Sofa_02',2.0,'R4_Fabric_teal'),(-30.4,-30.8,0.62),0)
put(armchair('Pav_FURN_Hall_Armchair','R4_Fabric_mustard'),(-30.4,-25.4,0.62),math.pi)
put(coffee_table('Pav_FURN_Hall_CoffeeTable'),(-30.8,-28.0,0.62),D)
rug=Piece('Pav_DECOR_Hall_Rug'); rug.box((0,0,0.01),(3.2,2.4,0.02),'R4_Rug_cream'); put(rug,(-30.9,-28.0,0.62),0,cdec,0)
dt=put(dining_table('Pav_FURN_Hall_DiningTable',2.0,0.95),(-28.2,-30.6,0.62),0)
ch=put(chair('Pav_FURN_Hall_Chair_01'),(-28.7,-29.8,0.62),math.pi)
for i,(x,y,r) in enumerate(((-27.7,-29.8,math.pi),(-28.7,-31.4,0),(-27.7,-31.4,0),(-29.4,-30.6,-D),(-27.0,-30.6,D))): place(ch,f'Pav_FURN_Hall_Chair_{i+2:02d}',(x,y,0.62),r,cf,PAR)
put(potted_plant('Pav_DECOR_Hall_Plant',1.5),(-33.4,-31.4,0.62),0,cdec)
# annex pantry
p=Piece('Pav_FURN_Annex_PantryCounter'); p.box((0,0,0.45),(0.62,5.0,0.9),'R4_Laminate_White').box((0,0,0.92),(0.66,5.04,0.04),'R4_Granite_Grey')
p.cyl((0,-0.4,0.94),0.2,0.02,'R4_Steel_Stainless',seg=4,rot=(0,0,math.pi/4)); p.bar((0.2,-0.4,0.95),(0.2,-0.4,1.2),0.012,'R4_Chrome',seg=6).bar((0.2,-0.4,1.2),(0.08,-0.4,1.2),0.012,'R4_Chrome',seg=6)
p.box((0.2,0,1.9),(0.36,5.0,0.7),'R4_Laminate_White')
for i in range(8): p.bar((0.05,-2.3+i*0.65,1.7),(0.05,-2.3+i*0.65,1.95),0.01,'R6_Steel_Brushed',seg=6)
put(p,(-22.45,-28.0,0.62),math.pi)
put(fridge('Pav_FURN_Annex_Fridge'),(-23.0,-31.5,0.62),math.pi)
put(dining_table('Pav_FURN_Annex_HighTable',1.2,0.7,'R4_Wood_Dark'),(-24.3,-27.0,0.62),0)
# lights + fixtures
dl=put(downlight('Pav_FIX_Downlight_01'),(-32.5,-26.5,3.55),0,cfx,0)
for i,(x,y) in enumerate([(-32.5,-30),(-29,-26.5),(-29,-30),(-26.8,-26.5),(-26.8,-30),(-24,-26),(-24,-30)]): place(dl,f'Pav_FIX_Downlight_{i+2:02d}',(x,y,3.55),0,cfx,PAR)
acx=put(ac_cassette('Pav_FIX_AC_01'),(-30.0,-28.0,3.52),0,cfx); place(acx,'Pav_FIX_AC_02',(-24.0,-28.0,3.52),0,cfx,PAR)
L=bpy.data.collections['17_Lighting_Interior']
for nm,(x0_,x1_,y0_,y1_,w) in {'LT_Room_GF_Pav_Hall':(-34,-26,-32,-24,17),'LT_Room_GF_Pav_Annex':(-26,-22,-32,-24,19)}.items():
    d=bpy.data.lights.new(nm,'AREA'); d.shape='RECTANGLE'; d.size=(x1_-x0_)*0.4; d.size_y=(y1_-y0_)*0.4; d.color=(1.0,0.86,0.68)
    base=w*(x1_-x0_)*(y1_-y0_); d.energy=base*0.5; d['base_energy']=base
    ob=bpy.data.objects.new(nm,d); ob.location=((x0_+x1_)/2,(y0_+y1_)/2,3.4); L.objects.link(ob); ob['r4']=1; ob.parent=bpy.data.objects[PAR]
# bollards + veranda lanterns
LE=bpy.data.collections['17_Lighting_Exterior']
for i,(x,y) in enumerate([(-34.5,-20.2),(-31.5,-19.4),(-28.5,-19.2),(-25.0,-19.4),(-21.7,-20.2),(-19.5,-23.0)]):
    p=Piece(f'Pav_FIX_Bollard_{i+1:02d}'); p.cyl((0,0,0.3),0.07,0.6,'R6_Alu_Graphite',seg=12).cyl((0,0,0.52),0.075,0.06,'R4_LED_Warm',seg=12).cyl((0,0,0.6),0.09,0.04,'R6_Alu_Graphite',seg=12)
    put(p,(x,y,0.0),0,cfx,0.002)
    d=bpy.data.lights.new(f'LT_Pav_Bollard_{i+1:02d}','POINT'); d.energy=40.0; d['base_energy']=40.0; d.shadow_soft_size=0.06; d.color=(1.0,0.76,0.5)
    ob=bpy.data.objects.new(d.name,d); ob.location=(x,y,0.5); LE.objects.link(ob); ob['r4']=1; ob.parent=bpy.data.objects[PAR]
for i,x in enumerate((-33.6,-30.0,-26.0,-22.4)):
    p=Piece(f'Pav_FIX_PostLantern_{i+1:02d}'); p.box((0,0,0),(0.16,0.12,0.26),'R4_LED_Warm').box((0,0,0.15),(0.2,0.16,0.04),'R6_Alu_Graphite')
    put(p,(x,-22.2,2.4),0,cfx,0.002)
    d=bpy.data.lights.new(f'LT_Pav_PostLantern_{i+1:02d}','POINT'); d.energy=45.0; d['base_energy']=45.0; d.shadow_soft_size=0.07; d.color=(1.0,0.76,0.5)
    ob=bpy.data.objects.new(d.name,d); ob.location=(x,-22.4,2.4); LE.objects.link(ob); ob['r4']=1; ob.parent=bpy.data.objects[PAR]
# old shell roof: hide original single-mass roof (kept, non-destructive)
hm=bpy.data.objects.get('Pav_ROOF_HipMass')
if hm: hm.hide_render=True; hm.hide_viewport=True; hm['r6_superseded_by']='Pav_ROOFD_*'
print('pavilion done')
