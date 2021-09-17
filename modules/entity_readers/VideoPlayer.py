from modules.entity_readers.helpers import *

def read_VideoPlayer(f):
	'''
	Video_Player (0x35 = 53) 10000001 
	1 entity: I guess, the theater.
	Node structure:
	- node_flags is 00000040.
	- node_string is not provided.
	- node_group_id is 540
	- node_ids is not provided.
	- node_float is not provided (-1.0).
	- node_ints is ([], [0]).
	- node_final_floats is 1.7943,  0.1929, -0.8953,  0.9852.
	'''
	return (
		read_byte_array(f, 5),     # 0: all 0
		read_id(f),                # 1: Machine_Panel-510 (video_main, the one to input the video codes in the theater)
		read_byte_array(f, 5),     # 2: all 0
		read_list(f, read_int),    # 3: 0x00260e1a, 0x00204c75, 0x00623438, 0x00527b6b, 0x004952c5, 0x004d869d, 0x01bfa4dc, 0x01dd9dff, 0x0516eaab, 0x028d60af, 0x00ad1944, 0x00daf10a, 0x00606e27, 0x00000000
		read_list(f, read_int),    # 4: 0x015407de, 0x015407de, 0x03799200, 0x03799200, 0x02350480, 0x02350480, 0x0b493b96, 0x0b493b98, 0x1445ffd0, 0x1445ffd0, 0x044d7130, 0x044d7130, 0x02bbbc14, 0x00000000
		read_list(f, read_int),    # 5: (48000, 48000, 48000, 48000, 48000, 48000, 44100, 44100, 48000, 48000, 48000, 48000, 48000, 0)
		read_list(f, read_int),    # 6: (    2,     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,     2, 0)
		read_array(f, 3, read_id), # 7: Audio_Marker-1150, Audio_Marker-4320, None
	)
