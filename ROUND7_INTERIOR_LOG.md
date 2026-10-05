# Round 7 – interior realism log

Status of the six requests (honest):

| # | Request | Status |
|---|---------|--------|
| 1 | Soft goods look like stone | **Done for all 6 beds** (pillows regenerated: puffy, pinched corners, seam, optional piping, woven-fabric shader; duvet/runner slabs with wrinkle noise). Sofas/armchairs replaced by scanned-quality Poly Haven models (see 6). |
| 2 | Layout audit / floating fan | Floating `FF_RoofHall_CeilingFan*` deleted (roof-stair hall has no ceiling). Further audit items listed in AUDIT docs. |
| 3 | Useless almirah-only rooms | FF Lobby3, FF Lobby4, GF LobbyG1 door cuts widened into corridor; doors/frames/hardware hidden. Door casing trim may remain (unverified). |
| 4 | Railings | Replaced: glass panels + stainless posts + timber handrail (balcony, main stair, roof stair, club stair, club FF void guard). Old railings hidden, not deleted. |
| 5 | Stair connections | Main, roof and club stairs regenerated as straight-flight + landing + straight-flight (timber treads, white soffit) with `R7_arch.py` generators; stair voids widened. |
| 6 | Hi-res furniture | 9 sofas, 13 armchairs, 6 coffee tables swapped to Poly Haven CC0 models (`sofa_02`, `modern_arm_chair_01`, `modern_coffee_table_01`). Gym machines: see CURRENT_STATE / pending. |

Scripts: `scripts/R7_soft.py` (pillow/duvet generator + fabric material), `scripts/R7_swap.py` (footprint-matching model swapper), `scripts/R7_gym.py` (explicit-position gym placement).
Old objects are hidden (`hide_render`/`hide_viewport`) rather than deleted so every swap is reversible.
