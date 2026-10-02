"""Round 4 - material library definition + R3->R4 remap table (module r4b)."""
import bpy, sys
m = sys.modules['r4m']
ERR = []

def build_all():
    B = {}
    def add(fn, name, *a, **k):
        try:
            B[name] = fn(name, *a, **k)
        except Exception as e:
            import traceback
            ERR.append((name, repr(e), traceback.format_exc()[-300:]))
    P = m.paint
    # --- paints / plasters
    add(P, 'R4_Paint_Ivory', '#E9E1CB'); add(P, 'R4_Paint_Cream', '#E4D9BD'); add(P, 'R4_Paint_Sand', '#DDCDAA')
    add(P, 'R4_Paint_Taupe', '#D3C7B1'); add(P, 'R4_Paint_Stone', '#D9D4C5'); add(P, 'R4_Paint_White', '#F1EFE8', 0.65)
    add(P, 'R4_Paint_Ceiling', '#F5F3EE', 0.92); add(P, 'R4_Paint_Teal', '#2E8FA8', 0.4, False)
    add(m.plaster_ext, 'R4_Plaster_Exterior', '#E7DEC9'); add(m.plaster_ext, 'R4_Plaster_Trim_White', '#EFEBE0', 0.25)
    add(m.plaster_ext, 'R4_Plaster_Plinth', '#B5AA97', 0.5)
    # --- floors / tiles
    add(m.tile, 'R4_Floor_Vitrified_Cream', '#DAD0BC', '#D0C5AE', 0.8, 0.8, 0.003, 0.07, grout='#BDB29E', vein='#BBAC92', coat=0.5, bump=0.12)
    add(m.tile, 'R4_Floor_Vitrified_Ivory', '#E0D8C6', '#D6CDB8', 0.6, 0.6, 0.003, 0.08, grout='#BDB29E', vein='#C2B59C', coat=0.5, bump=0.12)
    add(m.planks, 'R4_Floor_Laminate_Oak_Grey', '#6A5748', '#52443A', '#7F6B58')
    add(m.planks, 'R4_Floor_Laminate_Oak_Honey', '#9A6B3E', '#7E5530', '#B58652', rough=0.38)
    add(m.tile, 'R4_Floor_Tile_Kitchen', '#E3D9C5', '#D8CDB6', 0.6, 0.6, 0.003, 0.12, grout='#B0A692', coat=0.35, bump=0.2)
    add(m.tile, 'R4_Floor_Tile_Bath', '#8F8678', '#847B6E', 0.3, 0.3, 0.003, 0.45, grout='#6F675C', speck=0.4, bump=0.6)
    add(m.tile, 'R4_Floor_Tile_Utility', '#7C766E', '#726C64', 0.3, 0.3, 0.004, 0.55, grout='#5E5851', speck=0.5, bump=0.7)
    add(m.tile, 'R4_Floor_Tile_Balcony_Peach', '#D9B58B', '#CFA87D', 0.6, 0.6, 0.004, 0.22, grout='#A8947A', coat=0.2, bump=0.4, speck=0.25)
    add(m.tile, 'R4_Wall_Tile_Bath', '#D6CCB9', '#CBBFA9', 0.3, 0.6, 0.003, 0.1, grout='#A39984', vein='#B7AA94', coat=0.5, bump=0.3)
    add(m.marble, 'R4_Stair_Marble_Beige', '#D8CCB3', '#A8957A')
    add(m.tile, 'R4_Terrace_Tile_Grey', '#8A8780', '#7D7A74', 0.3, 0.3, 0.006, 0.7, grout='#5A5750', speck=0.5, bump=0.8)
    add(m.tile, 'R4_Paving_Sandstone', '#C7AB8B', '#B99A78', 0.6, 0.6, 0.01, 0.8, grout='#7B6E5E', speck=0.3, bump=1.0)
    add(m.tile, 'R4_Paving_Interlock_Grey', '#8C8680', '#7B7570', 0.2, 0.1, 0.006, 0.85, grout='#4F4B46', rows='half', speck=0.4, bump=1.0)
    add(m.tile, 'R4_Panel_Stone_Cladding', '#B9AC96', '#A89B85', 0.3, 0.15, 0.006, 0.6, grout='#6E6556', rows='half', speck=0.3, bump=1.2)
    add(m.mosaic, 'R4_Tile_Mosaic_Beige', '#C9B697', '#B7A07C')
    # --- ground
    add(m.grass, 'R4_Grass_Lawn', '#4C7A2D', '#3C6A24', '#6C9440'); add(m.grass, 'R4_Grass_Dry', '#8E8A4A', '#7A7640', '#A59F5A')
    add(m.soil, 'R4_Soil_Laterite', '#8A4A2C', '#6B3822'); add(m.soil, 'R4_Soil', '#4A3626', '#352619')
    # --- woods / laminates
    add(m.wood, 'R4_Door_Walnut', '#33200F', '#6E4527', 0.4); add(m.wood, 'R4_Door_Teak_Main', '#3A210F', '#7A4A20', 0.35, 0.35)
    add(m.wood, 'R4_Wood_Dark', '#2E1B10', '#58351D'); add(m.wood, 'R4_Wood_Med', '#5A3A20', '#8E6038'); add(m.wood, 'R4_Wood_Teak', '#7A4E22', '#B07A3E')
    add(m.wood, 'R4_Wood_Handrail', '#4A2A14', '#7C4A26', 0.35, 0.3, 14.0, False)
    add(m.laminate, 'R4_Laminate_Cream', '#E7DDC8'); add(m.laminate, 'R4_Laminate_White', '#EFEBE0')
    add(m.wood, 'R4_Laminate_Woodgrain_Grey', '#5E564E', '#8A8076', 0.35, 0.1, 18.0)
    # --- stone / masonry
    add(m.granite, 'R4_Granite_Brown', '#6B5237', ['#C8A878', '#2A1C10', '#9A7C55'])
    add(m.granite, 'R4_Granite_Grey', '#7A7873', ['#BDBAB2', '#2E2E2E', '#9C9A94'])
    add(m.marble, 'R4_Marble_White', '#EDEAE4', '#9A9A9A')
    add(m.granite, 'R4_Stone_Boulder', '#8A867F', ['#B8B4AA', '#4A4742'], 0.75, 120.0, 0.0)
    add(m.granite, 'R4_Stone_Plinth', '#6E6B66', ['#A9A59C', '#2E2D2B'], 0.45, 120.0, 0.05)
    add(m.granite, 'R4_Stone_Sill', '#B8B0A0', ['#E0DACB', '#7C766A'], 0.4, 160.0, 0.05)
    add(m.concrete, 'R4_Concrete'); add(m.concrete, 'R4_Concrete_Dark', '#6E6D6A')
    add(m.brick, 'R4_Brick_Red', '#8A3E2C', '#7A3426')
    # --- metals / plastics / ceramics / glass
    add(m.metal, 'R4_Metal_Black_Powder', '#18181A', 0.4, 0.85); add(m.metal, 'R4_Metal_Graphite', '#3A3C40', 0.35, 1.0)
    add(m.metal, 'R4_Brass_Satin', '#C7A045', 0.28, 1.0); add(m.metal, 'R4_Chrome', '#E8EAEC', 0.04, 1.0)
    add(m.metal, 'R4_Steel_Stainless', '#C9CCCE', 0.25, 1.0, True); add(m.metal, 'R4_Railing_Green_Steel', '#2E4030', 0.45, 0.7, False, 0.1)
    add(m.metal, 'R4_Frame_Aluminium_White', '#E9E6DD', 0.38, 0.0)
    for n, h, r in (('Black', '#141416', 0.35), ('White', '#ECEAE4', 0.3), ('Blue', '#2C6FB5', 0.35), ('Pink', '#E58AA8', 0.35), ('Purple', '#7A4A9A', 0.35),
                    ('Red', '#C52B2B', 0.35), ('Yellow', '#E8C23A', 0.35), ('Tank_Black', '#161616', 0.5), ('PVC_Grey', '#9A9A98', 0.4)):
        add(m.plastic, f'R4_Plastic_{n}', h, r)
    add(m.ceramic, 'R4_Ceramic_White', '#F3F1EC'); add(m.ceramic, 'R4_Glass_Black_TV', '#050506', 0.03)
    add(m.glass, 'R4_Glass_Clear', '#D8E8E4'); add(m.glass, 'R4_Glass_Smoked', '#3A3F44', 0.0, 0.06, True); add(m.glass, 'R4_Glass_Frosted', '#EAF0EE', 0.0, 0.06, False, True)
    add(m.mirror, 'R4_Mirror')
    add(m.grass, 'R4_Grass_Far', '#5C7A34', '#4A6A2C', '#7C8A44', 0.15, 0.4); add(m.emissive, 'R4_LED_Pool', '#BFEFFF', 1.0)
    add(m.emissive, 'R4_LED_Warm', '#FFC47A', 8.0); add(m.emissive, 'R4_LED_White', '#F4F6FF', 10.0)
    # --- fabrics / rugs / art
    for n, h in (('cream', '#E3D8C0'), ('brown', '#5B4030'), ('charcoal', '#3A3A3C'), ('grey', '#8A8A88'), ('taupe', '#A59580'), ('white', '#EDEAE2'),
                 ('green', '#4F6B45'), ('maroon', '#6E2230'), ('mustard', '#C79A2A'), ('ochre', '#B77B2E'), ('teal', '#2F7A7A')):
        add(m.fabric, f'R4_Fabric_{n}', h)
    add(m.fabric, 'R4_Fabric_black_floral', '#222222', '#E8DCC0', 'black_floral'); add(m.fabric, 'R4_Fabric_floral', '#EADFC8', '#7A9A5A', 'floral')
    add(m.fabric, 'R4_Fabric_mandala', '#E8D8B8', '#C8502A', 'mandala'); add(m.fabric, 'R4_Fabric_Headboard', '#7A5A44')
    add(m.rug, 'R4_Rug_blue', '#2B4A78', '#D9CBA8', '#C8A55A'); add(m.rug, 'R4_Rug_cream', '#E2D6BC', '#9C8460', '#B89A66')
    add(m.rug, 'R4_Rug_pink', '#C98095', '#E8D8C6', '#9E4A62'); add(m.rug, 'R4_Rug_red', '#8E2A28', '#D6C3A0', '#C99A4A')
    add(m.art, 'R4_Art_Blue', '#1F3F7A', '#E8DCC0', '#3A6FB0'); add(m.art, 'R4_Art_Ochre', '#B77B2E', '#E8DCC0', '#6B4A1E'); add(m.art, 'R4_Art_Red', '#9E2A2A', '#E8DCC0', '#4A1A1A')
    # --- plants / organics / misc
    for n, a, b in (('Leaf', '#2F6B2B', '#3F7F32'), ('Leaf_Dark', '#1D4521', '#2A5A2A'), ('Leaf_Light', '#5C9438', '#78AE45'), ('Leaf_Red', '#7A2B22', '#9A3A2A'),
                    ('Leaf_Yellow', '#A8A23A', '#C0B848'), ('Leaf_Olive', '#6B7A3E', '#808E4E'), ('Hedge_Foliage', '#24501E', '#33652A'),
                    ('Flower_Orange', '#E8742A', '#F08A3A'), ('Flower_Pink', '#D9558C', '#E872A4')):
        add(m.leaf, f'R4_{n}', a, b)
    add(m.bark, 'R4_Bark', '#5A4A3A'); add(m.bark, 'R4_Palm_Trunk', '#7A6A55', True)
    add(P, 'R4_Terracotta', '#B0592F', 0.75); add(P, 'R4_Clay_Dark', '#5A3828', 0.75); add(P, 'R4_Cardboard', '#B8946A', 0.9, False)
    add(m.paper, 'R4_Paper'); add(m.cane, 'R4_Cane_Weave', '#C9A66B', '#B58F55'); add(m.cane, 'R4_Wicker', '#E6E0D2', '#D8D0C0', True)
    # --- round-4 additions: leather, PVC, pool, rubber, roof tile, club/pavilion finishes
    add(m.leather, 'R4_Leather_Charcoal', '#2B2B2D'); add(m.leather, 'R4_Leather_Brown', '#4A2E1E'); add(m.leather, 'R4_Leather_Tan', '#9A6A3F')
    add(m.pvc_panel, 'R4_PVC_Panel_White'); add(m.water, 'R4_Water_Pool')
    add(m.rubber, 'R4_Rubber_Gym')
    add(m.tile, 'R4_Pool_Deck_Travertine', '#D5C6A8', '#C8B898', 0.6, 0.4, 0.006, 0.7, grout='#8E8268', speck=0.3, bump=0.8)
    add(m.tile, 'R4_Pool_Tile_Mosaic', '#4FA6B6', '#3E94A8', 0.025, 0.025, 0.002, 0.15, grout='#9FB5B8', coat=0.4, bump=0.5)
    add(m.tile, 'R4_Roof_Tile_Terracotta', '#A65432', '#8F4528', 0.3, 0.2, 0.01, 0.65, grout='#5A3020', rows='half', speck=0.3, bump=1.4)
    return B

