"""Round 4 - world, sun/sky, interior + exterior lights, time-of-day presets, render settings, hero cameras (module r4l)."""
import bpy, math, sys
from mathutils import Vector

SKY_OFFSET = 0.0     # sun_rotation (deg) = SKY_SIGN * az + SKY_OFFSET  (set after calibration)
SKY_SIGN = 1.0
PRESETS = {
    # az: sun azimuth deg clockwise from +Y (north); el: elevation deg
    'DAY':    dict(az=215, el=44, sun=4.2, sun_col=(1.0, 0.95, 0.86), bg=1.0, expo=0.0, room=0.30, led=(1.5, 3.0), ext=0.0, moon=0.0, dust=2.0),
    'GOLDEN': dict(az=262, el=9,  sun=3.0, sun_col=(1.0, 0.70, 0.40), bg=1.0, expo=0.2, room=0.65, led=(5.0, 6.0), ext=0.35, moon=0.0, dust=3.0),
    'NIGHT':  dict(az=215, el=-14, sun=0.0, sun_col=(1.0, 1.0, 1.0), bg=0.7, expo=0.9, room=1.0, led=(14.0, 14.0), ext=1.0, moon=0.12, dust=1.0),
}

def sun_dir(az, el):
    a = math.radians(az); e = math.radians(el)
    return Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))

def coll(name, parent='17_Lighting'):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.data.collections[parent].children.link(c)
    return c

def dust(sky, v):
    for a in ('aerosol_density', 'dust_density'):
        if hasattr(sky, a): setattr(sky, a, v); return a

def make_world():
    w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    bpy.context.scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
    sky = nt.nodes.new('ShaderNodeTexSky'); sky.name = 'R4_Sky'
    try: sky.sky_type = 'MULTIPLE_SCATTERING'
    except Exception: sky.sky_type = 'NISHITA'
    sky.sun_disc = False; sky.air_density = 1.0; sky.ozone_density = 1.0; sky.altitude = 0.0; dust(sky, 2.0)
    bg = nt.nodes.new('ShaderNodeBackground'); bg.name = 'R4_BG'
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(sky.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
    return w

def sun_lamps():
    sun = bpy.data.objects.get('LIGHT_Sun_Daylight')
    L = coll('17_Lighting_Sun')
    if sun:
        for c in list(sun.users_collection): c.objects.unlink(sun)
        L.objects.link(sun)
        sun.data.angle = math.radians(0.9)
    moon = bpy.data.objects.get('LIGHT_Moon')
    if not moon:
        d = bpy.data.lights.new('LIGHT_Moon', 'SUN'); d.angle = math.radians(1.5); d.color = (0.55, 0.65, 1.0); d.energy = 0.0
        moon = bpy.data.objects.new('LIGHT_Moon', d); moon.location = (0, 0, 80); L.objects.link(moon)
    return sun, moon

def aim(obj, direction_to_light):
    obj.rotation_euler = (-direction_to_light).to_track_quat('-Z', 'Y').to_euler()

def room_lights():
    L = coll('17_Lighting_Interior'); n = 0
    CE = {'GF': 3.57, 'FF': 6.77}
    for o in bpy.data.objects:
        if not (o.get('room_type') and o.parent and o.parent.name == 'BLD_Residence'): continue
        x0, x1, y0, y1 = o['bbox'][:4]; fl = o['floor']; key = f"{fl}_{o['room_name']}"
        nm = f'LT_Room_{fl}_{o["room_name"]}'.replace(' ', '_').replace('(', '').replace(')', '')
        if bpy.data.objects.get(nm): continue
        d = bpy.data.lights.new(nm, 'AREA'); d.shape = 'RECTANGLE'
        d.size = max((x1 - x0) * 0.45, 0.3); d.size_y = max((y1 - y0) * 0.45, 0.3)
        wet = 'Bath' in key
        d.color = (1.0, 0.90, 0.78) if wet else (1.0, 0.82, 0.62)
        area = (x1 - x0) * (y1 - y0); base = (24.0 if wet else 17.0) * area
        d.energy = base; d['base_energy'] = base
        ob = bpy.data.objects.new(nm, d); ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, CE[fl] - 0.16)
        L.objects.link(ob); ob['r4'] = 1; n += 1
    return n

