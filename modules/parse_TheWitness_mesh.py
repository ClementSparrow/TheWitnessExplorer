# -*- coding: utf-8 -*-

# Exporters
# =========

class ExporterBase(object):

	def export_global_infos(self, header, nb_LODs, bounding_box, centroid, unknown_float_vector): pass
	def export_materials(self, materials, base_filename, texture_dir, texture_ext): pass
	def export_mesh(self, filename, variant, component, LOD, base_filename, indexes, vertexes_and_additional_data, field_numbers, material_index, texture_dir, texture_ext, centroid): pass
	def set_bounding_box(self, min_coordinates, max_coordinates): pass
	def end_export(self, base_filename): pass

	def export_patched_mesh(self, current_mesh_index, nb_faces, nb_patches, patches, nb_kdtrees): pass
	def export_kdtree(self, current_mesh_index, kdtree_index, kdtree): pass
	def export_partition(self, partition_group_id, partition_id, facets): pass

	def export_joint(self, joint_name, translation_vector, rotation_info): pass # rotation_info = None or (rotation_axis, rotation_angle, invariant_point)


# Mesh parsing
# ============

if __name__ == '__main__':
	from readers import *
else:
	from modules.readers import *


def parse_header(src, debug, newformat):
	'''
	Reads the header bytes from a mesh file for The Witness and returns the information found in it as a tuple:
	- header flags (see bellow)
	- number of level of details (LOD) for the geometries in the mesh (usually two, sometime 1)
	- bounding box of the mesh (as a tuple of two 3D vectors: minimal coordinates and maximal coordinates). In case of an animated object, this bounding box contains the object whatever its animation state.
	- centroid of the mesh: 3D vector for the position of a reference point inside the mesh (defined by the designer). Seems to correspond to the bounding sphere center position provided in the entity node data.
	- 3 unknown floats (see below).
	- 2 additional vectors in newformat, that seem to be always ((1.0, 1.0, 1.0), (0.0, 0.0, 0.0)) except for grass_* mesh files where it is ((4.0, 4.0, 4.0), (-2.0, -2.0, -2.0)).

	The header flags are:
	- 1 unidentified int32 that could be an identifier or a bit mask or a CRC, or even possibly a float32
	- 1 int16 that is alway 0
	- 1 int16 that could be a bit mask or an identifier (author of the mesh?). Observed values are:
		- 9, most of the time.
		- A (for "camera_fly")
		- B (for "carl")
		- 4 or 5 for everything under "grass/*"
		- 0 for a bunch of "save*" files in the range 58000-58497 that have only a set of vertexes/faces/"colors" and eventually an uv-mapping for some meshes but nothing else,
		  and matches the grounds and/or vegetation of some part of the island (maybe indicate walkable areas or give the sound for the footsteps, or are temporaries used for shadowcasting?),
		  many of which are empty (minimal header with no data inside).
		  actually Blow mentioned that this range of entity IDs is attributed to automatically-generated 'clusters' (see http://the-witness.net/news/2011/12/engine-tech-concurrent-world-editing/).
		- 8 (for vs/reflectedfish_stump, vs/logicalflower_metal, vs/logicalflower_yellow, vs/elevatorshafttest_cl1 & 3 but not 2, vs/cloudtree, vs/tempcliff_automn_coll, vs/tempcliff_keep_coll, vs/statues/perspectivestatue_small_statue, vs/statues/keepcourt_test3_{bishop_altar,collecting,kingThrone,poor,queen,queenchair}, vs/shadowgarden_shadowtrees_{laser2,t6,w1new,w2,w4}, vs/mona_{enpuzzlepath2_curtain,newstupa_stupa,newstupa_shadowside_shape,newstupa_shadowside_extrafol,newstupa_shutters_* but A2_2},vs/laketest_{fountain_off,lakeblocker,lantern*,limestonecliff2_coll,limestonepiece,lotus*,main,refplane}, vs/fractalwall_testscene_{corten,cortenPuzzle,drawingtable},vs/factory_nichetest_{0,1,2,3},vs/end1_worktable_cave2_{solo,tree},vs/end1_worktable_cave_wm1,ter_rocks_{endcap*,set*},ter_rocks_hardsecret_{setA,boulderD},ter_rockpillars_{soloD,soloFragA},etc...)
		-> bit 0 is used to signal that the asset has levels of details? Its always set to 0 when there is only 1 LOD... -> No. The following meshes have value 8 but two LODs: vs/statues/perspectivestatue_small_statue, vs/mona_newstupa_stupa, vs_laketest_limestonepiece, vs_laketest_lantern*, ter_rocks_set{A-H}, ter_rockpillars_grad{B1,C3}, ter_rockpillars_{A1,A3,B*,C*,cave_{A,B,C}*}, ter_river_fallsrocksC...
		-> however, when there is only one LOD, this bit is always set to 0. So maybe it's an information about the extra LODs? Like, the bit is set if the extra-LODs have been generated automatically?

	The three unknown floats:
	- first one could be related to the radius of the bounding sphere centered on the centroid, as its value seem to be always positive and proportional to the bounding box general dimensions -> in newformat, it seems to be sometimes negative? and to sometimes match the bounding sphere radius defined in the corresponding entity.
	- the two others are actually integers encoded as float32 and could also be bitsets when converted into integers, and are most often multiples of 4 but not always.
	  Note that when two meshes exist for the two states (on/off) of a same object, like in the lake, the mesh file for the "on" state often has these integers as 0 and the mesh file for the "off" state as 20.
	'''
	header = (read_int(src), read_short(src), read_short(src))
	assert(header[1] == 0) # verified to be True.
	nb_LODs = read_int(src)
	bounding_box = (read_vector32(src), read_vector32(src))
	centroid = read_vector32(src)
	unknown_floats = (read_float32(src), read_float32(src), read_float32(src))
	# assert(all( (math.fabs(f-int(f))<0.000001) for f in unknown_floats[1:])) # was verified to be always True with oldformat.
	if debug:
		print('=== HEADER: ===')
		# print('{} {:3} {:3}'.format(*header))
		print('{:>8X} {:3} {:3}'.format(*header))
		print('this asset has {} LODs.'.format(nb_LODs))
		print('bounding box:', bounding_box[1], '->', bounding_box[0])
		print('centroid:', centroid)
		print('unknown floats:', unknown_floats)
	if newformat:
		new_unknown_vecs = (read_vector32(src), read_vector32(src))
		if debug: print('new unknown floats:', new_unknown_vecs) # Not in the windows data that were given to me, but present in the macos data from EGS
	return (header, nb_LODs, bounding_box, centroid, unknown_floats)



