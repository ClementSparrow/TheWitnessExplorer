
macosx_archive = '/Users/Shared/Epic Games/TheWitness/The Witness.app/Contents/Resources/data-osx.zip'

def theWitnessFileParserArguments(program_description, default_file=None):

	'''
	This function defines a basic parser of command line arguments, to ease the access to the content of the game's assets.
	It returns a parser object with attributes:
	- _from: where the assets should be taken from. This attribute should not be used directly, and the function parse_command_line_arguments should be used instead;
	- newformat: should be true for accessing the assets directly from the game, but can be false to analyse files extracted from a previous version of the game.
	- need_decompressing: if true, the asset will be uncompressed on the fly. Some file types are not compressed.
	- debug: if true, print debug information while reading the asset.
	Specific file parsing modules can add command lines arguments with this parser object.
	'''

	import argparse

	parser = argparse.ArgumentParser(description=program_description)

	parser.add_argument('--macosx', '-M', action='append_const', dest='_from', const=macosx_archive, default=None, help='Take the file from the game\'s main archive (default: take the file from the file system)')
	parser.add_argument('_from', nargs='*', action='append', default=default_file if default_file is not None else argparse.SUPPRESS, help='The file name (default: reads from standard input).')

	parser.add_argument('--old-format', '--old', '-o', dest='newformat', action='store_false', help='Parse a file from an older version of the game')
	parser.add_argument('--uncompressed', '-u', dest='need_decompressing', action='store_false', help='Parse a file that has already been uncompressed or was never compressed')

	parser.add_argument('--debug', '-d', dest='debug', action='store_true',  help='Print debug information')
	parser.add_argument('--quiet', '-q', dest='debug', action='store_false', help='Do not print debug information')
	return parser


def parse_command_line_arguments(parser):
	'''
	This function takes a command line argument parser created with theWitnessFileParserArguments and eventually extended, and uses it to parse the argument,
	returning the value of the arguments and the path of the asset as a list of files to access.
	'''
	args = parser.parse_args()
	filenames = sum( (f if isinstance(f, list) else [f] for f in args._from), [] ) if isinstance(args._from, list) else [ args._from ]
	return (args, filenames)


def parse_TheWitness_file(parsing_function, filenames, *args, **kw_args):

	'''
	Parses an asset from The Witness using the given parsing_function (which takes an opened stream as argument),
	and the filenames and arguments provided by parse_command_line_arguments.
	'''

	import subprocess, sys

	need_decompressing = kw_args.pop('need_decompressing', False)
	if need_decompressing or (len(filenames)>1):
		cmd = (sys.executable, 'witness_lz4d_stream.py') + (tuple() if need_decompressing else ('-u',)) + tuple(filenames)
		# print(cmd, filenames, need_decompressing)
		source = subprocess.Popen(cmd, stdin=sys.stdin, stdout=subprocess.PIPE).stdout
	else:
		# print('opening directly file', filenames[-1])
		source = open(filenames[-1], 'rb')

	# print(args, kw_args)
	result = parsing_function(source, filenames[-1], *args, **kw_args)
	source.close()
	return result
