from modules.entity_readers.helpers import *

def read_ParticleSource(f):
	'''
	Particle_Source (0x24 = 36) 10001111
	191 entities: 11 for the laser beams, 135 for the EPs, and 45 remaining… including water splashes, force fields, falling leaves, etc?
	node structure:
	- node_ids can point to a Door, Machine_Panel, Radar_Item or Inanimate entity
	- node_flags can be 00000011 or 00000010 for 'final_particles', 00000016 for 'env_particles', 00000018 for 'particles', 0000001c for 'foam_particles', 00008010 for 'final_particles' (which points to and are listed in Radar_Items) and 'Particle-Spark'.
	- node_string is never provided.
	- node_ints is never provided.
	- node_float is never provided (-1.0).
	- group_id can be 28, 55, 112, 335 or None.
	'''
	return (
		read_byte_array(f, 3),				#  0: Can be:
											#     - 30 60 00 for 'final_particles' with node_flags 00008010.
											#     - 30 00 00 for 'env_particles', 'Particle-Spark', and 'final_particles' with node_flags 00000010 or 00000011.
											#     - 20 81 03 for 'foam_particles' and 'particles'.
											#     -> 4th bit of node_flags tells if third byte is non-null?
											#     -> bytes 2 and 3 could actually be a short.
		read_byte(f),						#  1: Boolean. Always set, except for Particle_Source-186 (Particle-Spark).
		read_optional_string(f),			#  2: Always set. Usually 'final_particles', but can also be:
											#     - 'env_particles' (#178), for which node_ids point to Door-68 ('the_sun').
											#     - 'particles' (#35),
											#     - 'Particle-Spark' (#186), for which node_ids point to Machine_Panel-164 (spec_glass_panel_blank in town, I think it is the mirror).
											#     - 'foam_particles' (#3,7,162,163,166).
		read_optional_string(f),			#  3: Always None except for Particle_Source-178 which has value 'particles' (and is the only one to have 'env_particles' to the previous field)
		read_array(f, 4, read_float32),		#  4: Always 0.0, 1/3, 2/3 or 1.0. Could be colors?
		read_array(f, 35, read_float32),	#  5: Unknown parameters for the particles.
											#  6: four RGBA color vectors (range 0.0-1.0). Probably the colors of the particles.
		read_array(f, 4, lambda src: read_array(src,4,read_float32)), 
		read_float32(f),					#  7: 0.5 (always for Particle-Spark, foam_particles, env_particles and particles) or 0.6 or 0.75 (always for final_particles with node_flags 00008010 or 00000011).

		read_byte_array(f, 20),				#  8: Always all 0.
		
		read_byte(f),						#  9: Boolean. Only set for #107, for most of the final_particles with a string in field 8, env_particles (#178), Particle-Spark (#186), and all final_particles with node_flags 00008010.
		read_byte(f),						# 10: Boolean. Only set for final_particles (except #107)
		read_optional_string(f),			# 11: Only set for some 'final_particles' with node_flags 00000010 or 00000011:
											#     - boat: #113 (boat_drain) #110 (boat_spawn), #17 (boat_drips), #13-16 (boat_splash),
											#     - lake fountains: #38-39-45-49-51-53-58 (ob_fount_atlas_big), #25-29-30 (ob_fount_atlas_small),
											#     - end elevator rising out of water: #31 (end1_splash), #16 (end1_rocks)
		read_if(f, read_vector32),			# 12: Given only for env_particles (#178), final_particles with node_flags 00000011 and a second string, and final_particles with node_flags 00000010 and no second string.
		read_byte(f),						# 13: Always 1.
		read_byte(f),						# 14: 1 or 2 for final_particles, 1 for Particle-Spark and env_particles, 0 for foam_particles and particles.
		read_float32(f),					# 15: Always 0.0 except for some final_particles with node_flags 00000010 where it is -1.0.
		read_if(f, read_float32),			# 16: Only set for Particle-Spark with value 12.0
		read_byte(f),						# 17: Boolean. Only set for foam_particles, env_particles, and particles.
		read_byte(f),						# 18: Boolean. Only set for some of the Particle_Sources that have -1.0 in field 12.
		read_float32(f),					# 19: 50.0 for Particle-Spark, 65.0 for final_particles with node_flags 00008010, 80.0 for foam_particles and particles, 896.0 for env_particles, various values for others.
		read_float32(f), 					# 20: Usually 20.0, but 127.0 for env_particles, and can also be 3.0, 5.0 or 15.0 for some final_particles with node_flags 00000010.
		read_byte(f),						# 21: Boolean. Only set for env_particles and some final_particles with node_flags 00000010.
		read_byte_array(f, 3),				# 22: Always all 0. Might form an integer with the previous boolean.
		read_byte(f),						# 23: Boolean. Only set for some final_particles with node_flags 00000010.
		read_float32(f),					# 24: -999.0 most of the time but can take other negative or null values for some final_particles with node_flags 00000010.

		read_byte_array(f, 44),				# 25: Always all 0.
	)
