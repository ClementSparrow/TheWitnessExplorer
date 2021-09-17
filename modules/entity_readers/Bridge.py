from modules.entity_readers.helpers import *

def read_Bridge(f):
	'''
	Bridge (0x03 = 3) 01111101
	6 entities: the six puzzle bridges in the treehouse.
	node_group_id is always 560
	node_ids is always None
	node_ints never contains node ids
	'''
	return (
		read_byte(f),					# 0: always 0.
		read_list(f, read_id),			# 1: the list of MachinePanels forming the bridge.
		read_list(f, read_id),			# 2: the list of Inanimate entities that define the meshes of the puzzles forming the bridge.
		read_array(f, 5, read_float32),	# 3: always (0., 0., 0., 1., 0.) (so, except for the 1.0, the others could also be null integers rather than floats)
		read_id(f),						# 4: the id of the first puzzle of the bridge that has multiple exits, if any.
		read_int_array(f, 2),			# 5: Always 0
		read_id(f),						# 6: the id of the second puzzle of the bridge that has multiple exits, if any.
		read_int_array(f, 2),			# 7: Always 0
		read_int_array(f, 2),			# 8: usually (-1, -1), but (0, -1) for the first bridge (yellow), (1, -1) for the orange bridge close to the burnt house, and (5, 6) for the other orange bridge.
	)
