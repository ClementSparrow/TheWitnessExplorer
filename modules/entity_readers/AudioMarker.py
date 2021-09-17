# -*- coding: utf-8 -*-
from modules.entity_readers.helpers import *

def read_AudioMarker(f):
	'''
	'Audio_Marker (0x00 = 0) 01111100
	5495 entities.
	Node structure:
	- node_flags are most often 00000000, but can be 00000001 for #1591 and #2099 (which node_ids point to the Boat), and 00000400 for a few entities with node_group_id set to 383 or 405.
	- node_string is only provided for two entities: #3290 (windmill_turning) and #467 (windmill_turning_distant).
	- node_group_id is often provided, but usually not.
	- node_ids can point to a Boat, Bridge, Door, Force_Field, Inanimate (3399=loc_quarry_lift_platform, 2197=obj_panels_Tree_basic), or 
	  Machine_Panel (groupers_{multicolor_{packed,corners_a},and_stones_matched5,and_spacers_slide}) entity. -> For the Machine_Panel, it seems to be the bridge ones that have multiple exits. They have a specific sound?
	- node_float is only provided for three entities: 0.0 for #3102, and 45.0 for #2465 and #4618.
	- node_ints is never provided (Audio_Markers are not displayed in game, and thus not sensible to lighting conditions).
	- node_final_floats only has a vector position for a tenth entities.
	'''
	return (
		read_vector32(f),				#  0: Always specific values for sound types 0…2 (see bellow).
										#     For sound types 1 and 2, it defines the dimensions of a bounding box, which diagonal is exactly twice the radius provided in node_final_floats.
										#     For sound types 3, it is usually  (10.0, 4.0, 4.0), although it can occasionally take other values.
		read_byte(f),					#  1: 0…4. Type of sound.
										#     0 = ambiant sounds. Only have one sound file at most.
										#     1,2 = sounds with a possibility of footstep sound files.
										#     3 = presence and other environment sound files. No footstep files.
										#     4 = no sound file
		read_optional_string(f),		#  2: Name of a sound file. Most often provided but there are 9 exceptions.
		read_optional_string(f),		#  3: Base name of a sound file. Sometimes provided. The sound files actually have a "footstep_" prefix added to them and a suffix made of {left,right}{1…6}.
										#     (note that sounf names in the previous field can also be footstep sounds without these suffix and prefixes. Otther types of sound seem to have other possible suffixes too.)
		read_optional_string(f),		#  4: Another footsept sound file. When this one is provided, the previous one is too, but there are exceptions.
										#     -> I guess this one gives the sounds for the right foot and the previous field the sound for the left foot or both feet if only one is provided.
		read_vector32(f),				#  5: 
		read_id(f),						#  6: Rarely provided. Can be a Door, CollisionVolume-1653, or Audio_Marker-3344.
		read_float32(f),				#  7: Usually 0.0. Max 1.0.

		read_byte_array(f, 4),			#  8: Always all 0.

		read_float32(f),				#  9: 0.0, 5.0 or 20.0. Same ordering as field 7.
		read_byte_array(f, 2),			# 10: Booleans
		read_float32(f),				# 11: 0.0 to 30.0. Most frequent is 10. Often multiples of 5.0, but not always.
		read_byte(f),					# 12: Boolean.
		read_int(f),					# 13: Always positive, ≤ 63. (thus, on ly uses 1 byte, the three others are null).
		read_float32(f),				# 14: Between 0.0 and 1.0 (most frequent).
		read_id(f),						# 15: Point to another Audio_Marker. Only provided 5 times, always for sound of type 0 with a filename starting with 'amb'.
		# read_byte_array(f,16),
		read_float32(f),				# 16: Between 0.0 and 30.0.
		read_float32(f),				# 17: Between 0.0 and 100.0.
		read_float32(f),				# 18: Between 0.0 and some bugged value (2.3 otherwise).
		read_float32(f),				# 19: Between 0.0 and 1.9.
										#     -> I am not sure if these are really floats. The bugged value in field 18 suggests it's not.
										#        Indeed, we have either positive numbers that are less than 100.0 and have very few non-zero decimals.
										#        This type of number is represented in memory with four bytes, the first two being often 0 or the same (like 33), and the last one being often 3f, 40 or 41.
										#        So it's possible that these numbers are actually colors (RGBA between 0 and 255) or sequences of byte values or even short values.
		read_list(f, read_vector32),	# 20: Empty if sound type is not 3, but contains two vectors if type is 3, the value of which are most often (0.0, 1.0, 0.0, 0.0, -1.0, 0.0) and sometimes half of that or completely different values.
										#     -> When these floats are present, they represent positions, and the midpoint of these two positions is exactly the position vector in node_final_floats.
	)