MAP_R3 = {
 'R3_art_blue': 'R4_Art_Blue', 'R3_art_ochre': 'R4_Art_Ochre', 'R3_art_red': 'R4_Art_Red', 'R3_black_glass': 'R4_Glass_Black_TV',
 'R3_black_metal': 'R4_Metal_Black_Powder', 'R3_black_plastic': 'R4_Plastic_Black', 'R3_blue_plastic': 'R4_Plastic_Blue', 'R3_brass': 'R4_Brass_Satin',
 'R3_brick_red': 'R4_Brick_Red', 'R3_cane': 'R4_Cane_Weave', 'R3_cardboard': 'R4_Cardboard', 'R3_ceramic': 'R4_Ceramic_White', 'R3_chrome': 'R4_Chrome',
 'R3_clay_dark': 'R4_Clay_Dark', 'R3_concrete': 'R4_Concrete', 'R3_emit_warm': 'R4_LED_Warm', 'R3_emit_white': 'R4_LED_White',
 'R3_flower_orange': 'R4_Flower_Orange', 'R3_flower_pink': 'R4_Flower_Pink', 'R3_frosted': 'R4_Glass_Frosted', 'R3_glass': 'R4_Glass_Clear',
 'R3_glass_dark': 'R4_Glass_Smoked', 'R3_granite_brown': 'R4_Granite_Brown', 'R3_granite_grey': 'R4_Granite_Grey', 'R3_graphite': 'R4_Metal_Graphite',
 'R3_grass_dry': 'R4_Grass_Dry', 'R3_green_rail': 'R4_Railing_Green_Steel', 'R3_hedge': 'R4_Hedge_Foliage', 'R3_lam_cream': 'R4_Laminate_Cream',
 'R3_lam_grey': 'R4_Laminate_Woodgrain_Grey', 'R3_lam_white': 'R4_Laminate_White', 'R3_leaf': 'R4_Leaf', 'R3_leaf_dark': 'R4_Leaf_Dark',
 'R3_leaf_light': 'R4_Leaf_Light', 'R3_leaf_red': 'R4_Leaf_Red', 'R3_leaf_yellow': 'R4_Leaf_Yellow', 'R3_marble_white': 'R4_Marble_White',
 'R3_mirror': 'R4_Mirror', 'R3_mosaic': 'R4_Tile_Mosaic_Beige', 'R3_olive_leaf': 'R4_Leaf_Olive', 'R3_paint_white': 'R4_Paint_White',
 'R3_palm_trunk': 'R4_Palm_Trunk', 'R3_paper': 'R4_Paper', 'R3_pink_plastic': 'R4_Plastic_Pink', 'R3_plastic_white': 'R4_Plastic_White',
 'R3_purple_plastic': 'R4_Plastic_Purple', 'R3_pvc_grey': 'R4_Plastic_PVC_Grey', 'R3_red_plastic': 'R4_Plastic_Red', 'R3_soil': 'R4_Soil',
 'R3_steel': 'R4_Steel_Stainless', 'R3_stone_grey': 'R4_Stone_Boulder', 'R3_tank_black': 'R4_Plastic_Tank_Black', 'R3_teal_trim': 'R4_Paint_Teal',
 'R3_terracotta': 'R4_Terracotta', 'R3_tile_cream': 'R4_Floor_Tile_Balcony_Peach', 'R3_trunk': 'R4_Bark', 'R3_wicker': 'R4_Wicker',
 'R3_wood_dark': 'R4_Wood_Dark', 'R3_wood_med': 'R4_Wood_Med', 'R3_wood_teak': 'R4_Wood_Teak', 'R3_yellow_plastic': 'R4_Plastic_Yellow',
}
for n in ('black_floral', 'floral', 'mandala', 'brown', 'charcoal', 'cream', 'green', 'grey', 'maroon', 'mustard', 'ochre', 'taupe', 'teal', 'white'):
    MAP_R3[f'R3_fab_{n}'] = f'R4_Fabric_{n}'
for n in ('blue', 'cream', 'pink', 'red'): MAP_R3[f'R3_rug_{n}'] = f'R4_Rug_{n}'
