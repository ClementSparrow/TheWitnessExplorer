from modules.entity_readers.helpers import *

def read_VideoScreen(f):
	'''
	Video_Screen (0x37 = 55) 10000000
	3 entities: Two for the theater (one for each side), and one for end2_eyelidtest_tunnel (I guess the wake up video at the end).
	Node structure:
	- node_flags is 00840000 for the theater ones and 00040400 for the end video.
	- node_string is never provided.
	- node_group_id is 540 for theater screen, 405 for end video.
	- node_ids is never provided.
	- node_float is never provided (-1.0).
	- node_ints is always ([], [0]).
	- node_final_floats is (1.8, -0.0084, 0.0026, 0.0) for the theater ones and (21.3339, -12.9176, -0.2287, 1.2206) for the end video.
	'''
	return (
		read_optional_string(f), # "obj_panels_ScreenVideo" or "obj_panels_ScreenVideo_Flipped" or "end2_eyelidtest_tunnel"
		read_float32(f),         # 40.0 or 25.0
		read_id(f),              # node_id of the unique Video_Player.
		read_byte(f),            # Boolean: True if played in fullscreen, False if embedded?
		read_float32(f),         # always 1.0
		read_float32(f),         # always 1.0
		read_optional_string(f), # "black" or "obj_nostalghiaTest-blend" or None
	)
