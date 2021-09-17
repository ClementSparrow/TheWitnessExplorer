from modules.entity_readers.helpers import *

def read_Inanimate(f):
	'''
	Inanimate (0x15 = 21) 01111110
	26677 entities
	Node structure:
	- node_flags can take a lot of different values.
	- node_string is very rarely provided and only to indicate a group of objects.
	  It can be: CementFactory, QuarryDelta, avoid_intersecting, caveRocks, end2_the_room_path_collision, treehouse_veg_burned, windmill_wheel_do_not_stream_out, :lake_extents, :lake_ground
	- node_group_id is always provided and can take a lot of values.
	- node_ids can point to a Boat, Bridge, Door, Record_Player, Inanimate, Laser, Machine_Panel, or Multipanel entity.
	- node_float is often provided and when it is, it is always an integer, and it is most often a multiple of 5.
	- node_ints is most often provided, but it is usually the default ([], [0]).

	Despite the name Inanimate, it seems to be a very specific object rather than anything that is not animated.
	More precisely, it seems to be vertical cylinders, especially the ones defining colision surfaces around objects.
	As such, it seems to be an in-editor only object used to generate mesh files (or geometries inside a given mesh).
	'''
	return (
		read_int(f),				#  0: Always 1.
		read_float32(f),			#  1: Between 0.0100 and 6.0. Most often 6.0. Seems inversely related to field 3. Could be the height of the object when it's a vertical cylinder.
		read_float32(f),			#  2: Between 0.0100 and 3.0. Most often 3.0. Seems inversely related to field 3. Could be the radius of the object when it's a vertical cylinder.
		read_int(f),				#  3: Usually 4, but 8 for a few obj_fol_tree_maple_* entities, and can also be 10, 12, 14, 16, 20, 30, 40.
									#     -> For the entities that generate a vertical cylinder, this seems to be the number of faces of the cylinder.
		read_float32(f),			#  4: 1.0 (most frequent) or 2.0. All the entities where it is 2.0 are loc_newEnd*.
		read_float32(f),			#  5: Always 360.0 except for obj_fol_tree_maple_* with "tree_color" in field 7, for which it is 280.0. -> maybe the angle of a "vertical cylinder" around it's axis?
		read_optional_string(f),	#  6: The name of the mesh file to use. Almost always provided.
									#     if not provided, a slab-like or vertical cylinder mesh will be generated as save_{entity_id}.mesh file.
		read_optional_string(f),	#  7: The name of a texture/color file to use. Almost never provided.
									#	  When provided, it will appear as the first parameter of the material in the generated mesh file.
		read_optional_string(f),	#  8: Only provided for #783 and #908, for which it is "zigzag_dark_wood" (not a texture file?). Also, these two Inanimate have no mesh file in field 6.
		read_byte(f),				#  9: Always 4. No. Can also be 0 or 1.
									#     For the white flowers, it is always set to 1 except for the one at the top of the mountain, for which it is set to 0.
		read_vector32(f),			# 10: An rgb color in the 0.0-1.0 range. But it seems unrelated to the colors of the object, so maybe it's an editor color?
									#	  It may appear as the 13th-15th parameters of the material in the generated mesh file.
									#	  The study of the white flowers actually suggests that it is a filter color applied when instantiating the mesh? 
		read_float32(f),			# 11: Between 0.0 and 100.0. Values above 25.0 are all lamp meshes. Actually, most values above 1.0 are for light-emitting entities. -> some light intensity?
									#     -> This field and the previous one seem to define a light color and intensity.
		read_byte_array(f,4),		# 12: Always all 0.
	)
