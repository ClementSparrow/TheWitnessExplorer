from modules.entity_readers.helpers import *

def read_Marker(f):
	'''
	Marker (0x1e = 30) 01111110
	1055 entities.
	These entities may actually not be used in the game, but are just marked positions in the editor, e.g. to record positions from which visual scenes can be seen.
	Many markers seem to be control points and events on the flying elevator sequence.
	- node_flags can be 00000000, 00000020, 00000200, 00000400, 00000600, 00040000, 00040020, 00040400, 00040600, 00041000, 08040000 -> an important bit is BIT1= 00040000.
	- node_string is often provided.
	  Only 524 Markers have no node_string, one more than the number of panel puzzles in the game, but their positions do not match with puzzles.
	  101 Markers have the node_string 'reach' and seem to map with reachable areas delimited by doors or transportation systems.
	  35 markers with the name 'nav_runtime_link' seem to identify possible connexion points between these areas (but not where it's doors).
	- node_ids can point to a Boat, Cloud, Door, Slab, Inanimate, or Machine_Panel entity -> these are the intermediary points in EPs?
	- node_ints is never provided.
	- node_float is never provided (-1.0).
	- node_final_floats always has a radius but a null vector.
	'''
	return (
		read_vector32(f),			# 0: When BIT1 is not set:
									#       - First coordinate of this vector always matches the radius in node_final_floats.
									#       - This vector is usually (0.25, 1.0, 2.25), but not always: it is (1.0,1.0,1.0) for #407 and when node_string=SolvingPos, (23.1542, 30.0, 14.4263) when string in field 7 is hedge_maze
									#    When BIT1 is set:
									#       - The radius in node_final_floats always equals half the length of this vector plus twice the last coordinate of the vector in field 6.
									#       - This vector takes specific values for each entity, always strictly positive (can be greater than 100).
		read_optional_string(f),	# 1: Optional. Seems to describe the event that has to take place at this position.
		read_byte(f),				# 2: Boolean. Always 0 when BIT1 is 0. Usually 1 when BIT1 is 1, except when node_string=nav_runtime_link and the first id in field 4 is a Marker.
									#    In that case, all ids in this field are Markers, and all these makers have themselve a first id that point to the same Door entity.
		read_short(f),				# 3: Always 0 when BIT1 is 0, except 1 when the string in field 7 is hedge_maze.
									#    Often  0 when BIT1 is 1, but there are many exceptions: #1013 (node_string=lotus_gate_area), #397-403-431 (node_string=*tracks_starter), #636-702-766-855, #847 (light_prioritize), #626-680-687-743-826, #620-736-818 (fly_speed), #765, #872-906-925-963-965-984 (they all have (0.1, 0.1, 0.8541) as first vector), #982-998-1006-1016 (they all have similar values in the first vector), etc.
		read_array(f, 6, read_id),	# 4: It usually works as a null-terminated list but there are four exceptions where null ids precede non-null ones.
									#    (last three only:) Most often empty, but exceptions are:
									#    - (Marker-770, Marker-789, Marker-795) for #837,
									#    - (None, None, Marker-479) for #613 (hide_entry) and #740 (show_entry),
									#    - (None, None, Marker-34) for #788 (one of 'attention_proxy'),
									#    - (Machine_Panel-222, None, None) for #994 (flythrough_shut_down),
									#    - (Power_Cable-125, None, None) for #950 (flythrough_shut_down),
									#    - (Machine_Panel-375, Machine_Panel-414, None) for #550 (flythrough_disappear),
									#    - (Group-593, Waypoint_Path3-124, Waypoint_Path3-129) for #388 (teleport_by_best_marker).

		read_byte(f),				# 5: Always 0.

		read_vector32(f),			# 6: Not sure what it is and if it should really be taken as a vector rather than two floats and a third, independant one.
									#    Min values are (-1.0, -1.0, 0.0) but -1.0 seem to be the only allowed negative value. Max values are (120.0, 10.0, 10.0). Vector length is always ≥ 1.
		read_optional_string(f),	# 7: A texture: can be None or 0, blank-normal, blue, bright_red, brown3, cyan, darkish_gray, default-normal, gold1, gold3, green_yellow_check, hedge_maze, plaza_brick, tree_color, violet

		read_byte_array(f, 6),		# 8: Always all 0.
	)
