# TheWitnessExplorer
A set of python tools to explore the assets of The Witness. You can explore the game's main archive, extract textures, read various resource files, and visualize the assets in a viewer (although the viewer will be added in a later commit).

## Requirements

**Operating system:** This has curently only been tested on my mac, so it's possible that some minor edits will be needed for this to work on other systems. Just report bugs to me and I will fix them quickly!

**Python:** You will need Python3 installed on your system (3.6 and 3.9 are the versions that I have used). If you want to export textures as PNG files, you will also need to have either the OpenCV2 module installed in your python interpreter, or have an external program that can read PPM files (e.g., GIMP).

**Command line:** these are command line tools. I use Terminal on mac, but if you use Windows I have no idea what you should use.

(Not yet relevant because the viewer is not yet included here.) **Kivy:** The assets viewer uses Kivy 1.9, and while it's theoretically possible to turn it into an application, I have not tried that yet, and prefer using a kivy module installed in my python interpreter.


# The game's archive

## Structure

**Main archive:** Allmost all assets in the game are stored in a main archive file, which is an uncompressed zip file. In mac OS X this file is located in the application, following the path `The Witness.app/Contents/Resources/data-osx.zip`. In other systems, that should be something similar. Please tell me were it is so that I can add it to the code :-)

**Packages:** A few assets are stored directly in the main archive, but most are stored in packages that are themselves stored directly in the main archive. These packages have a `.pkg` extension and are also uncompressed zip files (you can extract them from the main archive, then change the extension from `.pkg` to `.zip` to extract their content).

**Additional compression:** Some assets use specific compression techniques (e.g. DTX for texture, ogg-vorbis for sound, etc.), and some files are additionally compressed with LZ4 compression.

## Extracting specific files

This project provides tools to read directly a file from the main archive using the "path" of packages it belongs to and the filename as accessors. For instance, if you want to see the content of a specific file in the archive but also want to avoid the extra steps of extracting the package it's in and then extract the file from that package and then LZ4-uncompress that file, you can use the following command that does everything in a single step (without creating temporary files):

    python3.9 witness_lz4d_stream.py {-u}? {archive path} {filename} {-f dest}?

...where `-u` is an optional flag to use when the file is actually not LZ4 compressed (default is to LZ4-decompress), and `dest` is an optional file name to which the extracted file will be stored (default is to use the standard output so that you can use it in a pipe).

There are special options to avoid giving the full path of the main archive. (Actually, currently there is only one, but please tell me where your archive is and I will add the corresponding option). So, on Mac OS X for a version of the game dowloaded from the Epic store, you can use the `-M` option instead of writing `/Users/Shared/Epic\ Games/TheWitness/The Witness.app/Contents/Resources/data-osx.zip`.

For instance, to extract the mesh file `lotus_barrier.mesh`, which is located in the package `globals_0.pkg`, and store it in a directory named `extracted_meshes`, you could do:

    python3.9 witness_lz4d_stream.py -M globals_0.pkg lotus_barrier.mesh -f extracted_meshes/lotus_barrier.mesh

## Searching for files

The main archive contains directly a text file that lists all the files in the archive (including in packages), so it can be convenient to use it to search for files with a specific term in their name (unfortunately, that will not tell you in what package they are). Since that file is not compressed you would use the `-u` flag and pipe it with a `grep` command to search for the term:

    python3.9 witness_lz4d_stream.py -u -M filelist.txt.raw | grep {searched_term}

A better alternative that can locate the module would be the command:

    python3.9 list_files.py -M | grep {searched_term}


# Export textures

Once you have located a texture file in the archive, you can extract it by using the command line tools with a syntax like:

    python3 modules/parse_TheWitness_texture.py -M Myst-ControlPanel.texture {export_filename}

