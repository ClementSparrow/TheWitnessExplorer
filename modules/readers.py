
# Readers for basic types
#========================


def read_byte(src):
	bytes = src.read(1)
	# print(bytes)
	return bytes[0]


# --- Integers ---

def read_int(src):
	return read_byte(src) + (read_byte(src) << 8) + (read_byte(src) << 16) + (read_byte(src) << 24)

def read_short(src):
	return read_byte(src) + (read_byte(src) << 8)


# --- Floats ---

import struct
def read_float32(src):
	return struct.unpack('<f', src.read(4))[0]

# import numpy as np
# def make_float16(low_byte, high_byte):
# 	return np.frombuffer((low_byte, high_byte), dtype=np.float16)[0]

from math import inf, nan
def make_float16(low_byte, high_byte):
	sign = high_byte & 0x80
	exp = ((high_byte & 0x7C)>>2)
	mantissa = ((high_byte&0x03)<<10) | (low_byte<<2)
	if exp == 0:
		hexstring = ('-0.' if sign else '+0.') + '{:03x}'.format(mantissa) + 'p-14'
	elif exp != 31:
		hexstring = ('-1.' if sign else '+1.') + '{:03x}'.format(mantissa) + 'p' + str(exp - 15)
	else:
		return (-inf if sign else inf) if mantissa == 0 else nan
	result = float.fromhex( hexstring )
	# print('{:02x}{:02x} -> {} -> {:f}'.format(r[1],r[0],hexstring,result))
	return result

def read_float16(src):
	r = src.read(2)
	result = make_float16(r[0], r[1])
	# print('read float16 0x{:02X}{:02X} -> {}'.format(r[1], r[0], result))
	return result

def short_as_fixed_point(r):
	if ((r & 0x8000) != 0):
		return float(r - 0x10000) / 0x8000
	return float(r) / 0x7fff

def short_as_fixed_point2(r):
	return float(r - 0x8000) / 0x4000

def short_as_fixed_point3(r):
	result = float(r & 0x7fff) / 0x7fff
	return result if (r & 0x8000) == 0 else -result

def read_fixed_point(src):
	return short_as_fixed_point(read_short(src))

def read_fixed_point2(src):
	return short_as_fixed_point2(read_short(src))

# def read_fixed_point3(src):
# 	s = read_short(src)
# 	r = short_as_fixed_point(s)
# 	print('0x{:04X} -> {}'.format(s, r))
# 	return r

def read_fixed_point8(src):
	r = read_byte(src)
	if (r & 0x80) != 0:
		return (float(r)-0x100)/0x7f
	return float(r)/0x7f

# --- Strings ---

def read_char(src):
	return src.read(1)

def read_string_of_known_length(src, nb_char):
	return '' if nb_char == 0 else (src.read(nb_char).decode("utf-8") )

def read_string(src):
	nb_char = read_int(src)
	return None if nb_char == 0 else read_string_of_known_length(src, nb_char - 1)

def read_nullterminated_string(src):
	c = src.read(1)
	result = u''
	while c != b'\x00':
		result += c.decode('utf-8')
		c = src.read(1)
	return result

# Readers for basic structures
#=============================

def read_string_or_float(src):
	bytes = src.read(4)
	# print bytes
	if bytes[3] != 0:
		return struct.unpack('<f', bytes)[0]
	nb_char = struct.unpack('<I', bytes)[0]
	# print nb_char
	if nb_char == 0:
		return 0.
	return src.read(nb_char - 1).decode("utf-8") 

def read_vector32(src):
	return (read_float32(src), read_float32(src), read_float32(src))

def read_vector16(src):
	return (read_float16(src), read_float16(src), read_float16(src))

def read_vector_fixed_point(src):
	return (read_fixed_point(src), read_fixed_point(src), read_fixed_point(src))

def read_vector_fixed_point2(src):
	return (read_fixed_point2(src), read_fixed_point2(src), read_fixed_point2(src))

def read_vector_fixed_point8(src):
	return (read_fixed_point8(src), read_fixed_point8(src), read_fixed_point8(src))

def read_with_useless_extra(src, reader, extra_reader, expected_value_of_extra):
	result = reader(src)
	extra = extra_reader(src)
	if(extra != expected_value_of_extra):
		print('warning: read', extra, 'but was expecting', expected_value_of_extra)
	assert(extra == expected_value_of_extra)
	return result


# Readers for arrays of basic types
#==================================

def read_byte_array(src, nb_bytes):
	return tuple(byte for byte in src.read(nb_bytes))

def read_int_array(src, nb_ints):
	return tuple( read_int(src) for counter in range(nb_ints) )

def read_short_array(src, nb_shorts):
	return tuple( read_short(src) for counter in range(nb_shorts) )


# Readers for complex structures
#===============================

def read_array(src, nb_items, item_reader):
	return tuple( item_reader(src) for counter in range(nb_items) )

def read_tuple(src, *readers):
	return tuple( r(src) for r in readers )

