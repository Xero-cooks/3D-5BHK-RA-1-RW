"""Read the tracked material library without importing or running Blender."""
import ast,json,sys,types,runpy,pathlib
root=pathlib.Path(__file__).resolve().parents[2]
functions={}
for node in ast.parse((root/'blender/r4_mat.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):
  names=[a.arg for a in node.args.args];defaults={}
  for name,value in zip(names[len(names)-len(node.args.defaults):],node.args.defaults):
   try:defaults[name]=ast.literal_eval(value)
   except Exception:pass
  functions[node.name]=(names,defaults)
rows={}
class Recorder(types.ModuleType):
 def __getattr__(self,kind):
  def record(name,*args,**kwargs):
   names,defaults=functions[kind];params=dict(defaults);params.update(zip(names[1:],args));params.update(kwargs)
   colors=[]
   for value in params.values():
    if isinstance(value,str) and value.startswith('#') and len(value)==7 and value not in colors:colors.append(value)
   rows[name]={'kind':kind,'parameters':params,'colors':colors,'source':'blender/r4_lib.py + blender/r4_mat.py'}
   return rows[name]
  return record
sys.modules['bpy']=types.ModuleType('bpy');sys.modules['r4m']=Recorder('r4m')
runpy.run_path(str(root/'blender/r4_lib.py'))['build_all']()
# These preserve the original palette per PHASE_B_LOG.md. They are simplified
# fallbacks, not a claim to bake the missing Round7_PhaseB node graphs.
aliases={'R7_Floor_Vitrified_Cream':'R4_Floor_Vitrified_Cream','R7_Floor_Vitrified_Ivory':'R4_Floor_Vitrified_Ivory','R7_Floor_Tile_Bath':'R4_Floor_Tile_Bath','R7_Floor_Tile_Kitchen':'R4_Floor_Tile_Kitchen','R7_Floor_Tile_Utility':'R4_Floor_Tile_Utility','R7_Floor_Tile_Balcony':'R4_Floor_Tile_Balcony_Peach','R7_Pool_Tile':'R4_Pool_Tile_Mosaic'}
for target,original in aliases.items():rows[target]={**rows[original],'source':rows[original]['source']+'; simplified Round 7 color-preserving alias','alias':original}
for n in ['mustard','white','cream']:
 original='R4_Fabric_'+n
 for prefix in ['R7_Fab_','R7_Pipe_']:rows[prefix+original]={**rows[original],'source':'scripts/R7_soft.py base_col/piping rule; original palette from blender/r4_lib.py','alias':original,'piping':prefix=='R7_Pipe_'}
# Explicitly authored constant in the tracked pool script, not a name-based guess.
source=(root/'blender/r6_pool.py').read_text()
for line in source.splitlines():
 if "pm('R6_Pool_Grate'" in line or 'pm("R6_Pool_Grate"' in line:
  call=ast.parse(line.strip()).body[0].value;rows['R6_Pool_Grate']={'kind':'metal','linearColor':ast.literal_eval(call.args[1])[:3],'parameters':{'rough':ast.literal_eval(call.args[2]),'metal':ast.literal_eval(call.args[3]) if len(call.args)>3 else 0},'source':'blender/r6_pool.py'}
out=root/'viewer/scripts/source-material-palette.json';out.write_text(json.dumps(rows,indent=2)+'\n');print('Extracted',len(rows),'source-defined palette entries.')
