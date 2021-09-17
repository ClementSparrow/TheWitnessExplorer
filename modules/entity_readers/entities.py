

from modules.entity_readers import *

def format_bytes(bytes):
	return ' '.join('{:02x}'.format(b) for b in bytes)


import math, statistics
def read_entities(f):
	
	'''Takes an openned stream. For dependency.raw, the first 4 bytes (which have value 12 as an int) should have already been read.'''

#	Read entity classes
	content_offset = read_int(f)
	nb_entity_classes = read_int(f)
	entity_classes = tuple( (read_nullterminated_string(f), read_int(f)) for _ in range(nb_entity_classes)) # name of the class and a mask (telling what fields of the node structure are used?)
	# for i, (name, mask) in enumerate(entity_classes):
	# 	print ('{:02x} : {:08b} {}'.format(i, mask, name))

	nb_nodes = read_int(f)
	# print('nb_nodes: {:08X}'.format(nb_nodes))

	nodes = tuple( list() for _ in entity_classes )
	nodes_dict = { 0: None }

#	Read nodes
	for node_iterator in range(nb_nodes):

	#	Read node structure
		try:
			node_id = read_id(f)
		except: break
		# print('node_id: {:08X}'.format(node_id))
		node_class = read_byte(f)
		node_world_position = read_vector32(f)
		node_rescale_factor = read_float32(f)
		# assert(math.fabs(node_world_position[3] - 1.0) < 0.0001) # clearly false
		node_world_orientation = read_array(f, 4, read_float32) # an unitary quaternion
		# assert(math.fabs(sum(x*x for x in node_world_orientation) - 1.0) < 0.001) # always True
		node_flags = read_int(f) # for the white flowers, bit 0x8000 is set only for the only white flower that is not displayed in the game (under the queen chair in the keep). Indeed, the four Audio_Recordings with that bit set are credits for a different system than mine.
		node_string = read_optional_string(f)
		node_group_id = read_id(f) # always the id of a node of class 0x13 - Group
		# todo: rename node_ids into node_parent
		node_ids = read_if_id(f, lambda src: (read_array(src, 8, read_float32), read_optional_string(src))) # optional string seem to be the name of a joint in the node whose id is given. The 8 floats seems to be a world or relative position, 1.0 (?), and a unitary quaternion.
		node_float = read_float32(f)
		# todo: rename node_ints into node_lighting_conditions. Actually, it seems that if this field is None, the entity will not be displayed, so maybe it's rather display_conditions?
		node_ints = None if read_int(f) == 0 else (read_list(f,read_id), read_list(f,read_int)) # first list can contain the node's id itself. It's always ids of Door or Light entities, which I guess are the entities that can affect the lighting of the entity. Second list often contains powers of 2 so I guess it's a mask list.
		# todo: rename node_final_floats into node_bounding_sphere
		node_final_floats = read_array(f, 4, read_float32) # In Notes, it is used as the radius and coordinates of the center of a bounding sphere for some positions given in the note.
		# if node_class == 0x26:
		# print('\n{:8}: node 0x{:08X}, class {:02X}: floats ='.format(node_iterator, node_id, node_class), node_world_position, node_world_orientation, node_flags, "None" if node_string is None else '"{}",'.format(node_string), 'parent={:08X}'.format(node_group_id), node_ids, node_float, node_ints, node_final_floats)

		# if (node_class == 0x24) and (len(nodes[0x24]) == 1):
		# # if node_id == 0x339b5:
		# 	print(format_bytes(read_byte_array(f, 1000)))
		# 	print(len(f.read()), 'bytes remaining.')
		# 	exit()

		# assert (node_class in (
		# 	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
		# 	0x10, 0x12, 0x13, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 
		# 	0x20, 0x21, 0x22, 0x23, 0x24, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2d, 0x2e,
		# 	0x32, 0x34, 0x35, 0x37, 0x39, 0x3b
		#))

	#	Read node content

		readers_by_nodetype = (
			read_AudioMarker, read_AudioRecording, None, read_Bridge, None, None, None, None,
			read_ColorMarker, None, read_Door, None, None, None, None, None,
			None, None, None, None, None, read_Inanimate, read_IssuedSound, read_Lake,
			None, read_Laser, None, read_Light, read_LightProbe, read_MachinePanel, read_Marker, read_MultiPanel,
			read_Note, read_Obelisk, read_ObeliskReport, read_Occluder, read_ParticleSource, None, read_PatternPoint, read_PowerCable, 
			read_PressurePlate, read_Pylon, readRadarItem, read_RecordPlayer, None, read_Slab, read_Speaker, None,
			None, None, read_TerrainGuide, None, None, read_VideoPlayer, None, read_VideoScreen,
			None, read_Waypoint_Path3, None, None,
		)
		if readers_by_nodetype[node_class] is not None:
			node_content = readers_by_nodetype[node_class](f)
		elif node_class == 0x02:
			# Boat (1 entity) 10100100
			# node_group_id is always 545
			# node_ids is always None
			# the ids in node_ints can be ids of Door entities
			node_content = (
				read_int(f), read_array(f,7,read_float32), read_byte(f), read_array(f,4,read_optional_string), read_byte_array(f,20), read_id(f), 
				read_byte_array(f,8), read_id(f), read_byte_array(f,5), read_id(f), read_id(f), read_byte_array(f,8), read_vector32(f), read_int(f),
				read_byte(f), read_float32(f), read_byte_array(f,57), read_array(f,11,read_id), read_byte(f), read_optional_string(f), read_byte_array(f,12),
				read_array(f,6,read_float32), read_byte_array(f,18), read_float32(f), read_int(f),
			)
		elif node_class == 0x04:
			# Cloud (306 entities) 01111110
			# node_ids can point to a Door or Cloud entity -> for the Black Cloud to turn white?
			# node_ints never contains node ids
			node_content = (
				read_int_array(f,2), read_optional_string(f), read_optional_string(f), read_array(f,4,read_float32), read_int_array(f,2), read_float32(f),
			)
		elif node_class == 0x05:
			# Cluster (248 entities) 01111100
			# node_ids is always None
			# node_ints never contains node ids
			# A save_{node_id}.mesh file can exist for the cluster, and it can contain a single geometry with only a colored triangle mesh that looks like (but is not identical) to some mesh of the entities listed in field 1.
			# But the file is usually empty (no mesh, no material, no physics nor joints, every byte is 0 except new unknown floats and physics bounding box)
			node_content = (
				read_list(f, read_id),	# 0: can be Audio_Recording, Bridge, Color_Marker, Door, Fog_Marker, Force_Field, Grass_Chunk, Inanimate, Light, Light_Probe, Machine_Panel, Multipanel, Note, Obelisk_Report, Occluder, Particle_Source, Power_Cable, Pressure_Plate, Pylon, Radar_Item, Record_Player, Slab, Speaker, Terrain_Guide, Video_Player, Video_Screen, Waypoint_Path3.
										#	 The list is usually of size 1 but can be very big, and fields 1 and 2 define a partition of this list.
				read_list(f, read_id),	# 1: Can be Pylon, Door, Slab, Inanimate, Machine_Panel, Multipanel
				read_list(f, read_id),	# 2: Can be the same entity types than field 1 except Pylon.
				read_list(f, read_id),	# 3: Actually always empty (maybe not a list be just 00 bytes)
				read_list(f, read_id),	# 4: Actually always empty (maybe not a list be just 00 bytes)
			)
		elif node_class == 0x06:
			# Collision_Path (276 entities) 01111101
			# node_ids can point to a Door entity -> I guess if a Door is open or closed makes a difference for collision pathes
			# node_ints never contains node ids
			node_content = (
				read_vector32(f), read_byte(f), read_short(f), read_optional_string(f), read_int(f), read_int(f), read_list(f, read_vector32),
			)
		elif node_class == 0x07:
			# Collision_Volume (4917 entities) 01111100
			# node_ids can point to an Obelisk, Boat, Cloud, Collision_Volume, Door, Record_Player, Slab, Speaker, Force_Bridge_Segment, Force_Field, Inanimate, Laser, Machine_Panel, or Multipanel entity.
			# node_ints never contains node ids
			# node_bounding_sphere usually only contains a radius but there are exceptions with a non-null position in it.
			node_content = (
				read_byte_array(f, 7),			# 0: Booleans. 6th is always 0.
				read_vector32(f),				# 1: Usually, the size of a bounding box, which diagonal length is twice the node_bounding_sphere's radius.
				read_optional_string(f),		# 2: Only provided for 8 entities, and is 'lumber_mill_metal_catwalk' for 7 (probably one for each of its seven positions?) of them and 'maze_glass_panel_brkn' for the last one.
				read_list(f, read_vector32),	# 3: Most often empty. Only non-empty when boolean field 0 is (0,1,1,0,0,0,0).
				read_optional_string(f),		# 4: Most often not provided. Can be 'bright_red': 35, 'blue': 28, 'brown2': 4, 'tree_color': 2, 'gold5': 1.
			)
		# elif node_class == 0x09: # Combined_Mesh (0 entities) 01111100
		elif node_class == 0x0b:
			# Double_Ramp (1 entity) 01111100 -- The set of two exclusive ramps in the Concrete Factory
			# node_group_id is always 184
			# node_ids is pointing to a Door entity
			# node_ints never contains node ids
			node_content = (
				read_optional_string(f), read_id(f), read_id(f), read_int(f), read_array(f,4,read_float32), read_int(f), read_array(f,7,read_id),
			)
		elif node_class == 0x0c:
			# Fog_Marker (31 entities) 10000001
			# node_ids is always None
			# node_ints never contains node ids
			node_content = (
				read_array(f,10,read_float32), read_byte_array(f,7), read_vector32(f),
			)
		elif node_class == 0x0d:
			# Force_Bridge 01111101
			# 3 entities: the three in the mountain interior
			# node_group_id is always 711
			# node_ids is always None
			# node_ints never contains node ids
			node_content = (
				read_id(f), read_array(f,9,read_vector32), read_list(f,read_id), read_list(f,read_id), read_list(f,read_id), read_id(f), read_id(f),
				read_id(f),
			)
		elif node_class == 0x0e:
			# Force_Bridge_Segment 01111100
			# 516 entities: I guess one for each possible segment of the grid
			# node_group_id is always None
			# node_ids always point to a Force_Bridge entity, obviously the one to which the segments belongs to
			# node_ints never contains node ids
			node_content = (
				read_int_array(f,2), read_array(f, 4, read_float32), read_int_array(f,5),
			)
		elif node_class == 0x0f:
			# Force_Field 10000011
			# 1 entity: I guess, the Entry Yard fence
			# node_group_id is always None
			# node_ids point to a Door entity, I guess the one of the hotel?
			# node_ints never contains node ids
			node_content = (
				read_array(f,9,read_float32), read_array(f,3,read_id), read_array(f,14,read_float32),
			)
		elif node_class == 0x10:
			# Gauge (16 entities) 10000000
			# node_ids can point to a Laser, Machine_Panel, or Pylon entity -> Gauges are counters that check that some minimal number of things are done?
			# -> 1 of 2 machine panels for the Keep Laser, 3 of 3 solutions for the Hub's 3-in-1 panel, at least 7 lasers to activate the pylon?
			# node_ints never contains node ids
			# Gauge-0 counts the number of puzzles solved in the top set of the desert ruins' +1 floor to activate the final puzzle of the floor.
			# Gauge-2 is for the desert ruin -1 floor: lights or floor panel?
			# Gauge-3 counts the number of puzzle sets that have been completed in the top floor of the mountain to open the door.
			# Gauge-4 counts the number of pillar rows that have been completed to activate the flying elevator.
			# Gauge-6 seems to count the number of puzzles solved in the row with the disapearing yellow line in symmetry island, probably to control the line transparency?
			# Gauge-8 counts the number of small puzzles solved in the giant floor puzzle of the mountain.
			# Gauge-9 counts the number of different solutions entered in the triple puzzle in the hub building near the docks.
			# Gauge-10 counts the number of access puzzle solved in the sawmill to activate the ramp. -> no, it seems to be counting the number of sides opened in the Quarry laser puzzle.
			# Gauge-11 seems to be related to the force field in the starting area.
			# Gauge-12 to the combo puzzle set in the mountain where constraints accumulate on all puzzles of the row.
			node_content = (
				read_id(f),						# 00: an entity affected by the value of the gauge?
				read_int(f),					# 01: the max value for the gauge?
				read_array(f, 4, read_float32),	# 02: ?
				read_short(f),					# 03: ?
				read_list(f, read_float32),		# 04: ?
				read_list(f, read_float32), 	# 05: ?
				read_optional_string(f),		# 06: ?
				read_byte_array(f, 2),			# 07: ?
				read_optional_string(f),		# 08: ?
				read_optional_string(f),		# 09: ?
				read_id(f),						# 10: ?
			)
		# elif node_class == 0x11: # Grass (0 entities) 10001000
		elif node_class == 0x12:
			# Grass_Chunk (2067 entities) 01111101
			# node_group_id is always None
			# node_ids is always None
			# the ids in node_ints can be ids of Door entities, or ids of Doors and Light entities
			# all Grass_Chunk entities have a list of ints in node_ints.
			node_content = ( 
				read_optional_string(f),			# 0: Always provided. Name of a texture for an alpha test.
				read_array(f, 8, read_float32),		# 1: Always in the range 0.0-1.0 -> two RGBA colors?
				read_int(f),						# 2: 0 (most of the time) or 1 (40 entities)
				read_int(f),						# 3: 0 (most of the time) or 1 (52 entities)
				read_short(f),						# 4: 
				read_short(f),						# 5: 0, 1, 2, or 3.
			)
		elif node_class == 0x13:
			# Group (741 entities) 01111100
			# node_string is almost always provided and unique, but None and duplicates can happen.
			# node_ids is always None
			# node_ints never contains node ids
			# node_final_floats is always (1.0, 0.0, 0.0, 0.0).
			node_content = (
				read_vector32(f),		# 0: Most of the time, (0.0, 1.0, 0.0). Coordinates are always in the range 0.0-1.0 => a color?
				read_float32(f),		# 1: Most of the time, 1.0 (for 735 Groups). 0.0 for 3 Groups, and 15.0, 0.02656245231628418, or 50.0 for one Group each.
				read_byte_array(f,4),	# 2: Always 0.
				read_byte_array(f,2),	# 3: booleans. Most often 0.
				read_byte(f),			# 4: Always 0.
				read_short(f),			# 5: Seems to actually be two independent bytes.
				read_float32(f),		# 6: Almost always 2.0. Between 0.0012825352605432272 and 8.0.
			)
		# elif node_class == 0x14: # Human (0 entities) 10000011
		elif node_class == 0x18:
			# Landing_Signal (0x18 = 24) 01111111
			# 6 entities: the six docks.
			# node_rescale_factor is always 1.0, node_flags is always 0x00048000, node_string is never provided, node_float is always -1.0, node_final_floats is always (2.9484095573425293, 0.0, -0.029403358697891235, 2.6444754600524902)
			# node_ids is always None
			# node_ints never contains node ids
			node_content = (
				read_short(f),					# 01: Always 0
				read_array(f,3,read_int),		# 02: Seems to be of the form 1000x+y, where x and y are both bitsets?
				read_array(f,2,read_id),		# 03: Two Marker entities,
				read_id(f),						# 04: A Door that has a buoy mesh, 
				read_id(f), 					# 05: A Waypoint_Path3 (consecutive ones: 211770 to 211775). Maybe the corresponding start circle in the boat path puzzle?
				read_byte(f),					# 06: Always 1
				read_vector32(f),				# 07: A world position close to the entity's world position (can be around 3m away), but not the position of any of the precedeing entities -> position of the calling puzzle?
				read_array(f,4,read_float32),	# 08: Always all 0.0 except for Door-Entity 5319 (Landing_Signal-1, the one in the marsh) where it is (1.0, 1.0, 0.0)
				read_short(f),					# 09: Always all 0.
				read_int(f),					# 10: Similar values as in field 02.
				read_int(f),					# 11: Seems to be actually four bytes defining an rgba color?
				read_float32(f),				# 12: idem
				read_byte_array(f, 6),			# 13: First four bytes and last four bytes are always 0. It could be an int followed by a null short, or a null short followed by a float32
			)
		# elif node_class == 0x1a: # Laser_Beam (0 entities) 01111101
		# elif node_class == 0x25: # Pathfind_Magnet (0 entities) 01111111
		# elif node_class == 0x2c: # Rumble (0 entities) 01111100
		# elif node_class == 0x2f: # Switch (0 entities) 01111100
		# elif node_class == 0x30: # Terrain (0 entities) 01111100
		# elif node_class == 0x31: # Terrain_Discontinuity (0 entities) 01111100
		# elif node_class == 0x33: # Terrain_Hole (0 entities) 01111100
		elif node_class == 0x34:
			# Touch_Collision (549 entities) 10001101
			# From their positions in the world, it seems to be invisible walls (and maybe some are related to puzzle panels?)
			# node_flags is always 0x00040000.
			# node_string is never provided.
			# node_ids can point to a Door or Machine_Panel entity but is only provided for 17 entities.
			# node_float is always -1.0.
			# node_ints never contains node ids.
			# node_final_floats usually only contains a radius and has a null vector, expect for 3 entities: 261199, 261230, and 261197.
			node_content = (
				read_vector32(f),		# 0: The dimensions of a bounding box that fits perfectly in the sphere defined by node_final_floats.
										#    x in range 0.05-10.0, most values below 1.0
										#    y in range 0.1-23.415, most values above 1.0
										#    z in range 0.05 - 27.931, most values above 1.0
				read_id(f),				# 1: None, Marker, or Machine_Panel.
				read_byte_array(f, 7),	# 2: Booleans.
				read_float32(f),		# 3: A value in the range [0.0, 40.0]. Maybe a height?
				read_float32(f),		# 4: -1.0 or a positive value smaller than 1.0 (0.0, 0.2, 0.5, or 0.55).
				read_id(f),				# 5: None or Door. Never defined when a node_ids is provided.
				read_byte_array(f, 5)	# 6: Booleans. 1st is always 0. 
			)
			# assert(all(b in (0,1) for b in node_content[2])) # Verified to always hold
		# elif node_class == 0x36: # Video_Recording (0 entities) 01111100
		# elif node_class == 0x38: # Walk_Manifold_Marker (0 entities) 01111100
		# elif node_class == 0x3a: # Window (0 entities) 01111100
		elif node_class == 0x3b:
			# World (1 entity) 01111100
			# node_group_id is None
			# node_ids is None
			# node_ints does not contain node ids
			node_content = (
				read_float32(f),	# -37.4
				read_float32(f),	# 18.9
				read_int(f),		# 0
				read_float32(f),	# -11.0
				read_float32(f),	# 78.0
				read_int(f), 		# 22
			)
		# Notes on readers:
		# - Marker, Multipanel, Machine_Panel, Obelisk, Particle_Source, and Radar_Item all end with what could be two boolean bytes and a float.
		# - Occluder, Marker, Audio_Marker, Touch_Collision, and Slab all start with a vector that is related to the node_final_floats.

	#	Register node
		# assert(node_id not in nodes_dict) # Verified to always hold
		nodes_dict[node_id] = (node_class, len(nodes[node_class]))
		nodes[node_class].append( (
			node_id,
			node_world_position,
			node_rescale_factor,
			node_world_orientation,
			node_flags,
			node_string,
			node_group_id,
			node_ids,
			node_float,
			node_ints,
			node_final_floats,
			node_content
		) )

	return (
		tuple(n for n,_ in entity_classes),
		dict((n,(i,c)) for i,(n,c) in enumerate(entity_classes)),
		nodes,
		nodes_dict
	)




	def get_id(i):
		if i==0: return (None, None)
		result = nodes_dict.get(i, None)
		return ('UnkownNode', i) if result is None else (entity_classes[result[0]][0], result[1])

	def format_id(i):
		if i==0: return 'None'
		return '{}-{:d}'.format(*get_id(i))

	def get_node_by_id(i):
		if i==0: return None
		c,j = nodes_dict.get(i, (None,i))
		return nodes[c][j] if c is not None else None

	def format_bool(i): return ('x' if i else '_')
	def format_boolset(s): return ''.join(format_bool(b) for b in s)

	def find_closest_panel(position):
		result = min(nodes[29], key = lambda n: sum((b-a)**2 for (a,b) in zip(position, n[1][:3])) )
		return (result[-1][0], result[1], math.sqrt(sum((b-a)**2 for (a,b) in zip(position, result[1][:3])))) # name, position, distance

	# print(len(nodes_dict), 'nodes')
	investigated_class = 0
	# for j, p in enumerate(nodes[investigated_class]):
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: (q[1][3])): # sort by flags.
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][4] if q[1][4] is not None else ''): # sort by node_string.
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: (-1 if q[1][5]==0 else nodes_dict[q[1][5]][1])): # sort by group_id
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][6][0] if q[1][6] is not None else 0): # by node_ids
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][7]): # by node_float
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][8] if q[1][8] is not None else tuple()): # by node_ints
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: (q[1][-2][0])): # by node_final_floats radius
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: (sum(x*x for x in q[1][-2][1:]))): # by node_final_floats norm
	for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][-1][-1]): # by some field
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: q[1][-1][9] if q[1][-1][9] is not None else ''): # by some optional string
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: (q[1][-1][17], q[1][-1][2] if q[1][-1][2] is not None else '')): # by some field then some optional string
	# for j, p in sorted(enumerate(nodes[investigated_class]), key=lambda q: get_node_by_id(q[1][-1][15])[-1][0]): # by some node_id field
		# if p[-1][1] != 3: continue
		# if p[-1][15] is None: continue
		# if all(b == 0 for b in p[-1][16][:2]): continue
		print(
			'{:4d}:'.format(j), # index
			# ''.join('{:02x}'.format(math.floor(f*255)) for f in p[-1][6]), # color in hexadecimal representation
			# '{: 9.4f}'.format(p[-1][11]), # float
			# '-'.join( ''.join('{:02x}'.format(math.floor(f*255))  for f in l) for l in (p[-1][17][2:6],p[-1][17][6:10],p[-1][17][10:14],p[-1][17][14:18])), # color in hexadecimal representation
			# ''.join('{:02x}'.format(math.floor(f*255)) for f in p[-1][5]), # a color in hexadecimal representation
			# ', '.join('{: 9.4f}'.format(f) for f in p[-1][14]), # vector or float array
			# ' '.join('{:02X}{:02X}{:02X}-{:02X}'.format(*tuple(math.floor(255*x) for x in f)) for f in p[-1][2]), # color list
			# ', '.join('{: 8.4f}'.format(f) for f in p[-1][7]), # vector or float array
			# ' '.join(', '.join('{: 8.4f}'.format(f) for f in v) for v in p[-1][5]), # vector array
			# '{: 9.4f}'.format(p[-1][5]), # float
			# '{:032b}'.format(p[2]), # flags
			# '{:08x}'.format(p[-1][0]),
			# p[-1][4],
			# '{:3d}'.format(len(p[-1][5])),
			# format_boolset(p[-1][10]), # booleans
			# format_bool(p[-1][13]),
			# format_bytes(p[-1][0]), # bytes
			# get_node_by_id(p[-1][4][0])[-1][0],
			# ', '.join(format_id(f) for f in p[-1][9]), # node_id list
			# ', '.join(get_node_by_id(f)[-1][0] for f in p[-1][4]), # node_id list
			# format_id(p[-1][3]),
			# ', '.join('({: 9.3f} {: 9.3f} {: 9.3f})'.format(*v) for v in p[-1][3]), # vector list
			# p[-1][4],
			# tuple( (max(x)+min(x))/2 for x in zip(*(p[-1][5])) ),
			# '|',
			# ','.join( '{: 9.3f}'.format(min(x)) for x in zip(*(p[-1][5])) ),
			p[-1][2],
			# format_id(p[-1][3]),
			# p[-1][-1],
			# '|',
			', '.join('{: 7.2f}'.format(f) for f in p[1][:3]), # node_world_position
			# '{:08x}'.format(p[3]), # node_flags
			# # '{: 5.1f}'.format(p[7]), # node_float
			# format_id(p[5]), # node_group_id
			# # '{: 8.4f}'.format( math.sqrt(sum( f*f for f in p[-1][0]))/2), # radius node_final_floats
			# ', '.join('{: 7.4f}'.format(f)for f in p[-2]), # node_final_floats
			# # '{: 8.4f}'.format(p[-2][0]), # radius in node_final_floats
			# None if p[6] is None else (format_id(p[6][0]), ', '.join('{: 7.2f}'.format(f) for f in p[6][1][0]), p[6][1][1]), # node_ids
			# # (', '.join(format_id(k) for k in p[8][0]), '-'.join('{:b}'.format(k) for k in p[8][1])) if p[8] is not None else None, # node_ints
			# p[4], # node_string
			'{0} at {2:.2f}'.format(*find_closest_panel(p[1][:3])),
		)
		# assert( p[-1][6] is not None )
		# assert( all( (math.fabs(f)<.0001) for f in p[-1][7][:1]) )
		# assert(p[-1][3] == 0)
		# assert(p[-1][0] is not None)
		# assert(all(math.fabs(x-y) < 0.001 for x,y in zip(p[-2][1:], (0.0,0.0,0.0))))
		# assert(all(b in (0,1) for b in p[-1][-9]))
		# assert(all(b==0 for b in p[-1][0]))
		# assert(p[-1][6] in nodes_dict)
		# assert(all((x in nodes_dict) for x in p[-1][7]))
		# assert(all(0. <= x <= 1.0 for x in p[-1][12]))
	# print(', '.join(sorted(set('{:08x}'.format(p[3]) for p in nodes[investigated_class])))) # node flags
	# print(', '.join(sorted(set(p[4] for p in nodes[investigated_class] if p[4] is not None)))) # node_strings
	# print(', '.join(sorted(set(p[-1][3] for p in nodes[investigated_class] if p[-1][3] is not None)))) # other optional strings
	# print(', '.join(entity_classes[c][0] if c>=0 else 'Unknown' for c in sorted(set(nodes_dict.get(p[-1][28], (-1,))[0] for p in nodes[investigated_class] if p[-1][28] != 0)))) # node_id classes
	# print( tuple(tuple(f(x) for x in zip(*tuple(p[-1][14] for p in nodes[investigated_class])))  for f in (min,max,statistics.mean) ) ) # bounding box
	# print(nodes[10][229]) # Door
	# print(nodes[21][17734][-1][6]) # Inanimate
	# print(nodes[29][16][-1][0]) # Machine_Panel
	# print(' '.join(nodes[29][n][-1][0] for n in (592,107,161,139))) # Machine_Panels
	# print(nodes[23][13]) # Lake
	# print(nodes[23][20]) # Lake
	# print(get_node_by_id(nodes[31][7][-1][4][0]))


	# 		# ', '.join(format_id(k) for k in p[-1][0]),
	# 		# p[-1][20],
	# 		# ' '.join('{: 9.4f}'.format(f) for f in p[-1][13]),
	# 		# '{:02d}-{:02d}'.format(*p[-1][6]),
	# 		# format_id(p[-1][1]),
	# 		# p[-1][10],
	# 		p[4],
	# 		# ' '.join('{: 9.4f}'.format(f) for f in p[1]),
	# 	)
	# print(set(get_id(p[-1][1])[0] for p in nodes[0x26]))
	# print(', '.join(sorted(set(p[-1][-5] for p in nodes[0x26] if p[-1][-5] is not None))))

	for i,l in enumerate(nodes):
		print(i, len(l))
	# 	for n in l:
	# 		if (n[7] is not None) and (len(n[7][1])>0):
	# 			print (format_id(n[0]), n[7][1] )


