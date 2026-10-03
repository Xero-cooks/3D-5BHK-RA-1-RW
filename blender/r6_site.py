import colorsys
# ---- lawn: de-saturate / natural palette
def retone(mname,names,ds=0.72,dv=0.92,dh=0.015):
    m=bpy.data.materials[mname]; nt=m.node_tree
    for nn in names:
        n=nt.nodes[nn]
        for idx in (6,7):
            c=n.inputs[idx].default_value; h,s,v=colorsys.rgb_to_hsv(c[0],c[1],c[2])
            if n.inputs[idx].is_linked: continue
            r,g,b=colorsys.hsv_to_rgb((h-dh)%1.0,min(1,s*ds),v*dv); n.inputs[idx].default_value=(r,g,b,1)
if not bpy.data.materials['R4_Grass_Lawn'].get('r6_retoned'):
    retone('R4_Grass_Lawn',['Mix','Mix.001','Mix.002']); bpy.data.materials['R4_Grass_Lawn']['r6_retoned']=1
if not bpy.data.materials['R4_Grass_Far'].get('r6_retoned'):
    retone('R4_Grass_Far',['Mix','Mix.001','Mix.002']); bpy.data.materials['R4_Grass_Far']['r6_retoned']=1
# ---- sky clouds
nt=bpy.context.scene.world.node_tree; N=nt.nodes; Lk=nt.links
if 'R6_cloudmix' not in N:
    norm=N['R6_norm']; sky=N['R4_Sky']; bg=N['R4_BG']
    sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(norm.outputs[0],sep.inputs[0]) if False else None
    sep=N.new('ShaderNodeSeparateXYZ'); nt.links.new(norm.outputs[0],sep.inputs[0])
    add=N.new('ShaderNodeMath'); add.operation='ADD'; add.inputs[1].default_value=0.16; nt.links.new(sep.outputs['Z'],add.inputs[0])
    mx=N.new('ShaderNodeMath'); mx.operation='MAXIMUM'; mx.inputs[1].default_value=0.06; nt.links.new(add.outputs[0],mx.inputs[0])
    dx=N.new('ShaderNodeMath'); dx.operation='DIVIDE'; nt.links.new(sep.outputs['X'],dx.inputs[0]); nt.links.new(mx.outputs[0],dx.inputs[1])
    dy=N.new('ShaderNodeMath'); dy.operation='DIVIDE'; nt.links.new(sep.outputs['Y'],dy.inputs[0]); nt.links.new(mx.outputs[0],dy.inputs[1])
    cb=N.new('ShaderNodeCombineXYZ'); nt.links.new(dx.outputs[0],cb.inputs['X']); nt.links.new(dy.outputs[0],cb.inputs['Y'])
    nz=N.new('ShaderNodeTexNoise'); nz.noise_dimensions='3D'; nz.inputs['Scale'].default_value=1.3; nz.inputs['Detail'].default_value=8; nz.inputs['Roughness'].default_value=0.62; nz.inputs['Distortion'].default_value=0.5
    nt.links.new(cb.outputs[0],nz.inputs['Vector'])
    mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.50; mr.inputs['From Max'].default_value=0.76; mr.clamp=True; nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    fd=N.new('ShaderNodeMapRange'); fd.inputs['From Min'].default_value=0.01; fd.inputs['From Max'].default_value=0.22; fd.clamp=True; nt.links.new(sep.outputs['Z'],fd.inputs['Value'])
    mm=N.new('ShaderNodeMath'); mm.operation='MULTIPLY'; nt.links.new(mr.outputs[0],mm.inputs[0]); nt.links.new(fd.outputs[0],mm.inputs[1])
    mix=N.new('ShaderNodeMix'); mix.name='R6_cloudmix'; mix.data_type='RGBA'; mix.inputs[7].default_value=(1.1,1.1,1.14,1)
    nt.links.new(mm.outputs[0],mix.inputs[0]); nt.links.new(sky.outputs[0],mix.inputs[6]); nt.links.new(mix.outputs[2],bg.inputs['Color'])
print('site done')
