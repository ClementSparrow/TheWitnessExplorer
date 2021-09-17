# -*- coding: utf-8 -*-

if __name__ == '__main__':
	from readers import *
	from entity_readers.helpers import *
else:
	from modules.readers import *
	from modules.entity_readers.helpers import *

import math

def parse_TheWitness_animation_stream(src, filename, object_name, exporters, debug, **kwargs):

#	Header
	magic_number_15, nb_steps, nb_bones = read_int_array(src, 3)
	assert(magic_number_15 == 15) # file type?
	if debug: print('Animation has', nb_steps, 'steps and concerns', nb_bones, 'bones')

	header_matrix = tuple(read_array(src, 4, read_float32) for _ in range(4))
	if debug:
		print('header matrix:')
		print('\n'.join( ' '.join('{: 08.5f}'.format(x) for x in l) for l in header_matrix))

#	Animation
	bones = list()
	nb_bones2 = read_int(src)
	assert(nb_bones2 == nb_bones)
	for bone_index in range(nb_bones2):
		
		bone_name = read_string(src)
		bone_id = read_signed_int(src)
		# assert( ((bone_id+1) == bone_index) or (bone_id==0) ) # often true but not always. the 'bone_id' could actually be the index of the bone this one is attached too if not bone_index-1 ?
		if debug: print(bone_name, bone_id)
		
	#	Read steps for this bone
		nb_steps2 = read_int(src)
		assert(nb_steps2 == nb_steps)
		# the format is actually: a vector32 as a position, four float32 as a unitary quaternion, and a vector32 that is always all between 0.0 and 1.0.
		# The later vector seems to be most of the time three times the same value, which can be 0.1, 0.85, or 1.0, and may be a multiplication factor to apply to the mesh's joint matrices and would explain why some have strange values.
		steps = tuple( read_array(src, 10, read_float32) for _ in range(nb_steps2))
		bones.append( (bone_name, bone_id, steps) )
		if debug:
			for step in steps:
				print('  ', ', '.join('{: 3.5}'.format(x) for x in step))
				assert( math.fabs(sum(x*x for x in step[3:7]) - 1) < 0.00001 )
				assert( all( (-0.00001 <= x <= 1.00001) for x in step[7:] ))



# To call directly from command line as python modules/parse_TheWitness_animation.py ... (see modules/parse_TheWitness_files.py for options)
if __name__ == '__main__':

	from parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments

	parser = theWitnessFileParserArguments('Parse a The Witness animated mesh file to simulate an export.')
	
	export_options = parser.add_argument_group('options for exporters', 'this program does not export anything but uses modules that implement the export API and need this')
	export_options.add_argument('--name', dest='objectname', nargs=1, action='store', default='', help='The name of the exported object (default: empty string).')
	export_options.add_argument('--texture-dir', '-td', nargs=1, dest='texture_dir', action='store', default='', help='The directory in which exporters can find the uncompressed textures')
	export_options.add_argument('--texture-ext', '-te', nargs=1, dest='texture_ext', action='store', default='texture.png', help='The file extension added to the name of textures')

	args, filenames = parse_command_line_arguments(parser)
	
	# print(filenames)
	parse_TheWitness_file(parse_TheWitness_animation_stream, filenames, args.objectname, tuple(), args.debug, need_decompressing = args.need_decompressing)

