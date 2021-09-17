
from modules.readers import *

''' Decompress a witness file (e.g., meshes or texture files). It is equivalent to the method used in to_lz4.py but written in pure Python (thus, slower) and able to read the input as a stream.'''

MAX_OUTPUT_SIZE = 1 << 24 # 16 megabytes. This is not a technical constraint, but just to avoid creating huge files when applying the program to invalid data.
# macosx_archive = '/Users/Shared/Epic Games/TheWitness/The Witness.app/Contents/Resources/data-osx.zip'

from modules.access_archive import find_file_in_archive

def uncompress_lz4d(src, dest):
	
	# skip 8 bytes in input file
	src.read(8)
	# print( read_int_array(src,2) )

	output_length = read_int(src)
	# print(output_length)
	if (output_length < 0) or (output_length > MAX_OUTPUT_SIZE):
		print("Outsize larger than max size {}; aborting. File might not be compressed.".format(MAX_OUTPUT_SIZE))
		return
	outdata = bytearray(output_length)
	
	outptr=0
	while outptr < output_length:

		b = read_byte(src)
		nb_bytes_to_copy  = (b & 0xf0) >> 4
		nb_bytes_to_recall = (b & 0x0f)

	#	Compute nb_bytes_to_copy
		b = b | 0x0f
		while b == 0xff:
			b = read_byte(src)
			nb_bytes_to_copy += b

	#	Copy bytes from src to dest
		if (nb_bytes_to_copy > 0):
			outdata[outptr:outptr+nb_bytes_to_copy] = src.read(nb_bytes_to_copy)
			outptr += nb_bytes_to_copy

		# try:
		# 	offset = read_short(src)
		# except IndexError:
		# 	break
		if outptr >= output_length:
			break
		offset = read_short(src)

	#	Compute nb_bytes_to_copy
		b = nb_bytes_to_recall | 0xf0
		while b == 0xff:
			b = read_byte(src)
			nb_bytes_to_recall += b
		nb_bytes_to_recall += 4

	#	Copy non-overlapping bytes from past dest to dest
		while nb_bytes_to_recall > 0:
			nb_nonoverlapping_bytes = min(nb_bytes_to_recall,offset)
			outdata[outptr:outptr+nb_nonoverlapping_bytes] = outdata[outptr-offset:outptr-offset+nb_nonoverlapping_bytes]
			outptr += nb_nonoverlapping_bytes
			nb_bytes_to_recall -= nb_nonoverlapping_bytes


	dest.write(outdata)


if __name__ == '__main__':

	from modules.parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments
	parser = theWitnessFileParserArguments('Extract a The Witness file.')

	# import argparse
	# parser = argparse.ArgumentParser(description='Extract a The Witness file.')
	# parser.add_argument('--macosx', '-m', action='append_const', dest='_from', const=macosx_archive, help='Take the file from the game\'s main archive (default: take the file from the file system)')
	# # parser.add_argument('--pkg',    '-p', nargs=1,   action='append', dest='_from',                       default=None, help='Take the file from the given .pkg archive inside the game\'s main archive (default: take the file from the file system)')
	# parser.add_argument('_from', nargs='*', action='append', default=argparse.SUPPRESS, help='The file name (default: reads from standard input).')
	parser.add_argument('--out', '-f', dest='_to', nargs=1, action='store')# help='The name of the file to write to (default: writes to standard output).')

	import sys
	# args = parser.parse_args()
	args, filenames = parse_command_line_arguments(parser)

	src, size  = find_file_in_archive(filenames) if filenames[-1] is not None else (sys.stdin.buffer, -1)
	# src  = find_file_in_archive(args._from) if args._from is not None else sys.stdin.buffer
	dest = open(args._to[0], 'wb') if args._to is not None else sys.stdout.buffer
	if args.need_decompressing:
		uncompress_lz4d(src, dest)
	else:
		dest.write(src.read(size))
	# print(' '.join('{:02X}'.format(b) for b in read_byte_array(src, 200)))
	src.close()
	dest.close()
