# -*- coding: utf-8 -*-
from modules.entity_readers.helpers import *

def read_Door(f):
	'''
	Door (0x0a = 10) 10000001
	327 entities: anything that can be open or closed (including, but actually not restricted to doors) or more generally in two different states (e.g. an elevator with two floors).

	Node structure:
	- node_flags …
	- node_string …
	- node_ids can point to a Boat, Door, Machine_Panel, or Inanimate entity
	- the ids in node_ints can be ids of Door entities, or ids of Doors and Light entities
	- node_float ….
	- node_ints …
	- node_final_floats …

	This seems to be an editor-only entity, which is always used to generate a mesh file, either as save_{entity_id}.mesh or from the filename given in field 18.
	'''
	return (
		read_vector32(f),						# 00: Dimensions of the Door (used to generate a Slab-like mesh if no mesh file is provided in field 18?)
		read_optional_string(f),				# 01: Name of a color, texture, or material. It can be:
												#     mid_brown, brown{1,3,5}, white, light_gray, gray, black, bright_red, violet, blue, tree_color, shar_cortenV2-medium, slate, loc_swamp_flatWood, rust
												#     -> In the generated mesh file, it will be the first parameter of the unique material. If not provided, 'entrance' is used as a default value.
												#        note that if a mesh file is provided in field 18, the name provided in field 1 may not appear in this mesh file.
		read_optional_string(f),				# 02: Only provided for Door-68 (#6324: ':the_sun:') where it is 'the_sun'.
		read_array(f, 20, read_float32),		# 03: - The first seven may be identical to (or close to) the node's world position and orientation.
												#     - The next seven can be identical to the floats in node_ids (except the 4th is missing) if provided (otherwise it's (0,0,0) and (0,0,0,1) ).
												#	  - 14 can take values between 0.01 and 10.0.
												#	  - 15 is always 0.0
												#	  - 16 is actually not a float but an int that can be 0 or 1. The value 1 happens only once, for Entity-4865 (Door-229).
												#	  - 17 is actually not a float but something that is usually all 0 but can also be 0x8000003f for 39 entities.
												#	  - 18 is always the same as the previous one (17).
												#	  - 19 is actually not a float but something that is usually all 0 but can also be 0x0000003f or 0x000000bf for 6 entities.
												#    -> The last values seem to be shifted from one byte and could actually merge with the next field (or fields) to encode floats 1.0 (0x3f800000) and -1.0 (0xbf800000) or 0.5 (0x3f000000).
												#	 -> It's thus likely that this field is actually a list of 16 floats followed by a boolean byte and 6 other floats, merging with the next two fields.
		read_byte(f),							# 04: Most often 0, but non-zero and looking like a bitmask for 43 entities:
												#     63=0x3f for entities [6566, 8635, 13064, 13076, 40842, 40866, 41548, 49860, 49943, 160356, 161325, 161594, 166269]
												#	  64=0x40 for entity 97402
												#     191=0xbf for entities [134, 1563, 2829, 6698, 13265, 13381, 13451, 14394, 15267, 19620, 19830, 40584, 40685, 40843, 41162, 41329, 97474, 97822, 97909, 98185, 98349, 99506, 99531, 99556, 99579, 99602, 99631, 99654, 99677]
		read_float32(f),						# 05: Can be -1.0, 0.0 or 1.0.
		read_optional_string(f),				# 06: Allways None, except for Door-131 ('open_speedrun') and Door-71 ('open_boat').
		read_optional_string(f),				# 07: Seems to be the name of a script to execute when the door is open. Can be:
												#     boat_ramp (3,59), bridge_control (127), clev_cable (164), complete_lotus (89), depower_triangle_cable (0), elevator_glow_control (257),
												#     glow_via_open_t (33,46,64,81,101,105), hull_doors (52), laser_platform (284),
												#     lotus_barrier (9,14,19,20,23,168,172,177,180,185,193,194,200,207,208,214,217,220,225,231,235,243,250,253,260,262,268,272,274,278,),
												#     peekaboo (86,238), quad_door_gauge (192,210,307), update_moving_water_level (229), vault_open (69,71,84,129,131,282,320)
		read_byte(f),							# 08: Boolean. More often set than unset, but unset is very common too.
		read_array(f, 8, read_float32),			# 09: last two are often 1.0 90.0 (or -90.0).
												#	  - 0 can take values between -3 and 21.2.
												#	  - 1 can take values between -0.73 and 0.44.
												#	  - 2 can take values between -1.476 and 1.942.
												#	  - 3 is always 0.0 except for Entity-55278 where it is 0.2 (the dock/wall of the glass factory).
												#     - 4-5-6 can only take two values: 0.0 or 1.0. (most often (0.0, 0.0, 1.0)).
												#	  - 7 seems to be a rotation angle, as it can take the values -90.0, -35.0, 0.0, 22.5, 25.0, 35.0, 90.0, 110.0, 135.0, 140.0, 174.0, 180.0, 360.0.
		read_array(f,6,read_optional_string),	# 10: Three pairs of names of sounds to play when the door opens (first of each pair) or closes (second of each pair). The three pairs concern respectively the start of the sound, then end of the sound, and the loop played between start and end.
		read_float32(f),						# 11: Usually 1.0, but can also take the values [0.5, 0.6, 0.8, 0.9, 1.2, 1.5]
		read_float32(f),						# 12: Usually 1.0, but can also take the values [0.4, 0.8, 0.9, 0.95, 1.2] (1.2 only for the Psalm46 vault's safe).

		read_byte(f),							# 13: Boolean. Usually unset, but still set for 52 Doors.
		read_list(f, read_vector32),			# 14: Always two vectors. They often differ only in their second coordinate with an 1.2 difference.
		read_id(f),								# 15: only set for the two obj_Boat_SideDoors (3 and 59) to a Collision_Volume, and for loc_specRuin_aqued_liftNew (284) and loc_quarry_lift (275) to another, mesh-less, Door.

												#     The next two fields seem to be respectively the end and the start times of an animation relatively to an external animation?
		read_float32(f),						# 16: Always 1.0 except for Entities-222299-222300 (sidedoors of the boat) where it is 0.95 and Entity-105253 (shady trees' timed door) where it is 0.9.
		read_float32(f),						# 17: Always 0.0 except for Entities-222299-222300 (sidedoors of the boat) where it is 0.08 and Entity-13381 where it is 0.3.
		read_optional_string(f),				# 18: Name of the mesh file that contains the object to be animated as a door, if any. Otherwise a slab is generated as save_{entity_id}.mesh.
		read_if_id(f, read_float32),			# 19: The id is the one of another Door that should be animated together with this one (only one of the two Doors has this field set).
												#	  Note that there is a problem with Entity-49822 (Door-62, the large container wall in the greenhouse), which refers to Entity-211382 that does not exists.
												#     So, it's still possible that I was wrong in some entity format and failed to notice it is actually two entities.
												#     The float is always 0.33.
		
		read_float32(f),						# 20: Always 0.0.

		read_float32(f),						# 21: Must often 5.0 but can also take values {0.0, 5.1, 8.0, 12.0, 17.0, 19.0, 20.0}. Values > 5 seem to concern timed doors, things that can raise and lower between two levels, and the glowing parts of the flying elevator (20.0).
		read_byte(f),							# 22: Boolean. Always set except for Entity-55278 (Door-295), which is the dock/wall of the glass factory.

		read_byte(f),							# 23: Always 1

		read_float32(f),						# 24: Always a float32-encoded integer. Can take values {0.0, 2.0, 3.0, 5.0, 6.0, 10.0, 20.0, -1.0}. Most frequent value is -1.0.
												#	  Highest values are for big heavy doors like the vault ones.
		read_float32(f),						# 25: It actually seems be two shorts. The first is usually 0 but can be 0xcccd (when x=1.8 in field 27) or 0x9ba6 (when x=1.0).
												#     The second is always 0 exccept for Entity-4809 (Door-31, rotating panel in the laser room of the desert?), where it is 0x0100.
		read_short(f),							# 26: Most of the time 0, but can also be 15172=0x3B44 (when x=1.0 in the next field) or 15564=0x3CCC (when x=1.8 in the next field)
		read_array(f,4,read_float32),			# 27: It is always (0.1, -1.0, x, 0.0), where x can be 0.8 (most of the time), 1.0 (only for Entity-1443 = Door-127) or 1.8 (for Entities-97909-98349-1563).
												#	  The four unique values are for marsh platforms and grates.
		read_int_array(f,4),					# 28: Usually (-1, -1, 0, 0), but can also be:
												#     - ( x, -1, 0, 0) where each value of x in 1…12 appears exactly for one entity, picked in order in (41066 to 41069) U (41073 to 41080): entities with name "clev_nolight{x-1}".
												#     - (-1, -1, y*256, 0) where each value of y in 1…8 appears exactly for one entity: 99579, 99654, 99506, 99556, 99631, 97822, 99602, 99677 (in that order), which are doors for each of the cages that can rise or lower in the final structure of the marsh (red pool).
												#	  - (-1, -1, 0, z) where z is a bitmask that can be 0x00010000, 0x00010100, 0x01000000 and multiple entities can have the same bitmask.
												#       The first group: I see no relation between these things
												#       The second group has objects that can slide at different positions (the ramp in wood factory and the color lab elevator cable).
												#       The third group has buoys as meshes.
												#    -> It seems to actually be two ints and 8 bytes which can be unique identifiers (for the third) or booleans (for the last 4)
		read_byte(f),							# 29: Boolean. Only set for 16 entities: [13903, 15281, 98100, 195280, 195285, 195287, 195288, 195291, 195292, 207210, 207216, 207222, 207228, 207234, 216795, 252535]
		read_vector32(f),						# 30: Always (1.0, 1.0, 1.0) except for entities [13903, 14161, 15281, 98100, 195280, 195285, 195287, 195288, 195291, 195292, 216795, 232140]
		read_float32(f),						# 31: Always 0.0 except for #232140 where it is 25.0 and #216795 where it is -0.9874706864356995 (=π^2/10)
	)
