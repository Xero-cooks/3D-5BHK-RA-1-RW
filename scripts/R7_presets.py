import bpy, math, os
HD=r'C:\Users\User\Documents\3D-5BHK-RA-1-RW\assets\hdri'
PRESETS={
 'GOLDEN':dict(hdri='qwantani_late_afternoon_puresky',az_local=143.9,az_target=-126.9,strength=1.0,sun=0.0,exp=-0.3,ext=0.0,intf=0.25),
 'DAY':dict(hdri='kloofendal_misty_morning_puresky',az_local=None,az_target=-126.9,strength=1.0,sun=0.0,exp=-0.3,ext=0.0,intf=0.35),
 'DUSK':dict(hdri='qwantani_dusk_2_puresky',az_local=None,az_target=-126.9,strength=1.0,sun=0.0,exp=0.0,ext=1.0,intf=1.0),
 'NIGHT':dict(hdri='qwantani_dusk_2_puresky',az_local=None,az_target=-126.9,strength=0.02,sun=0.0,exp=0.0,ext=1.0,intf=1.0),
}
def build_world():
    w=bpy.data.worlds.get('R7_World') or bpy.data.worlds.new('R7_World')
    w.use_nodes=True
    nt=w.node_tree; nt.nodes.clear()
    tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping'); mp.name='R7_map'
    env=nt.nodes.new('ShaderNodeTexEnvironment'); env.name='R7_env'
    bg=nt.nodes.new('ShaderNodeBackground'); bg.name='R7_bg'
    out=nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'],mp.inputs['Vector']); nt.links.new(mp.outputs[0],env.inputs['Vector'])
    nt.links.new(env.outputs['Color'],bg.inputs['Color']); nt.links.new(bg.outputs[0],out.inputs[0])
    return w
def apply(name):
    sc=bpy.context.scene; P=PRESETS[name]
    w=bpy.data.worlds.get('R7_World') or build_world()
    sc.world=w; nt=w.node_tree
    env=nt.nodes['R7_env']
    p=os.path.join(HD,P['hdri']+'_4k.hdr')
    env.image=bpy.data.images.load(p,check_existing=True)
    az=P['az_local'] if P['az_local'] is not None else 140.0
    r=P['az_target']-az
    nt.nodes['R7_map'].inputs['Rotation'].default_value=(0,0,math.radians(r))
    nt.nodes['R7_bg'].inputs['Strength'].default_value=P['strength']
    sc.view_settings.exposure=P['exp']
    sc['r4_time']=name; sc['r7_preset']=name
    for o in bpy.data.objects:
        if o.type!='LIGHT': continue
        be=o.data.get('base_energy')
        col=o.users_collection[0].name.split('/')[-1]
        if col=='17_Lighting_Interior':
            if be is None: o.data['base_energy']=be=o.data.energy
            o.data.energy=be*P['intf']
        elif col in('17_Lighting_Exterior','17_Lighting_Pool'):
            if be is None or be==0: be=o.data.get('r7_on',40.0); o.data['r7_on']=be
            o.data.energy=be*P['ext']; o.hide_render=P['ext']==0; o.hide_viewport=P['ext']==0
    sd=bpy.data.objects['LIGHT_Sun_Daylight']; sd.data.energy=P['sun']
    return name
