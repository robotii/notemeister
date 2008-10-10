#!/usr/bin/env python

import gtk
import sys, os, re, string, tarfile

def make_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

def check_read_permissions(filename):
	if filename == None or os.access(filename, os.R_OK) == 0:
		return gtk.FALSE
	else:
		return gtk.TRUE

def check_write_permissions(filename):
	if filename == None or os.access(os.path.dirname(filename), os.W_OK) != 1:
		return gtk.FALSE
	else:
		return gtk.TRUE

def check_path_exists(path):
	return os.path.exists(path)
		
def note_name_to_file_name(name):
	return name.lower().replace(' ', '_')

def get_word_count(text):
	wordcount = 0

	# split the string into a list of words
	# a word is delimited by whitespace or punctuation
	for word in re.split(
			"[" + string.whitespace + string.punctuation + "]+" ,
			text ) :

		# make the word lower case
		word = string.lower( word )

		# check to make sure the string is considered a word
		if re.match( "^[" + string.lowercase + "]+$" , word ) :
			wordcount += 1

	return wordcount
			