def exterior_lights():
    L = coll('17_Lighting_Exterior'); n = 0
    spec = (('LampPost', 'SITE_LampPost', 260.0), ('WallLantern', 'WallLantern', 45.0))
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or not o.name.endswith('.emit_warm'): continue
        kind = None
        for k, pat, w in spec:
            if pat in o.name: kind = (k, w)
        if not kind: continue
        nm = 'LT_' + o.name.replace('.emit_warm', '')
        if bpy.data.objects.get(nm): continue
        c = sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8.0
        d = bpy.data.lights.new(nm, 'POINT'); d.energy = kind[1]; d['base_energy'] = kind[1]; d.shadow_soft_size = 0.07; d.color = (1.0, 0.76, 0.5)
        ob = bpy.data.objects.new(nm, d); ob.location = c; L.objects.link(ob); ob['r4'] = 1; n += 1
    return n

def set_led(w, wt):
    for nm, v in (('R4_LED_Warm', w), ('R4_LED_White', wt)):
        m = bpy.data.materials.get(nm)
        if m and 'LED_STRENGTH' in m.node_tree.nodes: m.node_tree.nodes['LED_STRENGTH'].outputs[0].default_value = v

def set_time(name):
    p = PRESETS[name]; sc = bpy.context.scene
    w = sc.world; sky = w.node_tree.nodes['R4_Sky']; bg = w.node_tree.nodes['R4_BG']
    sky.sun_elevation = math.radians(p['el']); sky.sun_rotation = math.radians(SKY_SIGN * p['az'] + SKY_OFFSET); dust(sky, p['dust'])
    bg.inputs['Strength'].default_value = p['bg']
    sun, moon = sun_lamps()
    d = sun_dir(p['az'], max(p['el'], 1.0)); aim(sun, d); sun.data.energy = p['sun']; sun.data.color = p['sun_col']
    aim(moon, sun_dir(40, 52)); moon.data.energy = p['moon']
    sc.view_settings.exposure = p['expo']
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.get('r4'):
            f = p['room'] if o.name.startswith('LT_Room') else p['ext']
            if o.get('kind') == 'pool': f = p['ext']
            o.data.energy = o.data['base_energy'] * f; o.hide_render = (f <= 0.001)
    set_led(*p['led'])
    m = bpy.data.materials.get('R4_LED_Pool')
    if m and 'LED_STRENGTH' in m.node_tree.nodes: m.node_tree.nodes['LED_STRENGTH'].outputs[0].default_value = 1.0 + 11.0 * p['ext']
    sc['r4_time'] = name
    return name

def setup_render(final=False):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; cy = sc.cycles
    cy.samples = 384 if final else 96; cy.preview_samples = 48
    cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.01 if final else 0.03
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    cy.max_bounces = 10; cy.diffuse_bounces = 5; cy.glossy_bounces = 5; cy.transmission_bounces = 8; cy.transparent_max_bounces = 8; cy.volume_bounces = 0
    cy.sample_clamp_indirect = 8.0; cy.sample_clamp_direct = 0.0; cy.caustics_reflective = False; cy.caustics_refractive = False
    sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
    vs = sc.view_settings
    for t in ('AgX', 'Filmic', 'Standard'):
        try: vs.view_transform = t; break
        except Exception: pass
    for lk in ('AgX - Medium High Contrast', 'Medium High Contrast', 'AgX - Base Contrast', 'None'):
        try: vs.look = lk; break
        except Exception: pass
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
    return (vs.view_transform, vs.look)

CAMS = {
    'South_Facade': ((12, -36, 4.0), (12, 0, 3.4), 34), 'North_Entrance': ((12, 36, 3.4), (12, 14, 3.0), 32),
    'SW_Aerial': ((-18, -26, 11), (12, 6, 3.2), 30), 'NE_Aerial': ((44, 34, 13), (10, 8, 3.0), 30),
    'Hall': ((7.5, 0.5, 2.15), (1.8, 6.0, 1.5), 17), 'Dining': ((8.3, 6.6, 2.15), (11.6, 1.2, 1.5), 19),
    'Kitchen': ((13.4, 4.6, 2.15), (17.4, 1.0, 1.4), 17), 'Master_Bedroom': ((6.6, 4.6, 5.5), (1.4, 1.2, 4.7), 17),
    'Bathroom_G1': ((21.2, 5.25, 2.1), (19.6, 6.8, 1.2), 16), 'Balcony': ((23.0, -0.2, 5.4), (6.0, -1.8, 4.8), 20),
    'Porch_Dusk': ((12, 24, 2.0), (12, 14, 2.1), 28), 'Garden_Dusk': ((-6, -22, 4.5), (14, 2, 3.0), 26),
}

