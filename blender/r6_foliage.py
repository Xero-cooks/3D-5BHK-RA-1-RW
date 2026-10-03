"""Round 6: procedural foliage (Geometry Nodes leaf-card scatter) + leaf-card materials."""
import bpy, math

def leaf_card_material(name, base_a, base_b, rough=0.55, trans=0.15):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    N.clear()
    out = N.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    pb = N.new('ShaderNodeBsdfPrincipled'); pb.location = (400, 100)
    pb.inputs['Roughness'].default_value = rough
    try: pb.inputs['Specular IOR Level'].default_value = 0.3
    except Exception: pass
    for k in ('Transmission Weight',):
        if k in pb.inputs: pb.inputs[k].default_value = trans
    tr = N.new('ShaderNodeBsdfTransparent'); tr.location = (400, -200)
    mix = N.new('ShaderNodeMixShader'); mix.location = (700, 0)
    uv = N.new('ShaderNodeTexCoord'); uv.location = (-1100, -250)
    sb = N.new('ShaderNodeVectorMath'); sb.operation = 'SUBTRACT'; sb.inputs[1].default_value = (0.5, 0.5, 0.0); sb.location = (-900, -250)
    sc_ = N.new('ShaderNodeVectorMath'); sc_.operation = 'MULTIPLY'; sc_.inputs[1].default_value = (3.4, 2.0, 1.0); sc_.location = (-700, -250)
    ln = N.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; ln.location = (-500, -250)
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 7; nz.location = (-700, -500)
    wr = N.new('ShaderNodeMath'); wr.operation = 'MULTIPLY_ADD'; wr.inputs[1].default_value = 0.35; wr.location = (-300, -400)
    lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 1.0; lt.location = (-100, -300)
    L.new(uv.outputs['UV'], sb.inputs[0]); L.new(sb.outputs[0], sc_.inputs[0]); L.new(sc_.outputs[0], ln.inputs[0])
    L.new(uv.outputs['UV'], nz.inputs['Vector'])
    L.new(nz.outputs['Fac'], wr.inputs[0])
    wr.inputs[2].default_value = 0.0
    sub2 = N.new('ShaderNodeMath'); sub2.operation = 'SUBTRACT'; sub2.location = (-300, -250)
    L.new(ln.outputs['Value'], sub2.inputs[0]); L.new(wr.outputs[0], sub2.inputs[1])
    L.new(sub2.outputs[0], lt.inputs[0])
    oi = N.new('ShaderNodeObjectInfo'); oi.location = (-700, 200)
    ramp = N.new('ShaderNodeValToRGB'); ramp.location = (-400, 200)
    ramp.color_ramp.elements[0].color = base_a
    ramp.color_ramp.elements[1].color = base_b
    # per-leaf variation via noise on position
    gp = N.new('ShaderNodeNewGeometry'); gp.location = (-900, 0)
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 1.6; n2.inputs['Detail'].default_value = 4; n2.location = (-700, 0)
    mx2 = N.new('ShaderNodeMath'); mx2.operation = 'ADD'; mx2.location = (-200, 200)
    L.new(oi.outputs['Random'], mx2.inputs[0]); L.new(n2.outputs['Fac'], mx2.inputs[1])
    mx2.inputs[1].default_value = 0.0
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.5; mul.location = (-50, 200)
    L.new(mx2.outputs[0], mul.inputs[0]); L.new(mul.outputs[0], ramp.inputs['Fac'])
    L.new(gp.outputs['Position'], n2.inputs['Vector'])
    L.new(ramp.outputs['Color'], pb.inputs['Base Color'])
    L.new(lt.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(pb.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m

def make_group():
    if 'R6_FoliageScatter' in bpy.data.node_groups:
        return bpy.data.node_groups['R6_FoliageScatter']
    g = bpy.data.node_groups.new('R6_FoliageScatter', 'GeometryNodeTree')
    I = g.interface
    I.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    s = I.new_socket('Density', in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = 60.0
    s = I.new_socket('Leaf Size', in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = 0.2
    s = I.new_socket('Seed', in_out='INPUT', socket_type='NodeSocketInt'); s.default_value = 1
    I.new_socket('Leaf Material', in_out='INPUT', socket_type='NodeSocketMaterial')
    I.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = g.nodes; L = g.links
    gi = N.new('NodeGroupInput'); gi.location = (-1200, 0)
    go = N.new('NodeGroupOutput'); go.location = (1400, 0)
    dist = N.new('GeometryNodeDistributePointsOnFaces'); dist.distribute_method = 'RANDOM'; dist.location = (-600, 100)
    isv = N.new('GeometryNodeIsViewport'); isv.location = (-1000, -250)
    sw = N.new('GeometryNodeSwitch'); sw.input_type = 'FLOAT'; sw.location = (-800, -200)
    vdens = N.new('ShaderNodeMath'); vdens.operation = 'MULTIPLY'; vdens.inputs[1].default_value = 0.12; vdens.location = (-1000, -400)
    L.new(gi.outputs['Density'], vdens.inputs[0])
    L.new(isv.outputs[0], sw.inputs['Switch'])
    L.new(gi.outputs['Density'], sw.inputs['False']); L.new(vdens.outputs[0], sw.inputs['True'])
    L.new(gi.outputs['Geometry'], dist.inputs['Mesh']); L.new(sw.outputs[0], dist.inputs['Density']); L.new(gi.outputs['Seed'], dist.inputs['Seed'])
    # leaf card
    grid = N.new('GeometryNodeMeshGrid'); grid.location = (-600, -300)
    grid.inputs['Vertices X'].default_value = 2; grid.inputs['Vertices Y'].default_value = 2
    L.new(gi.outputs['Leaf Size'], grid.inputs['Size X']); L.new(gi.outputs['Leaf Size'], grid.inputs['Size Y'])
    sto = N.new('GeometryNodeStoreNamedAttribute'); sto.data_type = 'FLOAT2'; sto.domain = 'CORNER'; sto.location = (-400, -300)
    sto.inputs['Name'].default_value = 'UVMap'
    L.new(grid.outputs['Mesh'], sto.inputs['Geometry']); L.new(grid.outputs['UV Map'], sto.inputs['Value'])
    sm = N.new('GeometryNodeSetMaterial'); sm.location = (-200, -300)
    L.new(sto.outputs[0], sm.inputs['Geometry']); L.new(gi.outputs['Leaf Material'], sm.inputs['Material'])
    inst = N.new('GeometryNodeInstanceOnPoints'); inst.location = (200, 0)
    L.new(dist.outputs['Points'], inst.inputs['Points']); L.new(sm.outputs[0], inst.inputs['Instance'])
    L.new(dist.outputs['Rotation'], inst.inputs['Rotation'])
    # random scale
    rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.location = (-200, 150)
    rs.inputs['Min'].default_value = 0.6; rs.inputs['Max'].default_value = 1.5
    L.new(gi.outputs['Seed'], rs.inputs['Seed'])
    comb = N.new('ShaderNodeCombineXYZ'); comb.location = (0, 150)
    L.new(rs.outputs['Value'], comb.inputs['X']); L.new(rs.outputs['Value'], comb.inputs['Y']); comb.inputs['Z'].default_value = 1
    L.new(comb.outputs[0], inst.inputs['Scale'])
    # random tilt/spin
    rr = N.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'; rr.location = (200, -250)
    rr.inputs['Min'].default_value = (-0.9, -0.9, 0.0); rr.inputs['Max'].default_value = (0.9, 0.9, 6.28)
    rot = N.new('GeometryNodeRotateInstances'); rot.location = (600, 0)
    L.new(inst.outputs[0], rot.inputs['Instances']); L.new(rr.outputs[0], rot.inputs['Rotation'])
    join = N.new('GeometryNodeJoinGeometry'); join.location = (1000, 0)
    L.new(gi.outputs['Geometry'], join.inputs[0]); L.new(rot.outputs[0], join.inputs[0])
    L.new(join.outputs[0], go.inputs[0])
    return g

def scatter(obj, mat, density=60, size=0.2, seed=1):
    g = make_group()
    for m in list(obj.modifiers):
        if m.name == 'R6_Foliage': obj.modifiers.remove(m)
    md = obj.modifiers.new('R6_Foliage', 'NODES'); md.node_group = g
    ids = {it.name: it.identifier for it in g.interface.items_tree if getattr(it, 'in_out', '') == 'INPUT'}
    P = md.properties.inputs
    getattr(P, ids['Density']).value = float(density); getattr(P, ids['Leaf Size']).value = float(size); getattr(P, ids['Seed']).value = int(seed)
    getattr(P, ids['Leaf Material']).value = mat
    return md
