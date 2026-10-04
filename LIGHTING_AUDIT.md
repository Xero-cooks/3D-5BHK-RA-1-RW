# LIGHTING_AUDIT

- Sun `LIGHT_Sun_Daylight`: 3.2 W/m2, colour (1.0,0.95,0.86), 0.9 deg angle, rot (46,0,-35) => ~44 deg elevation, toward SW. `LIGHT_Moon` 0.
- Sky: Nishita multiple scattering, sun_elevation 44 deg, rot 215 deg, aerosol 0.35, sun_disc OFF; R6 cloud-mix nodes; BG strength 0.5. Sun-lamp azimuth vs Sky azimuth not verified aligned.
- Exposure -0.6, AgX Medium-High Contrast. Cycles 96 spp, 10 bounces (diffuse 5, gloss 5, trans 8), indirect clamp 8.
- 59 interior area, 35 exterior point, 8 pool point lights = 11,230 W total; presets scale by tag.
- Render evidence: exterior = high white overcast-like sky, weak/diffuse shadows, flat midday; no warm low-angle sun; no pink/violet dusk; reference others(1),(5),(6),(9) show golden/dusk.
- Interiors: soft, even, creamy; windows pale; no visible sun patches through sliders (ref balcony shows long sun streaks).
- Environment: no HDRI; flat 80 km green plane horizon; no hills/neighbour blocks/haze depth.

**Phase B plan:** physical sun+sky (or pure-sky HDRI) per time-of-day, sun elevation 8-15 deg for golden, ~ -3..+2 deg for dusk with sky-only fill; warm from atmosphere not tint; haze for NCR daylight; verify sun/sky alignment; re-expose.
