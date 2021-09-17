from modules.entity_readers.helpers import *

def read_Light(f):
	'''
	Light (0x1b = 27) 10000010
	37 entities: All lights in the game.
	Some of them can be switched on/off: the ones in the hub flowered container (#0-2-4 for green-blue-red), desert ruins -1 floor (#26-29-32) and -3 floor (#28) and view on the devs studio in secret ending (#22-23).
	Others are permanently on. They can match a physical lamp in the game, and some seem to be artificial?
	Node structure:
	- node_flags can be 00040000, 00040400, 00041000, 00048000, 00240000, 00440000, 00440400 (only for the start tunnel door), 00840000, 00841000.
	- node_string is only provided for the lights activated by a switch: spec_ruin, hub_container_{green,blue,red}, or :vr_light (secret ending). Also rgb_set_1 (magenta light in the greenhouse container) and some spec_ruin that are always on.
	- node_group_id is often provided.
	- node_ids can point to a Door entity, for lights attached to "doors". Only two: Door-219 (door end of the start tunnel) and Door-323 (mountain elevator leading to the deepest floor?).
	- node_float is never provided (-1.0).
	- node_ints is sometime provided (for nodes with flags 00840000, 00841000 and 00040400). When provided, it's usually ([], [0]), but there are two exceptions:
	  For the lights of hub_container_*, it's always ('Light-0, Light-2, Light-4, Door-255', (2, 4, 8)), which contains the lights hub_container_* and Door-255 (the ladder to enter the container).
	  -> The number 2,4,8 seem to be bitmasks for each entity in the previous list, with the least significant bit for the last element of the list (here, the Door). 
	     This lists the possible states of the entities, meaning that here, the lights are exclusive (cannot been on simultaneously), and can only be on if the Door is open (mask unset, which is strange).
	  For the lights in the -1 floor of the desert ruins, it's ([Light-32, Light-29], [0]) for Light-26 (central solution of the panel, near the floor puzzle),
	  ([Light-26, Light-32], [0]) for Light-29 (left when you enter the room, left on the panel), but ([Light-26, Light-29], [2,0]) for Light-32 (right solution of the panel, on your right when you solve it).
	  -> Maybe it's because the lights are on simultaneously for less than 1s when you switch them?
	- node_final_floats is can be (0.2339, -0.1725, -0.0031, -0.0009) or (0.1906, -0.0795, -0.0, 0.0024) (for the Lights with flags 00840000 or 00841000)
	  or (0.0378, 0.0, 0.0, 0.0) for #33 (the door at the end of the start tunnel).
	List of lights:
	-  0: hub_container_green
	-  1: ceiling lamp in the tunnels after the bridge in the theater, just on the right after the bridge, on the way toward the windmill and desert ruins.
	-  2: hub_container_blue
	-  3: In the windmill, just under the entrance, above the wooden staircase.
	-  4: hub_container_red
	-  5: In the windmill, in the corner of the dark place before reaching the aqueduct.
	-  6: Mountain interior, red room at -3 floor, yellowish hanging lamp above the statue of the puzzle creator.
	-  7: Mountain interior, floor 0 (top exterior of the structure), blue light before the stairs leading to the -1 floor.
	-  8: Burke vault, simulating the light coming in from the window.
	-  9: Mountain interior, blue light before the stairs at the exit of the -1 floor.
	- 10: Burke vault, white lamp above the entrance door, inside.
	- 11: Feynman vault, dark yellowish lamp above the safe.
	- 12: Cement factory, white ceiling lamp in the shortcut to quarry top.
	- 13: Hub, soundproof room, dark yellowish ceiling lamp.
	- 14: Greenhouse, opening container, magenta light.
	- 15: Mountain interior, in the suspended glass structure of the -1 floor, in front of the statue: blueish light from the tv screen showing the entry yard force field.
	- 16: Cavern, wooden room just after the entrance from the mountain interior, orange light.
	- 17: Cavern, wooden staircases between the four pillars and the challenge entrance, where there is the "authenticity" audio log: orange ceiling lamp.
	- 18: Aqueduct, entry of the aqueduct by the upper catwalk, above the theater: yellow ceiling lamp.
	- 19: Desert ruins, -3 floor (room with moving water), blue central ceiling lamp.
	- 20: Mountain interior, on the door to enter the -1 floor, blue wall-mounted lamp.
	- 21: Mountain interior, ceiling light in the elevator between the -2 and -3 floors (making blue light but the lamp is white).
	- 22: vr_light (near the puzzle that controls the light)
	- 23: vr_light (farther from the puzzle that controls the light)
	- 24: Challenge: yellow light hanging above the record player.
	- 25: Desert ruins, laser room, ceiling lamp.
	- 26: Desert ruins, -1 floor, near the final puzzle on the ground (central solution of the light control panel).
	- 27: Hub, inside the mine building, yellow lamp.
	- 28: Desert ruins, -3 floor (room with moving water), yellow light above the floating puzzle panel.
	- 29: Desert ruins, -1 floor, left solution of the light control panel, on your left when you enter the room.
	- 30: Aqueduct, exit by the hub's mine building, yellow ceiling lamp just before entering the building's basement.
	- 31: Desert ruins, -2 floor, ceiling lamp.
	- 32: Desert ruins, -1 floor, right solution of the light control panel, on your right when you solve it.
	- 33: Above the door at the end of the start tunnel.
	- 34: Aqueduct, room with the code to reset the entry yard force field, magenta ceiling lamp.
	- 35: Greenhouse, main room, wall-mounted lamp above the cyan glass door.
	- 36: Challenge vault, above the safe.
	'''
	return (
		read_vector32(f),				#  0: The RGB color of the light (diffuse color). Components can be greater than 1.0 (the red one for #25 and #34).
		read_array(f, 5, read_float32),	#  1: Take values between (0.4, 0.25, 0.0, 0.0, 2.5) and (45.0, 3.0, 1.0, 1.0, 45.0)
										#      - 1st is between 0.4 and 45.0. I have no idea what it is. Strangely, it's 45.0 for #26-32 but only 20.0 for #29. Which seems slightly less powerful. -> intensity?
										#      - 2nd is usually 1.0, except for #14 (magenta light in greenhouse container), where it's 0.25, and the three RGB lamps in the hub container, for which it's 3.0.
										#      - 3rd is either 0.0 or 1.0, and it's 0.0 for the red and green lights in the hub container (but not the blue one), the two of the view on devs' office,
										#        the three in desert ruins -1 floor, and the one above the floating panel in -3 floor.
										#        -> All lights with 0.0 are off initially, all others are on. -> Initial state?
										#      - 4th is always the same as 3rd.
										#      - 5th is between 2.5 and 45.0, don't know what it is. Default seems to be 10.0.
		read_byte(f),					#  2: Boolean. Only set for the desert ruin lamps, #12 (ceiling lamp in the shortcut between the cement factory and quarry top) and #36 (entrance of the challenge area?),
										#     which all have obj_lightProp_AtopRT in next field and flags 00840000 or 00841000.
		read_optional_string(f),		#  3: Name of a mesh file for this lamp. Can be obj_lightProp_AtopRT (spec_ruin), obj_primitives_lightCube (start tunnel), or lamp-wallTiny.
		read_short(f),					#  4: Always 0. Might also be two booleans or two optional strings.
		read_float32(f),				#  5: Always 1.0, except for the 3 lights of the desert ruins' -1 floor, for which it is 0.01.
		read_float32(f),				#  6: Usually 1.0, but also:
										#     - 4.0 for #31 (ceiling light in desert ruins -2 floor).
										#     - 10.0 for #25-34 (lights in the aqueduct tunnel near the desert ruins) and #26-29-32 (desert ruins -1 floor).
										#     - 15.0 for #10 (white lamp above the entrance in Burke's vault) and #8 (seems to be a light to fake the sunlight entering Burke's vault through the window).
										#     - 50.0 for #33 (above the door at the end of the start tunnel)
										#     - 60.0 for #19-20 (the two ceiling lamps in the desert ruins -3 floor with water).
										#     -> I don't know. Light intensity?
		read_optional_string(f),		#  7: Name of a light group or script to control these lights. Only provided for:
										#    - the three lights in the -1 floor of the desert ruins (#26-29-32): spec_ruin,
										#    - the ones in the devs studio (#22-23): vr_light,
										#    - one in the office furniture pile in the mountain (#15) : end1_tv.
										#      But I do not see anything scriptable in these lamps... Or is it for the light emitted by the tv screen? See field 13. -> probably light blinking script?
		read_array(f, 4, read_float32),	#  8: The first 3 are in the range 0.0-1.0, but are not the color of the light. 4th is between 2.0 and 45.0, always taking integer vaues. 
		read_id(f),						#  9: A Lake entity. Only provided 5 times:
										#     - Lake-11 for #31 (ceiling light in desert ruins -2 floor),
										#     - Lake-13 for #25 (desert ruins laser room) and #34 (room with the code to reset the entry yard force field),
										#     - Lake-20 (moving_water_level) for #28 (above the floating puzzle panel) and #19 (central ceiling light in desert ruins -3 floor).
		read_list(f, read_id),			# 10: A list of Machine_Panel or Marker entities. Only non-empty for:
										#     - #34 and #25 both have Machine_Panels 155 (spec_basement8) and 194 (spec_glass_panel), which are the two puzzles opening one laser's lock.
										#       #25 also has Marker-455-596-900. See previous field.
										#     - lights in desert ruins -1 floor:
										#        - #26 (central light) has Machine_Panel-477 (spec_extra_light2, lit by this lamp) and Marker-184-898.
										#        - #32 (right light)   has Machine_Panel-449 (spec_extra_light,  lit by this lamp) and Marker-39-988.
										#        - #29 (left light)    has Machine_Panel-477-449 (see above) and Marker-261.
										#     - #19 (central ceiling light in desert ruins -3 floor) has Machine_Panel-537-276-86-226-145 (spec_basement{5,10,6,9_flood_final} = all puzzles lit by this light)
										#     - #28 (above the floating puzzle panel) has Machine_Panel-334-145 (spec_basement_{growspot,flood_final} = all puzzles lit by this light).
										#     - #31 (ceiling light in desert ruins -2 floor) has Machine_Panel-566-486-257-240-425 (spec_basement{2,1,3,4,7}, all puzzles indirectly lit by this light)
										#    -> To the exception of the curved puzzles and the puzzle on the ground in -1 floor, this field seem to give the Machine_Panels for which a specular reflexion
										#       is visible for the light coming from this lamp. For the other panels, the markers could link to the panels?
		read_byte(f),					# 11: Always 0.
		read_array(f, 4, read_float32),	# 12: All in the range 0.0-1.0. Seems to be an RGBA color, or simply an RGB and some other coefficient, as the alpha is always set to 0.25.
										#     The RGB color is always white (1.0, 1.0, 1.0), except for:
										#     - #15 where it is #a844ff (magenta),
										#     - #19 where it is #90fefc (light blue),
										#     - #28, where it is #f9fec8 (light yellow).
										#     -> For #15, It seems to match the specular color of the light, which can be seen by passing in front of the statue, and compare the gray of the statue in our shadow
										#        with the blueish magenta it has in the lit part. But seen from the side, the statue is gray in the shadow and blueish in the light, so this is specular reflection.
										#     -> Specular reflexion color?
		read_vector32(f),				# 13: Always (1.0, 1.0, 1.0) except for #15 (statue in furniture pile), for which it is (0.3, 0.4, 0.8) = #4c66cc = blue-gray.
										#     -> matches the diffuse color of the lamp.
		read_byte(f),					# 14: Boolean: always set except for #15 (see next field) and #6 (lamp above the statue of the puzzle maker in the mountain end).
		read_id(f),						# 15: Only provided 3 times:
										#     - Inanimate-17734 (tv screen in front of the statue in the glass structure of the mountain, showing the entry yard force field) for #15,
										#     - Door-39 (door for the shortcut between the cement factory and the top of the quarry) for #12 (ceiling lamp in this shortcut),
										#     - Door-229 (water level) for #28 (above the floating panel in desert ruins -3 floor).
		read_id(f),						# 16: Only provided once: Light-23 for #22, both lights being those of the view on the devs' office.
		read_optional_string(f),		# 17: Name of a sound loop to play while the lamp is open.
										#     Only provided for the -1 floor of the desert ruins (spec_ruin_light_loop), and for the view on devs' office (end2_theroom_light_buzz_loop).
		read_byte_array(f, 8),			# 18: Always all 0.
	)
