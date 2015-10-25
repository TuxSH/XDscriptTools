""" See LICENSE for license"""

from XDscriptLib import *
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("files", help="XD script files to disassemble", nargs='+', type=str)
	args = parser.parse_args()

	for fname in args.files:
		with open(fname, "rb") as f:
			out_fname = fname.split('.')[0]+".txt"
			with open(out_fname, "w") as out_f:
				out_f.write(str(ScriptCtx(f.read())))