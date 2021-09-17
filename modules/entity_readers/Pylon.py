from modules.entity_readers.helpers import *

def read_Pylon(f):
	'''
	Pylon (0x29 = 41) 01111100
	1 entity: The thing above the Entry Yard's fence, used in the EP with the sun.
	node structure:
	- node_world_position is (-128.91, -163.77, 5.71).
	- node_flags = 00240000.
	- node_string is not provided.
	- node_group_id is not provided.
	- node_ids is not provided.
	- node_float is not provided (-1.0).
	- node_ints is ([], [0]).
	- node_final_floats is (8.4698, -0.0111, 0.2744, 7.4523).
	'''
	return (
		read_float32(f),         # 0: 2.0
		read_float32(f),         # 1: 2.5
		read_byte(f),            # 2: 1
		read_id(f),              # 3: Force_Field-0
		read_float32(f),         # 4: -1.0
		read_optional_string(f), # 5: loc_entryYard_gate_newdoortest
		read_float32(f),         # 6: 1.0
		read_float32(f),         # 7: 1.0
	)
