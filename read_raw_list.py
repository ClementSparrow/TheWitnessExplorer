# -*- coding: utf-8 -*-

from modules.readers import *
from modules.entity_readers.helpers import *
from modules.entity_readers.entities import read_entities

def read_assetlist_file(f, filename, debug=True):

	'''
	A general function to read an asset list file (usually, .raw files) and the following special files that have dedicated formats and parsing functions:
	- save.entities (all entities, see modules/entity_readers/entities.py)
	- save.asset_dependencies.raw.

	A special case of asset list files are the (sub)archive content descriptors:
	- save.asset_map.raw (for the whole archive)
	- save_{subarchive_name}_{subarchive_part}.pkg save_{subarchive_name}_{subarchive_part}.pkg_asset_list.raw (for subarchive, where parts=0...n)

	ASSET LIST FILE FORMAT:

	Data types:
	- strings start with a 0x01 byte and end with a 0x00 byte.
	- 32-bits integers are little endian encoded

	File header:
	- 05 00 00 00 File content type: 5 is for a list?
	- 04 00 00 00 or 06 00 00 00 (second bit defines the flag SHORT_FORMAT) List content type (see also 03 for shaders below)
	- int32 = number of items in the list

	La suite du fichier est une liste où chaque élément est codé avec la structure suivante :
	- un int32 (ou byte pour SHORT_FORMAT) de type:
	  -  0 pour les textures et autres images utilisées dans les materiaux (.tga, .bmp, .png, .dds, .jpg)
	  -  1 pour les .lightmap
	  -  3 pour les .fx
	  -  4 pour les géométries d'objets 3D (.triangle_list_mesh)
	  -  5 pour les fontes (.otf, .mod_otf, .ttf) et fichiers de config textuels (.variables, .sound_tweaks, .txt, "data/worlds/save/save_nav_data" et "data/worlds/save/save_exact_volumes") -> correspond à l'extension .raw ajoutée dans data-osx.zip.
	  -  6 pour la resource "save"
	  -  7 pour les .grass
	  -  8 pour les .keyframed_animation
	  -  9 pour les géométries 3D nommées "save", prebacked? (.triangle_mesh)
	  - 10 pour les probes, envmaps, shadowmaps et "data/worlds/save/global-atlas.tga" (.dds et .tga)
	  - 11 pour les sons (.ogg et .wav)
	  - 12 pour les LUT tables (.tga et .png)
	  - 13 pour les videos (.bk2)
	- une chaine de caractère (identifiant de resource à localiser. Ces identifiants sont utilisés dans save.entities)
	- une chaine de caractère (nom de fichier relatif, ou pas de chaîne pour la resource nommée simplement 'save'. Cependant, ces noms de fichiers relatifs ne correspondent pas à ceux trouvés dans l'archive principale du jeu). (pas pour SHORT_FORMAT, les entrées de l'asset_map correspondant aux fichier du pkg dans l'ordre). Le nom de fichier (sans chemin d'accès) apparait dans data-osx.zip>filelist.txt.raw avec la taille du fichier.
	- une liste de chaînes de caractères commençant par un int32 donnant sa taille (nombre d'éléments qu'elle contient).
	  - la liste est généralement vide, sauf pour les .fx où elle contient en alternance le nom d'une option graphique et la valeur numérique associée, encodée sous forme de chaîne de caractères.
	  - pas de liste pour SHORT_FORMAT
	- un short qui vaut normalement 511 = 0x1ff (mask avec les 9 bits de poids faible allumés), mais peut prendre des valeurs différentes pour les textures:
	  - 62 = 0x3e pour des textures .tga dont le nom se termine par "blend"
	  - 63 = 0x3f pour des textures .tga dont le nom se termine par "normal"
	  - 65 = 0x41, 386 = 0x182 ou 52 = 0x34 pour les fichiers "data/worlds/save/shadow_map_{n}.dds", où n vaut respectivement 2048, 4096, et 8192.
	- un short qui vaut 0 quand la liste de chaînes de caractère précédente est vide, ou 4 sinon. (absent pour SHORT_FORMAT)
	- un int32 qui vaut toujours 1, sauf si la resource est un fichier .tga dont le nom se termine par "blend" ou "normal" (et dans ce cas, le mask précédent vaut toujours 511). (pas pour SHORT_FORMAT)
	- pour SHORT_FORMAT uniquement : un int32 qui, sous forme hexadecimale, est ajouté à la fin du nom du fichier (précédé d'un _) (version number?)


	Note: shaders.shader_list.raw has a similar structure but with "list content type" set to 03 00 00 00, and the following fields per item:
	string, int32=id1, int32=id2, int32=mask (constant for same id1), short=mask=511, short=04 00, as in asset maps.
	'''

