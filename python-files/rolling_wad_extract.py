#!/usr/bin/env python3

# PoC mostly working roll_p.wad extractor
# (C) 2023 Lily Tsuru <lily@crustywindo.ws>

# The following ImHex pattern was used to help write this tool.
"""
#pragma eval_depth 2048

struct PakEnt {
	u32 blockOffset; // 0 = directory, in "blocks" 0x2000 byte units
	u32 nextEnt; // next file (bytes)
	u32 nextLink; // next directory (bytes)
	u32 byteSize; // -1 = directory (in bytes)
	char name[]; // filename

	if(nextLink != 0x0)
		PakEnt nextLinkEnt @ nextLink;

	if(nextEnt != 0x0)
		PakEnt nextEnt @ nextEnt;

};

u32 headerBlockSize @ 0x0;
PakEnt ent @ 0x4;
"""

import struct
import sys
import os
from pathlib import Path, PurePath
from enum import Enum

# converts a block count to bytes.
def blocks_to_bytes(block_count: int):
	return block_count * 2048

def read_asciiz(file):	# FUCK python i swear
	lastpos = file.tell()
	len = 0
	c = 0
	s = ""

	while True:
		c = file.read(1)
		if c[0] == 0:
			break
		s += c.decode('ascii')

	# go back
	file.seek(lastpos, os.SEEK_SET)
	return s

class WadEntryType(Enum):
	""" A file. """
	FILE = 0

	""" A directory. """
	DIRECTORY = 1

	# ugliness for argparse
	def __str__(self):
		return self.name

	@staticmethod
	def from_string(s):
		try:
			return WadEntryType[s]
		except KeyError:
			raise ValueError()

class WadHeader:								# wad file header
	def __init__(self, file):
		data = struct.unpack("I", file.read(4))
		self.header_block_count = data[0]

class WadEntry:									# a wad file entry
	def __init__(self, file):
		self._file = file
		data = struct.unpack("IIII", file.read(4*4))
		self.block_offset = data[0] 			# offset in blocks (see above)
		self.next_file = data[1]    			# used in files to go to next file in folder
		self.next_link = data[2]    			# used in folders to go to first entry
		self.size_bytes = data[3]				# data size in bytes. 0x80000000 for folders
		self.name = read_asciiz(file) 			# pretty self explainatory

		if self.size_bytes == 0x80000000:
			self.type = WadEntryType.DIRECTORY
		else:
			self.type = WadEntryType.FILE

		self.children = []

	def read_directory_children(self):
		last_ofs = self.next_link
		self._file.seek(last_ofs, os.SEEK_SET)

		entry = WadEntry(self._file)
		entry.parent = self

		while True:
			#print(entry.name, entry.type, "parent dir:", entry.parent.name)

			if entry.type == WadEntryType.DIRECTORY and entry.next_link != 0:
				entry.read_directory_children()

			if entry.next_file != 0:
				#print(f'seeking to {entry.next_file:x} (loop)')
				self._file.seek(entry.next_file, os.SEEK_SET)

			self.children.append(entry)

			if entry.next_file == 0:
				#print("done reading", self.name)
				self._file.seek(last_ofs, os.SEEK_SET)
				return

			entry = WadEntry(self._file)
			entry.parent = self


	def dump(self, pathObj):
		self._file.seek(blocks_to_bytes(self.block_offset), os.SEEK_SET)
		path = str(pathObj)
		with(open(path, "wb")) as file:
			file.write(self._file.read(self.size_bytes))
			print(f'Wrote file {self.name} ({self.size_bytes} bytes) to {path}.')
			file.close()

	def walk(self, rootPath):
		result = []
		for child in self.children:
			child_path = rootPath / child.name.lower()
			result.append((child_path, child))
			result.extend(child.walk(child_path))
		return result


# """""main loop"""""

rootPath = Path(os.getcwd()) / Path(sys.argv[1]).stem

# make root first
rootPath.mkdir(exist_ok=True)

with open(sys.argv[1], "rb") as file:
	header = WadHeader(file)
	root = WadEntry(file)
	root.read_directory_children()

	for tup in root.walk(rootPath):
		if tup[1].type == WadEntryType.FILE:
			tup[1].dump(tup[0])
		else:
			#print("mkdir:", tup[0], tup[1].name)
			(tup[0]).mkdir(parents=True, exist_ok=True)
