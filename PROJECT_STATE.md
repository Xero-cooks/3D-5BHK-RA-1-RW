# PROJECT_STATE (living doc - reload first after any context compression)

**Phase:** A (forensic audit) COMPLETE -> HARD STOP, awaiting user reply. Phase B (implementation) NOT started. No scene changes made in Phase A (renders only; camera/res/samples restored).
**Blend (user PC):** C:\Users\User\Documents\3D-5BHK-RA-1-RW\Round6_Final.blend, Blender 5.2.0 LTS, Cycles/CPU, AgX Medium-High-Contrast, exposure -0.6, 96 spp, 1920x1080, OIDN-style denoise on.
**Scene:** 3493 objects, 2698 meshes, ~353k polys, 152 materials (all procedural), 0 image textures, 0 UV maps, 104 lights, 38 cameras, 198 GN foliage modifiers (R6_Foliage), 0 particle systems.
**Coordinates:** X east, Y north, Z up, metres. Origin = residence SW corner. Residence x0-24,y0-14 (GF FFL 0.6, FF 3.8, roof 7.0). Clubhouse x32-48,y-26..-10. Pavilion x-34..-22,y-32..-24. Pool 24x12 (chamfered NE).
**Presets:** scene['r4_time'] = DAY (currently), GOLDEN, NIGHT (GOLDEN/NIGHT not re-rendered in Phase A).
**Render facts:** 800x450 @16-24spp = 18-31 s. MCP call times out ~60 s -> ONE render per execute_blender_code call. Return image as base64 print (auto-offloaded to file) and decode in sandbox.
**Connectivity:** Blender PC can reach api.polyhaven.com via Python urllib (verified). Addon Poly Haven/Sketchfab toggles are DISABLED (so MCP download tools are off; use Python urllib/bpy instead, or ask user to tick the checkbox). ambientCG API reachable from sandbox.
**Docs:** REFERENCE_AUDIT, ARCHITECTURE_AUDIT, MATERIAL_REALISM_AUDIT, LIGHTING_AUDIT, VEGETATION_AUDIT, EXTERNAL_RESOURCE_REQUESTS, FINAL_PRODUCTION_TODO. Older: docs/ROUND_*.md, project_state.json (stale: says round 6 final).
**Open user decisions:** see FINAL_PRODUCTION_TODO.md section D.
