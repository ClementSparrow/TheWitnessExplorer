from modules.entity_readers.helpers import *

def read_RecordPlayer(f):
	'''
	Record_Player (0x2b = 43) 01111100
	1 entity: the one to start the challenge.
	node structure:
	- node_world_position = (-37.0, -31.46, -11.05)
	- node_flags = 00841000
	- node_string is "the_lotus_eaters"
	- node_group_id is #558
	- node_ids is not provided.
	- node_float is 35.0.
	- node_ints is ([], [0]).
	- node_final_floas is  (0.5406,  0.0601,  0.0,  0.067).
	'''
	return (
		read_id(f),              # 0: Inanimate-9239 = recordPlayerArm.
		read_id(f),              # 1: Inanimate-19542 = recordPlayerPlatter.
		read_byte_array(f,40),   # 2: All 0.
		read_id(f),              # 3: Power_Cable-159
		read_optional_string(f), # 4: lotus_onlyone_2
		read_optional_string(f), # 5: lotus_onlyone_tricolor_2
		read_int(f),             # 6: 1
	)
