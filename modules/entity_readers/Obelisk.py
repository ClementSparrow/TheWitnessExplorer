from modules.entity_readers.helpers import *

def read_Obelisk(f):
	'''
	Obelisk (0x21 = 33) 10000111
	6 entities: 0=monastery, 1=town, 2=treehouse, 3=symmetry island, 4=river, 5=shaddy trees.
	- node_group_id is 3, 212, 460 or None
	- node_ids is always None
	- node_ints never contains node ids
	- all Obelisk entities have a list of ints in node_ints.
	'''
	return (
		read_optional_string(f),		# 0: Mesh file for the obelisk, always 'obj_Obelisk_01'
		read_int(f),					# 1: Always 0.
		read_int(f),					# 2: Number of environmental symbols for this obelisk.
		read_optional_string(f),		# 3: None or 'obelisk_peal_a' for #0 and #1, which is the name of a sound file.
		read_array(f, 8, read_float32),	# 5: Always (-1.0, -1.0, -2.0, 1.0, 3.0, 0.0, 0.463, 1.0) except for #0 (monastery) for which the 4th float is 0.4 instead of 1.0.
		read_array(f, 4, read_float32),	# 6: Always (1.0, 0.6, 0.0, 1.0). -> Could be an rgba color in the range 0.0-1.0.
										#    This color would be #FF9900FF, which is the orange of the traced symbols on the obelisk.
		read_float32(f),				# 7: Always 100.0. Could be the light intensity of the color in the previous field (as in the last fields of Inanimate entities).
		read_byte_array(f,9), 			# 6: Always all 0.
		read_float32(f),				# 7: Unknown number:
										#    * 1.0 for #0 (monastery), #1 (town), and #4 (river);
										#    * 2.0 for #2 (treehouse);
										#    * 5.0 for #3 (symmetry island) and #5 (shaddy trees)
										#    -> number of rings hidden in the ground? No, it does not seem to match. It's not related neither to the max number of puzzles on a face.
	)
