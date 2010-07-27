import lib8051
from lib8051.decutils import *

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

class SUD(object):
	def __init__(self, name):
		self.name = name
	def __get__(self, instance, owner):
		if self.name not in instance.__dict__:
			raise AttributeError, self.name
		return instance.__dict__[self.name]
	def __set__(self, instance, value):
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
	def __getstate__(self):
		dont_save = ["xrefs", "ds_link"]
		return dict([i for i in self.__dict__.items() if i[0] not in dont_save])

	def __setstate__(self, d):
		self.__dict__ = d
		self.__cdict.parent = self.push_changes

		# mutable, not serialized
		self.xrefs = []

	label = SUD("_label")
	length = SUD("_length")
	disasm = SUD("_disasm")
	comment = SUD("_comment")
	type = SUD("_type")

	def __get_cdict(self): return self.__cdict
	cdict = property(__get_cdict)


	def __init__(self, label, addr, length, disasm, comment = "", xrefs=[]):
		self._label = label
		self.addr = addr
		self._length = length
		self._disasm = disasm
		self._comment = comment
		self.xrefs = xrefs
		self.__cdict = proxy_dict(self.push_changes)
		self.ds_link = None

	def push_changes(self):
		if (self.ds_link):
			self.ds_link(self.addr, self)

def addBinary(ds, file, base_addr, start_offset, length):
	# Load the file
	file_data = [ord(i) for i in open(file).read()]

	if length == -1:
		end_offset = len(file_data)
		dis_len = len(file_data) - start_offset
	else:
		end_offset = start_offset + length
		dis_len = length

	seg = Segment(file_data[start_offset:end_offset], base_addr)
	ds.addSegment(seg)

	for offs,value in enumerate(file_data[start_offset:end_offset]):
		addr = offs + base_addr
		mi = MemoryInfo("", addr, 1, AE(".db 0x%02x"%value))
		mi.cdict["is_default"] = True
		ds[addr] = mi

def codeFollow(ds, entry_point):
	from types import FunctionType
	q = [entry_point]
	while q:
		pc = q.pop()

		if pc in ds and not ds[pc].cdict["is_default"]:
			continue
		
		try:
			ds[pc]
		except KeyError:
			continue

		try:
			fetched_mem = ds.readBytes(pc,6)
		except IOError:
			# If the generated addr is outside of mapped memory, skip it
			continue

		# HACK 6 repeated 0xFF's = uninited mem
		if all([i==0xFF for i in fetched_mem]):
			continue

		
		insn = lib8051.decode(pc, fetched_mem)

		q.extend([i for i in insn.dests])

		m = ds[pc]
		
		# Can't serialize this
		try:
			del insn.sim
		except AttributeError: pass
		except KeyError: pass

		m.disasm = insn.disasm
		m.length = insn.length
		m.cdict["insn"] = insn
		m.cdict["is_default"] = False
		
		for k,v in m.cdict["insn"].__dict__.iteritems():
			if type(v) not in  [int, str, list, dict] and k != "disasm":
				raise AttributeError, k
				

		for i in xrange(insn.length-1):
			try:
				del ds[pc + i + 1]
			except KeyError:
				pass

def xrefsPass(ds):
	# Clear all xrefs
	for i in ds.addrs():
		ds[i].xrefs = []
	
	for i in ds.addrs():
		try:
			insn = ds[i].cdict["insn"]
			dests = insn.dests
		except KeyError: continue
		for j in dests:
			if j == insn.addr + insn.length: continue
			try:
				ds[j].xrefs.append(i)
			except KeyError:
				pass
def labelsPass(ds):
	for i in ds.addrs():
		try:
			insn = ds[i].cdict["insn"]
			dests = insn.dests
		except KeyError: continue
		for j in dests:
			if j == insn.addr + insn.length: continue
			
			try:
				dest_info = ds[j]
			except KeyError: pass

			if dest_info.label: continue
			else: dest_info.label = "l%04x" % j

def follow(ds, addr):
	try:
		insn = ds[addr].cdict["insn"]
		dests = insn.dests
	except KeyError: return None

	for j in dests:
		if j == insn.addr + insn.length: continue
		
		try:
			dest_info = ds[j]
		except KeyError: pass


		return j

	return None

