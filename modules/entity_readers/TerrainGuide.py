from modules.entity_readers.helpers import *

def read_TerrainGuide(f):
	'''
	Terrain_Guide (0x32 = 50) 01111100
	325 entities
	Node structure:
	- node_flags are always 00050000.
	- node_string is never provided.
	- node_group_id is only provided for #160 and #235, and is Group-281 for both.
	- node_ids are never provided.
	- node_float is never provided (-1.0).
	- node_ints are never provided (terrain guides are not displayed, so they are not affected by lighting).
	- node_final_floats is always set, although the second and third floats are very often null and the fourth is very often negative.

	Note that this is an editor-only object, used to generate a save_{entity_id}.mesh file.
	'''
	return ( 
		read_byte_array(f, 5),			# 0: Always all 0

		read_array(f, 2, read_float32),	# 1: Both floats usually have a similar value, but the ratio can be as extreme as 10:1.
										#    First is in range 1.234 - 23.852, 2nd is in range 1.756 - 41.796
										#    -> It perfectly fits the bounding box for the vectors in the final list (first two coordinates)
										#    -> In addition, the length of this vector is always very close to (but lesser than) twice the first node_final_floats.
										#    -> It seems to be the dimensions of the rectangular terrain patch on the ground.
		read_int_array(f, 2),			# 2: These two ints are always 5 or greater, up to 40, often a multiple of 5.
										#	 Seems to be the dimensions of the grid on which the patch height are evaluated (number of lines in the grid, not cells).
										
		read_byte_array(f, 8),			# 3: Always all 0.
		read_byte(f),					# 4: Always 1.
										
		read_list(f, read_vector32),	# 5: Control point positions:
										#    Always at least 5 vectors, and usually the number of vectors increases when the dimensions in field 1 increase or when their ratio increases.
										#    All these vectors are bounded by a box which center's coordinates are (0,0,?) and dimensions are given in field 1.
										#    But as far as I can tell, the positions of these control points seem random and unrelated to the numbers in field 2.
	)
