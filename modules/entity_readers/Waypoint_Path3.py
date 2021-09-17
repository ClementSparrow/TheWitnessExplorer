from modules.entity_readers.helpers import *

def read_Waypoint_Path3(f):
	'''
	Waypoint_Path3 (0x39 = 57) 01111111
	134 entities: one less than the number of EPs… maybe it's giving the discontinuities in the meshes for the EPs? Or some information for the path of the particles of an environmental puzzle?
	These entities are only referenced in Landing_Signal (one for each of the six buoeys), Marker (only 3 times), Cluster, and PatternPoint entities.
	
	node_group_id can be None, 302, 14, 689, 28, 93
	node_string is only provided 29 times and can be: apple_trees, boat (only one that is given to multiple entities), desert, entry_leave, fly_green, fly_hub, fly_mountain, fly_ruin, garden_pan, laser_bounce, ruin_alt, side_door, swamp_fly, tower, towerfly, tree_spoiler, treehouse_entry, window_a, window_b
	node_ids can point to a Door entity
	node_ints never contains node ids
	node_final_floats always has only a radius, which is at least 1m and can be up to 259m and is often quite large.
	'''
	result = (
		read_list(f, read_vector32),	# 00: a list of positions inside the entity's bounding sphere, that seem to form a path.
		read_byte_array(f, 8),			# 01: Always all 0
		read_byte(f),					# 02: Boolean
		read_float32(f),				# 03: Between 1.0 and 52.5. Maybe a distance from the node_world_position?
		read_float32(f),				# 04: Always 10.0
		read_byte_array(f, 4),			# 05: Always all 0
		read_id(f),						# 06: Only provided for 12 entities, it is always a Marker.
		read_byte_array(f, 7),			# 07: Always all 0 except the third (which can be 1 for five entities) and 6th (which is 64 for Entity-124319 with node_string "towerfly")
		read_byte(f),					# 08: Boolean
		read_float32(f),				# 09: Always 1.0 except for Entities-210383-210384, for which it is 0.15.
		read_id(f),						# 10: Only provided for 8 entities, it is always a Marker.
		read_id(f),						# 11: Only provided for Entities-40379-40384, it is always a Marker.
	)
	return result
