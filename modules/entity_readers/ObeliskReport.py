from modules.entity_readers.helpers import *

def read_ObeliskReport(f):
	'''
	Obelisk_Report (0x22 = 34) 10000010
	135 entities
	- node_flags is always 0 or 0x20 (for church, flowers1, path, windmill, spec_ruin and spec_ruin_2, and shadow_tree_*)
	- node_string is always provided and gives an unique identifier for the environmental puzzle, which is also used to define the texture to use for the report ("env_{string_id}").
	- node_group_id is 3, 212, 460 or None, same as Obelisk
	- node_ids always point to the Obelisk on which the report stands, and the floats it contains are position and unitary quaternion to position the report relatively to the obelisk. Never an optional string.
	- node_float is always -1.0 (not used).
	- node_ints never contains any node id, and the integers list is always [0].
	- node_final_floats is always (0.2122, 0.0, 0.0, 0.0).
	'''
	return (
		read_id(f),						# 0: Only provided sometime.
										#    - For the Keep platforms, it is the id of the corresponding Pressure_Plate.
										#    - for the Mountain bridges, it is the id of the corresponding Force_Bridge
										#    - for the three EPs with the violet stuff in the purple pool of the Marsh, its is Force_Bridge-2 (the yellow one), which is probably a copy-paste error and unused.
										#    - for the treehouse buoy and marsh dock with the boat, it is the id of a Pattern_Point (665 and 711 respectively)
										#    - for the three EPs with the black hole of the theater in town, it is Pattern_Point-1045.
										#    - for the EP with the sun (hotel), it is Pattern_Point-1737
										#    - for the longest of the two EPs with the black sewer hole on the town docks, it is Pattern_Point-1845 (because we need to be on the moving boat?)
										#    -> Why is this needed, if the Report is just a report?
		read_id(f),						# 1: Obelisk on which it appears. (always provided)
		read_short(f),					# 2: Face of the obelisk on which it appears (face numbers increase when you turn around the Obelisk walking rightward).
										#    - monastery: 0 is east (you look at it facing the town)
										#    - town: 0 is east (you look toward the audio log behind the Obelisk)
										#    - treehouse: 0 is north-east
										#    - symmetry island: 0 is east (with the snake EP pattern)
										#    - river: 0 is west (rightmost empty face when you look at the mountain)
										#    - shaddy trees

	#	Unknown
		read_byte(f),					# 3: Always 1.
		read_array(f, 4, read_float32),	# 4: Always (1.0, 0.6, 0.0, 101.0) -> here are similar values in the Obelisk entities… Maybe the dimensions of the cells on the Obelisk?

	#	Special positioning of the symbol on the obelisk (editor data):
		read_int(f),					# 5: face: -1 if automatically placed, or the number of the face it should appear on (same as field 2, always 3).
		read_int(f),					# 6: vertical position of the report on the face: -1 if manually placed, top=0, bottom=8.
										#    So it seems to be editor data, and the game uses the node_world_position to display the symbol.
		read_id(f),						# 7: Only provided sometimes, and then matches the field 1: Obelisk on which the report appears.
										#    Used for the windmill EPs, for the sawmill EPs, and the cloud EP done from the mountain with a 14-minute cycle.
										#    -> I think these are the EPs for which the start point is actually closer to another obelisk. So maybe it's editor data to bypass an automatic attribution of EPs to Obelisks.
										#    Also, when this field is used, the EP is added below the others.

	#	Unknown
		read_float32(f),				# 8: Always 1.0
		read_float32(f),				# 9: Same value as last field of the Obelisk entity on which this Obelisk_Report appears.
	)