#	Read file header
	file_type = read_int(f)
	assert(file_type in (5,12))

#	Read special files
	if file_type == 12:
		read_entities(f) # contrarily to the other types of files, -M save.entities is also compressed. Use witness_lz4d_stream!
		exit()
	list_content_type = read_int(f)
	if list_content_type == 7: # save.asset_dependencies.raw
		read_asset_dependencies(f)
		exit()

#	Get the appropriate reader for that list
	content_reader = {
		3: (read_optional_string, read_int, read_int, read_int, read_short, read_short), # shader list
		4: (read_int, read_optional_string, read_optional_string, read_string_list, read_short, read_short, read_int), # save.asset_map.raw, long format
		6: (read_byte, read_optional_string, read_short, read_int), # other asset maps in subpackages, short format
	}[list_content_type]

#	Read resources in the list
	nb_resources = read_int(f)
	resources = list( read_tuple(f, *content_reader) for resource_index in range(nb_resources))

#   Remaining Data
	remaining_data = read_byte_array(f, -1)

	return (list_content_type, resources, remaining_data)



def read_asset_dependencies(f):

	offsets = read_int_array(f, 3)
	print(offsets)

#	Read the first part of the table: resource identifiers
	resource_basenames = list()
	offset = 0
	resource_basenames_dict = dict()
	while offset<offsets[1]:
		s = read_nullterminated_string(f)
		# print(offset, s)
		resource_basenames_dict[offset] = s
		offset += len(s) + 1
		resource_basenames.append(s)
	# print(', '.join(resource_basenames))
	print(len(resource_basenames), 'resource names')

#	Read the second part of the table: information about the resources
	nb_resource_infos = (offsets[2] - offsets[1]) // 15
	print(nb_resource_infos, 'resource infos')
	resource_infos = tuple( read_tuple(f, read_byte, read_int, read_int, read_short, read_int) for _ in range(nb_resource_infos) )
	# for (typ, string_offset, nullint, mask, resource_id) in resource_infos:
	# 	print(typ, resource_basenames_dict[string_offset], mask, '{:08X}'.format(resource_id))
	# # - the data format is actually very close to the SHORT_FORMAT found in asset_map.raw files from packages. Actually, the number of resources contained in the two files are the same, except for the 2031 resources of type 3 (.fx) that does not appear in this file, and there are 30 more resources of type 0 in this file.
	# # - typ is:
	# #     - 0 for textures
	# #     - 1 for save/lightmaps/*
	# #     - 2 is unused
	# #     - 3 is unused
	# #     - 4 for mesh resources (only visible ones? there don't seem to be any occluder, for instance)
	# #     - 5 for text files (variables, notably) and font files
	# #     - 6 for 'save' only
	# #     - 7 for some save/resources/*
	# #     - 8 for animations (there are 257 in this file, as there are 257 *.animation files in index.txt)
	# #     - 9 for save/clusters/* and some save/resources/*
	# #     - 10 for (light-?) probes
	# #     - 11 for sounds
	# #     - 12 for LUT tables
	# #     - 13 for windows? Only resources have base names window1, window1_unlit, window2, window2_unlit
	# # - string_offset is the position of the base string in the first section of the file.
	# # - mask is always 511 = 0x1ff, except for some textutres (type 0) where it can also be 63=0x3f or 62=0x3e, and for some lightprobes (tye 10) where it can also be 52=0x34, 65=0x41, or 386=0x182.
	# # - resource_id: some int in the range 0x0003a368-0xfffea4db, simingly random (CRC?)
	# #      Multiple resource_infos can have the same resource_id but it's rare (43 cases), and when it happens, it's always a pair of resources with the same string_offset (except one pair), and:
	# #        - both resources have typ=0, one has mask=511 and the other has mask=62, and the string ends with '-blend' or something containing 'blend'
	# #        - both resources have typ=0, one has mask=511 and the other has mask=63, and the string ends with '-normal'
	# #        - both resources have mask=511 but types 0 and 4.
	# #        - both resources have mask=511 but types 4 and 8 (only happens twice: for strings loc_factoryWood_rampSkirt and loc_coloredLights_Elevator_cable).
	# #        - both resources have mask=511 but types 1 and 10 (in that case that happens only once, the strings are different: save/lightmaps/09/195109_00 and save/resources/98855-probe).
	# # Therefore, the resource_infos seem to be used to generate a more complete resource name from the base name at position string_offset.
	# 	assert( nullint == 0 )
	# 	assert( typ in (0,1,3,4,5,6,7,8,9,10,11,12,13) )

	# print( ', '.join('{:08x}'.format(x) for x in sorted(y[4] for y in resource_infos) ) )
	# for i in range(80):
	# 	print(i, resource_basenames[i], '{} {} {} {} {:8x}'.format(*resource_infos[i]))

	# # print resource infos by resource type:
	# resource_infos_by_type = tuple( list() for _ in range(14) )
	# for x in resource_infos:
	# 	resource_infos_by_type[x[0]].append(x[1:])
	# for typ, r in enumerate(resource_infos_by_type):
	# 	print('for resource type', typ, 'there are', len(r), 'resources')
	# 	# if len(r)>0: print('  ', ', '.join(resource_basenames_dict[x[0]] for x in r))
	# 	# print('  ', set(x[2] for x in r)) # masks
	# # print(', '.join('{:08X}'.format(x) for x in sorted(tuple(y[-1] for y in resource_infos_by_type[4]))))

