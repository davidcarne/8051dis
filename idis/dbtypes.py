from dbtypes import *

class proxy_dict(dict):
	def __getstate__(self):
		return dict([i for i in self.__dict__.items() if i[0] != 'parent'])

	def __init__(self, parent, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.parent = parent

	def __setitem__(self, k,v):
		if self.parent:
			self.parent()
		return dict.__setitem__(self, k,v)

	def __delitem__(self, v):
		if self.parent:
			self.parent()
		return dict.__delitem__(self, v)


# On set force-update parameter
class SUD(object):
	def __init__(self, name, validator = None):
		self.name = name
		self.validator = validator
	def __get__(self, instance, owner):
		if self.name not in instance.__dict__:
			raise AttributeError, self.name
		return instance.__dict__[self.name]
		
	def __set__(self, instance, value):
		if self.validator: assert self.validator(value)
		instance.__dict__[self.name] = value
		instance.push_changes()



class Segment(object):
	def __init__(self, data, base_addr):
		self.data = data
		self.base_addr = base_addr

	def getLength(self):
		return len(self.data)

	def readBytes(self, start, length = 1):
		if (start < self.base_addr or start > self.base_addr + self.length):
			raise IOError, "not in segment"
		return self.data[start-self.base_addr:start-self.base_addr+length]

	length = property(getLength)



class MemoryInfo(object):

	@staticmethod
	def createFromDecoding(decoding):
		if __debug__:
			required_nouns = ["addr", "length", "disasm", "typeclass", "typename"]
			
			if decoding["typeclass"] == "code":
				required_nouns += ["dests"]
				
			for i in required_nouns:
				assert i in decoding, "No noun %s in supplied arg type: %s" %(i, type(decoding))

		m = MemoryInfo(	addr=decoding["addr"],
						length=decoding["length"],
						disasm=decoding["disasm"],
						typeclass=decoding["typeclass"],
						typename=decoding["typename"])
						
		m.cdict["decoding"] = decoding
		return m
		
		
	def __getstate__(self):
		dont_save = ["xrefs", "ds_link"]
		return dict([i for i in self.__dict__.items() if i[0] not in dont_save])

	def __setstate__(self, d):
		self.__dict__ = d
		self.__cdict.parent = self.push_changes

		# mutable, not serialized
		self.xrefs = []

	# Addr is read-only, since its a primary key. 
	# Delete and recreate to change
	def __get_addr(self): return self._addr
	addr = property(__get_addr)

	# length of this memory opcode
	length = SUD("_length")
	
	# Text form of the decoding [TODO: rename?]
	disasm = SUD("_disasm")
	
	# functionality comment
	comment = SUD("_comment")
	
	# General type of the data
	# Currently two valid values ["code", "data"]
	def __validate_typeclass(value):
		return value in ["code", "data", "default"]
	typeclass = SUD("_typeclass", __validate_typeclass)
	__validate_typeclass = staticmethod(__validate_typeclass)
	
	
	# Actual type of the data
	typename = SUD("_typename")

	# TODO: label goes away, sets should insert/update a symbol ent
	# in a separate table, reads should check that table, so proxy obj
	label = SUD("_label")
	
	def __get_cdict(self): return self.__cdict
	cdict = property(__get_cdict)
	
	def __init__(self, addr, length, disasm, typeclass, typename, label = "", comment = ""):
		self._label = label
		self._addr = addr
		self._length = length
		self._disasm = disasm
		
		assert MemoryInfo.__validate_typeclass(typeclass)
		self._typeclass = typeclass
		
		self._typename = typename
		self._comment = comment
		
		# Should go away too
		self.xrefs = []
		
		self.__cdict = proxy_dict(self.push_changes)
		self.ds_link = None

	def push_changes(self):
		if (self.ds_link):
			self.ds_link(self.addr, self)


