purge('Club_FURN_GF','Club_DECOR_GF','Club_FIX_GF','Club_CEIL_GF')
cf=coll('12_Club_Furniture'); cdec=coll('13_Club_Decor'); cfx=coll('17_Club_Fixtures')
PAR='BLD_Clubhouse'
def put(p,loc,rz=0.0,col=cf,bevel=0.004):
    return p.build(loc,rz,col,PAR,bevel=bevel)
def rep(src,base,pts,col=cf):
    out=[]
    for i,(x,y,rz) in enumerate(pts):
        out.append(place(src,f'{base}_{i+2:02d}',(x,y,src.location.z),rz,col,PAR))
    return out
D=math.pi/2
# ---------------- GYM (x32..48, y-26..-16) ----------------
t=put(treadmill('Club_FURN_GF_Treadmill_01'),(33.5,-24.2,0.62),D)
rep(t,'Club_FURN_GF_Treadmill',[(33.5,-22.8,D),(33.5,-21.4,D),(33.5,-20.0,D)])
e=put(elliptical('Club_FURN_GF_Elliptical_01'),(35.7,-24.2,0.62),D)
rep(e,'Club_FURN_GF_Elliptical',[(35.7,-22.8,D),(35.7,-21.4,D)])
put(multistation('Club_FURN_GF_MultiStation'),(45.3,-24.3,0.62),0)
put(squat_rack('Club_FURN_GF_SquatRack'),(40.0,-21.8,0.62),0)
b=put(bench('Club_FURN_GF_Bench_01'),(37.3,-19.0,0.62),0.0)
rep(b,'Club_FURN_GF_Bench',[(39.0,-24.2,D),(43.8,-19.6,0.0)])
put(dumbbell_rack('Club_FURN_GF_DumbbellRack'),(45.2,-16.6,0.62),math.pi)
put(kettlebells('Club_FURN_GF_Kettlebells'),(35.2,-16.7,0.62),0)
m=put(mat_yoga('Club_FURN_GF_Mat_01'),(41.8,-24.2,0.62),0.0,bevel=0)
rep(m,'Club_FURN_GF_Mat',[(42.6,-24.2,0.0),(43.4,-24.2,0.0)])
# wall bands (north wall inner face y=-15.94 is gym side? gym is y<-16 -> face at y=-16.06)
def wallpanel(name,x0,x1,z0,z1,y,mat,t=0.012):
    p=Piece(name); p.box(((x0+x1)/2,y,(z0+z1)/2),(x1-x0,t,z1-z0),mat); return p.build((0,0,0),0,cdec,PAR,bevel=0)
wallpanel('Club_DECOR_GF_Gym_BandDark_N',32.1,47.9,0.62,1.1,-16.075,'R6_Band_Dark')
wallpanel('Club_DECOR_GF_Gym_BandYellow_N',32.1,47.9,3.0,4.2,-16.075,'R6_Band_Yellow')
wallpanel('Club_DECOR_GF_Gym_BandGreen_N',32.1,47.9,2.9,3.0,-16.075,'R6_Band_Green')
for i,(a,b2) in enumerate(((33.0,37.4),(40.0,47.6))): wallpanel(f'Club_DECOR_GF_Gym_Mirror_N{i+1}',a,b2,1.1,2.9,-16.08,'R4_Mirror',0.02)
wallpanel('Club_DECOR_GF_Gym_BandYellow_E',47.88-0.0,47.88,0.0,0.0,0,'R6_Band_Yellow') if False else None
def wallpanelE(name,y0,y1,z0,z1,x,mat,t=0.012):
    p=Piece(name); p.box((x,(y0+y1)/2,(z0+z1)/2),(t,y1-y0,z1-z0),mat); return p.build((0,0,0),0,cdec,PAR,bevel=0)
wallpanelE('Club_DECOR_GF_Gym_BandDark_E',-25.9,-16.1,0.62,1.1,47.865,'R6_Band_Dark')
wallpanelE('Club_DECOR_GF_Gym_BandYellow_E',-25.9,-16.1,3.65,4.2,47.865,'R6_Band_Yellow')
wallpanelE('Club_DECOR_GF_Gym_BandGreen_E',-25.9,-16.1,3.6,3.65,47.865,'R6_Band_Green')
# exposed soffit + red sprinkler pipes
p=Piece('Club_CEIL_GF_Gym_ExposedSoffit'); p.box((40,-21,4.17),(15.9,9.9,0.03),'R6_Concrete_Soffit')
for yy in (-25.0,-21.0,-17.0): p.box((40,yy,4.0),(15.9,0.35,0.3),'R6_Concrete_Soffit')
put_c=p.build((0,0,0),0,cfx,PAR,bevel=0)
p=Piece('Club_FIX_GF_Gym_SprinklerPipes')
for yy in (-23.0,-19.0): p.bar((32.3,yy,3.78),(47.7,yy,3.78),0.045,'R6_Pipe_Red',seg=10)
p.bar((47.7,-23.0,3.78),(47.7,-17.0,3.78),0.045,'R6_Pipe_Red',seg=10).bar((32.5,-23.0,3.78),(32.5,-17.0,3.78),0.04,'R6_Pipe_Red',seg=10)
for yy in (-23.0,-19.0):
    for xx in range(34,48,3):
        p.bar((xx,yy,3.78),(xx,yy,3.55),0.012,'R6_Steel_Brushed').cyl((xx,yy,3.53),0.03,0.04,'R6_Steel_Brushed',seg=8)