#	Read the third part of the table: dependency lists (a list of lists of shorts, where each short is the index of a resource in the previous section)
	# all resource_infos are referenced at least once in a dependency list
	max_offset_for_depency_lists = (offsets[0] - offsets[2])
	t=0
	dependency_lists = []
	dependency_list_indexes = dict()
	while t<max_offset_for_depency_lists:
		dependency_list_indexes[t] = len(dependency_list_indexes) # keep track of the offset the list starts at, because it is used in the next part of the table
		n = read_short(f)
		deps = read_short_array(f, n)
		dependency_lists.append( deps )
		# if any(resource_infos[d][0]==12 for d in deps): print(len(dependency_lists), 'is a LUT table and points to', deps)
		# dependency_lists.append( tuple(resource_basenames_dict[resource_infos[x][1]] for x in deps) )
		# assert( len(set(resource_infos[dep][0] for dep in deps)) == 1 ) # -> false
		# assert( all(resource_infos[dep][0] in (0,1,5,6,12) for dep in deps) ) # -> false
		# print(len(dependency_list_indexes), '->', deps)
		t += (n+1)*2
	print(len(dependency_lists), 'dependency lists') # 32272 = 1282 (type 0) + 30954 (type 1) + 22 (type 5) + 1 (type 6) + 13 (type 12).

	# # the number of dependency lists containing a resource of type 9 is exactly the number of resources of type 9. Idem for type 12 (excluding 'save'. in that case, dependency lists only contain resources of type 12), 6 and 7.
	# for s in set(tuple(set(resource_infos[x][0] for x in l)) for l in dependency_lists):
	# 	print(s, sum(1 for l in dependency_lists if set(resource_infos[x][0] for x in l) == set(s)))

