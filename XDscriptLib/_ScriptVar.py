# See LICENSE for license

import struct

wellDefinedTypes = {
	0: "none_t",
	1: "int",
	2: "float",
	3: "str", # GLOBAL limit: 256 strings. max 255 chars for 1 string
	4: "vector",
	7: "list",
	8: "msg", # id to msg, not accessible directly
	35: "character",
	37: "pkm",
	44: "type44",
	53: "codeptr_t"
}

class ScriptVar(object):
	"""Script variable:
	struct XDscriptVar {
		s16 type; // 0x00 -- 0x01, s16
		// 0x02--0x03: padding
		union{
			s32 asInt;
			float asFloat;
			void* asPtr;
		}; // 0x04 -- 0x07:
	}
	"""

	@property
	def value(self):
		if self.varType == 1:
			val2 = struct.unpack(">i", self._rawValue)[0]
			return val2
		elif self.varType == 2:
			return struct.unpack(">f", self._rawValue)[0]
		else:
			return struct.unpack(">I", self._rawValue)[0]
	
	@value.setter
	def value(self, val):
		if self.varType == 2:
			 self._rawValue = struct.pack(">f", float(val))
		elif self.varType == 1:
			 self._rawValue = struct.pack(">i", int(val))
		else:
			self._rawValue = struct.pack(">I", int(val) & 0xffffffff) 

	def __str__(self):
		if self.varType == 0 and self.value == 0:
			return "None"
		elif self.varType == 0:
			return "none_t({0})".format(self.value)
		elif self.varType == 1:
			return str(self.value)
		elif self.varType == 2:
			return "{0:.7g}".format(self.value)
		else:
			return "{0}(*{1})".format(wellDefinedTypes.get(self._arType, str(self.varType)), hex(self.value))

	def __init__(self, src):
		self.varType = struct.unpack_from(">h", src)[0]
		self._rawValue = bytes(src[4:8])

def parseScriptArray(src):
	"""
	Script array:
	struct XDscriptArray {
		s32 size; // 0x00--0x03
		s32 iteratorPos; // 0x04--0x07
		// padding
		s16 arrayNo; // 0x0a -- 0x0b
		// padding
		XDscriptVar elems[]; // 0x10
	};
	"""
	sz = struct.unpack_from(">i", src)[0]
	return [ScriptVar(src[0x10 + 8*i:0x10 + 8*(i+1)]) for i in range(sz)]

