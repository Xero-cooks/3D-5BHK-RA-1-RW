# VEGETATION_AUDIT

- Lawn `SITE_Ground_Lawn`: 8 verts/6 faces, procedural noise + bump; no blades. `SITE_Ground_Far`: 80 km plane. => carpet look.
- Trees (LAND_Tree_Shade_xx, 50 objs ~ 10 trees): trunk 144 verts + 2-3 'leaf' proxy blobs each (650-1800 verts) with R6_Foliage GN leaf cards. Render: faceted broccoli/lollipop crowns, uniform green, no branching.
- Palms (50 objs ~ 10 palms): 1.4-1.7k-vert trunks + 2.7k leaf mesh; render = toy fan palms, no frond droop/ring scars; reference = areca/coconut-like palms.
- Shrub beds 345 objs, hedges 28 objs: GN leaf-card scatter on blob proxies (density x0.12 viewport). Hedges are acceptable at distance, blocky up close.
- Laterite beds: 3 rounded rectangles (ref: curved kidney beds with brick edge).
- Reference tree: slender casuarina/pine-like with wispy open crown and bare trunk (others 1,5,6).

Verdict: lawn REBUILD, trees REBUILD, palms REBUILD, beds/shrubs REFINE->REBUILD, hedges REFINE.
