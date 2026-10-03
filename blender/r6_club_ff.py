purge('Club_FURN_FF','Club_DECOR_FF','Club_FIX_FF','Club_CEIL_FF','Club_RAIL_Void')
cf=coll('12_Club_Furniture'); cdec=coll('13_Club_Decor'); cfx=coll('17_Club_Fixtures'); crl=coll('10_Club_Railings')
PAR='BLD_Clubhouse'; D=math.pi/2; Z=4.52
def put(p,loc,rz=0.0,col=cf,bevel=0.004): return p.build(loc,rz,col,PAR,bevel=bevel)
def rep(src,base,pts,col=cf):
    return [place(src,f'{base}_{i+2:02d}',(x,y,src.location.z),rz,col,PAR) for i,(x,y,rz) in enumerate(pts)]
def wp(name,x0,x1,y,z0,z1,mat,t=0.02,col=cdec):
    p=Piece(name); p.box(((x0+x1)/2,y,(z0+z1)/2),(x1-x0,t,z1-z0),mat); return p.build((0,0,0),0,col,PAR,bevel=0)
# ---------- STUDIO (x32..42,y-26..-16): cardio + spin ----------
t=put(treadmill('Club_FURN_FF_Studio_Treadmill_01'),(33.8,-17.7,Z),0)
rep(t,'Club_FURN_FF_Studio_Treadmill',[(35.2,-17.7,0),(36.6,-17.7,0)])
e=put(elliptical('Club_FURN_FF_Studio_Elliptical_01'),(40.4,-17.6,Z),0)
rep(e,'Club_FURN_FF_Studio_Elliptical',[(41.35,-17.6,0)])
s=put(spinbike('Club_FURN_FF_Studio_SpinBike_01'),(34.0,-21.6,Z),0)
rep(s,'Club_FURN_FF_Studio_SpinBike',[(35.3,-21.6,0),(36.6,-21.6,0),(37.9,-21.6,0),(34.0,-23.6,0),(35.3,-23.6,0),(36.6,-23.6,0),(37.9,-23.6,0)])
put(spinbike('Club_FURN_FF_Studio_SpinBike_Instructor'),(36.0,-25.0,Z),math.pi)
wp('Club_DECOR_FF_Studio_Mirror_W',32.4,37.6,-16.08,Z+0.5,Z+2.8,'R4_Mirror')
wp('Club_DECOR_FF_Studio_Mirror_E',39.7,41.8,-16.08,Z+0.5,Z+2.8,'R4_Mirror')
wp('Club_DECOR_FF_Studio_Skirting',32.1,41.9,-16.08,Z,Z+0.5,'R4_Paint_White',0.015)
# ---------- MULTI-PURPOSE / YOGA (x42..48,y-26..-16) ----------
m=put(mat_yoga('Club_FURN_FF_Multi_YogaMat_01','R6_Yoga_Mat_Teal'),(43.4,-19.5,Z),0,bevel=0)
rep(m,'Club_FURN_FF_Multi_YogaMat',[(44.4,-19.5,0),(45.4,-19.5,0),(46.4,-19.5,0)])
m2=put(mat_yoga('Club_FURN_FF_Multi_YogaMat_05','R6_Yoga_Mat_Plum'),(43.4,-22.5,Z),0,bevel=0)
rep(m2,'Club_FURN_FF_Multi_YogaMat_B',[(44.4,-22.5,0),(45.4,-22.5,0),(46.4,-22.5,0)])
p=Piece('Club_FURN_FF_Multi_BallsAndBlocks')
for i,x in enumerate((0,0.8,1.6)): p.sph((x,0,0.37),0.37,'R4_Plastic_Blue' if i!=1 else 'R4_Plastic_Purple',seg=16)
for i in range(3): p.box((2.6+i*0.3,0,0.1),(0.22,0.14,0.2),'R4_Plastic_Pink')
put(p,(43.3,-25.0,Z),0)
p=Piece('Club_FURN_FF_Multi_StorageShelf')
p.box((0,0,1.0),(0.45,3.0,2.0),'R4_Laminate_White')
for k in range(4): p.box((0.0,0,0.5+k*0.45),(0.47,2.9,0.03),'R4_Wood_Med')
for i in range(6): p.box((0.02,-1.2+i*0.45,0.7),(0.3,0.3,0.28),'R4_Plastic_PVC_Grey')
put(p,(47.75,-22.0,Z),0)
wp('Club_DECOR_FF_Multi_Mirror',42.4,47.0,-16.08,Z+0.5,Z+2.8,'R4_Mirror')
# ---------- GAMES LOUNGE (x32..48,y-16..-10) ----------
p=Piece('Club_FURN_FF_Games_SnookerTable'); L,Wd=3.85,1.95
p.box((0,0,0.72),(L,Wd,0.14),'R6_Mahogany').box((0,0,0.8),(L-0.45,Wd-0.45,0.045),'R6_Baize_Green')
p.box((0,0,0.78),(L-0.2,Wd-0.2,0.07),'R6_Baize_Green')
for sx in (-1,1): p.box((sx*(L/2-0.11),0,0.82),(0.18,Wd,0.1),'R6_Mahogany'); 
for sy in (-1,1): p.box((0,sy*(Wd/2-0.11),0.82),(L,0.18,0.1),'R6_Mahogany')
p.box((0,0,0.5),(L-0.3,Wd-0.3,0.3),'R6_Mahogany')
for sx in (-1,1):
    for sy in (-1,1):
        x,y=sx*(L/2-0.3),sy*(Wd/2-0.25)
        p.cyl((x,y,0.33),0.13,0.66,'R6_Mahogany',seg=14,r2=0.1).sph((x,y,0.45),0.15,'R6_Mahogany',seg=12)
