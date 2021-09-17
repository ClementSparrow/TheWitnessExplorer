# -*- coding: utf-8 -*-
from modules.entity_readers.helpers import *

def read_Laser(f):
	'''
	Laser (0x19 = 25) 10000100
	11 entities, obviously.
	Node structure:
	- node_flags is always 20060005, except for the monastery, for which it is 20860005.
	- node_string is always provided and gives the name of the area.
	- node_group_id is different for each laser.
	- node_ids is only provided for spec_ruin, which is attached to Door-284.
	- node_float is never provided (-1.0).
	- node_ints is always ([], [0]), except for spec_ruin, for which is is (Door-284, [0, 1]), as its mesh lighting depend on whether it's still underground or at the surface.
	- node_final_floats is always (3.8612, -0.0148, 0.0, 3.0195).

   0: Group-331 treehouse
   1: Group-273 keep
   2: Group-646 forest
   3: Group-651 quarry
   4: Group-326 shadow
   5: Group-302 colors
   6: Group-177 hub
   7: Group-550 spec_ruin
   8: Group-568 marsh
   9: Group-171 symmetry
  10: Group-431 monastery
	'''
	return (
		read_byte_array(f, 20),			#  0: Always all 0.

		read_int(f),					#  1: Always 7. Which is the number of lasers needed to enter the mountain…
		read_optional_string(f),		#  2: Only provided for keep: obj_Laser_Interior_keep, which is the name of an animation file. Indeed, the keep laser is the only one to be suspended.
		read_optional_string(f),		#  3: Only provided for keep: laser_phase_01_keep, which is the name of a sound file.
		read_int(f),					#  4: A unique id: 0 for shadow, 1 for symmetry, 2 for spec_ruin, 3 for treehouse, 4 for keep, 5 for quarry, 6 for marsh, 7 for forest, 8 for monastery, 9 for colors, 10 for hub
		read_byte(f),					#  5: Boolean. Only set for spec_ruin. -> the only broken laser. A boolean to prevent the animation of the head?

		read_byte_array(f, 8),			#  6: Always all 0.

		read_array(f, 4, read_float32),	#  7: First pulse color of the laser. RGBA in the 0.0-1.0 range.
										#     #c25400 for keep, #6fc55b for forest, #cccccc for quarry, #ff716a for shadow, #fff500 for colors, #ffffff for hub, #d2e000 for spec_ruin, #80ffb2 for marsh,
										#     #44ffe5 for symmetry, #b5ff68 for treehouse, #ff686e for monastery.
		read_array(f, 4, read_float32),	#  8: Second pulse color of the laser. RGBA in the 0.0-1.0 range. Always #44ffe5ff, a shade of cyan.
		read_array(f, 3, read_id),		#  9: Always two Inanimate, and optionally a Group (provided for all but forest, quarry, and monastery).
										#     The first Inanimate has always a obj_Laser_Head mesh, and the second Inanimate an obj_Laser_Neck.
		read_int(f),					# 10: A bit mask. Only 11 bits (2 to 12) are used, one by laser?
										#     000000001000    8 forest
										#     000000001000    8 symmetry
										#     000000010110   22 marsh
										#     000000100000   32 colors
										#     000001000000   64 quarry
										#     000010000000  128 treehouse
										#     000011101100  236 hub
										#     000100000000  256 spec_ruin
										#     001000000000  512 monastery
										#     010000000000 1024 keep
										#     100000000000 2048 shadow

		read_int(f),					# 11: Always 0.
	)