def parse_materials(src, debug):
	'''
	Parse the materials section of a The Witness mesh file. Returns a list of all materials found. Each material is a tuple containing:
	- the name of the material (probably the shader's name, actually).
	- 64 flags grouped as 8 bytes, describing the material (see bellow).
	- one unidentified 32-bit integer. It seems to be an identifier or number:
		- for many mesh files, all values from 0 to some small integer are used in the materials of the mesh, but two materials can have the same value.
		- for meshes related to the hedge mazes, value can be -8, otherwise it's always positive.
		- the value 4 appears frequently too.
	- a list of 32 values that can each be either a float or a texture resource name.
	  Usually, the resource names appear at the begining of the list only and there can be up to (at least) 9 of them.
	  First string is always provided (?) and is a texture name. It is usually (but not allways) followed by a normal map texture.
	  The 9 texture seems to (always?) be three groups in which each group is made of a texture, normal map and blend map.

	Material flags are not well understood yet. Here are some observations:
		- Most bytes usually have the value 0, except for bytes 0, 4, and 5.
		- Byte 0 can take values from 0x00 to 0x28. Following information is for old format:
			- 0x01 is set when there is a color texture, a normal texture and a blend texture ; but unset when there is only a color texture and a normal texture. -> false, it can be set without blend texture (until now, only seen for textures with alpha transparency).
			- 0x02 has only materials corresponding to leaves, pines, flowers and other herbs, often tagged as TWO_SIDED.
			       First texture is always a texture with reversed alpha (either because it has a vignette or because it's one of the exceptions).
			- 0x03 has only 'save*' meshes with byte4=6 and byte5=byte6=0 and the default (empty-string named) material LAMBERT1_FLOATS (see bellow)
			  Actually it can also have byte5=1.
			- 0x07 always have four textures: a diffuse, a normal, a blend and a second diffuse.
			- 0x08 has only 'save-58???' meshes with byte4=6 and byte5=byte6=0 and the default (empty-string named) material: UNNAMMED_LAMBERT1_FLOATS_VARIANT. Note that the values are different than LAMBERT1_FLOATS used for 0x03 only for the 17th and 19th values.
			- 0x0A only use textures of water.
			- 0x0B has only 'save-58???' meshes with byte4=6 and byte5=0 and byte6=0 or 1 and the same material than 0x08. (Note that 0x0B = 0x03+0x08)
			- 0x0C has only materials related to glass.
			- 0x0D has only 'save*' meshes with byte4=6 and byte5=byte6=0 and the default (empty-string named) material LAMBERT1_FLOATS (see bellow)
			  Note that this is the same material than 0x03.
			- 0x0E has only materials related to (opaque) panels.
			- 0x0F has only materials named with 'shadowOnly' or similar and a few occluders (probably for lamps and sun).
			- 0x10 seem to only use textures with alpha and always have masks 0x04 set for bytes 4 and 5 (and possibly other bits, too).
			- 0x11 is only used for meshes of the hedges in the Keep, with byte4=7, byte5=0x80, and byte6=0, and material name Hedge_Blockers.
			- 0x1D has only materials named 'collision', 'coll', 'walkable', or similar. It appears a lot in cylinders around tree trunks, so it's probably used only for collision detection.
			- …
			- 0x27 is used for end2_eyelidtest_tunnel.mesh, which has a texture and a normal map but no UV mapping... (probably uses screen-space coordinates to access the texture)
			- …
		- Byte 1, 2 and 3 are always 0. Therefore, Bytes 0-3 form an int32 with values between 0 and 40 included.
		- Byte 4 has often the value 6.
			- (oldformat) 0x04 seems to be set when the material is emissive (at least when byte 0 is 0x00), but only if 0x02 is unset.
			  (newformat) recordPlayerPlatter is a counterexample for the oldformat rule. In this file, when there is no normal texture as second parameter this byte is 0x80, and 0x84 otherwise.
			              recordPlayerBase similarly sets the 0x04 bit when there is a normal texture provided as second parameter.
			              but 'pylon non main' has a normal map parameter and bit 0x04 unset.
			- the glass factory vases use cyclic textures and have this byte set to 7.
			- (newformat) lotus_barrier.mesh has a material with value 70 for this byte
		- Byte 5:
			- 0x01 is often unset in a material of LOD0 but set in the material for the same mesh at LOD1.
			- it seems that 0x08 is set when a tangent is specified in the data but should be ignored (tangents are always null in that case)
		- Byte 6 …
		- Byte 7 is always null.
		- In some materials, the different non-zero bytes take successive values (if we ignore the most significant bit) and may indicate shader parameter indexes?
	'''
	nb_materials = read_int(src)
	if debug:
		print(nb_materials, 'material(s)')

	materials = []
	for material_index in range(nb_materials):
		material_name = read_string(src)
		material_flags = read_byte_array(src, 8)
		unknown_id = read_int(src)
		# assert( 0 <= unknown_id < nb_materials )
		material_mapfilenames_or_values = read_array(src, 32, read_string_or_float)
		m = (material_name, material_flags, material_mapfilenames_or_values)
		materials.append(m)
		if debug:
			# print('material {:2}'.format(material_index), '-', ('{:02X} '*len(material_flags)).format(*material_flags), '- {:2}'.format(unknown_id), material_name, material_mapfilenames_or_values)
			print('material ' + str(material_index) +':', material_name)
			print('   ({:3} {:3} {:3} {:3}) ({:3} {:3} {:3} {:3})'.format(*material_flags), unknown_id)
			print('   ', material_mapfilenames_or_values)
	return materials




def parse_mesh(src, mesh_index, nb_LODs, debug, newformat):

