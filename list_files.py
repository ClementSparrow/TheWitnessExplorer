import sys
from modules.access_archive import walk
from modules.parsing_TheWitness_files import macosx_archive

archive = sys.argv[1]
if archive == '-M':
	archive = macosx_archive

for path,_,_ in walk(archive):
	print(' '.join(path))
