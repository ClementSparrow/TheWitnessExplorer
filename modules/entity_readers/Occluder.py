from modules.entity_readers.helpers import *

def read_Occluder(f):
	'''
	Occluder (0x23 = 35) 01111100
	25 entities
	node structure:
	- node_ints is never provided.
	- node_flags is always 00a0001a.
	- node_float is always -1.0 (not provided)
	- node_group_id is never provided.
	- node_ids is never provided.
	- node_final_floats is always a different value for the first, and the three others are always 0.0.
	'''
	return (
		read_vector32(f),	# First coordinate is always 1.0. As a position, it's always slightly outside the bounding sphere defined by node_final_floats.
		read_byte(f),		# Always 1.
	)
