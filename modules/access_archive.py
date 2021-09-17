
from modules.readers import *

# data-osx.zip is an uncompressed zip file, and the .pkg it contains are also uncompressed zip files.
# So, getting a file only requires to be able to locate it in data-osx.zip, but do not need any uncompressing.
# Also, the first file in data-osx.zip is filelist.txt.raw, which gives the list of all files at the beginning of the zip. 
# And all the .pkg are groupped together near the beginning of the file for faster access, too.


def find_file_in_archive(filenames):

	# filenames = sum( (f if isinstance(f, list) else [f] for f in filenames), [] )
	# print(filenames)
	archive_filename = filenames.pop(0)
	archive = open(archive_filename, 'rb')

	while len(filenames)>0:
		searched_filename = filenames.pop(0)
		# print('searching file', searched_filename)
		while True:
			assert( read_int(archive) == 0x04034B50 ) # look for "Local file header signature". If assertion fails, file not found in the archive
			archive.seek(14, 1) # go to compressed size field
			compressed_size = read_int(archive)
			archive.seek(4, 1) # go to name size field
			filename_length = read_short(archive)
			extra_fields_length = read_short(archive)
			if (len(searched_filename) == filename_length):
				filename = read_string_of_known_length(archive, filename_length)
				# print('at', filename)
				if searched_filename == filename:
					archive.seek(extra_fields_length, 1) # skip the extra field to get content
					break # we have found the content
				else:
					archive.seek(extra_fields_length+compressed_size, 1)
			else:
				archive.seek(extra_fields_length+compressed_size+filename_length, 1)

	return (archive, compressed_size)


def walk(archive_filename):

	'''This is a generator function that reads the archive. Do not read the archive while the function has not returned.'''

	archive = open(archive_filename, 'rb')
	path = [ archive_filename ]

	while len(path)>0:

		block_magic_word = read_int(archive)
		if block_magic_word == 0x04034B50: # "Local file header signature"
		
			archive.seek(14, 1) # go to compressed size field
			compressed_size = read_int(archive)

			archive.seek(4, 1) # go to name size field
			filename_length = read_short(archive)
			extra_fields_length = read_short(archive)
			filename = read_string_of_known_length(archive, filename_length)
			archive.seek(extra_fields_length, 1) # skip the extra field to get content of package
			if filename.endswith('.pkg'):
				path.append(filename)
			else:
				yield (tuple(path) + (filename,), archive.tell(), compressed_size)
				archive.seek(compressed_size, 1) # skip content of file

		elif block_magic_word == 0x02014b50: # "Central directory file header signature"
			archive.seek(24, 1)
			filename_length = read_short(archive)
			extra_fields_length = read_short(archive)
			comment_length = read_short(archive)
			archive.seek(12, 1) # jump to file name
			# print('central directory file:', read_string_of_known_length(archive, filename_length))
			# archive.seek(extra_fields_length + comment_length, 1)
			archive.seek(filename_length + extra_fields_length + comment_length, 1)

		elif block_magic_word == 0x06054b50: # "End of central directory signature"
			path.pop()
			archive.seek(16, 1) # jump to comment length
			comment_length = read_short(archive)
			archive.seek(comment_length, 1) # skip comment

		else:
			print('0x{:08X}'.format(block_magic_word))
			assert(False)

	archive.close()