for sy in (-1,1):
    for sx in (-1,0,1): p.sph((sx*(L/2-0.1) if sx else 0,sy*(Wd/2-0.1),0.86),0.065,'R6_Machine_Black',seg=8)
cols=['R4_Plastic_Red','R4_Plastic_Yellow','R4_Plastic_White']
import random; rnd=random.Random(7)
for i in range(15): p.sph((0.5+0.12*(i%5)-0.0, (i//5-1)*0.12+0.0 if False else rnd.uniform(-0.1,0.1),0.855),0.026,cols[i%3] if i<14 else 'R4_Plastic_Pink',seg=8)
put(p,(41.0,-13.0,Z),0,bevel=0.003)
p=Piece('Club_FIX_FF_Games_SnookerLamp'); p.box((0,0,0),(2.6,0.35,0.06),'R6_Panel_Light'); p.box((0,0,0.1),(2.7,0.45,0.1),'R6_Mahogany')
for sx in (-1,1): p.bar((sx*1.2,0,0.15),(sx*1.2,0,3.0),0.008,'R6_Steel_Brushed')
put(p,(41.0,-13.0,Z+2.55),0,cfx,0.002)
p=Piece('Club_DECOR_FF_Games_CueRack')
p.box((0,0,1.0),(0.06,0.9,1.5),'R6_Mahogany')
for i in range(5): p.bar((0.05,-0.35+i*0.17,0.35),(0.05,-0.35+i*0.17,1.55),0.012,'R4_Wood_Med',seg=6)
put(p,(47.85,-15.2,Z),0,cdec)
put(sofa('Club_FURN_FF_Games_Sofa_01',2.2,'R4_Fabric_grey'),(34.8,-14.9,Z),0)
put(sofa('Club_FURN_FF_Games_Sofa_02',2.2,'R4_Fabric_grey'),(34.8,-11.2,Z),math.pi)
put(coffee_table('Club_FURN_FF_Games_CoffeeTable'),(34.8,-13.0,Z),D)
put(armchair('Club_FURN_FF_Games_Armchair_01','R4_Fabric_charcoal'),(33.3,-14.3,Z),-D)
put(armchair('Club_FURN_FF_Games_Armchair_02','R4_Fabric_charcoal'),(33.3,-11.7,Z),-D)
put(potted_plant('Club_DECOR_FF_Games_Plant_01',1.5),(47.3,-10.6,Z),0,cdec)
# high bar table + stools
p=Piece('Club_FURN_FF_Games_BarTable'); p.cyl((0,0,1.08),0.45,0.04,'R4_Wood_Dark',seg=20).bar((0,0,0.03),(0,0,1.06),0.035,'R6_Steel_Brushed').cyl((0,0,0.02),0.25,0.03,'R6_Steel_Brushed',seg=16)
for a in (0,2.1,4.2): 
    sx,sy=0.75*math.cos(a),0.75*math.sin(a); p.cyl((sx,sy,0.7),0.2,0.05,'R4_Leather_Charcoal',seg=14).bar((sx,sy,0.03),(sx,sy,0.68),0.025,'R6_Steel_Brushed')
put(p,(45.6,-12.4,Z),0)
p=Piece('Club_FURN_FF_Games_TV'); p.box((0,0,1.2),(0.05,1.5,0.85),'R4_Glass_Black_TV'); p.box((0,0,0.35),(0.4,1.8,0.7),'R4_Wood_Dark')
put(p,(47.8,-12.9,Z),0)
# ---------- CEILINGS, ACs, LIGHTS ----------
for nm,(x0,x1,y0,y1) in {'Studio':(32,42,-26,-16),'Multi':(42,48,-26,-16),'Games':(32,48,-16,-10)}.items():
    p=Piece(f'Club_CEIL_FF_{nm}'); p.box(((x0+x1)/2,(y0+y1)/2,8.07),(x1-x0-0.1,y1-y0-0.1,0.03),'R4_Paint_Ceiling'); put(p,(0,0,0),0,cfx,0)
ac=put(ac_cassette('Club_FIX_FF_Studio_AC_01'),(35.0,-19.5,8.03),0,cfx)
rep(ac,'Club_FIX_FF_Studio_AC',[(35.0,-23.5,0),(39.0,-19.5,0),(39.0,-23.5,0),(45.0,-19.5,0),(45.0,-23.5,0),(36.0,-13.0,0),(44.0,-13.0,0)],cfx)
dl=put(downlight('Club_FIX_FF_Downlight_01'),(33.5,-18.0,8.07),0,cfx,0)
pts=[(x,y,0) for x in (33.5,37,40.5) for y in (-18.0,-22.0,-25.0)]+[(x,y,0) for x in (44,46.5) for y in (-18.5,-21.5,-24.5)]+[(x,y,0) for x in (33.5,37,45,47) for y in (-15,-11.3)]
rep(dl,'Club_FIX_FF_Downlight',pts[1:],cfx)
# glass balustrade around stair void (east edge x=36.5) + return along north? (north is wall)
p=Piece('Club_RAIL_Void_FF_Glass')
p.box((0,0.0,0.55),(0.012,5.2,1.0),'R4_Glass_Clear').box((0,0,1.1),(0.05,5.25,0.04),'R6_Steel_Brushed').box((0,0,0.04),(0.06,5.25,0.08),'R6_Steel_Brushed')
for yy in (-2.6,0,2.6): p.bar((0,yy,0),(0,yy,1.1),0.02,'R6_Steel_Brushed')
put(p,(36.5,-12.95,Z),0,crl,0)
print('FF done')
