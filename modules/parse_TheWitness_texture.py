


# Basic color operations
# ----------------------

def mult_vec(vec, factor):
	(x,y,z) = vec
	return (round(x*factor), round(y*factor), round(z*factor))

def add_vecs(vec1, vec2):
	(x1,y1,z1) = vec1
	(x2,y2,z2) = vec2
	return (x1+y2, y1+y2, z1+z2)


def blend_colors(v0, v1, m_a, m_b):
	return add_vecs(mult_vec(v0, m_a), mult_vec(v1, m_b))

def unswizzle_normal(r,g,b,a):
	y = a
	z = g
	x = 128 + math.sqrt(max(0, 128*128-(z-128)**2-(y-128)**2))
	assert(b==248)
	return (x, y , z, 255)


# Color decoding
# --------------

rgb_encoding_order = (0, 1, 2) # should actually be (2,1,0) but cv2 also uses the BGR order.
components_depths = (5, 6, 5)
components_shifts = (0, components_depths[0], components_depths[0]+components_depths[1])
components_masks = tuple( ((1<<components_depth) - 1)<<components_shift for (components_depth, components_shift) in zip(components_depths, components_shifts) )
components_encoding = tuple(zip(components_masks, components_shifts, components_depths))
components_encoding = tuple( components_encoding[pos] for pos in rgb_encoding_order )

def decode_16b(v):
	components = tuple( ((v&components_mask)>>components_shift)<<(8-component_depth) for (components_mask, components_shift, component_depth) in components_encoding )
	# print('{:016b} ->'.format(v), components)
	return components

def read_rgba_pixel(src):
	return read_byte_array(src, 4)

def read_rgbt_pixel(src):
	return (read_byte(src), read_byte(src), read_byte(src), 255-read_byte(src))


# Block decoding
# --------------

from readers import *

def decode_dxt1_block(src):
	short0 = read_short(src)
	short1 = read_short(src)
	c0 = decode_16b(short0)
	c1 = decode_16b(short1)

	if short0 > short1:
		c2 = blend_colors(c0, c1, 2/3, 1/3)
		c3 = blend_colors(c0, c1, 1/3, 2/3)
	else:
		c2 = blend_colors(c0, c1, 0.5, 0.5)
		c3 = (0, 0, 0)

	# now compute the average of the 4x4 lookup table
	lookup_table = read_byte_array(src, 4) # 32bits, 4x4 array of 2bits per cell
	colors = (c0, c1, c2, c3)
	return tuple( (colors[idx&0x3], colors[(idx&0xC)>>2], colors[(idx&0x30)>>4], colors[(idx&0xC0)>>6]) for idx in lookup_table )


def decode_ati1_block(src):
	alpha0 = read_byte(src)
	alpha1 = read_byte(src)
	alphas = (alpha0, alpha1) + ( tuple( ((7-i)*alpha0 + i*alpha1)/7 for i in range(1,7) ) if alpha0 > alpha1 else ( tuple( ((5-i)*alpha0 + i*alpha1)/5 for i in range(1,5) ) + (0., 255.) ) )
	alpha_lookup_table = [ read_short(src), read_byte(src), read_short(src), read_byte(src) ]
	alpha_lookup_table[1] = (alpha_lookup_table[1]<<4) + (alpha_lookup_table[0]>>12)
	alpha_lookup_table[3] = (alpha_lookup_table[3]<<4) + (alpha_lookup_table[2]>>12)
	return tuple( (alphas[idx&0x7], alphas[(idx&0x38)>>3], alphas[(idx&0x1C0)>>6], alphas[(idx&0xE00)>>9]) for idx in alpha_lookup_table)

def decode_dxt5_block(src):
	pixels_alphas = decode_ati1_block(src)
	pixels_rgb = decode_dxt1_block(src)
	return tuple( tuple( (r,g,b,a) for ((r,g,b),a) in list(zip(*line_data)) ) for line_data in zip(pixels_rgb, pixels_alphas))

def decode_reverse_alpha_dxt5_block(src):
	pixels_alphas = decode_ati1_block(src)
	pixels_rgb = decode_dxt1_block(src)
	return tuple( tuple( (r,g,b,255-a) for ((r,g,b),a) in list(zip(*line_data)) ) for line_data in zip(pixels_rgb, pixels_alphas))

