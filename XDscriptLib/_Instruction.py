# See LICENSE for license

import struct
import warnings
from XDscriptLib import FunctionInfo

class Instruction(object):
	"""
	Instruction -- represents a XD script instruction
	
	For the PAL version, the script interpreter is at 8023D83C
	
	ctx: ScriptCtx (attribute)
	label: string
	position: int, nextPosition
	
	OOSSPPPP
	opcode: 8-bit integer, from 0 to 17
	subOpcode: 8-bit integer, not always used
	parameter: 16-bit signed integer, not always used
	
	**Opcodes**: 
		See below. int, float, str, and vector are the only 'copyable' types, ldvar is used for them.
		For all other existing types, ldncpvar is used (if ldncpvar is followed by setvar, the source variable is deleted)


	**Operators, functions, and their respective calling conventions**:
		Refer to FunctionInfo

	**Types**:
		Refer to ScriptVar

	**Stack**:
		It is limited to 256 elements. Each task has its own stack. See FunctionInfo for further details.

	**Tasks**:
		The XD script engine is based on multitasking. 8 tasks max., either synchronous (blocking, and in the same thread),
		or asynchronous (in a different thread). NB: GS uses its own threading system.

		Task signature: either:
			4 ints, 
			or a character (for character interaction handlers)

	Properties:
	
		- subSubOpcodes: 
			the sub-opcodes of 'loadvar',
			'setvar', 'setvector' and 'movevar', which access or modify
			variables, can be divided into 2 nibbles (4-bit) :
		
				- the rightmost stands for the variable's level of storage:
				see variableName
			
				- the leftmost, only used by 'setvector', is used
				to specify the index of the vector coordinate to be set
				(vec[0] <=> vec.vx, vec[1] <=> vec.vy, vec[2] <=> vec.vz)
		
		
		- instructionID : 24-bit integer made by concatenating the sub-opcode and the parameter,
		used by 'call', 'jumptrue', 'jumpfalse', and 'jump' 
			
		- name: the instruction name, determined from the opcode

		- etc...
		
	"""
	
	instructionNames = ("nop", "operator", "ldimm",
	"ldvar", "setvar", "setvector",
	"pop", "call", "return",
	"callstd", "jmptrue", "jmpfalse",
	"jmp", "reserve", "release",
	"exit", "setline", "ldncpvar")


	
	vectorCoordNames = ("vx", "vy", "vz", '4')	

		
	#---------------------Getters---------------------

	@property
	def name(self):
		return self.__class__.instructionNames[self._opcode]
	
	@property
	def position(self):
		return self._position
	
	@property
	def nextPosition(self):
		return self._nextPosition
	
	@property
	def label(self):
		return self._label

	@property
	def opcode(self):
		return self._opcode

	@property
	def subOpcode(self):
		return self._subOpcode
	
	@property
	def parameter(self):
		return self._parameter	
	
	@property
	def subSubOpcodes(self):
		return ((self._subOpcode >> 4), self._subOpcode & 0xf)
	
	@property
	def instructionID(self):
		return (self._subOpcode << 16) | (self._parameter & 0xffff)
		
	#-------------------------------------------------

	def checkVariable(self):
		_, level = self.subSubOpcodes
		if level == 0:
			if self._parameter < 0:
				warnings.warn("negative gloabl var ID encountered ({0} \
					at instruction #{1})".format(self._parameter, hex(self.position)))
		elif level == 2:
			if self._parameter != 0:
				warnings.warn("negative $lastResult ID encountered ({0} \
					at instruction #{1})".format(self._parameter, hex(self.position)))
		elif level == 3:
			if self._parameter < 0 or self._parameter > 0x2ff or 0x120 < self._parameter < 0x200:
				warnings.warn("invalid special variable ID encountered ({0} \
					at instruction #{1})".format(self._parameter, hex(self.position)))

	@property
	def variableName(self):
		_, level = self.subSubOpcodes
		if level == 0:
			return "$globals[{0}]".format(self._parameter)
		elif level == 1:
			return "$stack[{0}]".format(self._parameter)
		elif level == 2:
				return "$lastResult"
		else:
			if self._parameter < 0 or self._parameter > 0x2ff or 0x120 < self._parameter < 0x200:
				return "$invalidSpecials[{0}]".format(self._parameter)
			elif 0 <= self._parameter < 0x80: # possible singletons (fake objects)
				name = FunctionInfo.stdfunctions_name_dict.get(self._parameter, str(self._parameter))[0]
				return "${0}".format(name[0].lower() + name[1:])
			elif 0x80 <= self._parameter <= 0x120:
				return "$characters[{0}]".format(self._parameter - 0x80)
			else:
				return "$arrays[{0}]".format(self._parameter - 0x200) 



	#------------------Special methods-----------------
	
	def check(self):
		self._nextPosition = self._position + 1
		instrID = self.instructionID
		
		if self._opcode > 17:
			warnings.warn("illegal opcode encountered (opcode {0} \
			at instruction #{1})".format(self._opcode, hex(self.position)))
			
		elif self._opcode == 1:
			if FunctionInfo.getOperatorName(self._subOpcode) == str(self._subOpcode):
				warnings.warn("invalid operator encountered (operator '{0}' \
				at instruction #{1})".format(FunctionInfo.getOperatorName(self._subOpcode), hex(self.position)))
		
		elif self._opcode == 2:
			if self.ctx is not None:
				packed = None
				
				if self._subOpcode in (0, 1, 2, 0x35):
					assert not isinstance(self.ctx.sections["CODE"].instructions[self._position + 1], self.__class__)
					
					packed = struct.pack(">f", self.ctx.sections["CODE"].instructions[self._position + 1]) if\
					type(self.ctx.sections["CODE"].instructions[self._position + 1]) is float else\
					struct.pack(">I", self.ctx.sections["CODE"].instructions[self._position + 1] & 0xffffffff)
				
				
				if self._subOpcode in (0, 0x35):  # none_t/codeptr_t
					self.ctx.sections["CODE"].instructions[self._position + 1] = struct.unpack(">I", packed)[0]
					self._nextPosition = self._position + 2
				
				if self._subOpcode == 1:  # int
					self.ctx.sections["CODE"].instructions[self._position + 1] = struct.unpack(">i", packed)[0]
					self._nextPosition = self._position + 2
					
				elif self._subOpcode == 2:  # float
					self.ctx.sections["CODE"].instructions[self._position + 1] = struct.unpack(">f", packed)[0]
					self._nextPosition = self._position + 2
					
		
			if self._subOpcode == 3:
				if self._parameter < 0:
					warnings.warn("negative string offset encountered ({0} \
					at instruction #{1})".format(self._parameter, hex(self.position)))
		
			elif self._subOpcode == 4:
				if self._parameter < 0:
					warnings.warn("negative vector ID encountered ({0} \
					at instruction #{1})".format(self._parameter, hex(self.position)))
			
			elif self._subOpcode not in (0, 1, 2, 3, 4, 0x35, 0x2c):
				warnings.warn("ldimm does not support this type ({0} \
				at instruction #{1})".format(self._subOpcode, hex(self.position)))
					
		
		elif self._opcode in (3, 4, 17):
		    # ldvar, setvar, ldncpvar
			self.checkVariable()
			if self.subSubOpcodes[1] == 3 and self._opcode == 4:
				warnings.warn("cannot change immutable reference (instruction #{0})".format(hex(self.position)))
			
		elif self._opcode == 5:  # setvector
			vecindex, veclevel = self.subSubOpcodes
				
			if vecindex == 4:
				warnings.warn("out-of-range vector coordinate index encountered ({0} \
				at instruction #{1})".format(self._parameter, hex(self.position)))	
			
			if veclevel == 3:
				warnings.warn("Invalid vector storage type encountered \
				(instruction #{0})".format(hex(self.position)))
		
		elif self._opcode in (7, 10, 11, 12):  # call/jmptrue/jmpfalse/jmp
			if self.ctx is not None:
				if instrID >= len(self.ctx.sections["CODE"].instructions):
					warnings.warn("out-of-range destination \
					instruction encountered in jump/call instruction \
					(at instruction #{0}: {1}\t{2})".format(hex(self.position),
					self.name, hex(instrID)))
				
				else:
					if self._opcode == 7 and instrID not in self.ctx.sections["HEAD"].functionOffsets:
						warnings.warn("call to unreferenced function ({0} \
						at instruction #{1})".format(instrID, hex(self.position)))

					lbl = ''.join(["sub_" if self._opcode == 7 else "loc_", hex(instrID)[2:]])
					if not self.ctx.sections["CODE"].labels[instrID]: self.ctx.sections["CODE"].labels[instrID] = lbl
					if self._opcode != 7 and (True if self.ctx is None 
							   else self.position+1 < len(self.ctx.sections["CODE"].instructions)) :
						lbl2 = ''.join(["loc_", hex(self.position+1)[2:]])
						if not self.ctx.sections["CODE"].labels[self.position+1]: self.ctx.sections["CODE"].labels[self.position+1] = lbl2
				
					
		elif self._opcode == 9:  # callstd
			if FunctionInfo.stdfunctions_name_dict.get(self._subOpcode) is None:
				warnings.warn("invalid class id encountered ({0} \
				at instruction #{1})".format(self._subOpcode, hex(self.position)))
	
	
					
	
	#-------------------------------------------------


	#---------------------Setters---------------------
	
	@label.setter
	def label(self, val):
		self._label = str(val)
	
	@position.setter
	def position(self, val):
		if val < 0 or (self.ctx is not None and val >= len(self.ctx.sections["CODE"].instructions)):
			raise ValueError("Out-of-range position!")
		self._position = val
	
	@nextPosition.setter
	def nextPosition(self, val):
		self._nextPosition = int(val) if val >= 0 else 0
		
	@opcode.setter
	def opcode(self, value):
		val2 = int(value) & 0xff
		self._opcode = val2
		self.check()
		
	@subOpcode.setter
	def subOpcode(self, value):
		self._subOpcode = int(value) & 0xff
		self.check()
		
	@parameter.setter
	def parameter(self, value):
		val2 = int(value) & 0xffff
		# sign extend:
		self._parameter = -((~val2 + 1) & 0xffff) if ((val2 & 0x8000) == 0x8000) else val2
		self.check()
	
	@subSubOpcodes.setter
	def subSubOpcodes(self, values):
		self._subOpcode = ((int(values[0]) & 0xf) << 4) | (int(values[1]) & 0xf)
		self.check()
		
	@instructionID.setter
	def instructionID(self, value):
		val2 = int(value)
		self._subOpcode = (val2 >> 16) & 0xff
		self.parameter = val2 & 0xffff
		self.check()
	
	#-------------------------------------------------
	
	
	#---------------------Methods---------------------
	
	def fromRaw(self, rawWord=0):
		self._opcode = (rawWord >> 24) & 0xff
		self._subOpcode = (rawWord >> 16) & 0xff
		self.parameter = rawWord & 0xffff
		self.check()
	
	def toRaw(self):
		return (self._opcode << 24) | (self._subOpcode << 16) | self._parameter 
	
	def __init__(self, rawWord=0, ctx=None, position=0, label=""):
		#print(position)
		self.ctx = ctx
		self.position = position
		self._nextPosition = position + 1
		self.label = label
		self._opcode = 0
		self._subOpcode = 0
		self._parameter = 0
		self.fromRaw(rawWord)
		
		
	
	def __str__(self):
		self.check()

		instrnamestr = self.name if self._opcode <= 17 else "illegal{0}".format(self._opcode)

		instrstr = None
		
		if self._opcode > 17:
			return ''.join([labelstr, 
						"illegal{0}\t{1}, {2}, {3}".format(self._opcode, self._subOpcode, self._parameter)])
		
		elif self._opcode in (0, 8, 15):  # nop, return, exit
			instrstr = "{0}".format((self._subOpcode, self._parameter)) if\
			not (self._subOpcode, self._parameter) == (0, 0) else ""
			
		elif self._opcode == 1:  # operator
			instrstr = FunctionInfo.getOperatorName(self._subOpcode)
			
		elif self._opcode == 2:  # ldimm
			if self._subOpcode == 0:
				instrstr = 'none_t, ={0}'.format('None' if self.ctx is None or self.ctx.sections["CODE"].instructions[self._position + 1] == 0 
									 else self.ctx.sections["CODE"].instructions[self._position + 1])
			elif self._subOpcode == 1:
				instrstr = 'int, ={0}'.format("" if self.ctx is None else str(self.ctx.sections["CODE"].instructions[self._position + 1]))
			elif self._subOpcode == 2:
				if self.ctx is None:
					instrstr = 'float, ='
				else:
					fstr = '{0:.7g}'.format(self.ctx.sections["CODE"].instructions[self._position + 1])#.rstrip('0')
					fstr = fstr if fstr else "0."
					instrstr = 'float, ={0}'.format(fstr)
						
			elif self._subOpcode == 3:
				instrstr = 'str, ={0}'.format(self._parameter if self.ctx is None or self.ctx.sections.get("STRG") is None
								  else '"{0}"'.format(self.ctx.sections["STRG"].getString(self._parameter)))
			
			elif self._subOpcode == 4:
				instrstr = "vector, ={0}".format(self._parameter if self.ctx is None or self.ctx.sections.get("VECT") is None
									 else "<{0}, {1}, {2}>".format(*self.ctx.sections["VECT"].vectors[self._parameter]) )
			
			elif self._subOpcode == 0x2c:
				instrstr = "type44, {0}".format(self._parameter & 0xffff)  # unsigned parameter
			
			elif self._subOpcode == 0x35:
				typestr = "codeptr_t"
				valuestr = "={0}".format(hex(self.ctx.sections["CODE"].instructions[self._position + 1])\
											if self.ctx is not None else "")
			
			else:
				instrstr = "{0}, {1}".format(self._subOpcode, self._parameter & 0xffff)
			
		elif self._opcode in (3, 4, 17):  # ldvar, setvar, ldncpvar
			instrstr = self.variableName

		elif self._opcode == 5:  # setvector
			instrstr = "{0}, {1}".format(self.__class__.vectorCoordNames[self.subSubOpcodes[0]], self.variableName)
			
		elif self._opcode in (6, 13, 14):  # pop, reserve, release
			instrstr = "{0}{1}".format(self._subOpcode, "" if self._parameter == 0 else\
			"(, {0})".format(self._parameter))

		elif self._opcode in (7, 10, 11, 12):  # call/jmptrue/jmpfalse/jmp
			instrID = self.instructionID
			instrstr = hex(instrID) if (self.ctx is None or instrID >= len(self.ctx.sections["CODE"].instructions))\
			else self.ctx.sections["CODE"].labels[instrID]
			
		elif self._opcode == 9:  # callstd
			instrstr = FunctionInfo.getStdFunctionName(self._subOpcode, self._parameter)
				
		elif self._opcode == 16:  # setline
			instrstr = str(self._parameter)
		
		ret = ''.join([instrnamestr, (14 - len(instrnamestr)) * ' ', instrstr]) 
		return ret
	#-------------------------------------------------
	