def parse_TheWitness_entities_stream(f, filename, **kwdict):
	assert(read_int(f) == 12)
	return read_entities(f)


# Things to paste in a python interactive shell to analyse data:

# from modules.entity_readers.entities import parse_TheWitness_entities_stream
# from modules.parsing_TheWitness_files import macosx_archive, parse_TheWitness_file
# (entity_classes_names, entity_classes_infos, nodes, nodes_dict) = parse_TheWitness_file(parse_TheWitness_entities_stream, [macosx_archive, 'save.entities'], newformat=True, need_decompressing=True)

# def node(node_id):
#    c,j = nodes_dict[node_id]
#    return nodes[c][j]

# def node_info(n):
#   print('Entity data:')
#   for field_name, field_format, field_value in zip(('uid', 'position', 'scale', 'orientation', 'flags', 'name', 'group_uid', 'relative to joint', 'float', 'lighting states', 'bounding sphere:'), ('{}', '{}', '{}', '{}', '{:08X}', '{}', '{}', '{}', '{}', '{}', '{}', ), n[:-1]):
#     print(' ', (field_name+': '+field_format).format(field_value))
#   print('Entity Content:')
#   for field_number, field_value in enumerate(n[-1]):
#     print(' {:02}: {}'.format(field_number, field_value))

# def i(node_id):
#   node_class, node_index = nodes_dict[node_id]
#   print('Entity', node_id, 'is {}-{}'.format(entity_classes_names[node_class], node_index))
#   n = nodes[node_class][node_index]
#   node_info(n)

# def find_entity_by_mesh(mesh_name):
#    return tuple(n[0] for n in nodes[entity_classes_infos['Inanimate'][0]] if n[-1][6] == mesh_name)

# def locate_entity(min_x, max_x, min_y, max_y, entity_type=None):
#   return tuple( node[0] for node in (nodes[entity_type] if entity_type is not None else (n for c in nodes for n in c)) if (min_x <= node[1][0] <= max_x) and (min_y <= node[1][1] <= max_y) )
