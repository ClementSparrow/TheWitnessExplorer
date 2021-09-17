from modules.entity_readers.helpers import *

def read_Speaker(f):
	'''
	Speaker (0x2e = 46) 01111100
	13 entities: 5 in the challenge, 3 in the theater, 4 in the jungle (the first one is not camouflaged), and one for the shipwreck puzzle.
	Node structure:
	- node_flags are 00048000 for creaky_bunker and movie_speaker, 00840000 or 00841000 for the_lotus_eaters, 00042000 for bird2*, and 40842000 for bird1.
	- node_string is always provided and defines the category of speaker: the_lotus_eaters (challenge), movie_speaker (theater), bird{1,2_{a…c}} (jungle), creaky_bunker (shipwreck puzzle).
	- node_group_id is not provided for movie_speaker, is 27 for bird2*, 334 for bird1, 544 or 558 for the_lotus_eaters, and 564 for creaky_bunker.
	- node_ids is never provided.
	- node_float is only provided for the 3 challenge speakers with node_flags=00841000, for which it has value 33.0.
	- node_ints is not provided for creaky_bunker (it's invisible, so not affected by lighting), and ([], [0]) otherwise.
	- node_final_floats are always provided, with similar values inside the categories bird1 / bird2* / movie_speaker / the_lotus_eaters / creaky_bunker.
	'''
	return (
		read_array(f, 4, read_float32), # 0: All values are strictly positive and ≤ 1.0, but it does not seem to be a color. Maybe an audio setting?
										#    First two are always equal (left and right channels?), 3rd is the double or slightly more, and the 4th is 1.0 except for some challenge speakers where it is 0.5.
		read_optional_string(f),        # 1: Name of the mesh to use for the speaker:
										#    obj_Speakers_camouflaged, loc_secret_speedrun_speaker, loc_theater_soundSpeaker, obj_Speakers_default, 
										#    or None (for creaky_bunker, a hidden speaker for the shipwreck puzzle).
	)
