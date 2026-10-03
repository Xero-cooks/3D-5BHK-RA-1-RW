CAMS6={
 'Ext_South_Hero':((30,-34,3.2),(10,2,3.5),28),
 'Ext_SW_Aerial':((-18,-26,11),(12,6,3.2),30),
 'Ext_North_Entrance':((12,36,3.4),(12,14,3.0),32),
 'Ext_NE_Aerial':((44,34,13),(10,8,3.0),30),
 'Pool_Clubhouse':((3,-31,2.2),(20,-20,0.3),22),
 'Clubhouse_West':((26,-6,3),(34,-14,2.5),24),
 'Clubhouse_Aerial':((56,-8,13),(40,-18,3),28),
 'Pavilion_Veranda':((-20,-12,2.4),(-28,-24,2.6),22),
 'Pavilion_Interior':((-26.5,-25,1.7),(-32,-30,1.2),16),
 'Hall':((8.6,0.4,2.05),(1.8,6.0,1.4),16),
 'Dining':((8.3,6.6,2.15),(11.6,1.2,1.5),19),
 'Kitchen':((13.4,4.6,2.15),(17.4,1.0,1.4),17),
 'Master_Bedroom':((6.6,4.6,5.5),(1.4,1.2,4.7),17),
 'Bathroom_G1':((21.2,5.25,2.1),(19.6,6.8,1.2),16),
 'Balcony':((23.0,-0.2,5.4),(6.0,-1.8,4.8),20),
 'Club_Gym':((47.3,-17.2,2.3),(36,-22,1.2),16),
 'Club_Lobby':((39.7,-15.3,2.0),(35.5,-11.5,1.6),16),
 'Club_Studio':((41.5,-25.5,6.3),(34,-18,5.3),16),
 'Club_Games':((47.5,-15.5,6.3),(36,-12,5.2),16),
 'Club_Changing':((40.4,-13.4,1.9),(46.5,-12.8,1.2),16),
}
cc=bpy.data.collections['18_Cameras']
pl=bpy.data.objects.get('Club_DECOR_GF_Lobby_Plant_01')
if pl: pl.location=(39.65,-10.6,0.62)
for nm,(loc,tgt,lens) in CAMS6.items():
    name='CAM6_'+nm; ob=bpy.data.objects.get(name)
    if not ob:
        cd=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,cd); cc.objects.link(ob)
    ob.location=loc; ob.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    ob.data.lens=lens; ob.data.sensor_width=36; ob.data.clip_start=0.05; ob.data.clip_end=800; ob['r6']=1
print('cams',len(CAMS6))
