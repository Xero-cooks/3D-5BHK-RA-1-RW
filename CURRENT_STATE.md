# Current state (latest; supersedes PROJECT_STATE.md where they differ)

- Working file (PC): `Round7_PhaseB.blend` (backups: `Round7_PhaseB_backup_before.blend`, `Round6_Final.blend`). Saved after the interior pass.
- Priority per user: interior realism (furniture + walls + floors) for a real-estate / future FPP web walkthrough. Exterior is accepted; vegetation was reduced.
- Done: smooth-by-angle on 1,735 interior meshes, bevel modifiers on ~1,000, PBR wood/fabric/velvet/leather/plaster, new floors. See PHASE_B_LOG.md.
- Latest renders: `renders\v2_GOLDEN_*` (hall, dining, kitchen, master bedroom, hero), 1280x720 / 48 spp.
- NEXT (needs user decision): replace blocky hero furniture (sofa set, armchairs, dining chairs, bed, wardrobe, TV unit) with proper models in the same footprint; fix CAM6_Bathroom_G1 framing; generate UVs for game export; bedroom/hall wall colour grading vs. any real reference; D-1 / D-2 open questions in EXTERNAL_RESOURCE_REQUESTS.md.
- Gotchas: MCP call limit ~60 s (use headless batch `scripts/r7_batch_render.py`); bulk hide_viewport toggles stall Blender for minutes.
