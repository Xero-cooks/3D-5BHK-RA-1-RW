purge('Club_FURN_GF_Chg','Club_DECOR_GF_Chg','Club_FIX_GF_Chg','LT_Room_GF_Club','LT_Room_FF_Club')
pm('R6_Locker_Blue',(0.10,0.17,0.24,1),0.35,0.6); pm('R6_Locker_Grey',(0.45,0.47,0.50,1),0.35,0.6)
cf=coll('12_Club_Furniture'); cdec=coll('13_Club_Decor'); cfx=coll('17_Club_Fixtures'); PAR='BLD_Clubhouse'; D=math.pi/2
def put(p,loc,rz=0.0,col=cf,bevel=0.004): return p.build(loc,rz,col,PAR,bevel=bevel)
# lockers (south wall of changing room, y centre -15.62, front faces +y)
p=Piece('Club_FURN_GF_Chg_Lockers')
for i in range(14):
    x=-2.95+i*0.4538+0.0; m='R6_Locker_Blue' if i%2==0 else 'R6_Locker_Grey'
    p.box((x,0,0.9),(0.44,0.5,1.8),m).box((x,0.256,1.45),(0.3,0.01,0.02),'R6_Steel_Brushed').box((x,0.256,0.35),(0.3,0.01,0.02),'R6_Steel_Brushed')
    p.bar((x+0.14,0.265,0.95),(x+0.14,0.265,1.12),0.01,'R6_Steel_Brushed',seg=6)
    p.box((x,0.256,1.7),(0.3,0.01,0.04),'R4_Paper')
put(p,(44.0,-15.65,0.62),0)
p=Piece('Club_FURN_GF_Chg_Bench')
for k in range(5): p.box((0,-0.18+k*0.09,0.45),(3.8,0.075,0.04),'R4_Wood_Teak')
for sx in (-1.7,0,1.7): p.box((sx,0,0.22),(0.05,0.5,0.44),'R6_Steel_Brushed')
put(p,(44.0,-14.0,0.62),0)
# vanity on east wall
p=Piece('Club_FURN_GF_Chg_Vanity'); p.box((0,0,0.42),(0.55,2.4,0.8),'R4_Wood_Dark').box((0,0,0.84),(0.6,2.5,0.04),'R4_Marble_White')
for yy in (-0.6,0.6):
    p.cyl((0,yy,0.86),0.2,0.05,'R4_Ceramic_White',seg=20)
    p.bar((0.2,yy,0.88),(0.2,yy,1.05),0.012,'R4_Chrome',seg=6).bar((0.2,yy,1.05),(0.1,yy,1.05),0.012,'R4_Chrome',seg=6)
p.box((0.27,0,1.6),(0.02,2.3,1.0),'R4_Mirror')
put(p,(47.55,-13.7,0.62),0)
# shower cubicles (north-east corner)
p=Piece('Club_FIX_GF_Chg_ShowerCubicles')
for i in range(3):
    x=-0.9+i*0.9
    p.box((x,0,0.01),(0.88,1.18,0.02),'R4_Floor_Tile_Bath')
    p.box((x,0.55,1.0),(0.86,0.012,2.0),'R4_Glass_Frosted')
    p.box((x+0.45,0,1.05),(0.03,1.2,2.1),'R4_Laminate_White') if i<2 else None
    p.bar((x,-0.55,1.9),(x,-0.4,2.05),0.012,'R4_Chrome',seg=6).cyl((x,-0.38,2.07),0.07,0.02,'R4_Chrome',seg=14)
    p.cyl((x+0.25,-0.58,1.1),0.035,0.03,'R4_Chrome',axis='Y',seg=12)
p.box((-1.35,0,1.05),(0.03,1.2,2.1),'R4_Laminate_White')
put(p,(46.6,-10.7,0.62),0,cfx,0.003)
p=Piece('Club_DECOR_GF_Chg_Mirror_Wall'); p.box((0,0,0),(0.02,1.2,0.9),'R4_Mirror'); put(p,(47.88,-11.6,1.3),0,cdec,0)
# --- club lights (read by r4_light.set_time via r4 / base_energy; name must start LT_Room)
L=bpy.data.collections['17_Lighting_Interior']
def alight(nm,x0,x1,y0,y1,z,nx,ny,w,col):
    area=(x1-x0)*(y1-y0); base=w*area/(nx*ny)
    for i in range(nx):
        for j in range(ny):
            n=f'{nm}_{i}{j}'
            d=bpy.data.lights.new(n,'AREA'); d.shape='RECTANGLE'; d.size=(x1-x0)/nx*0.5; d.size_y=(y1-y0)/ny*0.5
            d.color=col; d.energy=base*0.5; d['base_energy']=base
            ob=bpy.data.objects.new(n,d); ob.location=(x0+(i+0.5)*(x1-x0)/nx,y0+(j+0.5)*(y1-y0)/ny,z); L.objects.link(ob); ob['r4']=1; ob.parent=bpy.data.objects[PAR]
warm=(1.0,0.88,0.72); neu=(1.0,0.93,0.84); wet=(1.0,0.9,0.78)
alight('LT_Room_GF_Club_Gym',32,48,-26,-16,3.7,4,2,15,neu)
alight('LT_Room_GF_Club_Lobby',32,40,-16,-10,3.9,2,2,17,warm)
alight('LT_Room_GF_Club_Changing',40,48,-16,-10,3.9,2,2,22,wet)
alight('LT_Room_FF_Club_Studio',32,42,-26,-16,7.85,2,2,16,neu)
alight('LT_Room_FF_Club_Multi',42,48,-26,-16,7.85,2,2,16,neu)
alight('LT_Room_FF_Club_Games',32,48,-16,-10,7.85,4,1,15,warm)
print('gf2 + lights done')