def cameras():
    c = bpy.data.collections.get('18_Cameras'); n = 0
    for nm, (loc, tgt, lens) in CAMS.items():
        name = f'CAM4_{nm}'
        ob = bpy.data.objects.get(name)
        if not ob:
            cd = bpy.data.cameras.new(name); ob = bpy.data.objects.new(name, cd); c.objects.link(ob); n += 1
        ob.location = loc; ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        ob.data.lens = lens; ob.data.sensor_width = 36; ob.data.clip_start = 0.05; ob.data.clip_end = 600
        ob['r4'] = 1
    return n

def ground_far():
    nm = 'SITE_Ground_Far'
    if bpy.data.objects.get(nm): return 0
    me = bpy.data.meshes.new(nm)
    S = 1500.0
    me.from_pydata([(-S, -S, -0.06), (S, -S, -0.06), (S, S, -0.06), (-S, S, -0.06)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(nm, me)
    c = bpy.data.collections['01_Site_Ground']; c.objects.link(ob); ob['r4'] = 1
    mt = bpy.data.materials.get('R4_Grass_Far')
    if mt: ob.data.materials.append(mt)
    return 1

def pool_shell():
    import bmesh
    cut = bpy.data.objects.get('POOL_Basin_Cutter')
    if not cut or bpy.data.objects.get('POOL_Shell_Tiles'): return 0
    cx, cy = cut.location.x, cut.location.y; dx, dy = cut.dimensions.x / 2 - 0.02, cut.dimensions.y / 2 - 0.02
    z0, z1 = -1.45, 0.0
    me = bpy.data.meshes.new('POOL_Shell_Tiles'); bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((-dx, -dy, z0), (dx, -dy, z0), (dx, dy, z0), (-dx, dy, z0), (-dx, -dy, z1), (dx, -dy, z1), (dx, dy, z1), (-dx, dy, z1))]
    for f in ((0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[i] for i in f])
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('POOL_Shell_Tiles', me); ob.location = (cx, cy, 0)
    bpy.data.collections['14_Pool_Water'].objects.link(ob); ob['r4'] = 1
    mt = bpy.data.materials.get('R4_Pool_Tile_Mosaic')
    if mt: me.materials.append(mt)
    # underwater lights (emissive niches + real lights)
    L = coll('17_Lighting_Pool'); lt = bpy.data.materials.get('R4_LED_Pool'); n = 0
    pos = [(cx + x, cy - dy + 0.02, -0.75, 0) for x in (-8, -3, 3, 8)] + [(cx + x, cy + dy - 0.02, -0.75, 1) for x in (-8, -3, 3, 8)]
    for i, (x, y, z, side) in enumerate(pos):
        nm = f'POOL_Light_{i + 1:02d}'
        d = bpy.data.lights.new('LT_' + nm, 'POINT'); d.energy = 120.0; d['base_energy'] = 120.0; d.color = (0.55, 0.9, 1.0); d.shadow_soft_size = 0.1
        lo = bpy.data.objects.new('LT_' + nm, d); lo.location = (x, y + (0.25 if side == 0 else -0.25), z); L.objects.link(lo); lo['r4'] = 1
        lo['kind'] = 'pool'
        me2 = bpy.data.meshes.new(nm); b2 = bmesh.new(); bmesh.ops.create_cube(b2, size=1.0); b2.to_mesh(me2); b2.free()
        e = bpy.data.objects.new(nm, me2); e.scale = (0.28, 0.03, 0.18); e.location = (x, y, z); bpy.data.collections['14_Pool_Water'].objects.link(e); e['r4'] = 1
        if lt: me2.materials.append(lt)
        n += 1
    return n

def run():
    make_world(); setup_render(False)
    r = {'room': room_lights(), 'ext': exterior_lights(), 'cams': cameras(), 'ground': ground_far(), 'pool': pool_shell()}
    set_time('DAY'); return r
