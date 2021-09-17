from modules.entity_readers.helpers import *

def read_LightProbe(f):
	'''
	Light_Probe (0x1c = 28) 01111110
	325 entities
	Node structure:
	- node_flags can be 00000000, 00000005, 00000200, 00000400, 00001000, 00008000.
	- node_string is only provided for #247 (:the_sky_probe:).
	- node_group_id is sometime provided.
	- node_ids can point to Door-152, Door-41, Door-37, and Door-219, but is most often not provided. -> opening the Door changes the light?
	- node_float is never provided (-1.0).
	- node_ints are never provided (light probes are not displayed).
	- node_final_floats is always (0.75, 0.0, 0.0, 0.0).
	'''
	return (
		read_byte_array(f, 4),			#  0: Always all 0.
		read_id(f),						#  1: Group-203, Obelisk-1-3 (town, treehouse, symmetry island),
										#     Inanimate-13-3399-4085-12946-17030 (loc_coloredLights_frontWindows, loc_quarry_lift_platform, loc_coloredLights_upperWindowsFrame, loc_coloredLights_slidingDoorNew, loc_quarryDelta_water),
										#     Multipanel-7 (fade), Machine_Panel-185-436 (symmetry_translucent_hub, symmetry_translucent5).
		read_id(f),						#  2: Marker-68 (#7), Marker-93 (#33,197,213,217,222,282), Marker-124 (#16), Marker-140 (#21), Marker-238 (#60), Marker-258 (#119), Marker-1023 (#187), Marker-1034 (#309)
		read_byte_array(f, 4),			#  3: Always all 0.
		read_byte(f),					#  4: Boolean.
		read_byte(f),					#  5: Always 0.
		read_float32(f),				#  6: 16.0 or 32.0.
		read_byte_array(f, 2),			#  7: Booleans.
		read_int(f),					#  8: 10, 16, 24, 32, 64, 128, or 256. Maybe a dimension of the probe bitmap?
		read_array(f, 5, read_float32),	#  9: 
		read_optional_string(f),		# 10: Name of a texture probe file. Rarely provided.
		read_int(f),					# 11: Always 0.
	)
