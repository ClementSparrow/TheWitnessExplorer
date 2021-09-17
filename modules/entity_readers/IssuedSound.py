from modules.entity_readers.helpers import *

def read_IssuedSound(f):
	'''
	Issued_Sound (0x16 = 22) 01111101
	2 entities
	Node structure:
	- node_flags is always 00040000.
	- node_string is never provided.
	- node_group_id is never provided.
	- node_ids always point to the Boat entity (maybe the boat is the only moving source of sound?). #1 is at the boat's origin of coordinates 
	- node_float is never provided (-1.0).
	- node_ints is never provided.
	- node_final_floats is always (0.5297,  0.0, 0.0, 0.0).
	'''
	return (
		read_optional_string(f),		# 0: Always "boat_coasting", which is the name of a sound file.
		read_byte(f),					# 1: Always 0.
		read_float32(f),				# 2: Always 29.4622.
		read_byte_array(f, 8),			# 3: Always all 0. Note: up to there, the structure of the entity is compatible with the start of AudioRecording entities.
		read_int(f),					# 4: Always 3. Which is the number of floats that follow, so this could just be a variable-length float list.
		read_vector32(f),				# 5: (1.0, 5.0, 15.0) for #0 and (1.0, 0.4, 10.0) for #2
		read_int(f),					# 6: Always 49.
		read_float32(f),				# 7: Always 1.0.
		read_byte_array(f, 14),			# 8: Always all 0.
		read_array(f, 9, read_float32),	# 9: Always (20.0, 0.5, 4.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0).
	)
