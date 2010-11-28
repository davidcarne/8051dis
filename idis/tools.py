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

def parseIhexLine(line):
	if line[0] != ':':
		print "STart char fail!"
		return
	bc = int(line[1:3], 16)
	addr = int(line[3:7], 16)
	rtype = int(line[7:9], 16)
	data = line[9:9 + 2 * bc]
	data = [int(data[i : i+2], 16) for i in xrange(0,len(data),2)] 
	ck = int(line[9 + 2 * bc: 9 + 2 * bc + 2], 16)

	if bc != len(data):
		print "data len fail!"
		return

	calcck = (0x100 - (sum([bc, addr & 0xFF, addr >> 8, rtype] + data) & 0xFF)) & 0xFF
	if calcck != ck:
		print data
		print "Checksum Fail, %02x = %02x!" % (calcck, ck)
		return

	return rtype, addr, data

def addIHex(ds, file):
	lines = open(file).readlines()

	recs = []
	for i in lines:
		record = parseIhexLine(i)
		if not record:
			print "Error parsing line %s" % i
		recs.append(record)
	
	addrs = [(addr, addr+len(data)) for rtype, addr, data in recs if rtype == 0x0]
	dmin = min([i[0] for i in addrs])
	dmax = max([i[1] for i in addrs])
	
	
	# build data array
	data = [0x0] * (dmax - dmin + 1)
	for rtype, addr, ldata in recs:
		if (rtype == 0x0):
			for offs, j in enumerate(ldata):
				data[offs + addr - dmin] = j
	
	seg = Segment(data, dmin)
	ds.addSegment(seg)

	for offs,value in enumerate(data):
		addr = offs + dmin
		mi = MemoryInfo("", addr, 1, AE(".db 0x%02x"%value))
		mi.cdict["is_default"] = True
		ds[addr] = mi


def undefine(ds, addr):
	l = ds[addr].length


	del ds[addr]

	for i in xrange(addr, addr+l):
		value = ds.readBytes(i)[0]
		mi = MemoryInfo("", i, 1, AE(".db 0x%02x"%value))
		mi.cdict["is_default"] = True
		ds[i] = mi


def rebuildClean(ds):
	cleanlist = []
	for i in ds:
		if "insn" in i.cdict:
			for j in xrange(i.length-1):
				if i.addr + j + 1 in ds:
					cleanlist .append( i.addr + j + 1)
	for i in cleanlist:
		del ds[i]

def rebuild(ds):
	for i in ds:
		if "insn" in i.cdict:
			fetched_mem = ds.readBytes(i.addr,6)	
			insn = lib8051.decode(i.addr, fetched_mem)
			
			if (insn.length != i.length):
				raise ValueError, "New instruction length, can't rebuild"

			i.disasm = insn.disasm
			i.cdict["insn"] = insn
		

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
				ds[j].xrefs.append((i, ds[i].cdict["insn"].disasm.opcode))
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

