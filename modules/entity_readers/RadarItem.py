from modules.entity_readers.helpers import *

def readRadarItem(f):
	'''
	Radar_Item (0x2A = 42) 10000000
	148 entities: 148 = 2x(78-1): maybe all the possible states of things in the Lake (two states each), excluding the statue that has 3 states?
	node structure:
	- node_group_id is always 112
	- node_ids is always None
	- node_ints never contains node ids
	- all Radar_Item entities have a list of ints in node_ints, which allways contains only the value 0.
	- node_string is :treasure_box for clams, counter_panel for triangle puzzles, the name of the area for lasers, and None for others.
	'''
	return (
		read_list(f, read_id),		# 0: Fountain particle sources. Always a list of Particle_Source entities, only non-empty for Radar_Item whose id in field 3 is an Obelisk:
									#    the list contains either 3 or 7 Particle_Source, I guess 3 for the small fountains and 7 for the big fountains (completed obelisks).
		read_optional_string(f),	# 1: Name of the mesh file to use when the radar is off (always given):
									#    ter_river_waterfalldecalB, vs_laketest_fountain_off, vs_laketest_lantern, vs_laketest_leaf2, vs_laketest_lotusleaves{,_s,_m}, vs_laketest_lotus{white,yellow},
									#    vs_laketest_vault
		read_optional_string(f),	# 2: Name of the mesh file to use when the radar is on (None if object is not tracked or an Obelisk):
									#    vs_laketest_lantern2, vs_laketest_leaf1, vs_laketest_lotus{white,yellow}2, vs_laketest_vault2
		read_id(f),					# 3: The entity tracked: Obelisk, Audio_Recording, Machine_Panel, Laser, Door, or None (for leaves that do not match anything in the world?)

		read_byte_array(f, 5),		# 4: Always all 0.

		read_int(f),				# 5: Number of possible states (I guess): 0 for non-tracked objects, 1 for tracked objects without particles, 46 for small fountains and 54 for big fountains.

		read_byte_array(f, 4),		# 6: Always all 0.
	)
