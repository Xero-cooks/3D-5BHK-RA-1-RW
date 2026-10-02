"""Round 4 session helpers (loaded into bpy.app.driver_namespace): load / bgr / fetch.
bgr renders a copy of the scene in a separate background Blender (--factory-startup) so the UI session never freezes."""
import bpy, os, sys, json, base64, subprocess, urllib.request, tempfile

REPO = 'https://raw.githubusercontent.com/Xero-cooks/3D-5BHK-RA-1-RW'
TMP = tempfile.gettempdir()

BG_SCRIPT = r'''
import bpy, sys, json, os, math, time
from mathutils import Vector
a = json.load(open(sys.argv[sys.argv.index('--') + 1]))
sc = bpy.context.scene
A = a
cam = None
if a.get('cam'):
    cam = bpy.data.objects[a['cam']]
else:
    cd = bpy.data.cameras.new('_BG_cam'); cam = bpy.data.objects.new('_BG_cam', cd); sc.collection.objects.link(cam)
    cam.location = a['loc']; d = Vector(a['tgt']) - Vector(a['loc'])
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cd.lens = a['lens']
sc.camera = cam
sc.render.engine = a.get('engine', 'CYCLES')
sc.render.resolution_x, sc.render.resolution_y = a['size']; sc.render.resolution_percentage = 100
if sc.render.engine == 'CYCLES':
    sc.cycles.samples = a['samples']; sc.cycles.device = 'CPU'; sc.cycles.use_adaptive_sampling = True
for h in a.get('hide', []):
    for c in bpy.data.collections:
        if c.name.startswith(h):
            c.hide_render = True
for code in a.get('pre', []):
    exec(code)
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
out = os.path.join(os.environ.get('TEMP', '/tmp'), a['name'] + '.jpg')
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
open(out + '.done', 'w').write('ok')
'''

def load(sha, file, modname):
    src = urllib.request.urlopen(f'{REPO}/{sha}/blender/{file}.py').read().decode()
    mod = type(sys)(modname); mod.__dict__['__name__'] = modname
    sys.modules[modname] = mod
    exec(compile(src, file + '.py', 'exec'), mod.__dict__)
    return mod

def bgr(name, loc=None, tgt=None, lens=28, size=(960, 540), samples=48, hide=(), cam=None, pre=(), engine='CYCLES'):
    blend = os.path.join(TMP, 'r4_bg.blend'); script = os.path.join(TMP, 'r4_bg_render.py'); js = os.path.join(TMP, name + '.json')
    for f in (os.path.join(TMP, name + '.jpg'), os.path.join(TMP, name + '.jpg.done')):
        if os.path.exists(f): os.remove(f)
    bpy.ops.wm.save_as_mainfile(filepath=blend, copy=True)
    open(script, 'w').write(BG_SCRIPT)
    json.dump(dict(name=name, loc=loc, tgt=tgt, lens=lens, size=list(size), samples=samples, hide=list(hide), cam=cam, pre=list(pre), engine=engine), open(js, 'w'))
    p = subprocess.Popen([bpy.app.binary_path, '--factory-startup', '-b', blend, '-P', script, '--', js], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('started', name, p.pid)

def fetch(name):
    f = os.path.join(TMP, name + '.jpg')
    if os.path.exists(f + '.done') and os.path.exists(f):
        print('SHOT:%s:%s:ENDSHOT' % (name, base64.b64encode(open(f, 'rb').read()).decode()))
    else:
        print('NOT READY')

def install():
    d = bpy.app.driver_namespace
    d['load'] = load; d['bgr'] = bgr; d['fetch'] = fetch
