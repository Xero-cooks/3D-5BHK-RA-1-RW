# MATERIAL_REALISM_AUDIT

**Facts:** 152 materials, ALL procedural (Noise/Voronoi/Wave/Checker/Math + Bump). 0 image textures. 0 UV maps on 2698 meshes -> patterns driven by world-position (Geometry node). Scan PBR needs box/triplanar projection from Object/World coords or UV unwrap per surface.

**Defects**
- Tile/floor materials (Vitrified, Laminate, Granite, Marble) are math-node grids: no true grout depth, no reflection blur, no photographic variation; render of hall floor reads matte-flat vs glossy mirror floor in hall(2),(3).
- Marble: Noise-veining, roughness 0.08, coat 0.4: no real veins.
- Plaster/paint: 132 uses of one Ivory paint, r=0.8 uniform; no stains, edges clean.
- R4_Plastic_White used 180x (default stand-in) -> plastic everywhere.
- Metals: Chrome 57x, Steel 85x, Brass 78x; roughness driven by noise but same family; R6 materials are flat constants (no variation maps).
- Fabric: Checker+Noise bump; no weave/sheen.
- Glass: Transparent+Anisotropic+Fresnel mix hack (no IOR/thickness); 59 uses; windows render pale/blown.
- Water: Principled tr=1 + VolumeAbsorption, grey mirror in render; tile floor not visible.
- Leaf: Principled sss 0.08, no translucency/vein map.
- Grass_Lawn on a single 8-vertex quad: noise only.
- R6_* (40 mats) are constants (no bump, no variation).

**Keep:** wall/floor world-space coordinates (no stretching), R4 bark/wood wave logic as fallback, naming scheme.
Priority replacement: lawn, wall plaster, floor tiles (vitrified/laminate/herringbone), roof tiles, pool tile+deck, glass, water, marble/granite.
