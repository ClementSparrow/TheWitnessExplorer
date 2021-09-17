from modules.entity_readers.helpers import *

def read_PressurePlate(f):
	'''
	Pressure_Plate (0x28 == 40) 10000000
	263 entities.
	Used for the pressure plates in the Keep, but also for the ones triggering timed doors:
	  in the Sagrada Familia (#201, node_string = peekaboo),
	  entrance of the secret cave (#17),
	  logging area (#84),
	  treehouse laser (#199).
	I guess they hide a platform in the ground, pressed by default, and exploit the mechanism
	to rise the platform by solving a puzzle panel to trigger a timed animation.
	Also, Pressure_Plates seem to be used in the recognition of the environmental patterns on them.
	node_ids is always None
	node_ints never contains node ids
	all Pressure_Plate entities have a list of ints in node_ints, that contains only the value 0.
	'''
	return (
		read_optional_string(f),		#  0: The name of the mesh file to use for this pressure plate. Always set.
		read_byte_array(f,24),  		#  1: Always all 0.

	#	Role of the platform in broader puzzles
		read_id(f),             		#  2: Pattern_Point-155 (247), Pattern_Point-2811 (223), Pattern_Point-279 (193), Pattern_Point-201 (74), Pattern_Point-254 (68),
										#     -> the start of a pressure plate environmental puzzle (there are five because the cyan platform maze has two start points).
		read_id(f),             		#  3: The Machine-Panel in which we draw by stepping on the Pressure_Plate: 470 (yellow), 355 (magenta), 567 (green), or 558 (cyan).
										#     Always set except for standalone platforms.
		read_byte(f),           		#  4: Platform type: 0 = node of a puzzle, 1 = grid segment of a puzzle, 2 = standalone platform
		read_byte(f),           		#  5: Platform shape: 0 = rectangular, 1 = Circular (start), 2 = end, 3 = connecting to a circle
		read_int_array(f, 2),   		#  6: Nodes of the puzzle connected by the platform (if the platform is on a node, then the second int is 0).
										#     In the Keep, puzzles use a 5x5 grid = 25 nodes plus up to two exits = 27 nodes, and the values can thus range from 0 to 26. 
										#     Node numbers start from 0 in the bottom-left corner to the right and then up when we see the maze from its puzzle panel.
										#     So, segments that are horizontal from this point of view have nodes n and n+1, and vertical ones have nodes n and n+5.
		read_byte(f),           		#  7: Always 0.

	#	Appearance and sound
		read_optional_string(f),		#  8: Name of a sound to play when the platform starts rising.
										#     Always None except for the standalone platforms: , "loc_end_pressure_plate_up" for peekaboo, and "pressure_plate_up_single" for the three others.
		read_float32(f),        		#  9: Always 1.0 except for two of the standalone platforms: 0.0 for #84 and 0.3 for #17.
		read_optional_string(f),		# 10: Name of a sound to play when the platform finishes rising.
										#     Always None except for the standalone platforms: "loc_end_pressure_plate_up_finish" for peekaboo, "pressure_plate_up_finish" for the three others.
		read_array(f,4,read_float32),	# 11: An RGBA 0.0-1.0 encoded color. Always (0.1, 0.1, 0.1, 1.0) except for peekaboo, for which it is (0.2840, 0.0, 0.0, 1.0) (dark red)
		read_array(f,4,read_float32),	# 12: An RGBA 0.0-1.0 encoded color. Always (0.7, 0.7, 0.7, 1.0) except for peekaboo, for which it is (0.9940, 0.0, 0.0, 1.0) (bright red)
		read_vector32(f),       		# 13: Position of the platform in the world. This is actually exactly the same values than the first three coordinates of node_world_position.
		read_byte_array(f, 5),  		# 14: Always all 0.
		read_vector32(f),       		# 15: An RGB color vector (values between 0.0 and 1.0) corresponding to the color of the platform when depressed.
		read_array(f,2,read_float32),	# 16: Allways (1.0, 10.0). The 1.0 is probably the alpha component of the previous color. I don't know what the 10.0 is.
		read_byte_array(f, 16), 		# 17: Always all 0.

	#	Stuff for the four timed doors only:
		read_id(f),             		# 18: Door-86 (201), Door-179 (199), Door-165 (84), Door-0 (17) -> the timed door opened by stepping on the plate (logging area, tree house laser cabin, access to the caves, access to the flying elevator room)
		read_float32(f),        		# 19: Always -1.0.
		read_float32(f),        		# 20: Timer in seconds: -1.0 for the platforms bound to a puzzle panel, a positive value for the others
										#     -> 12.5 for secret cave, 20.0 for logging area, 15.0 for the treehouse laser, and 17 for the Sagrada Familia doors.
		read_optional_string(f),		# 21: Always None except for the standalone platforms, which have "pendulum_tick".
		read_float32(f),        		# 22: Always 0.3, except the treehouse laser, for which it is 1.1. No idea what it is.
		read_byte(f),           		# 23: Boolean. Always 1 except for peekaboo, where it's 0. Auto-raises when 0? Raises even if we are on it when 0? Start clock when we step on it?
		read_vector32(f),       		# 24: Always (1.0, 0.5, 1.0) except for peekaboo, for which it is (0.25, 0.015, 0.04). No idea what it is, except maybe a color for the editor?
	)