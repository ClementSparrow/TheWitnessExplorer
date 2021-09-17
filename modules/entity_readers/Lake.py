# -*- coding: utf-8 -*-
from modules.entity_readers.helpers import *

def read_Lake(f):
	'''
	Lake (0x17 = 23) 01111101
	78 entities: Water planes.
	Node structure:
	- node_flags …
	- node_string is only provided for #12 (hardSecret_water), 20 (moving_water_level), and 60 (:OCEAN_REFL_Z_DONT_DELETE).
	- node_ids can point to a Door entity -> Because the state of the Statue depends on the openning of doors in the mountain, and clams for vault doors?
	- the ids in node_ints can be ids of Door entities
	- node_float is never provided (-1.0).
	- all Lake entities have a list of ints in node_ints.
	- node_final_floats depend on the presence of grid cordinates in field 6.

	This seems to be an editor-only entity, which is always used to generate a save_{entity_id}.mesh file.
	The mesh is a simple rectangle for the non-sea lakes, but for sea lakes the mesh contains 7 geometries, one for each level of detail from 0 to 6 included, with 2^(6-LOD) subdivisions of the geometry.
	In some sea lakes, the mesh is roughly cut along some simple polygonal shape (the same at all LODs), although nothing in the Lake entity data seems to match this shape. For instance, in #252276, we see the shape of the Hub's dock.
	'''
	return (
		read_array(f, 2, read_float32),		# 0: (10.0, 10.0) for sea tiles, otherwise two dimensions of a bounding rectangle which diagonal is twice the radius provided in node_final_floats.
		read_byte(f),						# 1: Boolean.
		read_byte(f),						# 2: Boolean. When set, grid coordinates are provided in field 6.
		read_id(f),							# 3: Optional Light_Probe. If set, usually #100290, ':the_sky_probe:'
		read_id(f),							# 4: Optional Light_Probe.
		read_byte_array(f, 3),				# 5: Booleans. Second is always 0.
		read_array(f, 2, read_signed_int),	# 6: Coordinates in a 8x8 grid or (-1, -1). For each cell of the grid, there is 0 or 1 Lake entity with its coordinates in this field.
											#    When grid coordinates are note provided, node_final_floats only provides a boundig sphere radius and the position vector is null.
											#    Otherwise, node_final_floats reflect the position in the grid with cells 96.0 units wide and a horizontal grid centered at (0,0,-0.5).
											#    There are however exceptions: coordinates (2,4), (3,3), (3,5), (4,2), (4,5), (5,4) and (6,3) are shifted from this grid.
											#    That's actually the cells adjcaent to the missing ones. And the missing ones would have coordinates matching the island surface.
											#    -> These are sea tiles.
		read_byte_array(f, 4),				# 7: Always all 0.
		read_array(f, 11, read_float32),	# 8: No idea. Probably shader parameters: water color, wave height, etc.
	)

