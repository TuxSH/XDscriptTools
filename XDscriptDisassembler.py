""" See LICENSE for license"""

from XDscriptLib import *
import argparse
import sys
import os


if __name__ == '__main__':
	if sys.version_info[0] < 3:
		raise RuntimeError("Python 3 required")

	parser = argparse.ArgumentParser()
	parser.add_argument("files", help="XD script files to disassemble", nargs='+', type=str)
	parser.add_argument("--display-code-offsets", help="Display code offsets", action="store_true") 
	args = parser.parse_args()
	fnames = args.files

	for fname in fnames:
		with open(fname, "rb") as f:
			out_fname = os.path.splitext(fname)[0]+'.txt'
			contents = f.read()
			with open(out_fname, "w") as out_f:
				out_f.write(str(ScriptCtx(contents, args.display_code_offsets)))