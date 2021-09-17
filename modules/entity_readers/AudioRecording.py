from modules.entity_readers.helpers import *

def read_AudioRecording(f):
	'''
	Audio_Recording (0x01 = 1) 10000100
	62 entities
	Node structure:
	- node_flags can be 00040000, 00040040 (non-platform-specific credits and brooke), 00048040 (platform-specific credits and testing), 00240040, 00240060, 00840000, 00a40040.
	- node_string is never provided.
	- node_group_id is often set but not always.
	- node_ids is provided only for the hotel audio logs (and all of them), placing them relatively to:
	  Door-37 (airport: testing, voicework, and platform-specific credits), Door-152 (hotel loby: tagore_end, core_team, audio, architecture), or Door-41 (additional and thanks).
	- node_float is never provided (-1.0).
	- node_ints is always ([], [0]) -> they are not affected by changes in lighting conditions?
	- node_final_flags is always (0.0710, -0.0046, -0.0000, 0.0095), because they all have the same size, and thus the same bounding sphere?
	'''
	return (
		read_optional_string(f),		#  0: name of the audio log, to locate sound file and subtitle files
		read_byte(f),					#  1: Boolean: 1 for the cave audio logs that have an orange flower, 0 for all others
										#	  (note: from this field up to the beginning of field 7, the structure is compatible with the fields ather the first three of an Inanimate entity)
		read_float32(f),				#  2: Always 1.0

		read_byte_array(f,6),			#  3: Always all 0

		read_optional_string(f),		#  4: Always None except for cusa_impossible, zen_physics_intellectual_catastrophe, and skinner_reciprocal, where it is "obj_audioPlayer_01". -> mesh file.
		read_byte(f),					#  5: Seems to be some flags?
										#     - LSB is always set when there is a non-white color in the next field.
										#     - Other bits can be set for credits logs, brooke, and skinner_reciprocal, but are 0 for all other logs.
		read_vector32(f),				#  6: Color of the plastic case. Non-white are:
										# 		#040100 credits_additional
										# 		#212121 tagore_boast
										# 		#585858 einstein_cosmic_religious_feeling
										# 		#d05507 eddington_generation_of_waves
										# 		#d05507 ryonen_autumn
										# 		#e24c00 feynman_uncertainty_of_science
										# 		#ff5316 arabi_veils
										# 		#ff5316 niffari_sea
										# 		#ff6a2c tagore_voyage

		read_array(f,7,read_float32),	#  7: Some floats:
										#     - 2nd and 3rd are always (0.8, 0.8) except for sandwich where it's (0.0, 1.0) and einstein_cosmic_religious_feeling where 3rd is 0.22317881882190704,
										#     - 4th is always 0.0 except for sandwich where it's 0.7730859518051147.
										#     - 5th is always 1.0,
										#       -> 2-3-4-5 could be a RGBA color in the range [0.0-1.0], usually yellow-orange.
										#          Might be the color of the recorder's light? No, it's usually yellow-green, and the exceptions (baby blue for authenticity and sandwich, and
										#          orange for einstein_cosmic_religious_feeling) do not match.
										#     - 6th is usually 32.0 except for some cave audiologs: authenticity, conference, dirac and dreams (all in Group-147), for which it is 0.8, and sandwich (2.0)
										#       -> reverb?
										#       Note: we have something similar at the end of field 17 of Patter_Point entities, also after a color.
										#     - 7th is 8.0 or 5.0 except for einstein_mystical where it's 5.6 and sandwich where it's 3.0.

	#	For the lake
		read_byte(f),					#  8: Boolean: 1 for the hotel audiologs (credits and tagore_end), 0 for the others -> those with value 1 do not have a flower on the lake.
		read_id(f),						#  9: Only provided for augustine_silence (Marker-398), einstein_library (Marker-392), feynman_atoms_with_curiosity (Marker-642), schweickart_eva (Marker-819).
										#     -> The coordinates of these markers are very close to the position of the corresponding audio log. Since augustine_silence and feynman_atoms_with_curiosity
										#        are next to each other and their flowers on the lake would be confounded, and schweickart_eva is too close to the statue and einstein_library too close to
										#        the obelisk, these markers are probably used to shift the flowers a little bit on the lake.
										#     -> Probably the position to take for the automatic placement of these audio log flowers on the lake.
		read_id(f),						# 10: Only provided for chuang_tzu_boat, for which it is Marker-714.
										#     -> According to the position of this marker, it may be the position of the lotus flower in the lake corresponding to this audio log, which is near the cascade.
										#        So, it's the opposite of the previous field. Here, we bypass the automatic placement of the flowers and position the flower manually.
		read_byte(f),					# 11: Size of the lily leaves around the flower: 0 for small, 1 for medium, or 2 for big.
	)
