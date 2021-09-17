from modules.entity_readers.helpers import *

def read_MachinePanel(f):
	'''
	Machine_Panel (0x1d = 29) 10001001
	594 entities. I guess, all puzzle panels that are not grouped with others in a line, including shortcut door openers
	node structure:
	  - node_ids can point to a Boat, Door, Force_Bridge, Slab, Inanimate, Video_Player, Lake, Machine_Panel, or Multipanel entity.
	     It seems to be parameters for the autofocus mode:
	     - id of the entity relativelly to which the camera get positioned,
	     - floats to specify this position: 3 or 4 coordinates for a position vector (the 4th is always 1.0?), then 4 coordinates for an orientation of the camera as an unitary quaternion.
	     - and eventually a joint name to say that the position is relative to this bone.
	     In multipanel puzzles, the node_id is the one of the multipanel, and the second float seem to be a coordinate on the horizontal axis.
	     For door-mounted panels, the node id is the node of the door and the joint name is used so that we can still autofocus on the puzzle when the door is open.
	     But if this data is absent, does it mean there is no autofocus, or does it mean it gets the default autofocus position?
	  - node_string seems to be the name of a group and is only set for pannels controlling something or whose state has to be synchronized with other puzzles (including puzzles whose solution depend on the state of other puzzles like the two sound puzzles in town khatz_crazyhorse, or the giant_floor).
	  - the ids in node_ints can be ids of Light and/or Door entities
	  - all Machine_Panel entities have a list of ints in node_ints.
	Note on puzzle names:
	- names of the mechanics:
	   - counter is the orange triangle puzzles
	   - groupers are the stars. groupers_and_spacers* is the green bridge.
	   - stones are the black and white rounded squares.
	   - dots/touch are the hexagons (touch{1…5} are the tutorial panels, touch2_groupers_* are the reprisal in the treehouse magenta bridge).
	   - shaper are the polyominos
	   - sight_cookie are ? the ones seen through the shaders in the monastery?
	   - tree are the apple trees
	   - reflect are symmetry puzzles with tw lines
	- names of areas:
	   - in the entry yard, puzzles are straight (there is another one in the monastery), right_angle, simple_maze{1…3}, two_starters_one_finisher, entry_area_cable_switcher,
	     junction_force_field_new (opens the fence) and junction_force_field_new_sly (this one opens the hotel, but is actually hidden under the hill between the fort and the vault).
	   - in symmetry island, puzzles are reflect_hmirror{1…6} (1 is on the building's door), reflect_rotation* (1 and _asymmetric_maze{1,2} on the first side, _asymmetric_maze{3,4,4} on the other side,
	   	 although the last two are different puzzles even if they have the same name).
	   	 Door to symmetry island is touch_dots_entry_guard. First row is reflect_touch{1…5} (6 and 7 are in the caves), second row is reflect_colored{1…6}, disappearing line is fade{1…7}.
	   	 Door to the laser row is junction_sym_isle_ramp. Laser row is implicit_reflect_dots{_partner}?_{1…3} (_partner for the blue ones). Optional set is symmetry_translucent{1…5}.
	   - khatz is the interior of the mountain
	   - lotus is the challenge
	   - symmetry_translucent are the optional puzzles on symmetry island
	   - bird is the jungle
	   - shadow is the shadow forest. Subgroups are shadow_grid{,2,3} for the first puzzles, shadow_part2_{1…5} for the next ones with the metal grid shadows as distractors, shadow_landing_{0…7} for the pines and shadowpath_{1…3,5,6} for the dead trees.
	   - colored_lights_intro* are the two in the container in the greenhouse.
	- special puzzle names:
	   - end_laser_progress is the yellow box at the top of the mountain
	   - hub_duo is the red puzzle that mixes shadow and specular reflexion
	   - junction_force_field_new_sly ?
	   - khatz_crazyhorse is the hexagonal entrance of the mountain.
	   - _combo* are the multi-panel in the mountain where you have to accumulate the constraints from the previous ones in the row.
	   - letorre ? the stone pillar puzzle in the entry yard?
	   - creaky_bunker ?
	   - dot_sling is the puzzle in the cave that looks like the ripple ones but is separated from the them and do not have hexagons at every intersection.
	   - snake_path is the puzzle shaped like the river at the top of the mountain.
	   - violet_swipe_{a,b} ?
	   - spec_glass_panel_blank seems to be the mirror in town
	   - touch2_groupers_{a,b} are the two treehouse puzzles that are reprisals from the hexagons tutorial set.
	   - divide{n} are the segregation tutorial
	   - divide_field_* are treehouse puzzles, among the first ones in the first bridge.
	   - open_pressure_plate_door are all the puzzles with a straight line to open a door (or a treasure chest in a vault). But not the laser activation ones, that are just "laser".
	   - ripple* are the puzzles where we need to pass through every intersection of the grid (1…5 in the cave, new_{a,b} near the entry yard).
	   - knowledge_stones_colored_fade1 is the Gangaji vault.
	'''
	# Things to look for:
	# - there should be a way to know whether the grid is drawn by the software or if it uses a predrawn texture
	# - can the line know where to go from the drawing of the grid alone, as for the EPs? Otherwise we need the graph structure of the grid an positions of the starting and end points
	# - In both cases we need the colors of the grid.
	# - colors of the line for tracing, traced, blinking upon completion, and error
	# - I think we only need definitions of symbols types and positions and colors for the grids that can be drawn by the software.
	# - and size of breaks in the grid, rounded corners, grid width, etc.
	# - need autofocus position
	# - need booleans to know if errors should be highlighted and if the puzzle should be shut off in case of wrong input.
	# - concerning the definition of the grid structure, note that in the melted row of the glass factory, all three puzzles are different entities, but share a same solution. The last two have the same grid structure (only melted for the last one) and the same name in the first field.
	# Some puzzles blink the line in case of error (e.g. the monastery bonsai), but some others don't. There should be a parameter for that.
	result = (
		
		read_optional_string(f),				#  0: The name of the puzzle. Multiple puzzles can have the same name. Always provided. -> is this how we access the puzzle definition, by its name?

	#	Appearance
		read_array(f, 6, read_float32),			#  1: All except 2nd and 3rd are in the range [0.0-1.0]. Seems to be two colors in the extreme range of those used in the puzzle?
												#  2: Colors of the puzzle (19 RGBA values between 0.0 and 1.0)
												#     - 1st seems to be the color of the grid (although often slightly darker because specular reflexion brightens the grid).
												#     - 2nd seem to be the color of the black hexagons. Or is it 3rd?
												#       2nd to 6th included are 030303 (almost black) for all sight_cookie* puzzles, which do not have this color. -> Seem to be default value when not applicable.
												#     - 3rd-4th-5th are the colors of the hexagons on the grid: any line / line we control / other line. (not necessarily: for the shipwreck puzzle, the two line colors are reversed)
												#     - 6th 
												#     - 7th is the color of the line as we draw in the puzzle.
												#     - 8th is the background color of the grid.
												#       actually, it can be FFFFFF (white), e.g. for the shadow puzzle in town, so I guess it only appears darker than actual ingame color because specular reflexion brightens it.
												#       But for sight_cookie*, it is 3A341B, very dark brown, which does not match any color of the puzzle.
												#     - 9th color matches the color of the line once the puzzle is solved (or maybe one of the lighter ones when the line blinks on successful completion)
												#       Note that the alpha channel is usually FF but not on the reset_pressure_plate puzzles (93) to reset the keep platform puzzles.
												#       I think it is used to make the line fade to gray after the line has been drawn, to put the puzzle back in a state where it appears unsolved.
												#       Same thing should happen with the container openers in the greenhouse.
												#       For the Keep pressure_plates{1…4}, the puzzle panel gets a white line when the maze is completed, but the color given by this field matches a darker
												#       version of the pressure plates.
												#     - 10th color is most often 00FF00FF (green), but when it's not, it matches the cell fill colors. Tested for divide* (blue) and touch{n} (green).
												#       But for the glass factory puzzles, where cells are transparent, it also matches the color of the line when completed (slightly greener).
												#       Idem in first row of symmetry island, the blue puzzles of the laser set and the door to that set (slightly bluer: 00FFE1FF instead of 00FFDEFF).
												#       In the second row, with two different colors for the two lines, it matches the yellow of the second line when completed (FFEE00FF).
												#       It is the same color for the third row with the yellow line disappearing, but the alpha channel goes from FF to OC when the line totally disappear.
												#       For the yellow puzzles of the laser set, 9th color matches the color of the line completed (FFDE24FF, yellow slightly orange), but the 10th color is white.
												#       -> it is the same as the 9th color, but for the second line? Value would be irrelevant if there is only one line.
												#     - 11th has been white all the time, but is D8FFFFFF (very light sky blue) for the first row of symmetry island puzzles,
												#       CAFFFB (light sky blue) for the second row, 4DFFF4 (sky blue) for the third row, but white again for the door to the laser and the laser set.
												#     - 12th is the same than 11th, except in the symmetry island puzzles with two lines of different colors:
												#       it is FFF9C4FF (a light yellow) in the first row, F3EA8FFF in fade{1…4} and F3EA8F00 in fade{5…7} (same color but totally transparent when the line is not visible anymore)
												#       -> it is the same as the 11th color, but for the second line? Value would be irrelevant if there is only one line.
												#     - 13th was FF0000FF (red) until first row in symmetry island where it is 060010FF (almost black) -> color of the hexagons? 
												#       But it is not used in the next two sets (two line colors).
												#       But it is 000000FF (pure black) on the puzzle on the door to the laser, which has blue hexagons, so it cannot be the color of the hexagons.
												#       And it is 060010FF again for all the puzzles of the laser set.
												#       It's 00361AFF (almost black also, but slightly green) for the apple tree puzzles.
												#       It's pure black for the windmill door.
												#       -> Might be the color of the line in case of error. It matches for the apple trees and laser set (we see it before the puzzle shuts down).
												#     - 14th is B29926FF (lemon ginger, the color of the grid in discarded triangle puzzles).
												#       It's also the color of the flashing line when entering a code in the theater main control.
												#       Previous idea was: could be the color of the grid. Or the color of the line that fades off when you abandon the puzzle.
												#     - 15th is 00FF00FF (green), but for the laser activation puzzles it is FFB900FF, an orange that is very close to the background color of the puzzle.
												#       For theater_entrance* it is FFAB00FF, also an orange but lighter.
												#       -> from the marsh puzzles, it seems to be the color of the filled polyominoes, and 16th color is for the hollow ones.
												#          I guess for lasers its a copy/paste remnant.
												#          Actually, colors 15th to 19th included are the colors of the symbols used in the cells of the puzzle, as shown by the shapers_bridge_control
												#     - 16th is FF00FFFF (magenta)
												#     - 17th is 000000FF (black)
												#     - 18th is FFFFFFFF (white)
												#     - 19th is 0000FFFF (blue)
												# Note: there is only one puzzle with 5 different colors for symbols in the grid: the rotatory bridge in the marsh. All others have less than five.
												# (greenhouse puzzles can display more but they use dedicated textures, and internally the puzzles have at most 4 colors).
												# Puzzles use less than 16 symbols in grid cells, but there is one exception: the cave reprisal of mountain's color puzzles, which uses 31 rounded squares.
		read_array(f, 19, lambda src: read_array(src, 4, read_float32)),
		read_byte(f),							#  3: Boolean, but I don't know what for.
		read_array(f, 4, read_float32),			#  4: Seems to be some color. For the grid or background? 4th float is always 1.0 except for khatz_crazyhorse
		read_int(f),							#  5: Always 0, 1, 2, or 3 (but the only puzzle with value 3 is khatz_crazyhorse). Maybe flags for the solution checker?
												#     In darkid's trainer, it could be: int stateOffset = _solvedTargetOffset - 0x14; ?
		read_array(f, 4, read_float32),			#  6: 1st can be negative, others are in the range 0.0-1.0 and most often take the extreme values in this range. Coordinate in a normalized system?
	
		read_byte_array(f, 12),					#  7: Always all 0.
												#     In darkid's trainer, the start of this field could be _solvedTargetOffset ?
												#	  The field would include: int hasEverBeenSolvedOffset = _solvedTargetOffset + 0x04;

	#	Dependencies with other entities
		read_id(f),								#  8: If not None, id of a Power_Cable, Machine_Panel, Door, Force_Bridge, Laser, Double_Ramp, Gauge, Pylon, Light, Record_Player, or Pressure_Plate.
												#	  -> Probably the object whose state is changed by solving the puzzle.
												#        When it's a Machine_Panel, it's the id of the next panel in the Multipanel row, and the same than the node_id given by another field below.
												#     in darkid's trainer, this would be: int idToPowerOffset = _solvedTargetOffset + 0x20;
												#     unless it's field #28?
		read_byte(f),							#  9: Boolean. Seems to be set often and mainly for challenge puzzles, bird puzzles, and apple tree puzzles, but not only.
												#     It's never set for the first puzzle of a sequence, even if it's set for the other puzzles in the sequence.
												#     It's also mainly for puzzles with their own stand and a Power_Cable powering them, although erasers_and_shapers* is an exception.
												#     -> Maybe to say the puzzle should only be switched on when the previous one has been solved? -> No, because it's not set for erasers_and_groupers* that also have this behavior.
												#     -> So, actually I think it's a flag that is set when a puzzle should be shut down if a wrong solution is entered. The ones in the sawmill do that.
		read_id(f),								# 10: If not None, always the id of a Gauge, Machine_Panel, or Power_Cable entity.
		read_id(f),								# 11: If not None, always the id of a Multipanel entity. -> The Multipanel set the puzzle belongs to.
		read_id(f),								# 12: If not None, always the id of a Bridge entity. And always for a treehouse puzzle.
		read_id(f),								# 13: Id of the Landing_Signal controlled by the puzzle, for puzzles calling the boat (they have name "boat_summon_new").
		read_array(f,8,read_optional_string),	# 14: Some strings:
												#	  - 1st seems to be a mesh file without extension, but is only present when the puzzle has its own mesh, as multi-panel puzzles share the same mesh.
												#	  - 2nd is a shader effect applied to the screen content: values are: obj_panels_BG_LCD
												#	  - 3rd is the screen effect when the screen goes off.
												#	  - 4th is a screen animation or type? values are: scanline and dot-bigger.
												#	  - 6th is the effect of success, including playing a sound? 
												#	  - 7th is the name of a 'rattle', it is used for puzzles with different exits that control different things?
												#	  - 8th is the name of a reverb.
		read_id(f),								# 15: This id is only provided twice and is always equal to the id of the Machine_Panel itself ('spec_glass_panel' or 'hedge_maze1' as field #0).

		read_byte_array(f,12),					# 16: Always all 0

	#	Lighting model parameters?
		read_float32(f),						# 17: Always 8.0 except for letorre (18.0). -> maybe the time in seconds to fade the line in case of error?
		
		read_byte_array(f,12),					# 18: Always all 0.

		read_float32(f),						# 19: Always 1.0 except for letorre (90.0).
		
		read_float32(f),						# 20: Always 0.0.
		
		read_float32(f),						# 21: A value between 0.0 and 20.0. Only 5 puzzles have values above 1.0 :
												#	  khatz_overlay_pinholes (5.0), cyl_gateway_b (10.0), cyl_gateway and lotus_cyl_{dots,stones} (20.0)
		read_float32(f),						# 22: Specular reflexion power?
												#     Always 0.0 except for all spec ruins panels (except control panels that don't have specular halos), but also for:
												#     khatz_hperspective, shapers_bridge_control, hub_symmetry_and_stones{1…5}, shadow_landing_{0…7}, shadow_laser, shapers_bridge_control_sliding
												#	  and junction_force_field_new_sly, with small values (except for the later, these are all puzzles where you can have the sun in your back)
		read_float32(f),						# 23: Specular reflexion size?
												#     Always 0.0 except for spec ruins panels and shadow forest panels (with absurdly huge values for the later, which are extremely bright in the game)
												#     and junction_force_field_new_sly
		read_byte(f),							# 24: Boolean. Always 1 except for: khatz_giant_floor, shapers_and_groupers_hub1, letorre, shapers_floodgate_control, windmill_control,
												#     shapers_bridge_control_sliding, monastery_abc, spec_slide, spec_turn, spec_shadow_block, spec_light_picker, 
		read_byte(f),							# 25: Boolean. Always 1 except for the puzzles that do not emit light by themselves?:
												#     hub_triple, hub_duo, cyl_gateway_b, spec_*, sight_cookie_*, shadow*, khatz_occlusion_threes, khatz_giant_floor, giant_floor_lifter_control, 
												#     khatz_vperspective, two_starters_one_finisher, creaky_bunker, tricolor_new_{1…4}, end_laser_progress, khatz_crazyhorse, shapers_and_groupers_hub1, 
												#	  set_tricolor_intro, letorre, colored_lights_*, khatz_occlusion_*, monastery_abc, broken_laser_horizontal, junction_force_field_new_sly, clev_nolight
												#     But colorfilter_yellow_and_cyan and colorfilter_cyan are 1, as are lotus_cyl_stones and lotus_cyl_dots, but maybe there are two puzzles for the on/off states?
												#     Note: knowing if a puzzle emits light is important for the glow after effects.

		read_byte_array(f,9),					# 26: Always all 0

	#	Integration with other gameplay elements
		read_id(f),								# 27: Id of the previous Machine_Panel in the set, if any.
												#     But there can be multiple puzzles with the same previous one, possibly if two puzzles are actually the same under different lighting conditions?
		read_id(f),								# 28: Id of the next Machine_Panel in the set, if any
		read_float32(f),						# 29: Most often 0.0 but ranges from -1.3 to 2.0. 
												#     In the positive values, all groupers are 0.425 except groupers_lightswitch (0.7), reflect_rotation_asymmetric_maze3 is 0.8, and khatz_elevator{1,2} is 2.0.
		# tuple(x/0x100000000 for x in read_int_array(f,4)),
		# read_array(f,8,read_fixed_point),
		# read_array(f,8,read_float16),
		# read_array(f,4,read_float32),
		read_byte_array(f,16), # seems to be 4 4-byte values that are not floats. Maybe pointers or more probably RGBA colors. The last two often have only the most significant bits set.
		read_vector32(f),						# 31: Usually (1.0, 0.0, 0.0) (or very close) but a null vector for letorre, and (0.0, 0.0, 1.0) for treehouse horizontal puzzles:
												#     divide_field_{a…c}, gg_*, groupers* (except {1,_bridge_control,_eight_door,_second_panel,_lightswitch}), newgroupers_{four_b,maze1}, touch2_groupers_{a,b}
												#     and cylindrical puzzles: cyl_gateway*, khatz_cyl_*, lotus_cyl_*.
												#     -> Might be a normal to the puzzle, but I guess it might also be related to navigation in puzzle sequences, as the treehouse ones move forward instead of laterally.
		read_if(f, read_vector32),				# 32: Only given for cylindrical puzzles:
												#     (-0.5472, 0.6778, 0.1956) for lotus_cyl_*,
												#     (-0.6000, 0.6000, 0.1950) for cyl_gateway,
												#     (-0.6313, 0.5921, 0.2069) for cyl_gateway_b, 
												#     (-1.0765, 1.0765, 0.4944 … 0.5939) for khatz_cyl_*, 
		read_float32(f),						# 33: I don't know. Smaller puzzles seem to have a small value and big puzzles a bigger one, so maybe it's a size-related parameter.
		read_byte(f),							# 34: Boolean. Probably indicating procedurally generated puzzles or timed puzzles, as it is set only for:
												#     khatz_elevator{1,2}, and the challenge puzzles (lotus_onlyone{_tricolor}?_{0…2}, lotus_simple_maze{1,3}, lotus_stones_1, lotus_scramble_{0…3}, lotus_gates,
												#     lotus_gates_decoy_{a,b}, lotus_cyl_{stones,dots}, lotus_{minutes,tenths,eighths}_0)
		read_byte(f),							# 35: Boolean. Only set for pressure_plates{1…4}. If it's the ones from the Keep, it may indicate that segments can not make a line?
		
		read_byte_array(f,4),					# 36: Always all 0.

		read_float32(f),						# 37: Always close or equal to 1.0. Only greater than 1 for monastery_abc (1.0410) and snake_path (1.1)
		read_float32(f),						# 38: Always 1.0 except for one of the two shapers_bridge_control_sliding (1.25), shapers_bridge_control (1.5), and shapers_floodgate_control (1.3).
		read_float32(f),						# 39: Always 1.0 except for simple_maze3 (0.6), simple_maze2 (0.7), simple_maze1 (0.75) and letorre (1.5)
												#     -> maybe the radius of the rounded corners of the grid lines, as a proportion of the grid line width?
		read_byte(f),							# 40: Boolean. Set for puzzles that can be seen from multiple angles? Either because they are transparent:
												#     symmetry_translucent*, reflect_{hmirror1,touch{1…5, but not 6 or 7 which are in the caves},colored*}, fade{1…7}, spec_glass_panel, shapers_and_groupers_hub1,
												#     are pillar puzzles: lotus_cyl_*, khatz_cyl_*, cyl_gateway*, 
												#     are on the floor/horizontal: divide_field_a_extra, letorre, monastery_abc, 
												#     others: end_laser_progress, record_player_control.
		read_float32(f),						# 41: Always 1.0, except for end_elevator_* puzzles where it can be 0.5.
												#     -> because a puzzle on both sides of the elevator need to be completed to solve the puzzle, the contribution of one side is only 0.5?

		read_byte_array(f,4),					# 42: Always all 0.

		read_byte(f),							# 43: Boolean. Set only for:
												#     lotus_cyl_{dots,stones}, cyl_gateway, clev_nolight, tricolor_four_{a…c}, tricolor_new_{1…4}, set_tricolor_intro, end_laser_progress, spec_glass_panel.
		read_float32(f),						# 44: Usually -1.0, but sometime a positive value smaller than 1. Seems to concern puzzles that are traced simultaneously in multiple instances. An update rate?
												#     0.1 for shapers_floodgate_control;
												#     0.05 for water_level_*, spec_glass_panel*, sight_cookie{1,_rear,_hub}, monastery_abc, khatz_occlusion_{cross,orig,line,threes};
												#     0.01 for open_pressure_plate_door, khatz_crazyhorse, khatz_blockage_{dots,stones_new_a,stones_new_b}, counter_secret_door, and reflect_hmirror6;
												#     0.005 for laser;
												#     0.001 for force_bridge_{a,b1,b2}, :empty, end_elevator_door_{open,close}_left, and the_treehouse_door.
												#     -> No, it seems to concern puzzles that trigger an animation when solved. A delay in seconds for the animation to start? Or the speed of the animation?
		read_byte(f),							# 45: Boolean. Only set for letorre and khatz_giant_floor. Which are very big puzzles on the floor. And the only ones whose mesh are hidden until they are powered?
		read_byte(f),							# 46: Always 0.
		read_float32(f),						# 47: -1.0 or a small positive number (between .003 and .4, often a multiple of .003).
	)
	return result
