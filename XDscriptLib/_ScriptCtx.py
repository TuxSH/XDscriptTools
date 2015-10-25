# See LICENSE for license

import struct
import warnings
import copy
from XDscriptLib import Instruction, ScriptVar, parseScriptArray
import io

class ScriptSection(object):
	"""
	Script section

	0x00: const char magic[4]
	0x04: s32 sectionSize
	0x08 to 0x0f: padding
	0x10: s32 nbElems. For CODE, HEAD, and FTBL, it is the number of functions. For all other sections, it should be obvious.
	0x14: s32 valueOffset. For FTBL, the name buffer offset. For HEAD, the entry point
	0x18: u32 unknown (used by FTBL and GVAR)
	0x1c to 0x1f: padding ?
	0x20: data
	"""

	def __init__(self, src):
		self.name = src[:4].decode('ascii')
		data = memoryview(src)
		self.totalSize = struct.unpack_from(">I", data, 4)[0]
		self.nbElems = struct.unpack_from(">i", data, 0x10)[0]
		self.valueOffset = struct.unpack_from(">I", data, 0x14)[0]
		self.unknown = struct.unpack_from(">I", data, 0x18)[0]
		self.data = bytes(data[0x20:self.totalSize])

class ScriptCtx(object):
	"""Script context class (assembler / disassembler)

	0x00: const char magic[4] = "FTBL"
	0x04: s32 scriptTotalSize
	0x08 to 0x0f: padding
	0x10: sections
	"""
	
	#Oh, and f*ck properties ...

	def loadSections(self, src):
		self.sections = dict()
		offset = 0x10
		while offset < self.totalSize:
			currentSection = ScriptSection(src[offset:])
			offset += currentSection.totalSize
			self.sections[currentSection.name] = currentSection

	def parseFTBLSection(self):
		sec = self.sections.get("FTBL")
		if sec is None: return
		sec.functionTable = []
		for i in range(sec.nbElems):
			code_off = struct.unpack_from(">I", sec.data, 8*i)[0]
			nm_off = struct.unpack_from(">I", sec.data, 4 + 8*i)[0] - 0x20
			if 0 > nm_off or nm_off + 0x20 >= len(sec.data): continue 
			nm = sec.data[nm_off:sec.data.find(b'\x00', nm_off)].decode('sjis')
			sec.functionTable.append((code_off, nm))

	def parseHEADSection(self):
		sec = self.sections["HEAD"]
		sec.functionOffsets = [struct.unpack_from(">I", sec.data, 4*i)[0] for i in range(sec.nbElems)]

	def parseCODESection(self):
		sec = self.sections["CODE"]
		sec.instructions = list(struct.unpack_from(">{0}I".format(len(sec.data) // 4), sec.data))
		sec.labels = [""]*len(sec.instructions)

		pos = 0
		while pos < len(sec.instructions):
			if not isinstance(sec.instructions[pos], Instruction):
				sec.instructions[pos] = Instruction(sec.instructions[pos], self, pos)
				pos =  sec.instructions[pos].nextPosition

	
	def parseSTRGSection(self):
		"""String constants"""
		sec = self.sections.get("STRG")
		if sec is None: return
		sec.stringContents = sec.data.decode('sjis')
		sec.getString = (lambda offset: sec.stringContents[offset:sec.stringContents.find('\x00', offset)])

	def parseVECTSection(self):
		"""Vector constants"""
		sec = self.sections.get("VECT")
		if sec is None: return
		sec.vectors = [struct.unpack_from(">3f", sec.data, 12*i) for i in range(sec.nbElems)]
	
	def parseGIRISection(self):
		"""Characters. (grpID = 0, resID = 100) is the player itself"""
		sec = self.sections.get("GIRI")
		if sec is None: return
		sec.characters = [(struct.unpack_from(">I", sec.data, 8*i)[0], struct.unpack_from(">I", sec.data, 8*i + 4)[0]) for i in range(sec.nbElems)]

	def parseGVARSection(self):
		"""Global variables"""
		sec = self.sections.get("GVAR")
		if sec is None: return
		sec.globalVars = [ScriptVar(sec.data[8*i:8*i+8]) for i in range(sec.nbElems)] 

	def parseARRYSection(self):
		"""Arrays"""
		sec = self.sections.get("ARRY")
		if sec is None: return

		sec.arrays = []
		for i in range(sec.nbElems):
			off = struct.unpack_from(">I", sec.data, 4*i)[0]
			if (off - 0x10) >= 4*sec.nbElems: sec.arrays.append(parseScriptArray(memoryview(sec.data)[off-0x10:]))
	

	def load(self, src):
		if src[:4] != b'TCOD': warnings.warn("Apparently not a XD script file!")
		self.totalSize = struct.unpack_from(">I", src, 4)[0]
		self.loadSections(src)
		self.parseFTBLSection()
		self.parseHEADSection()
		self.parseCODESection()
		self.parseSTRGSection()
		self.parseVECTSection()
		self.parseGIRISection()
		self.parseGVARSection()
		self.parseARRYSection()

		ftbl = self.sections.get("FTBL")
		code = self.sections["CODE"]
		if ftbl is not None:
			for (off, nm) in ftbl.functionTable:
				code.labels[off] = nm

		entryPoint = self.sections["HEAD"].valueOffset
		if not code.labels[entryPoint]: code.labels[entryPoint] = "__start" 
		
	def __init__(self, src): self.load(src)
	
	def __str__(self):
		out = io.StringIO()

		ftbl = self.sections.get("FTBL")
		code = self.sections["CODE"]
		head = self.sections["HEAD"]
		strg = self.sections.get("STRG")
		vect = self.sections.get("VECT")
		giri = self.sections.get("GIRI") # Characters
		gvar = self.sections.get("GVAR")
		arry = self.sections.get("ARRY")

		if ftbl is not None:
			out.write('.section "FTBL":\n')
			for (off, nm) in ftbl.functionTable:
				out.write('\t.function {0}, "{1}"\n'.format(code.labels[off], nm))
			out.write('\n')


		out.write('.section "HEAD":\n')
		out.write('\t.set __ENTRY_POINT__, {0}\n'.format(code.labels[head.valueOffset]))
		for off in head.functionOffsets: out.write('\t.function {0}\n'.format(code.labels[off]))
		out.write('\n')

		out.write('.section "CODE":\n')
		for instr in code.instructions:
			if not isinstance(instr, Instruction): continue
			
			separator_printed = False
			if (ftbl is not None and code.labels[instr.position] in [nm for (off, nm) in ftbl.functionTable])\
			or code.labels[instr.position][:4] == 'sub_':
				 out.write('\n\n;=================SUBROUTINE===================\n')
				 separator_printed = True

			elif code.labels[instr.position][:4] == 'loc_':
				out.write(';----------------------------------------------\n')
				separator_printed = True

			if code.labels[instr.position]:
				out.write('{0}:\n'.format(code.labels[instr.position]))

			if instr.opcode == 16 and not separator_printed:
				out.write('\n')

			out.write('\t{0}\n'.format(str(instr)))


		out.write('\n')

		if strg is not None:
			out.write('.section "STRG":\n')
			splt = strg.stringContents.split('\x00')
			if splt != ['']:
				for s in splt:
					out.write('\t"{0}",\n'.format(s))
			out.write('\n')
		
		if vect is not None:
			out.write('.section "VECT":\n')
			for v in vect.vectors:
				out.write('\t.vector <{0}, {1}, {2}>\n'.format(*v))
			out.write('\n')

		if giri is not None:
			out.write('.section "GIRI":\n')
			for character in giri.characters:
				out.write('\t.character (grpID = {0}, resID = {1})\n'.format(*character))
			out.write('\n')


		if gvar is not None:
			out.write('.section "GVAR":\n')
			for var in gvar.globalVars:
				out.write('\t.global_var {0}\n'.format(str(var)))
			out.write('\n')

		if arry is not None:
			out.write('.section "ARRY":\n')
			for ar in arry.arrays:
				out.write('\t.array [{0}]\n'.format(', '.join(str(elem) for elem in ar)))
			out.write('\n')


		return out.getvalue()
		