The type of export is determined by the file extension in {export_filename}:

  - as PNG or anything else (requires that CV2 for python is installed in your python3 interpreter):

    python3 modules/parse_TheWitness_texture.py -M Myst-ControlPanel.texture Myst-ControlPanel.texture.png

  - as PPM (readable by GIMP, for instance; does not require any extra installed lib):

    python3 modules/parse_TheWitness_texture.py -M Myst-ControlPanel.texture Myst-ControlPanel.texture.ppm



# Analyzing meshes

I have done a mesh exporter for Blender in the past but it does not work anymore on recent versions of Blender, so I have not included that in the project. Instead, I have done my own viewer that I will soon add to the project. You can also learn about the content of a mesh file (notably the textures it uses) by running the following command (you need to use the `-d` flag to print debug information, otherwise it does not print anything):

    python3.9 modules/parse_TheWitness_mesh.py -d -M loc_hub_bld1_modtower.mesh

If you want to make your own exporter, there is a base class that you can use to make your own exporter. I let you check the code for that.

If you're interested in the file format for the meshes, I invit you to look at the code of that python file. Note that there is an option for using an old format, as the mesh file format changed (I think, when they released the iOS version of the game). So if you're using an old version of the game or files that have been extracted from an old version, think about it.



# Other files in the archive

## Lists in `.raw` files

    python3.9 read_raw_list.py {file path}

This script can be used to analyse the data provided in:
- the file `save.asset_map.raw` of the main archive (this is the default if no command line argument is provided)
- the files `save.asset_dependencies.raw` present in every `*.pkg` subarchive, which describe the content of each subarchive.

## Resources dependencies

The above command can also be used to read resource dependency files, which end with the extension `.asset_dependencies.raw`. This is still work in progress, though.

## Entities

The above command can also be used to read the file `save.entities` in the main archive, which contains all the objects the game engine has to know (and even some objects that should only be in the game's edition software). However, to analyse these objects, you should probably use instead in a python command line the code that is commented at the end of `modules/entity_readers/entities.py` as it will provide you with more tools to search for specific entities. This is still work in progress.

## World navigation files

The code in `read_save_nav_data.py` is a work in progress to analyze the file `save_nav_data.raw` in the main archive, that seems to hold the information about walkable surfaces, doors, and how to navigate the world from one point to another.


# Python API to work with files in the structure

If you want to make your own python scripts, these modules can be useful to you :

`modules.parsing_TheWitness_files` provides three useful functions:
- `theWitnessFileParserArguments` creates a command line arguments parser that supports the syntax of the `witness_lz4d_stream.py` command presented in the previous section. You can extend the parser with your own options (check the documentation of python's native module `argparse`). In addition, there is a `-d` flag to add debug information and a `-q` flag to remove debug information.
- `parse_command_line_arguments` will use that parser to actually parse the command line arguments, and return an object hosting the options set by the arguments, as well as the path of the file provided.
- `parse_TheWitness_file` will execute the provided function on the file whose path is provided, dealing with the access and decompressing of the file from the archive and packages, if needed. Of course you can also call the function on a file that you have already extracted.

`modules.access_archive` provides two functions to locate files in the archive and packages:
- `walk` is a python generator that will iterate on all the files in the archive. You use it with a syntax like `for (path, seek_position, filesize) in walk(archive_filename): ...` where:
  - `path` is the path to the file in the archive, starting with the archive's filename, ending with the file's filename, and possibly having package filenames between those two. that's what you need to pass as arguments to `witeness_lz4d_stream.py`to extract the file.
  - `seek_position` is the start position of the file in the archive. That's convenient for me but you probably don't want to use it directly.
  - `filesize` is the size of the file in bytes :-)
- `find_file_in_archive` takes a path to a file in the archive and tries to access that file, returning an open file object that can read directly that file, and the size of the file in the archive. You can then read the file directly if it not compressed (assuming you count the bytes you read in it), or use the function `uncompress_lz4d` in `witness_lz4d_stream.py` to uncompress it. But you probably don't want to do that and should use `parse_TheWitness_file` instead.
