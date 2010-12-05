#import lib8051
#from lib8051.decutils import *
from arch.shared_opcode_types import *
from arch.shared_mem_types import *

from dbtypes import *
from tools_algos import *
from tools_loaders import *


# Undefine a specific opcode [should this have a follow-until-other-assigned mode]?
def undefine(ds, addr):
	l = ds[addr].length
	del ds[addr]

def decodeAs(ds, dec_type, memaddr):
	old_mem = ds[memaddr]
	
	params = getDecoder(dec_type)(ds, memaddr)
	
	if not params:
		return False
	
	# Make sure the range needded for the new data is clear
	for i in xrange(params["length"]):
		try:
			if ds[memaddr + i].typeclass != "default" : return
		except KeyError: pass
			
	# Carry over old label and comment
	m = MemoryInfo.createFromDecoding(params)
	m.label = old_mem.label
	m.comment = old_mem.comment
	
	for i in xrange(params["length"]):
		try:
			del ds[memaddr + i]
		except KeyError:
			pass

	ds[memaddr] = m



def follow(ds, addr):
	try:
		insn = ds[addr].cdict["decoding"]
		dests = insn["dests"]
		
	except KeyError: return None

	for j in dests:
		if j == addr + ds[addr].length: continue
		
		try:
			dest_info = ds[j]
		except KeyError: pass


		return j

	return None

