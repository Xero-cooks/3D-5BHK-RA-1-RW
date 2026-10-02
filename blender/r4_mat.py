"""Round 4 - procedural PBR material library for the 5BHK residence (module r4m).
All materials are node-based, UV-free (world-space planar/triplanar projection) and named R4_*.
"""
import bpy, math, traceback

def srgb(h):
    if isinstance(h, str):
        h = h.lstrip('#'); r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    else:
        r, g, b = h[:3]
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1.0)

def shade(h, k):
    c = srgb(h); return (min(c[0] * k, 1), min(c[1] * k, 1), min(c[2] * k, 1), 1.0)

class M:
    def __init__(s, name):
        old = bpy.data.materials.get(name)
        s.mat = old if old else bpy.data.materials.new(name)
        try: s.mat.use_nodes = True
        except Exception: pass
        s.nt = s.mat.node_tree
        s.nt.nodes.clear()
        s._geo = None; s._pl = None; s.name = name
    # ---- plumbing
    def n(s, t, **kw):
        nd = s.nt.nodes.new(t)
        for k, v in kw.items(): setattr(nd, k, v)
        i = len(s.nt.nodes); nd.location = (-260 * (i % 9) - 200, -180 * (i // 9))
        return nd
    def setin(s, sock, v):
        if v is None: return
        if isinstance(v, bpy.types.NodeSocket): s.nt.links.new(v, sock)
        else:
            try: sock.default_value = v
            except TypeError: sock.default_value = tuple(v)
    def math(s, op, a, b=None, c=None, clamp=False):
        nd = s.n('ShaderNodeMath', operation=op); nd.use_clamp = clamp
        s.setin(nd.inputs[0], a)
        if b is not None: s.setin(nd.inputs[1], b)
        if c is not None: s.setin(nd.inputs[2], c)
        return nd.outputs[0]
    def vmath(s, op, a, b=None, c=None):
        nd = s.n('ShaderNodeVectorMath', operation=op)
        s.setin(nd.inputs[0], a)
        if b is not None: s.setin(nd.inputs[1], b)
        if c is not None: s.setin(nd.inputs[2], c)
        return nd.outputs[0]
    def sep(s, v):
        nd = s.n('ShaderNodeSeparateXYZ'); s.setin(nd.inputs[0], v); return nd.outputs
    def comb(s, x, y, z):
        nd = s.n('ShaderNodeCombineXYZ'); s.setin(nd.inputs[0], x); s.setin(nd.inputs[1], y); s.setin(nd.inputs[2], z); return nd.outputs[0]
    def geo(s):
        if not s._geo: s._geo = s.n('ShaderNodeNewGeometry')
        return s._geo
    def mixf(s, fac, a, b):
        return s.math('MULTIPLY_ADD', s.math('SUBTRACT', b, a), fac, a)
    def mixc(s, fac, a, b, blend='MIX'):
        nd = s.n('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        s.setin(nd.inputs[0], fac); s.setin(nd.inputs[6], a); s.setin(nd.inputs[7], b)
        return nd.outputs[2]
    def ramp(s, fac, stops, interp='LINEAR'):
        nd = s.n('ShaderNodeValToRGB'); nd.color_ramp.interpolation = interp
        el = nd.color_ramp.elements
        while len(el) < len(stops): el.new(0.5)
        for e, (p, c) in zip(el, stops):
            e.position = p; e.color = c if len(c) == 4 else (*c, 1.0)
        s.setin(nd.inputs[0], fac); return nd.outputs[0]
    def noise(s, vec, scale, detail=2.0, rough=0.5, dist=0.0):
        nd = s.n('ShaderNodeTexNoise'); nd.noise_dimensions = '3D'
        s.setin(nd.inputs['Vector'], vec); s.setin(nd.inputs['Scale'], scale); s.setin(nd.inputs['Detail'], detail)
        s.setin(nd.inputs['Roughness'], rough); s.setin(nd.inputs['Distortion'], dist)
        return nd.outputs['Fac']
    def voronoi(s, vec, scale, rnd=1.0, feature='F1', out='Distance'):
        nd = s.n('ShaderNodeTexVoronoi'); nd.voronoi_dimensions = '3D'; nd.feature = feature
        s.setin(nd.inputs['Vector'], vec); s.setin(nd.inputs['Scale'], scale); s.setin(nd.inputs['Randomness'], rnd)
        return nd.outputs[out]
    def wave(s, vec, scale, dist=2.0, detail=2.0, direction='X', wtype='BANDS', profile='SIN', dscale=1.0, drough=0.5):
        nd = s.n('ShaderNodeTexWave'); nd.wave_type = wtype; nd.bands_direction = direction; nd.wave_profile = profile
        s.setin(nd.inputs['Vector'], vec); s.setin(nd.inputs['Scale'], scale); s.setin(nd.inputs['Distortion'], dist)
        s.setin(nd.inputs['Detail'], detail); s.setin(nd.inputs['Detail Scale'], dscale); s.setin(nd.inputs['Detail Roughness'], drough)
        return nd.outputs['Fac']
    def white(s, vec):
        nd = s.n('ShaderNodeTexWhiteNoise'); nd.noise_dimensions = '3D'; s.setin(nd.inputs['Vector'], vec); return nd.outputs['Value']
    def checker(s, vec, scale):
        nd = s.n('ShaderNodeTexChecker'); s.setin(nd.inputs['Vector'], vec); s.setin(nd.inputs['Scale'], scale); return nd.outputs['Fac']
    def mapping(s, vec, scale=(1, 1, 1), loc=(0, 0, 0)):
        nd = s.n('ShaderNodeMapping'); nd.vector_type = 'POINT'
        s.setin(nd.inputs['Vector'], vec); s.setin(nd.inputs['Location'], loc); s.setin(nd.inputs['Scale'], scale); return nd.outputs[0]
    def bump(s, h, strength=0.3, dist=0.01, nrm=None):
        nd = s.n('ShaderNodeBump'); s.setin(nd.inputs['Strength'], strength); s.setin(nd.inputs['Distance'], dist)
        s.setin(nd.inputs['Height'], h)
        if nrm is not None: s.setin(nd.inputs['Normal'], nrm)
        return nd.outputs['Normal']
    def ao(s, color, dist=0.5):
        nd = s.n('ShaderNodeAmbientOcclusion'); nd.samples = 6
        s.setin(nd.inputs['Color'], color); s.setin(nd.inputs['Distance'], dist); return nd.outputs['Color']
    def objrand(s):
        nd = s.n('ShaderNodeObjectInfo'); return nd.outputs['Random']
    def gen(s):
        nd = s.n('ShaderNodeTexCoord'); return nd.outputs['Generated']
    # ---- projections
    def P(s): return s.geo().outputs['Position']
    def planar(s):
        """world-space planar UV: floors -> (x,y); walls -> (horizontal, z)."""
        if s._pl: return s._pl
        Pp = s.sep(s.P()); Nn = s.sep(s.geo().outputs['Normal'])
        horiz = s.math('GREATER_THAN', s.math('ABSOLUTE', Nn[2]), 0.7)
        wallx = s.math('GREATER_THAN', s.math('ABSOLUTE', Nn[1]), 0.5)
        wallu = s.mixf(wallx, Pp[1], Pp[0])
        U = s.mixf(horiz, wallu, Pp[0]); V = s.mixf(horiz, Pp[2], Pp[1])
        s._pl = (s.comb(U, V, 0.0), U, V); return s._pl
    def grid(s, U, V, sx, sy, gw, rows='none'):
        u = s.math('DIVIDE', U, sx); v = s.math('DIVIDE', V, sy); fl = s.math('FLOOR', v)
        if rows == 'half':
            u = s.math('ADD', u, s.math('MULTIPLY', s.math('MODULO', fl, 2.0), 0.5))
        elif rows == 'random':
            u = s.math('ADD', u, s.math('MULTIPLY', s.white(s.comb(fl, 7.3, 0.0)), 3.0))
        fu = s.math('FRACT', u); fv = s.math('FRACT', v)
        du = s.math('MULTIPLY', s.math('MINIMUM', fu, s.math('SUBTRACT', 1.0, fu)), sx)
        dv = s.math('MULTIPLY', s.math('MINIMUM', fv, s.math('SUBTRACT', 1.0, fv)), sy)
        d = s.math('MINIMUM', du, dv)
        g = s.math('MULTIPLY', s.math('SUBTRACT', d, gw * 0.5), 1.0 / 0.0012, clamp=True)
        joint = s.math('SUBTRACT', 1.0, g)
        rnd = s.white(s.comb(s.math('FLOOR', u), fl, 0.0))
        return joint, rnd, fu, fv
    # ---- shading
    def principled(s, base, rough=0.5, nrm=None, **kw):
        b = s.n('ShaderNodeBsdfPrincipled')
        s.setin(b.inputs['Base Color'], base); s.setin(b.inputs['Roughness'], rough)
        if nrm is not None: s.setin(b.inputs['Normal'], nrm)
        names = {'metal': 'Metallic', 'coat': 'Coat Weight', 'coat_rough': 'Coat Roughness', 'sheen': 'Sheen Weight', 'sheen_rough': 'Sheen Roughness',
                 'spec': 'Specular IOR Level', 'trans': 'Transmission Weight', 'ior': 'IOR', 'sss': 'Subsurface Weight', 'sss_scale': 'Subsurface Scale',
                 'emit': 'Emission Color', 'emit_str': 'Emission Strength', 'alpha': 'Alpha', 'aniso': 'Anisotropic', 'aniso_rot': 'Anisotropic Rotation'}
        for k, v in kw.items():
            try: s.setin(b.inputs[names[k]], v)
            except KeyError: pass
        return b
    def out(s, shader_out):
        o = s.n('ShaderNodeOutputMaterial'); s.nt.links.new(shader_out, o.inputs['Surface'])
        s.mat.diffuse_color = (0.5, 0.5, 0.5, 1); return s.mat
    def finish(s, b): return s.out(b.outputs['BSDF'])

# ------------------------------------------------------------------ generators
def paint(name, hexc, rough=0.8, ao=True, peel=0.12, dirt=0.0):
    m = M(name); P = m.P()
    var = m.noise(P, 0.7, 3.0, 0.5)
    c0 = srgb(hexc); lo = shade(hexc, 0.95); hi = shade(hexc, 1.025)
    base = m.ramp(var, [(0.3, lo), (0.7, hi)])
    if dirt:
        d = m.ramp(m.noise(m.mapping(P, (3, 3, 0.4)), 2.5, 4.0, 0.6), [(0.45, (0, 0, 0, 1)), (0.8, (1, 1, 1, 1))])
        base = m.mixc(m.math('MULTIPLY', d, dirt), base, shade(hexc, 0.7))
    if ao: base = m.mixc(0.55, base, m.ao(base, 0.35))
    h = m.noise(P, 700.0, 2.0, 0.6)
    nrm = m.bump(h, peel * 0.4, 0.002)
    return m.finish(m.principled(base, rough, nrm, spec=0.4))

def plaster_ext(name, hexc, dirt=0.35, rough=0.88):
    m = M(name); P = m.P(); Pz = m.sep(P)[2]
    var = m.noise(P, 0.5, 3.0, 0.5)
    base = m.ramp(var, [(0.3, shade(hexc, 0.94)), (0.7, shade(hexc, 1.03))])
    splash = m.math('MULTIPLY', m.math('SUBTRACT', 1.0, m.math('DIVIDE', m.math('SUBTRACT', Pz, 0.6), 1.2, clamp=True)), 0.45 * dirt / 0.35)
    streak = m.ramp(m.noise(m.mapping(P, (2.2, 2.2, 0.9)), 2.0, 4.0, 0.6), [(0.5, (0, 0, 0, 1)), (0.9, (1, 1, 1, 1))])
    d = m.math('ADD', splash, m.math('MULTIPLY', streak, 0.22 * dirt / 0.35))
    base = m.mixc(m.math('MINIMUM', d, 0.7), base, shade('#6E6558', 1.0))
    base = m.mixc(0.7, base, m.ao(base, 0.5))
    h = m.math('ADD', m.noise(P, 220.0, 6.0, 0.65), m.math('MULTIPLY', m.noise(P, 30.0, 3.0), 0.4))
    nrm = m.bump(h, 0.3, 0.003)
    return m.finish(m.principled(base, rough, nrm, spec=0.3))

def tile(name, base, varc, sx, sy, gw, rough, grout='#B7AC98', vein=None, rows='none', coat=0.0, bump=0.5, speck=0.0, grout_rough=0.85):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, sx, sy, gw, rows)
    col = m.mixc(m.math('MULTIPLY', rnd, 0.85), srgb(base), srgb(varc))
    if vein:
        P = m.P(); n = m.noise(m.mapping(P, (1, 1, 1), (0, 0, 0)), 1.6, 8.0, 0.62, 1.6)
        sv = m.math('SUBTRACT', 1.0, m.math('MULTIPLY', m.math('ABSOLUTE', m.math('SUBTRACT', n, 0.5)), 14.0, clamp=True))
        sv = m.math('MULTIPLY', sv, m.math('ADD', 0.25, m.math('MULTIPLY', rnd, 0.6)))
        col = m.mixc(m.math('MULTIPLY', sv, 0.6), col, srgb(vein))
        cl = m.mixc(m.math('MULTIPLY', m.noise(m.P(), 0.9, 4.0, 0.5), 0.5), col, shade(base, 0.93)); col = cl
    if speck:
        sp = m.ramp(m.noise(m.P(), 350.0, 1.0, 0.5), [(0.55, (0, 0, 0, 1)), (0.7, (1, 1, 1, 1))])
        col = m.mixc(m.math('MULTIPLY', sp, speck), col, shade(base, 0.6))
    col = m.mixc(joint, col, srgb(grout))
    r = m.mixf(joint, rough, grout_rough)
    h = m.math('SUBTRACT', 1.0, m.math('MULTIPLY', joint, 1.0))
    if speck or rough > 0.3:
        h = m.math('ADD', m.math('MULTIPLY', h, 0.8), m.math('MULTIPLY', m.noise(m.P(), 300.0, 2.0), 0.2))
    nrm = m.bump(h, bump, 0.003)
    return m.finish(m.principled(col, r, nrm, coat=coat, coat_rough=0.03, spec=0.5))

def planks(name, base, dark, light, length=1.2, width=0.19, rough=0.42, coat=0.15, gap='#1E1812', along='x'):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, length, width, 0.0012, 'random')
    gv = m.comb(m.math('MULTIPLY', U, 0.07), m.math('ADD', m.math('MULTIPLY', V, 1.0), m.math('MULTIPLY', rnd, 9.0)), 0.0)
    g = m.wave(gv, 38.0, 3.5, 4.0, 'Y', 'BANDS', 'SIN', 2.0, 0.6)
    g2 = m.noise(m.comb(m.math('MULTIPLY', U, 0.15), m.math('ADD', m.math('MULTIPLY', V, 12.0), m.math('MULTIPLY', rnd, 5.0)), 0.0), 18.0, 5.0, 0.55)
    tone = m.mixc(m.math('MULTIPLY', rnd, 0.9), srgb(dark), srgb(light))
    col = m.mixc(m.math('MULTIPLY', g, 0.55), srgb(base), tone)
    col = m.mixc(m.math('MULTIPLY', g2, 0.35), col, shade(base, 0.8))
    col = m.mixc(joint, col, srgb(gap))
    h = m.math('ADD', m.math('MULTIPLY', g, 0.25), m.math('MULTIPLY', m.math('SUBTRACT', 1.0, joint), 0.75))
    nrm = m.bump(h, 0.35, 0.0015)
    r = m.mixf(joint, rough, 0.7)
    return m.finish(m.principled(col, r, nrm, coat=coat, coat_rough=0.12, spec=0.5))

def wood(name, dark, light, rough=0.4, coat=0.25, scale=14.0, vertical=True, stripes=1.0, fine=1.0):
    m = M(name); Uv, U, V = m.planar()
    P = m.P()
    if vertical: vec = m.comb(m.math('MULTIPLY', U, 1.0), m.math('MULTIPLY', V, 0.035), 0.0); direction = 'X'
    else: vec = m.comb(m.math('MULTIPLY', U, 0.035), m.math('MULTIPLY', V, 1.0), 0.0); direction = 'Y'
    w = m.wave(vec, scale, 3.2, 5.0, direction, 'BANDS', 'SIN', 2.0, 0.7)
    fn = m.noise(m.mapping(P, (1, 1, 1)), 90.0, 4.0, 0.55) if fine else 0.5
    t = m.math('ADD', m.math('MULTIPLY', w, 0.75 * stripes), m.math('MULTIPLY', fn, 0.25))
    col = m.ramp(t, [(0.0, srgb(dark)), (1.0, srgb(light))])
    h = m.math('ADD', m.math('MULTIPLY', w, 0.5), m.math('MULTIPLY', fn, 0.5))
    nrm = m.bump(h, 0.18, 0.0012)
    return m.finish(m.principled(col, rough, nrm, coat=coat, coat_rough=0.15, spec=0.5))

def laminate(name, hexc, rough=0.35, tint='#000000', grain=0.12, tone=0.07):
    m = M(name); Uv, U, V = m.planar()
    vec = m.comb(m.math('MULTIPLY', U, 1.0), m.math('MULTIPLY', V, 0.04), 0.0)
    w = m.wave(vec, 30.0, 4.0, 4.0, 'X', 'BANDS', 'SIN', 2.0, 0.7)
    col = m.mixc(m.math('MULTIPLY', w, grain * 2.0), srgb(hexc), shade(hexc, 0.82))
    nrm = m.bump(w, 0.06, 0.001)
    return m.finish(m.principled(col, rough, nrm, coat=0.1, spec=0.5))

def granite(name, base, specks, rough=0.18, scale=260.0, coat=0.3):
    m = M(name); P = m.P()
    n1 = m.noise(P, scale, 2.0, 0.5)
    col = srgb(base)
    for i, sp in enumerate(specks):
        nz = m.noise(m.mapping(P, (1, 1, 1), (i * 3.7, i * 1.3, i * 5.1)), scale * (1.0 - 0.25 * i), 1.0, 0.5)
        mask = m.ramp(nz, [(0.52 + 0.04 * i, (0, 0, 0, 1)), (0.60 + 0.04 * i, (1, 1, 1, 1))])
        col = m.mixc(mask, col, srgb(sp))
    cl = m.noise(P, 1.5, 3.0); col = m.mixc(m.math('MULTIPLY', cl, 0.25), col, shade(base, 1.15))
    h = m.math('MULTIPLY', n1, 1.0); nrm = m.bump(h, 0.04, 0.0006)
    return m.finish(m.principled(col, rough, nrm, coat=coat, coat_rough=0.05, spec=0.5))

def marble(name, base, vein, rough=0.08):
    m = M(name); P = m.P()
    n = m.noise(m.mapping(P, (1, 2.2, 1)), 2.4, 9.0, 0.6, 1.8)
    sv = m.math('SUBTRACT', 1.0, m.math('MULTIPLY', m.math('ABSOLUTE', m.math('SUBTRACT', n, 0.5)), 10.0, clamp=True))
    col = m.mixc(m.math('MULTIPLY', sv, 0.55), srgb(base), srgb(vein))
    col = m.mixc(m.math('MULTIPLY', m.noise(P, 1.2, 4.0), 0.3), col, shade(base, 0.9))
    return m.finish(m.principled(col, rough, None, coat=0.4, coat_rough=0.03, spec=0.5))

def fabric(name, hexc, accent=None, pattern=None, sheen=0.6, rough=0.92):
    m = M(name); P = m.P()
    col = srgb(hexc)
    var = m.noise(P, 8.0, 3.0); col = m.mixc(m.math('MULTIPLY', var, 0.18), col, shade(hexc, 0.85))
    if pattern in ('floral', 'black_floral', 'mandala') and accent:
        if pattern == 'mandala':
            v = m.voronoi(m.mapping(P, (7, 7, 7)), 1.0, 1.0, 'DISTANCE_TO_EDGE', 'Distance')
            ring = m.wave(m.mapping(P, (1, 1, 1)), 12.0, 1.5, 2.0, 'X', 'RINGS', 'SIN')
            mask = m.ramp(m.math('MULTIPLY', ring, m.math('SUBTRACT', 1.0, v, clamp=True)), [(0.3, (0, 0, 0, 1)), (0.6, (1, 1, 1, 1))])
        else:
            v = m.voronoi(m.mapping(P, (5, 5, 5)), 1.0, 1.0, 'F1', 'Distance')
            mask = m.ramp(v, [(0.18, (1, 1, 1, 1)), (0.34, (0, 0, 0, 1))])
        col = m.mixc(mask, col, srgb(accent))
    wv = m.checker(m.mapping(P, (1, 1, 1)), 900.0)
    h = m.math('ADD', m.math('MULTIPLY', wv, 0.6), m.math('MULTIPLY', m.noise(P, 900.0, 1.0), 0.4))
    nrm = m.bump(h, 0.25, 0.0006)
    return m.finish(m.principled(col, rough, nrm, sheen=sheen, sheen_rough=0.4, spec=0.2))

def metal(name, hexc, rough=0.25, metallic=1.0, brushed=False, coat=0.0):
    m = M(name); P = m.P()
    nrm = None
    if brushed:
        h = m.noise(m.mapping(P, (1, 60, 60)), 200.0, 2.0); nrm = m.bump(h, 0.08, 0.0004)
        rr = m.mixf(m.noise(P, 40.0), rough * 0.8, rough * 1.25)
    else:
        rr = m.mixf(m.noise(P, 25.0, 3.0), rough * 0.85, rough * 1.2)
    return m.finish(m.principled(srgb(hexc), rr, nrm, metal=metallic, coat=coat, spec=0.5))

def plastic(name, hexc, rough=0.35):
    m = M(name); P = m.P()
    nrm = m.bump(m.noise(P, 500.0, 1.0), 0.03, 0.0004)
    return m.finish(m.principled(srgb(hexc), rough, nrm, coat=0.15, coat_rough=0.2, spec=0.5))

def ceramic(name, hexc, rough=0.04):
    m = M(name)
    return m.finish(m.principled(srgb(hexc), rough, None, coat=0.5, coat_rough=0.02, spec=0.6))

def glass(name, tint='#DDEBE8', rough=0.0, tintk=0.06, smoked=False, frosted=False):
    m = M(name)
    col = srgb(tint)
    if frosted:
        b = m.principled(col, 0.28, None, trans=1.0, ior=1.45, spec=0.5)
    else:
        # thin-sheet glass: tinted transparency + Fresnel reflection (no refraction blur, light still reaches interiors)
        tr0 = m.n('ShaderNodeBsdfTransparent'); m.setin(tr0.inputs['Color'], shade('#202226', 1.0) if smoked else col)
        gl = m.n('ShaderNodeBsdfGlossy'); m.setin(gl.inputs['Color'], (1, 1, 1, 1)); m.setin(gl.inputs['Roughness'], max(rough, 0.01))
        fr = m.n('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
        mx = m.n('ShaderNodeMixShader')
        m.nt.links.new(fr.outputs[0], mx.inputs[0])
        m.nt.links.new(tr0.outputs[0], mx.inputs[1]); m.nt.links.new(gl.outputs[0], mx.inputs[2])
        b = mx
    lp = m.n('ShaderNodeLightPath'); tr = m.n('ShaderNodeBsdfTransparent')
    m.setin(tr.inputs['Color'], col if not smoked else shade('#202226', 1.0))
    mix = m.n('ShaderNodeMixShader')
    m.nt.links.new(lp.outputs['Is Shadow Ray'], mix.inputs[0])
    m.nt.links.new((b.outputs['BSDF'] if frosted else b.outputs[0]), mix.inputs[1]); m.nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
    mat = m.out(mix.outputs[0])
    try: mat.surface_render_method = 'DITHERED'
    except Exception: pass
    return mat

def sheer(name, hexc='#F1ECE0', opacity=0.5):
    m = M(name); P = m.P()
    wv = m.noise(P, 900.0, 2.0, 0.5)
    d = m.n('ShaderNodeBsdfDiffuse'); m.setin(d.inputs['Color'], srgb(hexc))
    t = m.n('ShaderNodeBsdfTranslucent'); m.setin(t.inputs['Color'], srgb(hexc))
    dt = m.n('ShaderNodeMixShader'); dt.inputs[0].default_value = 0.55
    m.nt.links.new(d.outputs[0], dt.inputs[1]); m.nt.links.new(t.outputs[0], dt.inputs[2])
    tr = m.n('ShaderNodeBsdfTransparent')
    fac = m.math('ADD', m.math('MULTIPLY', wv, 0.3), opacity, clamp=True)
    mx = m.n('ShaderNodeMixShader'); m.nt.links.new(fac, mx.inputs[0])
    m.nt.links.new(tr.outputs[0], mx.inputs[1]); m.nt.links.new(dt.outputs[0], mx.inputs[2])
    return m.out(mx.outputs[0])

def mirror(name):
    m = M(name); P = m.P()
    return m.finish(m.principled((0.9, 0.92, 0.93, 1), 0.01, None, metal=1.0, spec=0.5))

def emissive(name, hexc, strength):
    m = M(name)
    e = m.n('ShaderNodeEmission'); s = m.n('ShaderNodeValue'); s.name = 'LED_STRENGTH'; s.label = 'LED_STRENGTH'; s.outputs[0].default_value = strength
    e.inputs['Color'].default_value = srgb(hexc); m.nt.links.new(s.outputs[0], e.inputs['Strength'])
    return m.out(e.outputs[0])

def leaf(name, h1, h2, rough=0.5, sss=0.08):
    m = M(name); P = m.P()
    r = m.objrand(); mixk = m.math('ADD', m.math('MULTIPLY', r, 0.6), m.math('MULTIPLY', m.noise(P, 3.0, 2.0), 0.4))
    col = m.mixc(mixk, srgb(h1), srgb(h2))
    veins = m.voronoi(m.mapping(P, (30, 30, 30)), 1.0, 1.0, 'DISTANCE_TO_EDGE', 'Distance')
    col = m.mixc(m.math('MULTIPLY', m.math('SUBTRACT', 1.0, veins, clamp=True), 0.25), col, shade(h2, 1.35))
    nrm = m.bump(m.noise(P, 120.0, 3.0), 0.2, 0.002)
    return m.finish(m.principled(col, rough, nrm, sss=sss, sss_scale=0.01, spec=0.4))

def grass(name, c1, c2, c3, scale=1.0, bump=1.0):
    m = M(name); P = m.P()
    a = m.noise(P, 0.35 * scale, 3.0, 0.5); b = m.noise(P, 4.0 * scale, 4.0, 0.6); f = m.noise(P, 220.0, 3.0, 0.7)
    col = m.mixc(a, srgb(c1), srgb(c2)); col = m.mixc(m.math('MULTIPLY', b, 0.5), col, srgb(c3))
    col = m.mixc(m.math('MULTIPLY', f, 0.35), col, shade(c1, 0.55))
    nrm = m.bump(m.math('ADD', f, m.math('MULTIPLY', b, 0.3)), 0.9 * bump, 0.02)
    return m.finish(m.principled(col, 0.92, nrm, sss=0.15, sss_scale=0.02, spec=0.2))

def soil(name, c1, c2, rough=0.95):
    m = M(name); P = m.P()
    a = m.noise(P, 20.0, 5.0, 0.6); b = m.noise(P, 300.0, 2.0)
    col = m.mixc(a, srgb(c1), srgb(c2)); col = m.mixc(m.math('MULTIPLY', m.ramp(b, [(0.5, (0, 0, 0, 1)), (0.75, (1, 1, 1, 1))]), 0.5), col, shade(c1, 0.5))
    nrm = m.bump(m.math('ADD', a, b), 1.0, 0.03)
    return m.finish(m.principled(col, rough, nrm))

def bark(name, hexc, ring=False, rough=0.9):
    m = M(name); P = m.P()
    if ring:
        w = m.wave(m.mapping(P, (1, 1, 0.4)), 14.0, 2.0, 3.0, 'Z', 'BANDS', 'SIN'); h = w
    else:
        h = m.noise(m.mapping(P, (4, 4, 0.5)), 9.0, 6.0, 0.7, 0.4)
    col = m.ramp(h, [(0.0, shade(hexc, 0.55)), (1.0, shade(hexc, 1.15))])
    return m.finish(m.principled(col, rough, m.bump(h, 1.2, 0.03)))

def rug(name, field, border, accent, pile=0.9):
    m = M(name); g = m.gen(); G = m.sep(g)
    ex = m.math('MINIMUM', G[0], m.math('SUBTRACT', 1.0, G[0])); ey = m.math('MINIMUM', G[1], m.math('SUBTRACT', 1.0, G[1]))
    e = m.math('MINIMUM', ex, ey)
    outer = m.math('GREATER_THAN', e, 0.025); band = m.math('GREATER_THAN', e, 0.085); inner = m.math('GREATER_THAN', e, 0.115)
    stripe = m.math('MULTIPLY', m.math('GREATER_THAN', m.math('MODULO', m.math('MULTIPLY', e, 90.0), 2.0), 1.0), 0.0)
    pat = m.checker(m.mapping(g, (14, 14, 14)), 1.0)
    pat2 = m.voronoi(m.mapping(g, (9, 9, 9)), 1.0, 1.0, 'DISTANCE_TO_EDGE', 'Distance')
    fcol = m.mixc(m.math('MULTIPLY', pat, 0.12), srgb(field), shade(field, 0.75))
    fcol = m.mixc(m.math('MULTIPLY', m.ramp(pat2, [(0.0, (1, 1, 1, 1)), (0.06, (0, 0, 0, 1))]), 0.55), fcol, srgb(accent))
    col = m.mixc(inner, srgb(border), fcol)
    col = m.mixc(m.math('MULTIPLY', m.math('SUBTRACT', band, inner), 1.0), col, srgb(accent))
    col = m.mixc(m.math('SUBTRACT', 1.0, outer), col, shade(border, 0.7))
    P = m.P(); h = m.noise(P, 420.0, 2.0); nrm = m.bump(h, 0.5 * pile, 0.003)
    return m.finish(m.principled(col, 0.97, nrm, sheen=0.7, sheen_rough=0.5, spec=0.1))

def art(name, c1, c2, c3):
    m = M(name); P = m.P()
    v = m.voronoi(m.mapping(P, (9, 9, 9)), 1.0, 1.0, 'F1', 'Color')
    d = m.sep(v)[0]
    col = m.ramp(d, [(0.0, srgb(c1)), (0.5, srgb(c2)), (1.0, srgb(c3))], 'CONSTANT')
    return m.finish(m.principled(col, 0.5, None, spec=0.4))

def paper(name, hexc='#EFEBE0'):
    m = M(name); P = m.P(); return m.finish(m.principled(srgb(hexc), 0.8, m.bump(m.noise(P, 900.0, 1.0), 0.1, 0.0004)))

def concrete(name, hexc='#8D8B86', rough=0.92, dirt=True):
    m = M(name); P = m.P()
    a = m.noise(P, 2.0, 4.0); b = m.noise(P, 60.0, 5.0, 0.7)
    col = m.mixc(a, srgb(hexc), shade(hexc, 0.78)); col = m.mixc(m.math('MULTIPLY', b, 0.2), col, shade(hexc, 1.2))
    if dirt: col = m.mixc(0.6, col, m.ao(col, 0.6))
    return m.finish(m.principled(col, rough, m.bump(m.math('ADD', b, m.math('MULTIPLY', a, 0.2)), 0.6, 0.004)))

def brick(name, hexc, hex2, sx=0.23, sy=0.075, gw=0.01):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, sx, sy, gw, 'half')
    col = m.mixc(rnd, srgb(hexc), srgb(hex2)); col = m.mixc(joint, col, srgb('#B7B2A6'))
    nrm = m.bump(m.math('ADD', m.math('SUBTRACT', 1.0, joint), m.math('MULTIPLY', m.noise(m.P(), 150.0, 3.0), 0.3)), 0.8, 0.004)
    return m.finish(m.principled(col, 0.9, nrm))

def mosaic(name, base, var, grout='#9C9384'):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, 0.03, 0.03, 0.0025, 'none')
    col = m.mixc(rnd, srgb(base), srgb(var)); col = m.mixc(m.math('MULTIPLY', m.noise(m.P(), 40.0, 2.0), 0.3), col, shade(base, 0.8)); col = m.mixc(joint, col, srgb(grout))
    nrm = m.bump(m.math('SUBTRACT', 1.0, joint), 0.7, 0.002)
    return m.finish(m.principled(col, m.mixf(joint, 0.3, 0.85), nrm, coat=0.2, coat_rough=0.1))

