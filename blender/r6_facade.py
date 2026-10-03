purge('Club_FACADE','Club_SIGN')
cdet=coll('02_Club_Facade_Details'); PAR='BLD_Clubhouse'
pm('R6_Brass_Sign',(0.75,0.55,0.2,1),0.3,1.0)
# coping cap on parapets
p=Piece('Club_FACADE_Coping')
x0,x1,y0,y1=31.8,48.2,-26.2,-9.8; zc=9.23
p.box(((x0+x1)/2,y0+0.1,zc),(x1-x0,0.34,0.07),'R6_Alu_Graphite').box(((x0+x1)/2,y1-0.1,zc),(x1-x0,0.34,0.07),'R6_Alu_Graphite')
p.box((x0+0.1,(y0+y1)/2,zc),(0.34,y1-y0-0.6,0.07),'R6_Alu_Graphite').box((x1-0.1,(y0+y1)/2,zc),(0.34,y1-y0-0.6,0.07),'R6_Alu_Graphite')
p.build((0,0,0),0,cdet,PAR,bevel=0.004)
# slab-edge band between floors (graphite) on all four facades
p=Piece('Club_FACADE_FloorBand')
zb=4.35
p.box((40,-26.17,zb),(16.5,0.08,0.3),'R6_Alu_Graphite').box((40,-9.83,zb),(16.5,0.08,0.3),'R6_Alu_Graphite')
p.box((31.83,-18,zb),(0.08,16.5,0.3),'R6_Alu_Graphite').box((48.17,-18,zb),(0.08,16.5,0.3),'R6_Alu_Graphite')
p.build((0,0,0),0,cdet,PAR,bevel=0.004)
# stone feature columns flanking the entrance (west facade)
p=Piece('Club_FACADE_StoneFeature')
for (ya,yb) in ((-11.7,-10.2),(-15.9,-14.8)):
    p.box((31.77,(ya+yb)/2,4.35),(0.2,yb-ya,7.5),'R4_Panel_Stone_Cladding')
p.box((31.77,-13.25,8.0),(0.2,3.2,0.35),'R4_Panel_Stone_Cladding')
p.build((0,0,0),0,cdet,PAR,bevel=0.005)
# vertical fins on south facade between ribbon windows
p=Piece('Club_FACADE_Fins_South')
for i in range(9): p.box((34+i*1.5,-26.2,4.1),(0.1,0.22,7.4),'R6_Alu_Graphite')
p.build((0,0,0),0,cdet,PAR,bevel=0.003)
# sign (editable text object)
cu=bpy.data.curves.new('Club_SIGN_Text','FONT'); cu.body='RA-1 CLUBHOUSE'; cu.size=0.45; cu.extrude=0.02; cu.align_x='CENTER'; cu.align_y='CENTER'
ob=bpy.data.objects.new('Club_SIGN_Name',cu); cdet.objects.link(ob)
ob.location=(31.62,-13.25,3.95); ob.rotation_euler=(math.pi/2,0,-math.pi/2); ob.parent=bpy.data.objects[PAR]
cu.materials.append(bpy.data.materials['R6_Brass_Sign'])
print('facade done')