for xx in (36,44): p.bar((xx,-23.0,3.78),(xx,-23.0,4.15),0.02,'R6_Machine_Grey')
put(p,(0,0,0),0,cfx,0)
ac=put(ac_cassette('Club_FIX_GF_Gym_AC_01'),(36.0,-19.0,3.75),0,cfx)
rep(ac,'Club_FIX_GF_Gym_AC',[(36.0,-23.0,0),(40.0,-21.0,0),(44.0,-19.0,0),(44.0,-23.0,0)],cfx)
# gym light panels (emissive linear) + real area lights
for i,(x,y) in enumerate([(35,-21),(41,-21),(47,-21)]):
    pp=Piece(f'Club_FIX_GF_Gym_LinearLED_{i+1:02d}'); pp.box((0,0,0),(0.12,8.0,0.05),'R6_Panel_Light'); put(pp,(x,y,3.9),0,cfx,0)
# ---------------- LOBBY (x32..40, y-16..-10) ----------------
p=Piece('Club_FURN_GF_Lobby_Reception')
p.box((0,0,0.55),(2.6,0.7,1.1),'R4_Wood_Dark').box((0,0.0,1.12),(2.7,0.8,0.05),'R4_Marble_White').box((0,0.38,0.5),(2.4,0.03,0.7),'R4_Brass_Satin')
p.box((0,-0.55,0.48),(0.55,0.55,0.06),'R4_Leather_Charcoal').box((0,-0.82,0.8),(0.55,0.08,0.55),'R4_Leather_Charcoal').bar((0,-0.55,0.03),(0,-0.55,0.45),0.03,'R6_Steel_Brushed')
p.box((0.6,0.0,1.3),(0.5,0.02,0.32),'R4_Glass_Black_TV',rot=(0,0,0))
put(p,(37.8,-10.8,0.62),math.pi)
put(sofa('Club_FURN_GF_Lobby_Sofa',2.0,'R4_Fabric_taupe'),(39.0,-12.6,0.62),-D)
put(armchair('Club_FURN_GF_Lobby_Armchair_01','R4_Fabric_taupe'),(37.8,-14.7,0.62),math.pi)
put(coffee_table('Club_FURN_GF_Lobby_CoffeeTable'),(38.0,-13.0,0.62),0)
put(potted_plant('Club_DECOR_GF_Lobby_Plant_01',1.4),(39.4,-15.4,0.62),0,cdec)
put(potted_plant('Club_DECOR_GF_Lobby_Plant_02',1.2),(32.7,-10.6,0.62),0,cdec)
# lobby ceiling with downlights (white panel at 4.2)
p=Piece('Club_CEIL_GF_Lobby'); p.box((36,-13,4.19),(7.9,5.9,0.03),'R4_Paint_Ceiling'); put(p,(0,0,0),0,cfx,0)
p=Piece('Club_CEIL_GF_Changing'); p.box((44,-13,4.19),(7.9,5.9,0.03),'R4_Paint_Ceiling'); put(p,(0,0,0),0,cfx,0)
dl=put(downlight('Club_FIX_GF_Lobby_Downlight_01'),(34.5,-11.5,4.17),0,cfx,0)
rep(dl,'Club_FIX_GF_Lobby_Downlight',[(37.5,-11.5,0),(34.5,-14.5,0),(37.5,-14.5,0),(39.0,-13.0,0),(42,-11.5,0),(45,-11.5,0),(42,-14.5,0),(45,-14.5,0)],cfx)
# stair railings
def rail_pts(p,pts,h=0.95):
    for a,b2 in zip(pts[:-1],pts[1:]):
        p.bar((a[0],a[1],a[2]+h),(b2[0],b2[1],b2[2]+h),0.03,'R4_Wood_Handrail',seg=8)
        n=max(2,int(math.hypot(b2[0]-a[0],b2[1]-a[1])/0.14))
        for i in range(n+1):
            t_=i/n; x=a[0]+(b2[0]-a[0])*t_; y=a[1]+(b2[1]-a[1])*t_; z=a[2]+(b2[2]-a[2])*t_
            p.bar((x,y,z),(x,y,z+h),0.009,'R6_Alu_Graphite',seg=6)
    for a in pts: p.bar((a[0],a[1],a[2]),(a[0],a[1],a[2]+h),0.025,'R6_Alu_Graphite',seg=8)
p=Piece('Club_RAIL_Stair_GF_FF')
rail_pts(p,[(34.4,-15.6,0.6),(34.4,-12.52,2.55)])      # flight A inner edge
rail_pts(p,[(35.0,-12.52,2.55),(35.0,-15.6,4.5)])      # flight B inner edge (rises toward -y)
rail_pts(p,[(34.4,-12.52,2.55),(34.4,-10.4,2.55),(35.0,-10.4,2.55),(35.0,-12.52,2.55)],0.95)
rail_pts(p,[(33.0,-15.6,0.6),(33.0,-12.52,2.55),(33.0,-10.4,2.55)])
rail_pts(p,[(36.4,-15.6,4.5),(36.4,-12.52,2.55),(36.4,-10.4,2.55)])
p.build((0,0,0),0,coll('10_Club_Railings'),PAR,bevel=0)
print('GF done')
