from modules.entity_readers.helpers import *

def read_Slab(f):
	'''
	Slab (0x2d = 45) 01111100
	422 entities: I guess slabs are just rectangular boxes that do not need a mesh and are used to hold some undisplayed entities?
	node structure:
	- node_flags can be 00000200, 00000202, 00000400, 00008000, 00040000, 00048000, 00048002, 00048080, 00048082, 000480a0, 00048420, 00049000, 00049080, 00208000, 00248000, 00840000, 00840080, 00841080, 00a40000, 20048000, 20048080, 20048400
	- node_string is set only for node #396 to "Lady Marker 3dsmax Ref".
	- node_group_id can be provided or not.
	- node_ids is often provided and can point to a Door entity or to Slab-358, Lake-20, Machine_Panel-234 (laser_platform), Machine_Panel-579 (symmetry_translucent3) or Marker-985 entities.
	- node_float is never provided (-1.0).
	- node_ints: When node_flags 00008000 is set, node_ints are rarely provided and are then always ([], [0]).
	             When node_flags 00008000 is unset, node_ints are always provided and are usually ([], [0]) but can sometime contain lighting dependencies.
	- node_final_floats: radius is always provided, but the center position is always (0,0,0).

	Note that this is an editor-only object, used to generate a save_{entity_id}.mesh file.
	'''
	return (
		read_vector32(f),				# 0: Dimensions of the slab (x,y,z)? Always strictly positive.
										#    Could also be a position in the bounding sphere, as the lenth of this vector always equals the double of the first node_final_floats.
										#    Or it is the dimensions of the slab and it defines the bounding sphere, centered at the center of the slab.
		read_optional_string(f),		# 1: A color/texture/material name. Can be brown{1…5}, white, light_gray, gray, darkish_gray, dark_gray, black, blue, cyan, bright_red, gold4, slate, tree_color,
										#    clev_{red,green}, shar_goldleaf, shar_Metal_Painted_{Blue,Yellow}, shar_StackStone_dark, shar_Stone_Wet, shar_StoneWhite, shar_stone_cobblestone-edge,
										#    shar_concrete_bunkerwall-A, shar_corten-light-flatStyle, shar_cortenV2-{dark,light,rail}, shar_wood-civ2-rough-nobreak-dark, shar_Metal_BlackSteel{_spec,-dark},
										#    shar_metal_galvanized_01, loc_swamp_flatCement, code_{burke,feynman,sagan,psalm46,rupert,gangaji}, puzzle_sketch{1…5}, puzzle_disclosure_sly.
		read_byte(f),					# 2: Always 0.
		read_optional_string(f),		# 3: Can be glowing, grass_blocker, shar_Metal_Painted_Yellow (probably a mistake), shadow_only, vr_window, window_lights, window_lights_brighter.
										#	 -> In the generated mesh, it seems to be the name of the unique material (or 'default' if not provided)
		read_byte(f),					# 4: Boolean. Might indicate (if set) that the next two field contains something (otherwise it is usually four 0.0 but not always).
		read_array(f, 4, read_float32),	# 5: In [0.0-1.0]. An RGBA color?
		read_float32(f),				# 6: In [0.0-50.0], although most values are below 1.0. This field and field 5 are usually either both null or both non-null.
		read_float32(f),				# 7: Always 1.0.
	)