#	Read the fourth part of the table: dependencies by resource id.
	nb_dependencies_by_resource_id = read_int(f)
	print(nb_dependencies_by_resource_id, 'unknown ints') # -> 38096 = 32272 (dependency lists) + 3142 (typ 4) + 22 (typ 5) + 2067 (typ 7) + 257 (typ 8) + 319 (typ 10) + 13 (typ 12) + 4 (typ 13)
	dependencies_by_resource_id = tuple( (read_int(f), dependency_list_indexes[read_int(f)]) for _ in range(nb_dependencies_by_resource_id) )
	# - le premier int est un identifiant unique entre -3 et 0x436C1=276161,
	#   -> ça semble correspondre exactement aux nombres N qu'on trouve dans les fichiers save_{N}_*.lightmap (31471), save_{N}-envmap.texture (22), save_{N}-probe.texture (296) et save_{N}.mesh_dependencies.raw (2728) listés dans filelist.txt.raw, en quel cas une des resources listées dans la liste de dépendence (champ suivant) a une basename compatible avec cette resource.
	#   -> dans ce cas, pour N = -3 … -1, ça serait les save_common ou quelque chose comme ça ?
	#   -> mais il y a aussi des entrées qui ne correspondent pas à des lightmaps/envmaps et dont la liste de dépendences ne contient que des meshes ou que des sons (footsteps?).
	# - le second int est l'index d'une dependency_list (elles sont toutes utilisées, parfois plusieurs fois)
	# for i,j in dependencies_by_resource_id:
	# 	print('{:8X} {}'.format(i,j), dependency_lists[j])

	# reverse_dependencies_by_resource_id = tuple(list() for _ in range(len(dependency_lists)))
	# for i,(x,l) in enumerate(dependencies_by_resource_id): reverse_dependencies_by_resource_id[l].append(i)
	# # for i,(a,b) in enumerate(zip(reverse_dependencies_by_resource_id,dependency_lists)): print(i,a,b)
	# # assert(all(set(a)==set(b) for a,b in zip(reverse_dependencies_by_resource_id,dependency_lists))) #-> false
	# for n in range(max(len(r) for r in reverse_dependencies_by_resource_id)+1):
	# 	print('  ', sum(1 for r in reverse_dependencies_by_resource_id if (len(r)==n)), 'dependency_lists pointed by', n, 'dependencies_by_resource_id, but', sum(1 for d in dependency_lists if len(d)==n), ' dependency list of size', n)

#	Read the fifth part of the table: mesh resource names
	nb_mesh_resourcenames = read_int(f)
	print( nb_mesh_resourcenames, 'mesh resource names' ) # -> 4565 = 1 (typ 6=save) + 3142 (typ 4 = meshes) + 1422 (typ 9 = clusters?). They appear in that order. It is also the number of mesh files with these type (6/4/9) in save.asset_map.raw
	mesh_resourcenames = tuple( (read_optional_string(f), read_int(f), read_int(f)) for i in range(nb_mesh_resourcenames) )
	# structure is:
	# - mesh filename (they appear in alphabetical order and seem to match the relative paths provided in save.asset_map.raw),
	# - an unique id (which is 0 for the first empty-named one, but can be anything for the others),
	# - an int that is usually 1D37B53 but can also be 1D37B54 (for carl) or 1D37B5C (for data/worlds/save/cluster*) or 0 (for the first, empty-named one) -> these are neither ids of dependencies_by_resource_id or ids in resource_infos.
	for m in mesh_resourcenames:
		# if m[2] != 0:
			print('{} {:8X} {:8X}'.format(*m))

	return (resource_basenames, resource_infos, dependency_lists, dependencies_by_resource_id, mesh_resourcenames)






if __name__ == '__main__':

	from modules.parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments, macosx_archive

	parser = theWitnessFileParserArguments('Parse a The Witness texture file to simulate an export.', [macosx_archive, 'save.asset_map.raw'])	
	args, filenames = parse_command_line_arguments(parser)

	list_content_type, resources, remaining_data = parse_TheWitness_file(read_assetlist_file, filenames, args.debug, need_decompressing = False)#(filenames == [macosx_archive, 'save.entities']))

	# print(' '.join('{:3}'.format(x) for x in remaining_data))
	# print(len(remaining_data), 'bytes remaining.')
	assert( len(remaining_data) == 0 ) # verified to be always True!

	# Check assertions
	if list_content_type == 3:
		for (name, id1, id2, id1mask, mask, four) in resources:
			assert( (mask == 511) )
			assert( four == 4 )
	elif list_content_type == 4:
		for (typ, resource_name, resource_filename, shader_strings, mask, four_or_null, unknown) in resources:
			assert( typ in (0,1,3,4,5,6,7,8,9,10,11,12,13) )
			assert( (len(shader_strings) == 0) or (typ==3) )
			assert( (mask == 511) or (typ==0) or ( (typ==10) and (resource_name[:16] == 'save/shadow_map_') ) )
			assert( four_or_null == (0 if len(shader_strings) == 0 else 4) )
			assert( (unknown == 1) or ((typ==0) and (mask==511)) ) # only .tga files use this field. More precisely, it's not 1 only for textures with a name ending in "blend" or "normal". Probably a scale factor used to decode the texture.
	elif list_content_type == 6:
		for (typ, resource_name, mask, crc) in resources:
			assert( typ in (0,1,3,4,5,7,8,9,10,11,12,13) )
			# assert( (mask == 511) )


	for resource in resources:
		# if resource[0] in (6,4,9):
			print(resource)

	print(len(resources), 'resources in', filenames)
