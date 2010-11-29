from dbtypes import *


# Algorithms that affect more than one memory location in the database

def clean(ds):
	cleanlist = []
	for i in ds:
		if "insn" in i.cdict:
			for j in xrange(i.length-1):
				if i.addr + j + 1 in ds:
					cleanlist .append( i.addr + j + 1)
	for i in cleanlist:
		del ds[i]

def rebuild(ds, arch):
	for i in ds:
		if "insn" in i.cdict:
			fetched_mem = ds.readBytes(i.addr,6)	
			insn = arch.decode(i.addr, fetched_mem)
			
			if (insn.length != i.length):
				raise ValueError, "New instruction length, can't rebuild"

			i.disasm = insn.disasm
			i.cdict["decoding"] = insn

	
def codeFollow(ds, arch, entry_point):
	from types import FunctionType
	q = [entry_point]
	while q:
		pc = q.pop()

		if pc in ds and ds[pc].typeclass != "default":
			continue
		
		try:
			ds[pc]
		except KeyError:
			continue

		try:
			fetched_mem = ds.readBytes(pc,arch.maxInsnLength)
		except IOError:
			# If the generated addr is outside of mapped memory, skip it
			continue

		# TODO: HACK: 6 repeated 0xFF's = uninited mem
		if all([i==0xFF for i in fetched_mem]):
			continue
			
		insn = arch.decode(pc, fetched_mem)
		
		# If we can't decoded it, leave as is
		if not insn:
			continue
			
		q.extend([i for i in insn["dests"] ])

		# Carry over old label and comment
		old_mem = ds[pc]
		m = MemoryInfo.createFromDecoding(insn)
		m.comment = old_mem.comment
		m.label = old_mem.label
		
		# Can't serialize this
		try:
			del insn.sim
		except AttributeError: pass
		except KeyError: pass

		for i in xrange(m.length):
			try:
				del ds[pc + i]
			except KeyError:
				pass

		ds[pc] = m
		
def xrefsPass(ds):
	# Clear all xrefs
	for i in ds.addrs():
		ds[i].xrefs = []
	
	for i in ds.addrs():
		if ds[i].typeclass != "code": continue
		
		try:
			insn = ds[i].cdict["decoding"]
			dests = insn["dests"]
		except KeyError: continue
		
		for j in dests:
			if j == ds[i].addr + ds[i].length: continue
			try:
				ds[j].xrefs.append((i, ds[i].disasm.opcode))
			except KeyError:
				pass
				

def guessLabelName(caller, meminfo):
	if meminfo.typeclass == "default":
		return "u%04x" % meminfo.addr
		
	elif meminfo.typeclass == "data":
		if meminfo.cdict["decoding"]["typename"] == "astring":
			return "a%s" % meminfo.cdict["decoding"]["suggested_label"]
		else:
			return "d%04x" % meminfo.addr
	elif meminfo.typeclass == "code":
		# HACK HACK HACK
		if "call" in caller.disasm.opcode:
			return "sub_%04x" % meminfo.addr
		else:
			return "l%04x" % meminfo.addr
			
	assert False
	
		
def labelsPass(ds):
	for i in ds.addrs():
		try:
			insn = ds[i].cdict["decoding"]
			dests = insn["dests"]
		except KeyError: continue
		for j in dests:
			# If the dest is a jmp to the next insn, skip
			if j == ds[i].addr + ds[i].length: continue
			
			try:
				dest_info = ds[j]
			except KeyError: continue

			if dest_info.label: continue
			else: dest_info.label = guessLabelName(ds[j], dest_info)
			