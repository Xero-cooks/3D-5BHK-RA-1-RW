purge('POOL_Coping','POOL_Grate','POOL_Ladder','POOL_Step')
def add_bump(m,scale=40.0,strength=0.15,detail=8.0):
    nt=m.node_tree; b=nt.nodes.get('Principled BSDF')
    if nt.nodes.get('R6_bump'): return
    tc=nt.nodes.new('ShaderNodeTexCoord'); n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=detail
    bp=nt.nodes.new('ShaderNodeBump'); bp.name='R6_bump'; bp.inputs['Strength'].default_value=strength; bp.inputs['Distance'].default_value=0.02
    nt.links.new(tc.outputs['Object'],n.inputs['Vector']); nt.links.new(n.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
cm=pm('R6_Stone_Coping_Dark',(0.085,0.09,0.10,1),0.62); add_bump(cm,60,0.25)
# grate material: white with dark transverse slits
gm=bpy.data.materials.get('R6_Pool_Grate')
if not gm:
    gm=pm('R6_Pool_Grate',(0.9,0.9,0.9,1),0.45); nt=gm.node_tree; b=nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord'); w=nt.nodes.new('ShaderNodeTexWave'); w.wave_type='BANDS'; w.bands_direction='DIAGONAL'; w.inputs['Scale'].default_value=34; w.inputs['Distortion'].default_value=0
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.45; cr.color_ramp.elements[1].position=0.55
    cr.color_ramp.elements[0].color=(0.02,0.025,0.03,1); cr.color_ramp.elements[1].color=(0.88,0.9,0.9,1)
    nt.links.new(tc.outputs['Object'],w.inputs['Vector']); nt.links.new(w.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
cp=coll('15_Pool_Coping')
x0,x1,y0,y1=6.0,30.0,-26.0,-14.0; zt=0.12; cw=0.5; gw=0.25
p=Piece('POOL_Coping_Stone')
p.box(((x0+x1)/2,y1+gw+cw/2,zt/2+0.0),(x1-x0+2*(gw+cw),cw,zt),'R6_Stone_Coping_Dark')
p.box(((x0+x1)/2,y0-gw-cw/2,zt/2),(x1-x0+2*(gw+cw),cw,zt),'R6_Stone_Coping_Dark')
p.box((x0-gw-cw/2,(y0+y1)/2,zt/2),(cw,y1-y0,zt),'R6_Stone_Coping_Dark')
p.box((x1+gw+cw/2,(y0+y1)/2,zt/2),(cw,y1-y0,zt),'R6_Stone_Coping_Dark')
p.build((0,0,0),0,cp,'BLD_Clubhouse' if False else None,bevel=0.01)
p=Piece('POOL_Grate_Channel')
p.box(((x0+x1)/2,y1+gw/2,zt/2-0.01),(x1-x0,gw,zt+0.0),'R6_Pool_Grate'); p.box(((x0+x1)/2,y0-gw/2,zt/2-0.01),(x1-x0,gw,zt),'R6_Pool_Grate')
p.box((x0-gw/2,(y0+y1)/2,zt/2-0.01),(gw,y1-y0+2*gw,zt),'R6_Pool_Grate'); p.box((x1+gw/2,(y0+y1)/2,zt/2-0.01),(gw,y1-y0+2*gw,zt),'R6_Pool_Grate')
p.build((0,0,0),0,cp,None,bevel=0.004)
# steel ladders (north edge, two) + diagonal corner step marker
def ladder(name,x,y):
    p=Piece(name)
    for dx in (-0.25,0.25):
        p.bar((x+dx,y+0.45,0.14),(x+dx,y+0.45,0.95),0.022,'R4_Chrome',seg=10)
        p.bar((x+dx,y+0.45,0.95),(x+dx,y+0.2,1.0),0.022,'R4_Chrome',seg=10).bar((x+dx,y+0.2,1.0),(x+dx,y-0.12,0.95),0.022,'R4_Chrome',seg=10)
        p.bar((x+dx,y-0.12,0.95),(x+dx,y-0.12,-0.95),0.022,'R4_Chrome',seg=10)
    for k in range(4):
        z=-0.15-k*0.28; p.bar((x-0.25,y-0.12,z),(x+0.25,y-0.12,z),0.014,'R4_Chrome',seg=8)
    return p.build((0,0,0),0,cp,None,bevel=0)
ladder('POOL_Ladder_N1',12.0,y1); ladder('POOL_Ladder_N2',24.0,y1)
# housekeeping: normalise POOL_Light scales
for o in bpy.data.objects:
    if o.name.startswith('POOL_Light_') and o.type=='MESH' and any(abs(s-1)>1e-6 for s in o.scale):
        o.data.transform(Matrix.Diagonal((o.scale[0],o.scale[1],o.scale[2],1.0))); o.scale=(1,1,1)
print('pool done')
