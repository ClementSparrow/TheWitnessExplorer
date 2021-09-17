# -*- coding: utf-8 -*-
from modules.readers import *

def assert_read(function, src, value, msg, tolerate=False):
	r = function(src)
	if r==value: return r
	print('assertion failed:', msg)
	print(r, '≠', value)
	assert(tolerate)
	return r

def read_list(src, reader):
	length = read_int(src)
	return tuple( reader(src) for _ in range(length))

def read_short_list(src, reader):
	length = read_short(src)
	return tuple( reader(src) for _ in range(length))

def read_if(src, reader):
	test = read_byte(src)
	return None if test == 0 else reader(src)

def read_optional_string(src):
	return read_if(src, read_nullterminated_string)

def read_string_list(src):
	return read_list(src, read_optional_string)

def read_id(src):
	return read_int(src)

def read_if_id(src, reader):
	i = read_id(src)
	return None if i == 0 else (i, reader(src))

def read_signed_int(f):
	i = read_int(f)
	if i & 0x80000000:
		i -= 0x100000000
	return i