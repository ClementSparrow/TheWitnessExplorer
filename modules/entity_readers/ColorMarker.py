from modules.entity_readers.helpers import *

def read_ColorMarker(f):
	'''
	Color_Marker (0x08) 01111101
	25 entities, which are positions in the world controlling the use of LUT tables.
	Node structure:
	- node_flags is always 00040000.
	- node_string is never provided.
	- node_group_id can be None, Group-543 (most frequent), 383 (for #6) or 296 (for #17).
	- node_ids is only provided for #6 (entry_lighten-lut) and point to Door-219 (which both seem to be in the hotel) -> I guess opening a door can change the lighting and call for a different LUT table?
	- node_float is never provided (-1.0).
	- node_ints is never provided (color markers are not displayed in game, and thus, not affected by lighting conditions).
	- node_final_floats always have a node-specific radius but a null-vector position. Radius can be as low as 3.0 (#10) and as high as 103 (for #22: DesertColor01-lut).
	'''
	return (
		read_vector32(f),					# 0: All three coordinates are integers. First can be 0.0 or 1.0, second and third are always equal and can be 1.0, 3.0, 4.0, 5.0, or 10.0.
		read_vector32(f),					# 1: The dimensions of a bounding box, which diagonal's length is twice the radius provided in node_final_floats.
		read_optional_string(f),			# 2: Name of the LUT file. Always set, except for Color_Marker-10 (which seems to be located very close to the bottom of the hub tower).
		read_array(f, 16, read_float32),	# 3: All positive or null except 3rd and 4th, 4.0 at max, and each can be greater than 1.0. Last two are always 0.
											#    There seems to be a 4-float structure repeated 4 times:
											#    - first float is always an integer (0.0, 1.0, 2.0, 3.0, or 4.0). When a 0.0 appears here, all floats following are also 0.0 (exception for #12).
											#      For each entity, the values in this field cannot appear twice in different 4-float structures.
											#    - then three floats, most often in decreasing values.
		read_if(f, read_float32),			# 4: Only provided for Color_Marker-10, where it is 0.5.
	)
