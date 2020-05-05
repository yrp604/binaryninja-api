#!/usr/bin/env python3
# Copyright (c) 2015-2020 Vector 35 Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import sys
import os
from glob import glob

import binaryninja.log as log
from binaryninja.binaryview import BinaryViewType
import binaryninja.interaction as interaction
from binaryninja.plugin import PluginCommand

# 2-3 compatibility
from binaryninja import range
from builtins import str


def get_bininfo(bv, filename=None):
	if bv is None:
		if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
			return("Cannot read {}\n".format(filename))
		bv = BinaryViewType.get_view_of_file_with_options(filename, options={'analysis.mode': 'basic', 'analysis.linearSweep.autorun' : False})
	else:
		filename = ""

	log.log_to_stdout(True)

	contents = "## %s ##\n" % os.path.basename(bv.file.filename)
	contents += "- START: 0x%x\n\n" % bv.start
	contents += "- ENTRY: 0x%x\n\n" % bv.entry_point
	contents += "- ARCH: %s\n\n" % bv.arch.name
	contents += "### First 10 Functions ###\n"

	contents += "| Start | Name   |\n"
	contents += "|------:|:-------|\n"
	for i in range(min(10, len(bv.functions))):
		contents += "| 0x%x | %s |\n" % (bv.functions[i].start, bv.functions[i].symbol.full_name)

	contents += "### First 10 Strings ###\n"
	contents += "| Start | Length | String |\n"
	contents += "|------:|-------:|:-------|\n"
	for i in range(min(10, len(bv.strings))):
		start = bv.strings[i].start
		length = bv.strings[i].length
		string = bv.read(start, length)
		contents += "| 0x%x |%d | %s |\n" % (start, length, string)

	# Note that we need to close BV file handles that we opened to prevent a
	# memory leak due to a circular reference between BinaryViews and the
	# FileMetadata that backs them

	if filename != "":
		bv.file.close()
	return contents


def display_bininfo(bv):
	interaction.show_markdown_report("Binary Info Report", get_bininfo(bv))


if __name__ == "__main__":
	if len(sys.argv) == 1:
		filename = interaction.get_open_filename_input("Filename:")
		if filename is None:
			log.log_warn("No file specified")
		else:
			print(get_bininfo(None, filename=str(filename, 'utf8')))
	else:
		for i in range(1, len(sys.argv)):
			print(sys.argv[i])
			pattern = sys.argv[i]
			for filename in glob(pattern):
				print(get_bininfo(None, filename=filename))
else:
	PluginCommand.register("Binary Info", "Display basic info about the binary using minimal analysis modes", display_bininfo)
