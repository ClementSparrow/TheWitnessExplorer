
from modules.parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments, macosx_archive
from modules.readers import *
from modules.entity_readers.helpers import *

def read_save_nav_data(src, filename, debug):
	
	print( read_int(src) ) # 60
	
	# string: there are 61 None, which is one more than the header -> a number of levels in the hiearchy?
	# ints:
	# - walkable_surfaces_facets for this connected_region:
	#   - #0 is the offset of the first walkable_surface_facet for this connected region. It is always the sum of #1 and #2 of the previous item.
	#   - #1 number of facets in this connected region.
	# - #2 is a bitmask (only 8 bits are used)
	# - #3 and #4 could actually be ids, but are more likely indexes in walkable_surface_facets_connections.
	#   non-zero #3 are all different, but often make sequences (if sorted), and then the items have the same #4.
	#   When multiple items have the same #4, they also have the same string (often None), #1 (always 2), #2 (always 11), and #11 (4 or 5), which means these data could be defined by or related to the entity with id #4?
	# - #5-6-7-8: walkable connections between this connected_region and its neighbors, as a subset of walkable_surface_facets_connections.
	#   - #5 is the index of the first entry for the connected region in the walkable_surface_facets_connections list or 0.
	#     If non-0, it is the sum of the #5 and #8 of the last item with a non-zero #8.
	#   - #6 is the index of the first vertex in walkable_surfaces_vertexes for this connected_region, or 0.
	#     When non-zero (see #8), it is always in the range 61136-61927 (the largest #10 is 61124), as if all the vertexes for the walkable connexions between regions were at the end of the list.
	#   - #7 is either 0 or the index of the first unknown_ints for this connected_region. (When non-zero, it is the sum of the #7 and #8 of the last item with a non-zero #8.)
	#     unknown_ints seem to actually contain indexes in general part of the walkable_surface_facets_connections table.
	#   - #8 see #7 -> number of walkable_surface_facets_connections for this region to connect with other connected_regions (not within the connected_region). When it is 0, then #5-6-7 are also 0.
	# - #9 can only increase or stay equal. If it increases, it's always by the #11 of the previous item
	# - #10 is always increasing from item to item, lesser than #0, and is equal to the sum of #10 and #11 of the preceding item when it has a non-zero #11 -> a start offset, the None string marks the end of a hiearchy?
	# - #11 -> a size (see #9 and #10)
	# - #12 is always 0
	connected_regions = read_list(src, lambda s: (read_string(s), read_int_array(s,13)) )
	# for i, (x,y) in enumerate(connected_regions):
	# 	print(i, '->', x, y)

	# 32 vertexes -> 2 grilles horizontales 4x4 couvrant à peu-près le monde en x-y mais pas en hauteur
	vector_list1 = read_list(src, read_vector32)
	# print(len(vector_list1), 'vectors')
	# for v in vector_list1:
	# 	print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*v))

	# 479 vertexes -> un nuage de point assez symétrique et tenant dans une sphère de rayon 3 centrée sur l'origine.
	vector_list2 = read_list(src, read_vector32)
	# print(len(vector_list2), 'vectors') 
	# for v in vector_list2:
	# 	print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*v))

	# 616 ints (see #7). Les valeurs sont soit nules, soit dans le range 180510-180694, soit dans le range 240052-240066.
	unknown_ints = read_list(src, read_int)
	# for i, (name, connected_region) in enumerate(connected_regions):
	# 	print('{:03d} ({}) ->'.format(i, name), unknown_ints[connected_region[7]:connected_region[7]+connected_region[8]])

	# 61931 vectors -> tous les points de l'île ? -> en fait, ça semble être toutes les surfaces walkable du jeu.
	# Notons aussi que les chemins de terre dans l'herbe sont matérialisés, donc cette structure peut aussi contenir des informations sur les sons des footsteps.
	# le nombre 61931 est 4 de plus que le plus grand #6 dans la première liste, sachant que ce nombre 4 est celui qui apparait comme #11 de l'item avec le plus grand #6, et que les #6 semble agir la plupart du temps comme des offsets cummulés par addition des #11, mais dans le désordre.
	walkable_surfaces_vertexes = read_list(src, read_vector32)
	# for v in walkable_surfaces_vertexes: 
	# 	print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*v))

	# walkable surfaces facets
	walkable_surfaces_facets = read_list(src, lambda s: (read_signed_int(s), read_signed_int(s), read_signed_int(s), read_int(s)))
	# assert(len(walkable_surfaces_facets) == connected_regions[-1][1][0] + connected_regions[-1][1][1]) # true
	# for i,(name,connected_region) in enumerate(connected_regions):
	# 	# list of size #1 (so #0 is the start index of this list), containing quartets of 3 ints and 1 bitmask.
	# 	# - The 3 ints are vertex indexes (or -1) and the smallest index in the list is always #10 (or -1) but the greatest can be over #10+#11.
	# 	#   Indeed, all lists have disjoint sets of indexes, and the ranges of index follow each other in the same order than the lists, with never more than 2 unused indexes inbetween.
	# 	#   Across all lists, the indexes fills up the range 0-61135, where 61135 is one less than the smallest non-zero #6 (for the item 27), and thus seem to be vertexes from the previous list.
	# 	#   -> 3 vertexes each time, these lists are facets lists for the walkable areas.
	# 	# - The bitmask are always 0x0000ffff or 0x8000ffff, except in the second region (where it can also be 0x4036FFFF and 0x4053FFFF) and the first region ('main'), which uses 256 masks (something to do with the 4x4=16 grid in the first vertex list?)
	# 	#   actually, the bitmask could be a packing of multiple integers values...
	# 	data = walkable_surfaces_facets[connected_region[0]:connected_region[0]+connected_region[1]]
	# 	# min_index, max_index = min(d[j] for d in data for j in range(3)), max(d[j] for d in data for j in range(3))
	# 	# print(i, connected_region[1], 'min={}, max={}, range={}'.format(min_index, max_index, max_index-min_index), connected_region[10]-min_index, connected_region[10]+connected_region[11]-max_index)
	# 	# for v_index in range(min_index, max_index+1): 
	# 	# 	print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*walkable_surfaces_vertexes[v_index]))
	# 	masks = tuple( (d[3]>>30, (d[3]>>16) & 0xff, (d[3]>>12) & 0xf, d[3]&0xfff) for d in data)
	# 	# masks = tuple( d[3] for d in data)
	# 	mdict = {}
	# 	for m in masks: mdict[m] = (mdict.get(m,0) + 1)
	# 	print(i, connected_region[1], 'facets with', len(set(masks)), 'masks:', ', '.join('{}:{}'.format(m,mdict[m]) for m in sorted(set(masks),key=lambda x:-mdict[x])) )
	# 	# for l in zip(*masks): print(i, len(set(l)), set(l))
	# 	# for l,m in zip(data, masks): print('  {:8d}, {:8d}, {:8d}'.format(*l), m)

	# A list of 247684 connexion data.
	# The beginning of the list is not referenced directly by the header table, but the second part is referenced by index ranges #5-#5+#8. It seems to be the connexions between areas.
	# - the first int is -1 (not available, for the boat) or an index in walkable_surfaces_facets above, in the range of the connected region considered.
	# - the second int idem, but always in another region
	# - the third int has byte 0 being the number of the region, then 13 bits forming a number, then 7 bits forming another number (the 3 last bits are always 0), then a byte for a bitmask (with the second bit always set, and the first almost always).
	# In addition, when a couple of facet indexes (a,b) appears in the list of one region, then the couple (b,a) appears in the facet of the other region, and both have the same bitmask part in the 3rd integer. Moreover, for all the couples common to both regions, the numbers in the third integer only differ by a constant number.
	# A same couple of facet indexes (a,b) can appear twice in a same region, with a same bitmask, and consecutive numbers in the third integer.
	# A same facet can be involved in more than three couples
	walkable_surface_facets_connections = read_list(src, lambda s: (read_signed_int(s), read_signed_int(s), read_int(s)))
	assert(len(walkable_surface_facets_connections) == connected_regions[-1][1][5] + connected_regions[-1][1][8])
	assert(all((a==-1) or (i//3==a) for i,(a,b,c) in enumerate(walkable_surface_facets_connections[:connected_regions[0][1][5]])))
	for connected_region, (name, table) in enumerate(connected_regions):
		print(connected_region, name)
		for a,b,c in walkable_surface_facets_connections[table[5]: table[5]+table[8]]:
			new_a = -1 if a==-1 else (a-table[0])
			if b == -1:
				new_b = -1
			else:
				region_b = 0
				while not( 0 <= (b - connected_regions[region_b][1][0]) < connected_regions[region_b][1][1] ): region_b += 1
				new_b = (b, region_b, b - connected_regions[region_b][1][0])
				# if region_b<connected_region: assert( any((x[0]==b) and (x[1]==a) and ((c>>21)==(x[2]>>21)) for x in walkable_surface_facets_connections[connected_regions[region_b][1][5]:connected_regions[region_b][1][5]+connected_regions[region_b][1][8]]) )
			print('{}, {}, {:04b}, {}, {}'.format(new_a, new_b, c>>28, (c>>21)&0xf, (c >> 8) & 0x1fff))
			assert(((c>>25) & 0x7)==0)
			assert(((c>>29) & 0x1) == 0x1)
			assert((c & 0x7f) == connected_region)
			assert(0 <= (new_a+1) <= table[1])

	# 246 structures:
	# - doorway geometry:
	#    - f0-f1-f2 if a vector that is a position in the world
	#      Visualisation of the data shows that these world positions are in the middle of the doorway_connections defined in the next section.
	#      It could thus be used as navigation data to guide the avatar through doors.
	#    - f3-f4-f5 is a normed vector but can also be None (the three coordinates are 0x7F7FFFFF). From the visualisation, I would say it's a direction to walk as we pass through the doorway.
	#      z-coordinate is almost always 0, except for the door of the shipwreck's vault and the doors of the town tower?
	#    - f6-f7 are two positive numbers. From the visualisation, I would say that it represents the height and width of the doorway.
	# - Door entity:
	#    - i8 values start at 134 and increase (by as little as 1) up to 249056=0x0003CCE0 (1372 more than the size of walkable_surface_facets_connections) in 85 items,
	#      and after that all values are 0 for the 161 other items.
	#      -> it is actually the id of a Door entity declared in save.entities.
	# - doorway_connections:
	#    - i9 seems to be an index in the 'doorway_connections' table since it takes values between 0 and 1562. The indexes are all different.
	#    - i10 is in the range 2-50, and the sum of all i10 is 1566, the size of the doorway_connections table -> number of items to take from i9 in this table.
	# - mysterious bitset and integer: i11.
	#    - 0x10 is set iff there are float values in f4-f5-f6. In that case, i11 is always 24=0x18.
	#    - Otherwise, i11 can be 0, 1, 8 or an int ending with 0x05.
	#      So 0x04 seems to be a flag that, when set, indicates that bytes 1-2-3 contain an integer (even if byte 3 is always zero).
	# 	   There are 60 such items, all packed at the end of the list, and the integers increment by either 5, 60, or 65, and all these items have the same f6 and their i8 is zero.
	#      Also, it seems to be the doors of the challenge's maze. -> it's probably the id of the maze segment where the door is, see the encoding of PressurePlate entities.
	#    - in all cases the flag 0x8 is not set, the doorway has no unitary vector and matches a door that can open or not:
	#       - flag 0x0: three grillaged doors in the marsh (entrance and the two under the structure with the red puzzles), the bamboo door of the jungle laser, the two doors of the automn forest chapel, timed door providing access to the caves from the mountain end
	#       - flag 0x1: the trap wall in the jungle, the saw mechanism in the basement tunnel of the sawmill + the walls in the challenge maze
	#       -> it seems flag 0 indicates a door that opens horizontally if not set but vertically if set?
	doorways = read_list(src, lambda s: (read_array(s,8,read_float32) + read_int_array(s,4)))
	# for x in doorways: # show positions
	# 	print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*x[:3]), 'none' if x[4]>1000 else '{:8.3f}, {:8.3f}, {:8.3f}'.format(*x[3:6]), '{:8.3f}, {:8.3f}'.format(*x[6:8]))
	# for i, x in enumerate(doorways): # show data
	# 	if x[11] & 0x4:
	# 		assert(x[11]&0xff == 0x05)
	# 		new_x11 = '{:4d}'.format(x[11] >> 8)
	# 	else:
	# 		assert(x[11]&0xffffff00 == 0)
	# 		new_x11 = ' 0x{:02X}'.format(x[11])
	# 	print(
	# 		'{:3d}'.format(i), 
	# 		' '.join('{:8.3f}'.format(y) for y in x[:3]),
	# 		' '.join('{:8.3f}'.format(y) for y in x[3:6]) if x[4]<10000 else '-------- -------- --------',
	# 		' '.join('{:8.3f}'.format(y) for y in x[6:8]),
	# 		'{:08X}'.format(x[8]), 
	# 		'{:4d} {:3d}'.format(*x[9:11]), 
	# 		new_x11
	# 	)

	# 1566 ints between 79 and 234557 -> indexes in walkable_surface_facets_connections, which is of length 247684
	# the indexes are all different, in an apparently random order, and successive indexes can be in the list at non-successive positions
	# According to a visualization of the corresponding vertexes, it seems to be doors in a broad sense of the term, whether they can actually be closed in the game or if it is just a narrow opening
	# in a wall or unwalkable obstacle. So it's probably a data structure used by the pathfinding algorithm.
	doorway_connections = read_list(src, read_int)
	# # visualizing the vertexes:
	# facets = set(walkable_surface_facets_connections[i][j] for i in doorway_connections for j in (0,1))
	# vertexes = set(v for f in facets for v in walkable_surfaces_facets[f][:3])
	# for v in vertexes: print('{:8.3f}, {:8.3f}, {:8.3f}'.format(*walkable_surfaces_vertexes[v]))

	# print(len(read_byte_array(src, -1)), 'bytes remaining.')


# Main function
# =============

if __name__ == '__main__':

	parser = theWitnessFileParserArguments('Parse a file like save_nav_data.raw')
	
	export_options = parser.add_argument_group('options for exporters', 'this program does not export anything but uses modules that implement the export API and need this')
	export_options.add_argument('--name', dest='objectname', nargs=1, action='store', default='', help='The name of the exported object (default: empty string).')
	export_options.add_argument('--texture-dir', '-td', nargs=1, dest='texture_dir', action='store', default='', help='The directory in which exporters can finf the uncompressed textures')
	export_options.add_argument('--texture-ext', '-te', nargs=1, dest='texture_ext', action='store', default='texture.png', help='The file extension added to the name of textures')

	args, filenames = parse_command_line_arguments(parser)
	if filenames[-1] is None:
		parse_TheWitness_file(read_save_nav_data, [macosx_archive, 'save_nav_data.raw'], False, args.debug)
	else:
		parse_TheWitness_file(read_save_nav_data, filenames, args.need_decompressing, args.debug)
