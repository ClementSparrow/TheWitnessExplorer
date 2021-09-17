from modules.entity_readers.helpers import *

def read_PatternPoint(f):
	'''
	Pattern_Point (0x26 = 38) 10001101
	3119 entities.
	A start/intermediary/end point of an environmental puzzle.
	node structure:
	- node_flags can be 00000000 (most frequent), 00000002, 00000020, 00000400, 00001000, 10000000, 20000000, 20001000.
	- node_string
	- node_group_id is often provided but not always.
	- node_ids can point to a Inanimate, Door, Pattern_Point, or Boat entity. -> The entity on which the pattern point is?
	- node_float is never provided (-1.0).
	- node_ints is never provided.
	- node_final_floats only has a first float set, the three others are 0.0.
	'''
	return (
		# note: this start is almost a match for the end of a node structure, starting at the optional string. (but there is no additional structure if the second id is not null)
		read_optional_string(f),        #  0: None or the name of the pattern of which this is a point (all patterns that share the same start point have the same name).
										#     The name matches the node_string of the corresponding Obelisk_Report, unless multiple environmental puzzles start from the same circle and then, they all
										#     have a node_string starting with the same prefix and followed by an _ and a letter, and then this field matches the prefix.
		read_id(f),                     #  1: Can be None, Pattern_Point, Inanimate, Obelisk_Report, Collision_Volume (and there is an UnkownNode that would be Entity-13104 in Entity-13106 that is Pattern_Point-193 for the 'sun' pattern).
		read_id(f),                     #  2: Can be None, a Collision_Volume, or a Pattern_Point -> The condition for this Pattern_Point to be reachable? (Collision_Volume for the start points and Pattern_Point for the other points?)
		read_array(f,11,read_float32),	#  3: No idea what it is.
										#     Last four floats might be an RGBA color with values in the [0.0-1.0] range, but the color does not match anything in the puzzle
										#     -> unless it's a color contrast, chosen specifically to be different?

		read_byte(f),					#  4: Always 0.
		read_float32(f),				#  5: Always 1.0.

		read_byte_array(f, 4),			#  6: Four booleans.
										#     - 1st seems to indicate a possible start point for a pattern. There is usually only one entity that has the first boolean set for each environmental puzzle.
										#       However, some pattern can have multiple start points, possibly corresponding to different conditions.
										#		For instance, all 5 banyan EPs share a same branch network, but each has his own start point.
										#     - 2nd seems to indicate a possible end point for a pattern. There is always at least one for each environmental puzzle.
										#       It's possible that it also indicate fail states (e.g. the slope in cement factory if the slope is not raised). Then, there is a condition provided in field 27.
										#       The complete name of the EP ending in this point is provided in field 20, or is the name in field 0 if field 20 is None.
										#       Note: "church" has two end points, because we can finish it with the sawmill slope going up or down?
										#             generated_force_bridge_a has 3 endpoints and generated_force_bridge_b{1,2} have 6 each…
										#       When multiple EPs have different start points but a same endpoint (like the two on the sliding marsh platform or the treehouse bridges),
										#       field 20 is used in the Pattern_Point for the start point rather than in the endpoint.
										#     - 3rd is only set for some entities with node_flags=20000000 for b_front, b_rear, dam, dock_stripe, lake_dip, and water_level.
										#     - 4th is very rarely set: only for the start points of church, shadow_tree_{1…3}, shapers_{rotate,slide} and stretched_line,
										#       and two other points for each ofshadow_tree_3 and shapers_slide. When it's set there is always an integer as the last float of field 17.


		read_byte_array(f,4),			#  7: Always all 0.
		
		read_float32(f),				#  8: In the range [0.42-4.0], most often 1.0.
		read_id(f),						#  9: a Marker or Pattern_Point or None.
		read_id(f),						# 10: an Inanimate or Boat or None.
		read_float32(f),				# 11: in the range [0.0-1000.0], all possible values.
		read_if(f, lambda src: (read_nullterminated_string(src), read_int(src))), # 12: Only provided for all the 'b_front' Pattern_Points except #567 and those that have a Boat entity in field 10. It is then always ('b_front', 0). -> My guess is that it's a joint name, because the Boat is a different class than the Inanimate, so it is treated differently.
		read_byte_array(f, 6),			# 13: Six booleans. Second and fourth can only be set if the first is set.
		read_float32(f),				# 14: -1.0, 0.0 (most frequent), 1.0, 5.0, 10.0, 15.0, or 100.0
		read_byte_array(f, 2),			# 15: Booleans
		read_id(f),						# 16: a Pattern_Point or Slab or None. When a Pattern_Point, it's allways one for the same environmental puzzle, or a link between a b_rear and b_front.
		read_array(f,19,read_float32),	# 17: Seems to be 2 floats, 4 RGBA 0.0-1.0 encoded colors, and another float.
										#     When first boolean in field 6 is set, the colors seem to match the particles of the environmental puzzle and last float has a different value.
										#     (otherwise, they are often -but not always- white and 0.7). -> the last float could be a light intensity value, as in the Inanimate entities?
		read_byte(f),					# 18: 1, 16, 32 (for all tree_bridge_a, b_front, askew, colored_glass_door, DesertShorelinePuzzle, and church but 1), 96 (for all spec_ruin but 1), or 100 (for all spec_wall_a but 2) -> flags? Exceptions are always 1.
		read_float32(f),				# 19: in the range [0.05-6.0]. Most frequent is 1.0.
		read_optional_string(f),		# 20: The name of the environmental puzzle, if different than group name in field 0. See field 6.
		read_byte(f),					# 21: Boolean.
		read_float32(f),				# 22: ≥0.0, always an integer value, min 0.0 (most frequent) max 40.0. Non-null values are:
										#     1 for surface_angle (on the side of the two-part linear bridge in the marsh), 3 for askew (cement factory slope), 4 for three_over_a (one of the shipwreck hexagon),
										#     5 for bush and monastery_front, 8 for (another) monastery_front, symmetry_glass_{down,up}, 9 for (another) monastery_front, 10 for bridge (town bridge from tower),
										#     mountain1 (yellow pipe of the Gangaji vault), spec_boat (desert ruler), starting_wall{_b}? (walls from from the boat), 12 for flow_{around,inward,outward}
										#     (purple marsh pool), 28 for surprise (see cirle near the marsh viewed from the tree bridge in the mountain),
										#     and 40 for hitch (yellow agricultural stuff near tutorials?) and path (river).
										#     -> A minimal view distance?
		read_byte_array(f, 3),			# 23: Booleans. Second is always 0.
		read_array(f,7,read_id),		# 24: Seven independent entities (not a null-terminated list!)
										#     - 1st can be a Marker or None;
										#     - 2nd can be a Marker or None;
										#     - 3rd can be a Cloud, Door, Laser, Lake, Light, Machine_Panel, Marker or Pattern_Point;
										#     - 4th can be a Door, Marker or Pattern_Point;
										#     - 5th can be a Lake, Marker or Pattern_Point;
										#     - 6th can be a Door (Door-296 with node_string 'double_ramp_top' for Pattern_Point-2482 in EP 'church' in the cement factory) or Pattern_Point;
										#     - 7th can be a Pattern_Point or None. -> Next Pattern_Point? No, it's only provided 129 times for Pattern_Points from only 47 environmental puzzles.
		read_byte(f),					# 25: Boolean.
		read_int(f), 					# 26: bitset. Most often 4.
		read_optional_string(f),		# 27: The name for a condition that must be satisfied to be able to trace the puzzle (which can take arguments?). Can be None, 0, clip_to_markers, cloud_must_be_lit, disable_if_door_is_not_open, dynamic_particle_target, extra_marker_ids, intersector, intersector_new, intersector_new_that_always_can_move, intersector_new_with_colinearity, intersector_on_water, intersector_sun, intersector_with_intersector_id3, intersector_with_nearest_dynamic2d, light_must_be_on, min_solve_tv_scale, movie_interp, no_magnetism, nop_with_colinearity, nop_with_colinearity_and_clip_to_markers, panel_must_be_on, project_through_marker, project_through_marker_and_door_must_be_open, pylon_and_force_field, snake_max_solve_distance, sun_spec, valid_only_below_top_plane, valid_only_when_point_inside_marker, valid_only_when_viewpoint_inside_marker, water_completes_me
		read_vector32(f),				# 28: Most often (1.0, 1.0, 1.0), but can be different, although usually close to these values (can be greater than 1, always strictly positive)
		read_id(f),						# 29: Always a Waypoint_Path3 or None. Provided 745 times (in comparison, there are 787 positions in total in the first fields of Waypoint_Path3 entities).
		read_array(f,4,read_float32),	# 30: min: (0.25, 0.0, -0.5, 0.0), max: (1.7, 0.0, 6.0, 1.5) -> second is always null.
		read_byte(f),					# 31: Boolean. Only set for one of each generated_force_bridge_{a,b1,b2} and for all 16 colored_glass_door (cyan door of the greenhouse).
		read_id(f),						# 32: Always None or a Pattern_Point. When a Pattern_Point, it's always one for the same environmental puzzle (same string in field 1). But it only happens for two tree_bridge_a, one ship_positive, and one rope_outer.
		read_byte(f),					# 33: Boolean. Only set for #910 (askew)
	)