def cane(name, hexc, hex2, wicker=False):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, 0.012 if wicker else 0.02, 0.012 if wicker else 0.02, 0.0025, 'half')
    col = m.mixc(rnd, srgb(hexc), srgb(hex2)); col = m.mixc(joint, col, shade(hexc, 0.35))
    nrm = m.bump(m.math('SUBTRACT', 1.0, joint), 0.9, 0.0015)
    return m.finish(m.principled(col, 0.55, nrm, sheen=0.2))

def led_white_tube(): return emissive('R4_LED_Tube_White', '#F6F8FF', 12.0)

def leather(name, hexc, rough=0.48):
    m = M(name); P = m.P()
    v = m.voronoi(m.mapping(P, (1, 1, 1)), 220.0, 1.0, 'F1', 'Distance')
    cr = m.math('SUBTRACT', 1.0, m.math('MULTIPLY', v, 1.6, clamp=True))
    wear = m.noise(P, 6.0, 4.0)
    col = m.mixc(m.math('MULTIPLY', wear, 0.25), srgb(hexc), shade(hexc, 1.25))
    col = m.mixc(m.math('MULTIPLY', m.math('SUBTRACT', 1.0, cr), 0.18), col, shade(hexc, 0.6))
    r = m.mixf(m.noise(P, 18.0, 3.0), rough * 0.8, rough * 1.25)
    nrm = m.bump(m.math('ADD', cr, m.math('MULTIPLY', m.noise(P, 60.0, 3.0), 0.3)), 0.35, 0.0012)
    return m.finish(m.principled(col, r, nrm, coat=0.12, coat_rough=0.3, sheen=0.15, spec=0.5))

