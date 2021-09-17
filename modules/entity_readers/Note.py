from modules.entity_readers.helpers import *

def read_Note(f):
	'''
	Note 01111100
	11 entities: editor's sticky notes on the world.
	node structure:
	- node_ints is never provided.
	- node_flags is always 00040000 except for Note-6, for which it is 00040020.
	- node_float is always -1.0 (not provided)
	- node_string is never provided.
	- node_group_id is sometime provided.
	- node_ids is never provided.
	- node_final_floats is always provided, each time with a different value, but I don't known what it means.
	'''
	return (
		read_optional_string(f),		# 0: Text of the note, always provided.
		read_byte(f),					# 1: Always 0.
		read_float32(f),				# 2: Always 0.2 except Note-5 ('FOREST'), for which it is 0.5.
		read_list(f, read_vector32),	# 3: Two or three positions that all fit in the ounding sphere defined by node_final_floats (radius, then the coordinates of the center).
	)