def decode_normal_dxt5_block(src):
	pixels_alphas = decode_ati1_block(src)
	pixels_rgb = decode_dxt1_block(src)
	return tuple( tuple( unswizzle_normal(r,g,b,a) for ((r,g,b),a) in list(zip(*line_data)) ) for line_data in zip(pixels_rgb, pixels_alphas))



# Image decoding
# --------------

def decode_mipmap(src, w, h, exporters, mipmap_level, plane, block_decoder):
	result = []
	for y in range(math.ceil(h/4)):
		lines = ([], [], [], [])
		for x in range(math.ceil(w/4)):
			for line, line_pixels in zip(lines, block_decoder(src)):
				line.extend(line_pixels)
		# result.extend(lines)
		for line in lines:
			del line[w:]
			result.insert(0, line)
			# print(line)
	del result[h:]
	for e in exporters: e.export_mipmap(mipmap_level, plane, result)
	return result


# Main
# ----

import math
def parse_TheWitness_texture_stream(src, texture_name, exporters, debug=False):

	w = read_short(src)
	h = read_short(src)
	if debug: print("W: {} H: {}".format(w, h))

	nb_planes, nb_mipmaps, flags = (read_short(src), read_short(src), read_int(src)) # second short seems to be the number of mipmaps levels present in the file (they all use the same compression)
	if debug: print(nb_planes, 'planes,', nb_mipmaps, 'mipmaps, flags=0x{:08X}'.format(flags) )
	header_floats = read_array(src, 4, read_float32)
	# if debug: print('mean color:', header_floats, '->', tuple(int(255*c) for c in header_floats))

	compression_type_raw = src.read(4)
	compression_type = compression_type_raw.decode("utf-8") 
	if debug: print("Compression method is '{}'".format(compression_type), tuple(int(x) for x in compression_type_raw))

	block_compressions = {'DXT1': decode_dxt1_block, 'DXT5': decode_dxt5_block, 'ATI1': decode_ati1_block }
	if compression_type in block_compressions:
		block_decoder = block_compressions[compression_type] if compression_type != 'DXT5' else ( (decode_normal_dxt5_block, decode_reverse_alpha_dxt5_block, decode_dxt5_block, decode_dxt5_block)[flags&0x3] )
		# block_decoder = decode_dxt5_block
		for plane in range(nb_planes):
			for i in range(nb_mipmaps):
				decode_mipmap(src, math.ceil(w/(1<<i)), math.ceil(h/(1<<i)), exporters, i, plane, block_decoder)
		if (flags&0x2) != 0:
			w_vignette = read_int(src)
			h_vignette = read_int(src)
			assert((w_vignette%8)==0)
			w_bits_vignette = max(w_vignette//8, 4)
			vignette_pixels = []
			for y in range(h_vignette): # todo: it's vertically reversed. The bits set to 1 correspond to the visible area.
				bytes_vignette_line = read_byte_array(src, w_bits_vignette)
				vignette_pixels.insert(0, tuple( 0 if (byte&(0x80>>bit_index)!=0) else 255 for byte in bytes_vignette_line for bit_index in range(8) ) )
			for e in exporters: e.export_vignette(vignette_pixels)

	elif compression_type in ('\x15\x00\x00\x00', '\x16\x00\x00\x00'): # TODO: what is the difference between these two?
		pixel_decoder = read_rgba_pixel if (compression_type == '\x15\x00\x00\x00') and ((flags&0x1)==0) else read_rgbt_pixel
		for plane in range(nb_planes):
			for i in range(nb_mipmaps):
				pixels = tuple( tuple( pixel_decoder(src) for x in range(math.ceil(w/(1<<i))) ) for y in range(math.ceil(h/(1<<i))) ) 
				for e in exporters: e.export_mipmap(i, plane, pixels)
	elif compression_type == '\x51\x00\x00\x00':
		for plane in range(nb_planes):
			for i in range(nb_mipmaps):
				pixels = tuple( tuple( read_short(src)>>8 for x in range(math.ceil(w/(1<<i))) ) for y in range(math.ceil(h/(1<<i))) )
				for e in exporters: e.export_mipmap(i, plane, pixels)
	elif compression_type == '\x71\x00\x00\x00':
		# cubeMap_Test_01-probe, cubeMap_Test_02-probe, cubeMap_Test_03-probe, save_10001-probe, save_10003-prob, save_10004-probe, , save_10024-envmap, save_100265-envmap, save_100288-probe, save_100289-envmap, save_100290-probe, save_10299-envmap, save_104371-probe, save_109270-probe, save_109520-probe, save_142635-probe, save_142636-probe, save_142692-probe, save_142695-probe, …, save_99081-probe. specRuins_EndRoom-probe, specRuins_RedRoom.probe
		# flags=0x8 for envmaps, 0xC for probes
		pixel_decoder = (lambda s: (read_short(s)>>8)) if (flags&0x4)!=0 else (lambda s: (255*read_float16(s)))
		# h *= 3 * 2
		# w *= 2 * 2
		h *= 6
		for plane in range(nb_planes):
			for i in range(nb_mipmaps):
				# decode_mipmap(src, math.ceil(w/(1<<i)), math.ceil(h/(1<<i)), exporters, i, plane, decode_ati1_block)
				pixels = tuple( tuple( (pixel_decoder(src), pixel_decoder(src), pixel_decoder(src), pixel_decoder(src)) for x in range(math.ceil(w/(1<<i))) ) for y in range(math.ceil(h/(1<<i))) )
				for e in exporters: e.export_mipmap(i, plane, pixels)
	else:
		raise Exception('Unkown compression method!')




def parse_TheWitness_texture_file(fn, exporters):

	with open(fn, "rb") as src:
		parse_TheWitness_texture_stream(src, fn, exporters)
		remaining_data = read_byte_array(src, -1)
		assert(len(remaining_data) == 0)
		# print(len(remaining_data), 'remaining data bytes.')





class ImageFileExporterBase(object):

	def __init__(self, base_filename, extension):
		self.base_filename = base_filename
		self.extension = extension

	def export_mipmap(self, mipmap_level, plane, pixels):
		if plane == 0:
			if mipmap_level != 0:
				return
			filename = self.base_filename if mipmap_level==0 else (self.base_filename[:-4] + ' - mipmap ' + str(mipmap_level) + self.extension)
		else:
			filename = self.base_filename[:-4] + ' - plane ' + str(plane) + ('' if mipmap_level==0 else (' - mipmap ' + str(mipmap_level))) + self.extension
		self.write_file(filename, pixels)

	def export_vignette(self, pixels):
		self.write_file(self.base_filename[:-4] + ' - vignette' + self.extension, pixels)


# worked before to export as PNG, but it requires cv2 and I don't want to reinstall it to test.
class OpenCVImageExporter(ImageFileExporterBase):

	def __init__(self, base_filename):
		super(OpenCVImageExporter, self).__init__(base_filename, '.png')

	def write_file(self, filename, pixels):
		import cv2
		import numpy
		cv2.imwrite(filename, numpy.array(pixels))

class PPMImageExporter(ImageFileExporterBase):

	def __init__(self, base_filename):
		super(PPMImageExporter, self).__init__(base_filename, '.ppm')

	def write_file(self, filename, pixels):
		with open(filename, 'w') as f:
			f.write('P3\n{} {}\n255\n'.format(len(pixels[0]), len(pixels)))
			for row in pixels:
				for pixel in row:
					f.write('{2} {1} {0}\n'.format(*pixel)) # BGR format is used but PPM uses RGB


# if __name__ == '__main__':
# 	import sys
# 	src = sys.argv[1]
# 	parse_TheWitness_texture_file(src, [OpenCVImageExporter(sys.argv[2])] if len(sys.argv) > 2 else [])


# To call directly from command line as python modules/parse_TheWitness_texture.py ... (see modules/parse_TheWitness_files.py for options)
if __name__ == '__main__':

	from parsing_TheWitness_files import theWitnessFileParserArguments, parse_TheWitness_file, parse_command_line_arguments

	parser = theWitnessFileParserArguments('Parse a The Witness texture file to simulate an export.')
	parser.add_argument('dest', nargs=1, action='store', help='The name of the file you want to export the texture to.')
	
	args, filenames = parse_command_line_arguments(parser)
	
	# print(filenames)
	extension = args.dest[0].split('.')[-1].upper()
	exporter = PPMImageExporter if extension == 'PPM' else OpenCVImageExporter
	parse_TheWitness_file(parse_TheWitness_texture_stream, filenames, (exporter(args.dest[0]),), args.debug, need_decompressing = args.need_decompressing)