def pvc_panel(name, hexc='#EEECE6', pitch=0.2):
    m = M(name); Uv, U, V = m.planar()
    joint, rnd, fu, fv = m.grid(U, V, pitch, 50.0, 0.003, 'none')
    col = m.mixc(joint, srgb(hexc), shade(hexc, 0.72))
    nrm = m.bump(m.math('SUBTRACT', 1.0, joint), 0.8, 0.002)
    return m.finish(m.principled(col, 0.38, nrm, coat=0.15, coat_rough=0.2, spec=0.5))

def water(name, deep='#1F95AD', clear='#74CBD6'):
    m = M(name); P = m.P()
    w1 = m.noise(m.mapping(P, (1.0, 1.0, 0.2)), 2.2, 3.0, 0.5); w2 = m.noise(m.mapping(P, (1.0, 1.0, 0.2), (3, 1, 0)), 7.5, 2.0, 0.5)
    h = m.math('ADD', m.math('MULTIPLY', w1, 0.6), m.math('MULTIPLY', w2, 0.4))
    nrm = m.bump(h, 0.12, 0.05)
    b = m.principled(srgb(clear), 0.02, nrm, trans=1.0, ior=1.333, spec=0.5)
    ab = m.n('ShaderNodeVolumeAbsorption'); ab.inputs['Color'].default_value = srgb(deep); ab.inputs['Density'].default_value = 0.55
    tex = m.n('ShaderNodeOutputMaterial')
    m.nt.links.new(b.outputs['BSDF'], tex.inputs['Surface']); m.nt.links.new(ab.outputs[0], tex.inputs['Volume'])
    return m.mat

def rubber(name, hexc='#2A2B2D'):
    m = M(name); P = m.P()
    sp = m.ramp(m.noise(P, 500.0, 1.0), [(0.55, (0, 0, 0, 1)), (0.8, (1, 1, 1, 1))])
    col = m.mixc(m.math('MULTIPLY', sp, 0.5), srgb(hexc), srgb('#5A5C60'))
    return m.finish(m.principled(col, 0.8, m.bump(m.noise(P, 300.0, 2.0), 0.4, 0.002)))