#	Mesh header
	material_index = read_int(src)
	geometry_flags = read_int(src)
	(vstride, nb_vertexes, nb_indexes) = read_int_array(src, 3)
	nb_instances = read_int(src) if not newformat else 1
	level_of_detail = read_int(src) # it seems to be the level of detail. Or maybe not. Usually, it is 0 or 1, but some save files in the range 252240-252308 have all values from 0 to 6...
	if debug:
		# print('geometry', mesh_index, 'has flags 0x{:0>8X},'.format(geometry_flags), nb_vertexes, 'vertexes,', nb_indexes//3, 'faces, and uses material', material_index, 'for LOD', level_of_detail)
		# print()
		print('Geometry', mesh_index)
		print('    material_index:', material_index)
		print('    flags: 0x'+'{:0>8X}'.format(geometry_flags))#, struct.unpack('<4B', struct.pack('<I', geometry_flags)))
		print('   ', vstride, 'vstride', nb_vertexes, 'vertexes', nb_indexes, 'indexes ('+str(nb_indexes//3)+' facets)')
		if not newformat: print('   ', nb_instances, 'instances of the same geometry')
		print('    LOD: {}/{}'.format(level_of_detail+1, nb_LODs)) # note: corresponding meshes at different LOD does not necessarilly appear in the same order between LOD0 and LOD1, but all LODn meshes appear after all LOD(n-1) meshes. LOD is usually 0-1 but some "save" meshes have the full range 0-6. LOD>0 seem to have been automatically computed from LOD0.
	# assert(level_of_detail < nb_LODs) # verified to be always True!
	
#	Definition of facets (3 vertex indexes by facet)
	size_list_indexes = read_int(src)
	(fstride, facet_reader) = (2, read_short_array) if nb_vertexes < 0x10000 else (4, read_int_array)
	# assert(size_list_indexes == (nb_instances*nb_indexes*fstride)) # verified to be always True!
	indexes = tuple( facet_reader(src, 3) for counter in range(size_list_indexes//fstride//3))#nb_indexes//3) )
	# if debug:
	# 	print 'facets:', indexes
	
#	Vertexes and associated data
	size_list_vertexes = read_int(src)
	# assert(size_list_vertexes == (nb_instances*nb_vertexes*vstride))# verified to be always True!

	global vstride_remaining_length
	vstride_remaining_length = vstride
	vstride_parsing_info = []
	field_numbers = dict()

	def make_parsing_info(flags, field_name, reader_dict):
		flag = sum((1<<i) if (geometry_flags & bitmask) != 0 else 0 for i, bitmask in enumerate(flags))
		# print('-'.join('{:0>8X}'.format(f) for f in flags), flag, reader_dict)
		new_info = reader_dict.get(flag, None)
		if new_info is None: return
		field_numbers[field_name] = len(vstride_parsing_info)
		vstride_parsing_info.append( new_info )
		global vstride_remaining_length
		vstride_remaining_length -= new_info[-1]

	# Vertex coordinates:
	# sure about 0x00000004 but not about 0x00000002
	# -> it seems that 0x00000004 is "4 float16, the first 3 being coordinates and the last being 1.0" but 0x00000002 is "3 float 16 for coordinates plus 1 short for facet instantiation id."
	# -> grass meshes use the 0x00000002 flag a lot and it seems their vertex coordinates are banana.
	make_parsing_info( (0x00000002, 0x00000004), 'vertex_positions', {
		0 : (read_vector32, tuple(), 12),
		1 : (read_vector_fixed_point2 if newformat else read_vector16, tuple(),  6),
		2 : (read_with_useless_extra, (read_vector16, read_float16, 0.0), 8), # with newformat = false, it can be 1.0 insead of 0.0?
	})
	
	# Instance ID:
	make_parsing_info( (0x00000002, ), 'instance_ids', { 1: (read_short, tuple(), 2) })

	# UV texture coordinates:
	# 0x00000000 = no UV coordinate, 0x00000010 = 2xf32, 0x00000050 = 2xf16
	make_parsing_info( (0x00000010, 0x00000020, 0x00000040), 'texture_coordinates', {
		1: (read_array, (2, read_float32    ), 8), 
		3: (read_array, (2, read_fixed_point), 4),
		5: (read_array, (2, read_float16    ), 4),
	})

	# Secondary UV coordinates (for normal maps?)
	# 0x00000000 = no such coordinate, 0x00000300 = 2 2-byte fixed-point signed number. Probably 0x00000100 = 2xf32, but not tested.
	make_parsing_info((0x00000100, 0x00000200), 'additional_texture_coordinates', {3:(read_array, (2,read_fixed_point), 4)} )
	
	# Vertex normal
	# 0x00000000 = no normal, 0x00001000 = 3xf32, 0x00005000 = 4 2-byte fixed-point signed number (last one is 0.0). 
	make_parsing_info((0x00001000, 0x00002000, 0x00004000), 'normals', {
		1: (read_vector32, tuple(), 12),
		# 3: (read_array, (2, read_fixed_point), 4), #
		3: (read_with_useless_extra, (read_vector_fixed_point8, read_byte, 0), 4),
		5: (read_with_useless_extra, (read_vector_fixed_point, read_fixed_point, 0.0), 8),
	})
	
	# Vertex tangent (in direction of increasing U)
	# 0x00000000 = no tangent, 0x00050000 = 4 2-byte fixed-point signed number (last one is 1.0). Probably 0x00010000 = 3xf32, but not tested.
	# -> Actually, according to loc_swamp_grass_puzzle.mesh (0x00133310), this is clearly not an unitary vector. It looks more like texture coordinates.
	make_parsing_info((0x00010000, 0x00020000, 0x00040000), 'tangents', {
		3: (read_array, (2, read_fixed_point), 4),
		5: (read_array, (4, read_fixed_point), 8),
	})
	
	# Color (RGBA)
	# 0x00000000 = no color data, 0x00100000 = 4 bytes, one by component.
	# -> In the new version of the parser at least, it does not seem to be colors: the sum of component is always 255, as the interpolation lists in the next section of the file (see loc_swamp_grass_puzzle).
	make_parsing_info((0x00100000,), 'vertex_colors', {1: (read_byte_array, (4,), 4) })

	# Animation
	# 0x00000000 = not animated, 0x03800000 = 2xi32 (the first one identifies a transformation group, second one could be a mask?)
	make_parsing_info((0x00800000, 0x01000000, 0x02000000), 'animation_group', { 7: (read_int_array, (2,), 8), })
	
	# Check that we have everything:
	# assert( (geometry_flags&0xFC6AACA9)==0 )# verified to be always True!
	assert(vstride_remaining_length == 0)# verified to be always True!
	# print(vstride_parsing_info)

	vertexes_and_additional_data = tuple( tuple(structure_reader(src, *parsing_info) for (structure_reader, parsing_info, _) in vstride_parsing_info) for counter in range(nb_vertexes*nb_instances) )
	# if debug:
	# 	formats = {
	# 		'vertex_positions': 'pos=({:8f}, {:8f}, {:8f})',
	# 		'instance_ids': 'instance={:8n}',
	# 		'texture_coordinates': 'UV=({:8f}, {:8f})',
	# 		'additional_texture_coordinates': 'ST=({:8f}, {:8f})',
	# 		# 'normals': 'n=({:8f}, {:8f}, {:8f})',
	# 		# 'tangents': 't=({:8f}, {:8f}, {:8f})',
	# 		'normals': 'n=({:8f}, {:8f})',
	# 		'tangents': 't=({:8f}, {:8f})',
	# 		'vertex_colors': 'rgba=({:3n}, {:3n}, {:3n}, {:3n})',
	# 		'animation_group': 'group={:8n}',
	# 	}
	# 	format_s = ' '.join(formats[f] for f in ('vertex_positions', 'instance_ids', 'texture_coordinates', 'additional_texture_coordinates', 'normals', 'tangents', 'vertex_colors', 'animation_group') if f in field_numbers)
	# 	for va in vertexes_and_additional_data:
	# 		print(format_s.format(*(x for f in va for x in f)))
	# 	# print 'vertex additional data length is', vertex_additional_info_length, 'bytes'

	vertexes = tuple( v[0] for v in vertexes_and_additional_data )
	# additional_data = tuple( additional_datum for (coordinates, additional_datum) in vertexes_and_additional_data )
	# if debug:
	# 	for i,v in enumerate(vertexes):
	# 		print('          ', '{:6}'.format(i), ' '.join('{:3}'.format(x) for x in v))

	computed_bounding_box = ( tuple(min(v[i] for v in vertexes) for i in (0,1,2)), tuple( max(v[i] for v in vertexes) for i in (0,1,2) ) )
	center_of_computed_bounding_box = tuple( (computed_bounding_box[0][i]+computed_bounding_box[1][i])/2 for i in (0,1,2) )
	if debug: print('    computed bounding box:', computed_bounding_box, center_of_computed_bounding_box)

#	Other data
	mesh_centroid = read_vector32(src)
	if debug:
		print('    bounding box is centered on:', mesh_centroid)
	assert( all(math.fabs(center_of_computed_bounding_box[i] - mesh_centroid[i]) < 0.0000001) for i in (0,1,2)) # this has been checked, assertion always True.
	# assert( all( (math.sqrt(sum((c2-c1)*(c2-c1) for (c1,c2) in zip(v,centroid)))<unknown_floats[0]) for v in vertexes) ) # definitely False
	# assert( math.fabs(math.sqrt(sum((c2-c1)**2 for (c1,c2) in zip(*bounding_box)))/2 - unknown_floats[0]) < 0.0001 ) # False
	# print( max( (math.sqrt(sum((c2-c1)*(c2-c1) for (c1,c2) in zip(v,center_of_computed_bounding_box)))-unknown_floats[0]) for v in vertexes) )

	return (material_index, nb_vertexes, nb_indexes, nb_instances, level_of_detail, mesh_centroid, vertexes, vertexes_and_additional_data, indexes, field_numbers)


import math

def compute_transformation(jm_index, jm, debug, joint_names):

	if debug:
		print('    joint matrix', jm_index, 'for joint', joint_names[jm_index])
		for l in jm: print('       ', l)

	translation_vector = tuple(l[3] for l in jm[:3])
	rotation_axis = ( jm[2][1] - jm[1][2], jm[0][2] - jm[2][0], jm[1][0] - jm[0][1] )
	rotation_amplitude = math.sqrt( sum( (c*c) for c in rotation_axis) )
	if rotation_amplitude==0:
		if debug: print('    => translation matrix with translation vector', translation_vector)
		return (translation_vector, None)

	rotation_axis = tuple( c/rotation_amplitude for c in rotation_axis )
	# if rotation_amplitude > 2.:
	# 	print('warning: bad rotation matrix for joint {}, "fixing" it.'.format(joint_names[jm_index]))
	# 	rotation_amplitude = 2.
	# rotation_angle = math.asin(rotation_amplitude/2)
	rotation_angle = rotation_amplitude
	if debug: print('    => rotation axis is', rotation_axis, 'rotation angle is {}°'.format(math.degrees(rotation_angle)))
	vn = sum( (a*b) for a,b in zip(translation_vector, rotation_axis))
	remaining_translation_vector = tuple( vn*a for a in rotation_axis)
	v = tuple( (a-b) for a,b in zip(translation_vector, remaining_translation_vector) )
	norm_v = math.sqrt( sum( (c*c) for c in v) )
	if norm_v != 0.:
		v = tuple(c/norm_v for c in v)
	w = tuple( rotation_axis[k1]*v[k2] - rotation_axis[k2]*v[k1] for k1,k2 in zip((1,2,0),(2,0,1)) )
	invariant_point = tuple( math.cos(rotation_angle/2)*a - math.sin(rotation_angle/2)*b for a,b in zip(w,v))
	if debug: print( '       invariant point on rotation axis is', invariant_point, 'and remaining translation vector is', remaining_translation_vector)
	return (remaining_translation_vector, (rotation_axis, rotation_angle, invariant_point))






def parse_TheWitness_mesh_stream(src, filename, object_name, exporters, texture_dir, texture_ext, debug, newformat):

#	Header
	header_data = parse_header(src, debug, newformat)
	for e in exporters: e.export_global_infos(*header_data)
	nb_LODs = header_data[1]

#	Materials
	if debug:
		print()
		print('=== MATERIALS: ===')
	materials = parse_materials(src, debug)
	for e in exporters: e.export_materials(materials, object_name, texture_dir, texture_ext)


#	Geometries
	if debug:
		print()
		print('=== GEOMETRIES ===')

	# Loop on geometry groups.
	# Meshes in the second group seem to be used for shadowing, not for rendering:
	#   - they correspond to those in the first group (always in the same order?), except:
	#     - sometime multiple meshes from the first group can be merged into a single one in the second group
	#       (because differences in the material does not mater for shadows, unless the materials have transparency)
	#     - some meshes of the first group may not appear in the second group (shadow-less objects, e.g. fully transparent ones, flat patches on the ground, or collision meshes)
	#   - (to be checked) they appear in the second group with the same amount of facets but fewer vertexes than their corresponding mesh(es) in the first group
	#     (because normals are attached to vertexes, not facets, so in case of an hard edge, vertexes are duplicated with different normals, but these difference does not mater for casting shadows)
	#   - smaller vstride. Meshes in the second group usually only have:
	#      - the vertexes, of course
	#      - "color" and "uv" fields for transparent objects (to check)
	#        -> there can only be two meshes in the second group (at some LOD) if some parts of the object are transparent and others are fully opaque (to check)
	#      - animated objets also have an "animation_group" field, of course (to check).
	#	   - they never have any of the other fields (to check).
	geometry_groups = list()
	for geometry_group_index, geometry_group_type in enumerate(('rendering', 'shadows')): 

		geometry_group_size = read_int(src)
		if debug: print('--- Group {} ({}) has {} meshes ---'.format(geometry_group_index + 1, geometry_group_type, geometry_group_size))

		meshes_in_group = list()
		for mesh_index in range(geometry_group_size):

			(material_index, nb_vertexes, nb_indexes, nb_instances, level_of_detail, mesh_centroid, vertexes, vertexes_and_additional_data, indexes, field_numbers) = parse_mesh(src, mesh_index, nb_LODs, debug, newformat)
			for e in exporters:
				e.export_mesh(object_name, geometry_group_index + 1, mesh_index, level_of_detail, object_name, indexes, vertexes_and_additional_data, field_numbers, material_index, texture_dir, texture_ext, mesh_centroid)
			meshes_in_group.append( (material_index, nb_vertexes, nb_indexes, nb_instances, level_of_detail, mesh_centroid, vertexes, indexes) )

		geometry_groups.append(meshes_in_group)

	for e in exporters: e.end_export(object_name)


#	Physical aspects of meshes? Or animation? Not all mesh files have an entry in this section for every mesh they contain... Maybe precomputed radiosity data?
	has_physics_section = True
	if newformat:
		has_physics_section = read_byte(src)
		assert(has_physics_section in (0,1))
		has_physics_section = (has_physics_section != 0)

	if debug:
		print()
		print('=== PHYSICS ===')
		if not has_physics_section: print('no physics section')

	if has_physics_section:
		# Two unknown vectors (might actually be considered as the the end of the previous section).
		# It actually seems to be a bounding box for the vertex as they are given in the file, which, in the case of an animated object, would only be a valid bounding box for the default animation state.
		physics_bounding_box = (read_vector32(src), read_vector32(src))
		if debug: print('physics bounding box:', physics_bounding_box[0], physics_bounding_box[1])
		for e in exporters: e.set_bounding_box(*physics_bounding_box)
		
		# Loop on meshes
		nb_meshes = read_int(src)
		if debug: print(nb_meshes, 'physics properties.')
		# assert(nb_meshes >= 0)# verified to be always True! (oldformat)
		mesh_id = 0
		face_count = 0
		for current_mesh_index in range(nb_meshes):
			
			if debug: print('Physics #{}:'.format(current_mesh_index))

			# if current_mesh_index > 0:
			# 	print('reading two extra ints')
			# 	assert( (read_int(src) == 0) and (read_int(src) == 0) )

		#	Read facets definitions
			# nb_faces often corresponds to the number of faces of one of the meshes in the "geometry" section.
			# and it seems to always be the case that the sum of the nb_faces for a few "physics" is equal to the number of facets of one mesh in the "geometry" section.
			# however, I cannot find any way to determine which of these meshes is the right one.
			# Sometime, the "physics" to use in the sum are not even consecutive ones or the "geometry" is a "shading" one.
			# An example of both situations is loc_hub_Terrain_Plaza.mesh.decoded_mesh where physics 0 and 2 combined match geometry 0 for shadows, but physics 1 match geometry 2 from rendering… which has no UV mapping)
			# Unless it's not geometry 0 for shadows, but the union of geometry 0 and 1 for rendering?
			nb_faces = read_int(src)
			if debug: print('    physics has', nb_faces, 'facets.')
			face_count += nb_faces

			if newformat:
				physics_facets =  tuple( read_short_array(src, 3) for _ in range(nb_faces))
				# if debug:
				# 	for f in physics_facets: print('     {:3} {:3} {:3}'.format(*f))
				
		#	Read vertexes definitions
			nb_vertexes = read_int(src)
			# assert(max(x for f in physics_facets for x in f) == (nb_vertexes-1))
			# if not newformat: assert(nb_vertexes == 0)# verified to be always True!
			if debug: print('    physics has', nb_vertexes, 'vertexes')
			physics_vertexes = read_array(src, nb_vertexes, read_vector32)
			# if debug:
			# 	for v in physics_vertexes: print('       {: 8f} {: 8f} {: 8f}'.format(*v))

		#	Oldformat style: reading patches
			# the vertexes and facets are defined by a patch structure		
			if newformat:
				nb_patches = 0
				patches = None
			else: # oldformat only
				# List of patches made of 4 facets (usually the same number of facets than one of the meshes, but not always).
				# The patch contains the coordinates of the 3x4=12 vertexes defining the 4 facets (3 vertexes by facet). By noting x1-2 the x-coordinate of the first vertex defining the second facet, the format is:
				#  (x1-1 x1-2 x1-3 x1-4) (y1-1 y1-2 y1-3 y1-4) (z1-1 z1-2 z1-3 z1-4)
				#  (x2-1 x2-2 x2-3 x2-4) (y2-1 y2-2 y2-3 y2-4) (z2-1 z2-2 z2-3 z2-4)
				#  (x3-1 x3-2 x3-3 x3-4) (y3-1 y3-2 y3-3 y3-4) (z3-1 z3-2 z3-3 z3-4)
				# If the number of facets is not a multiple of 4, the vertexes of the last facets in the last patch have coordinates with meaningless values.
				# -> question: is there a meaning to the patch structure, or is it just an optimization to pipeline four facets in parallel?
				nb_patches = math.ceil(nb_faces/4)
				if debug:
					print('    physics has', nb_patches, '4-facet patches.')
				patches = tuple( # a list of patches
					tuple(zip( *( # where each patch is a list 
						zip(*(
							read_array(src, 4, read_float32)
							for coord_index in (0,1,2)
						))
						for vertex_index in (0,1,2) 
					)))
					for i in range(nb_patches)
				)
				# if debug:
				# 	for patch_index, patch in enumerate(patches):
				# 		print('        patch', patch_index)
				# 		for vertex_index, vertex in enumerate(patch): print('          vertex {}:'.format(4*patch_index+vertex_index), vertex)
			
			nb_physics_kdtrees = read_byte(src)
			# nb_physics_kdtrees is either 0 or 1.
			# 0 seems to be for planes with transparency or light emission, decals, or surfaces that will display changeable content (notably puzzle surfaces).
			# So, 0 seems to be for planes that are not concerned by re-emitting the light they receive -> elements present when nb_physics_kdtrees is 1 are for radiosity?
			if debug: print ('   ', '+' if nb_physics_kdtrees > 0 else '-', 'the physics has {} KDtrees'.format(nb_physics_kdtrees))
			for e in exporters: e.export_patched_mesh(current_mesh_index, nb_faces, nb_patches, patches, nb_physics_kdtrees)

			for index_extra_vectors in range(nb_physics_kdtrees):

				# if debug: print('        -- KDtree {} --'.format(index_extra_vectors))

				if not newformat:
					# Two vectors that are the same than the ones at the beginning of this section
					assert( (read_vector32(src) == physics_bounding_box[1]) and (read_vector32(src) == physics_bounding_box[0]) )# verified to be always True!

			#	The KDtree
				# This is a (relaxed) KD-tree (k=3) to find, given a point coordinate or ray, the facets of the physics it should be tested again.
				# The KDtree is encoded as a list of nodes corresponding to a traversal of the tree in which each node outputs first the data of its two children,
				# then recursively encodes each of its two children. Since the procedure does not output the data of the node itself, it is applied on a fake root node that has the real root of the KDtree
				# as first children and a fake node as second children.
				kdtree_size = read_int(src)
				global kdtree_cells
				kdtree_cells = list()
				def kdnode_reader(s):
					flags = read_int(s)
					if (flags&0xC0000000) == 0xC0000000: # 0xC0000000 = -2.0
						# Fake node for the second child of the fake root, just ignore it.
						assert(flags == 0xFFFFFFFE) # 0xFFFFFFFE = NaN
						assert( read_int(s) == 0)
						return (True, None)
					if (flags&0x80000000) != 0:  # This is a leaf of the KDtree, it contains a subset of the facets as a partition of the unknown_facets_list
						# The kdtree_cells seem to be always in order? I.e., if a KDtree leaf gives (start_pos, end_pos), then the next leaf of this type will give (end_pos, …).
						# But also, the facets in the unknown_facets_list seem to be in increasing order of index inside each kdtree_cell.
						start_pos = (flags&0x3FFFFFFF)//4
						list_size = read_int(s)
						global kdtree_cells
						kdtree_cells.append( (start_pos, start_pos+list_size) )
						return (True, (start_pos, list_size))
					# This is a separation plane node of the KDtree. It defines a plane with an equation of the form x=value, y=value, or z=value.
					# The first child should be considered if we are interested by the facets with coordinates lesser than or equal to the value provided, and the second child otherwise.
					test_axis = flags%4            # The axis involved in the test: 0=x, 1=y, 2=z.
					node_index = flags>>4          # Index of the node in a depth-first traversal of the KDtree.
					tested_value = read_float32(s) # Value of the equation.
					return (False, (test_axis, node_index, tested_value))
				def kdtree_reader(s):
					(is_leaf1, node_data1) = kdnode_reader(s)
					(is_leaf2, node_data2) = kdnode_reader(s)
					return ( (node_data1, None) if is_leaf1 else (node_data1, kdtree_reader(s)), (node_data2, None) if is_leaf2 else (node_data2, kdtree_reader(s)) )
				kdtree = kdtree_reader(src)[0]
				if debug:
					# print('KDtree ({} items):'.format(kdtree_size), kdtree)
					print('      KDtree defines {} cells.'.format(len(kdtree_cells)))
				# def kdtree_check(kdtree, bounding_box_min, bounding_box_max, indent=''):
				# 	(node_data, subtree) = kdtree
				# 	if subtree is None: return # it's a leaf
				# 	(test_axis, node_index, tested_value) = node_data
				# 	test = (bounding_box_min[test_axis] <= tested_value <= bounding_box_max[test_axis])
				# 	print(indent, '+' if test else '-', 'kdtree node', node_index, 'has equation', '{}={}'.format(('x','y','z')[test_axis], tested_value), 'in bounding box', bounding_box_min, '->', bounding_box_max)
				# 	# assert( test ) # not always true
				# 	kdtree_check(subtree[0], bounding_box_min, tuple( (tested_value if i==test_axis else c) for i,c in enumerate(bounding_box_max)), indent+' ')
				# 	kdtree_check(subtree[1], tuple( (tested_value if i==test_axis else c) for i,c in enumerate(bounding_box_min)), bounding_box_max, indent+' ')
				# kdtree_check(kdtree, physics_bounding_box[1], physics_bounding_box[0])
				for e in exporters: e.export_kdtree(current_mesh_index, index_extra_vectors, kdtree)

			#	Then a list of facet indexes from which the kdtree cells are defined
				unknown_facets_list_size = read_int(src) # I have seen prime number for this value, so the list is not breakable in same-sized groups
				unknown_facets_list = read_int_array(src, unknown_facets_list_size)
				# if debug: print('    	unknown_facets_list ({} items for {} facets):'.format(unknown_facets_list_size, nb_faces), unknown_facets_list)
				# assert(all(0 <= i < nb_faces for i in unknown_facets_list)) # all the numbers in the list are compatible with facet indice.# verified to be always True!
				# assert(all(i in unknown_facets_list for i in range(nb_faces))) # all the facets appear at least once in this list.# verified to be always True!

			#	Read and export kdtree_cells
				for cell_id, (kdtree_cell_start, kdtree_cell_end) in enumerate(kdtree_cells):
				# 	print()
					facets = unknown_facets_list[kdtree_cell_start:kdtree_cell_end]
					# assert( len(facets) == len(set(facets)) )# verified to be always True!
					for e in exporters: e.export_partition(current_mesh_index, index_extra_vectors, cell_id, facets)
				# 	print(p, facets, current_mesh_index, geometry_groups[0][current_mesh_index][:-2])
				# 	vertexes, mesh_indexes = geometry_groups[0][current_mesh_index][-2:]
				# 	indexes = set( mesh_indexes[i][j] for i in facets for j in (0,1,2))
				# 	print(indexes)
				# 	for indice in indexes:
				# 		print('{:8f}, {:8f}, {:8f}'.format(*vertexes[indice]))

			if newformat:
				# UV mappings for each vertex of each face of the physics model, as indexes for the texture coordinates defined in physics_texture_coordinates.
				physics_UV_mapping_size = read_int(src)
				physics_UV_mapping = read_short_array(src, physics_UV_mapping_size) # for objects with lots of facets, it might be int32-encoded instead of short-encoded
				# assert(physics_UV_mapping_size in (0, nb_faces*3)) # Verified to be always True -> an adjacency map to tell what facets are neighbors of a given facet? Or a reverse map to know for each vertex the facet it belongs to?
				# if debug: print('    Unknown facets list 2 ({} items):'.format(physics_UV_mapping_size), ' '.join('{:3}'.format(i) for i in physics_UV_mapping))
				if debug: print('   ', '+' if physics_UV_mapping_size > 0 else '-', 'Physics model has', 'no' if physics_UV_mapping_size == 0 else 'one', 'per-vertex UV mapping.')
			else:
			#	A list of pairs of floats
				# It actually seem to be texture coordinates.
				# In loc_end_elevator_panel_door2 (the flat surface in the flying elevator where there are the "puzzles" to close the door) the material does not display the puzzle line, but the floats here could be uv-coordinates in a texture that displays it.
				# -> check if that section is only available for meshes that hold a puzzle.
				# Since we have an entry in the list for each vertex of each face, the two numbers could be some parameter of global illumination to be interpolated in the facet?
				intervals_list_size = read_int(src) # seems to be null or 3 x nb_faces = nb vertexes
				# assert(intervals_list_size in (0, nb_faces*3))# verified to be always True!
				# intervals_list = tuple( read_int_array(src, 2) for i in range(intervals_list_size) )
				# if debug: print('    intervals list ({} items):'.format(intervals_list_size), ' '.join('({:08x} {:08x})'.format(*i) for i in intervals_list))
				intervals_list = read_array(src, intervals_list_size, lambda x: (read_float32(x), read_float32(x)))
				if debug: print('    intervals list ({} items):'.format(intervals_list_size), ' '.join('({:8f}, {:8f})'.format(*i) for i in intervals_list))
				# assert( all((a<=b) for a,b in intervals_list[:-1]))
			
		#	A list of unknown purpose
			# There is exactly one entry in the list per vertex, i.e. 3 x nb_facets.
			nb_physics_pervertex_interpolations = read_int(src)
			assert(nb_physics_pervertex_interpolations in (0, nb_faces*3))# verified to be always True!
			if debug: print('   ', '+' if nb_physics_pervertex_interpolations > 0 else '-', 'model', 'does not have' if nb_physics_pervertex_interpolations == 0 else 'has', 'per-vertex interpolation values.')#, tuple(t[0] for t in physics_pervertex_interpolations) )
			if newformat:
				# The interpolation values are not given directly anymore, but instead they are given as indexes in physics_interpolation_values.
				# Note: These four interpolation values could be the respective proportions of the different types of lights (ambient, diffuse, specular, self-emitted)?
				#       -> no, there would be purely ambient faces, which seems unlikely. Unless ambient is last?
				physics_pervertex_interpolations = read_array(src, nb_physics_pervertex_interpolations, read_short)
				# if (nb_physics_pervertex_interpolations > 0) and debug:
				# 	print(physics_pervertex_interpolations[:min(500,nb_physics_pervertex_interpolations)])
			else:
				# The list contains 4-floats32 vectors.
				# The sum of the coordinates is 1 => interpolation values? or pre-squared coordinates of an unitary quaternion?
				physics_pervertex_interpolations = tuple( read_array(src, 4, read_float32) for i in range(nb_physics_pervertex_interpolations) )
				# assert(nb_physics_pervertex_interpolations == nb_indexes)
				# assert( all( (z==0.0) and (w==0.0) and (math.fabs(x+y-1.0)<0.000001) for x, y, z, w in physics_pervertex_interpolations) ) # a common case, but not always
				# assert( all( (math.fabs(x+y+z+w-1.0)<0.000001) for x, y, z, w in physics_pervertex_interpolations) )# verified to be always True!
				# See:
				#	loc_hub_bld5_basement_shadow
				#	loc_newEnd_box_panel
				#	vs_mona_newstupa_shutters_A* (those without holes only have 1 0 0 0, but those with holes have other values — in the holes ? Also, there is a ring of facets around the holes, which correspond to the dark areas on the shutters, but these don't have a gradient or straight border) -> these interpolation values are used to compute stain with a threshod in a volumetric noise ?
				#	obj_Buoy_* -> same thing, it seems to be used to display rust.
				if debug:
					for i,t in enumerate(physics_pervertex_interpolations):
						v = patches[i//12][(i//3)%4][i%3]
						vr = tuple( (c-a)/(b-a) for a, b, c in zip(physics_bounding_box[0], physics_bounding_box[1], v))
						print('    ', '      ' if (i%3)!=0 else '{:<6d}'.format(i//3), '{:+.3f}, {:+.3f}, {:+.3f}, {:+.3f}'.format(*t), '   v: {:+.3f}, {:+.3f}, {:+.3f}'.format(*v), '   vr: {:+.3f}, {:+.3f}, {:+.3f}'.format(*vr))
			
		#	Another list of unknown purpose
			# Actually, these UV texture coordinates are only provided for the geometries that have transparent parts, like the leaves, flowers, or roots of plants (see for instance loc_coloredLights_prop_hangrackA)
			if newformat:
				# UV texture coordinates for objects like foliage that have a lot of similar instances.
				physics_texture_coordinates_size = read_int(src)
				if debug: print('   ', '+' if physics_texture_coordinates_size > 0 else '-', 'model has {} UV texture coordinates'.format(physics_texture_coordinates_size))
				# assert( (physics_texture_coordinates_size == 0) or ( (physics_UV_mapping_size>0) and (physics_texture_coordinates_size == max(physics_UV_mapping)+1)) ) # not always true? see e.g. loc_swamp_grass_puzzle.mesh
				# This is a list of vertexes coordinates… But why only two coordinates? 
				# -> It seems to be coordinates on the surface of the object in some parameterized space.
				physics_texture_coordinates = read_array(src, physics_texture_coordinates_size, lambda x: (read_float32(x), read_float32(x)))
				# if debug and (physics_texture_coordinates_size>0):
				# 	# print('      ->', ' '.join('({: .4f} {: .4f})'.format(*f) for f in physics_texture_coordinates))
				# 	for f in physics_texture_coordinates: print('{: .4f}, {: .4f}'.format(*f))

				nb_physics_interpolation_values = read_int(src)
				if debug: print('   ', '+' if nb_physics_interpolation_values > 0 else '-', 'interpolation values list has size', nb_physics_interpolation_values)
				# Here again, this is a list of elements made of 4 floats in the range 0-1, which sum is equal to 1 (and the fourth seem to be always null).
				physics_interpolation_values = read_array(src, nb_physics_interpolation_values, lambda x: read_array(x,4,read_float32))
				if debug and (nb_physics_interpolation_values>0):
					assert(max(physics_pervertex_interpolations) == (nb_physics_interpolation_values - 1) )
					# print('      ->', ' '.join('({: .2f} {: .2f} {: .2f} {: .2f})'.format(*f) for f in physics_interpolation_values))

			unknown_list_size4 = read_int(src)
			# The list contains 3-float32 unitary vectors (normals?)
			# Here again, the list is either absent or have a size of 3 x nb_faces, so we have one normal vector at each vertex of each facet (direction of the sun, for delayed illumination?)
			# It matches geometries that have normals and tangents, so it could be one or the other. But it would more likely be tangents, necessary for bump mapping.
			# -> meshes with this part are mainly terrains, possibly all objects with specular effects (computing these effects in delayed rendering requires the normal).
			#    It's very rarely present for "normal" objects, but there are exceptions such as fol_cypressBranch_{1,2}.
			# -> Actually, the vectors are not always unitary.
			# assert(unknown_list_size4 in (0, nb_faces*3))# verified to be always True!
			unknown_list4 = read_array(src, unknown_list_size4, read_vector32)
			# assert( all( (math.fabs(x*x + y*y + z*z - 1.) <= 0.00001) for x,y,z in unknown_list4) )# verified to be always True!
			if debug:
				print('   ', '+' if unknown_list_size4 > 0 else '-', 'unknown unitary vectors list has ' + ('no' if unknown_list_size4 == 0 else str(unknown_list_size4)) + ' unitary vectors.')
				# for i,v in enumerate(unknown_list4): print('    ', '      ' if (i%3)!=0 else '{:<6d}'.format(i//3), '{: .3f}, {: .3f}, {: .3f}'.format(*v))
			
			# Note: the material index could actually be used to know what geometries are fused together in a physics mesh.
			# It seems that all materials with first flag byte 0 and a same fourth flag byte are fused together (no, not true),
			#  and all materials with first flag byte 2 and a same texture as first parameter are fused together.
			physics_material_index = read_int(src)
			if debug: print ('    material index:', physics_material_index)

			# if (physics_material_index != current_mesh_index):
			# 	print( nb_faces*3, face_count*3, geometry_groups)
			# if (face_count >= (geometry_groups[0][mesh_id][2]//3)):
			# 	assert(face_count == (geometry_groups[0][mesh_id][2]//3))
			# 	mesh_id += 1
			# 	face_count = 0

			# print( str(nb_physics_kdtrees) + " " + ("F" if intervals_list_size == 0 else "T") + ("F" if nb_physics_pervertex_interpolations == 0 else "T") + ("F" if physics_texture_coordinates_size == 0 else "T") + "\t" + str(current_mesh_index) + "\t" + str(physics_material_index) + "\t" + filename )
			# On the 5646 meshes considered, 3763 (2/3) have none of the last 3 lists.

#	Joints data
	if debug:
		print()
		print('=== Joints ===')

	joints_list_size = read_int(src)
	if debug: print('The model has', '{} joints:'.format(joints_list_size) if joints_list_size > 0 else 'no joint.')

	joint_matrices = tuple( tuple( read_array(src, 4, read_float32) for l in range(4) ) for joint_index in range(joints_list_size) ) # 4x4 matrices, allow for rotation around any position.

	joint_names = read_array(src, joints_list_size, read_string)
	if debug and (joints_list_size > 0): print('   Joint names:', joint_names)

	for joint_matrix_index, joint_matrix in enumerate(joint_matrices):
		(joint_translation_vector, joint_rotation_parameters) = compute_transformation(joint_matrix_index, joint_matrix, debug, joint_names)
		for e in exporters: e.export_joint(joint_names[joint_matrix_index], joint_translation_vector, joint_rotation_parameters)


#	Remaining Data
	remaining_data = read_byte_array(src, -1)
	# # print(' '.join('{:3}'.format(x) for x in remaining_data))
	# if debug: print(len(remaining_data), 'bytes remaining.')
	assert(len(remaining_data) == 0)# verified to be always True!



# deprecated. Use parse_TheWitness_mesh_stream with modules.parsing_TheWitness_files.parse_TheWitness_file instead.
# def parse_TheWitness_mesh_file(filenames, object_name, exporters, texture_dir, texture_ext, debug=False, newformat=True, need_decompressing=False):

# 	import subprocess, sys

# 	if need_decompressing or (len(filenames)>1):
# 		cmd = ('python3', 'witness_lz4d_stream.py') + tuple(filenames)
# 		source = subprocess.Popen(cmd, stdin=sys.stdin, stdout=subprocess.PIPE).stdout
# 	else:
# 		source = open(filenames[-1], 'rb')

# 	parse_TheWitness_mesh_stream(source, filenames[-1], object_name, exporters, texture_dir, texture_ext, debug, newformat)
# 	source.close()


# To call directly from command line as python modules/parse_TheWitness_mesh.py ... (see modules/parse_TheWitness_files.py for options)
if __name__ == '__main__':

	from parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments

	parser = theWitnessFileParserArguments('Parse a The Witness mesh file to simulate an export.')
	
	export_options = parser.add_argument_group('options for exporters', 'this program does not export anything but uses modules that implement the export API and need this')
	export_options.add_argument('--name', dest='objectname', nargs=1, action='store', default='', help='The name of the exported object (default: empty string).')
	export_options.add_argument('--texture-dir', '-td', nargs=1, dest='texture_dir', action='store', default='', help='The directory in which exporters can find the uncompressed textures')
	export_options.add_argument('--texture-ext', '-te', nargs=1, dest='texture_ext', action='store', default='texture.png', help='The file extension added to the name of textures')

	args, filenames = parse_command_line_arguments(parser)
	
	# print(filenames)
	parse_TheWitness_file(parse_TheWitness_mesh_stream, filenames, args.objectname, tuple(), args.texture_dir, args.texture_ext, args.debug, args.newformat, need_decompressing = args.need_decompressing)

