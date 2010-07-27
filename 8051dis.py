#!/usr/bin/python

from lib8051 import decode

from array import array

import psyco
psyco.full()


insns = {}


from optparse import OptionParser


parser = OptionParser()
parser.add_option("--start-at", dest="start_at", metavar="START", help="start disassembly at offset START in the file", type="int", default=0)
parser.add_option("--length", dest="length", metavar="LENGTH", help="disassemble max LENGTH bytes", type="int", default=-1)
parser.add_option("--base-addr", dest="base_addr", metavar="BASE", help="base addr for loaded code", type="int", default=0)
parser.add_option("--entry-point", dest="entry_point", metavar="BASE", help="entry point for loaded code", type="int", default=-1)
parser.add_option("--print-trace", dest="print_trace", help="display a trace while running", default=False, action="store_true")

(options, args) = parser.parse_args()




# Load the file
file_data = [ord(i) for i in open(args[0]).read()]

# Figure out disassembly addresses
start_offset = options.start_at

if options.length == -1:
	end_offset = len(file_data)
	dis_len = len(file_data) - start_offset
else:
	end_offset = start_offset + options.length
	dis_len = options.length

base_addr = options.base_addr
entry_point = options.entry_point
if entry_point == -1:
	entry_point = base_addr;



# Create a bitmap to mark used bytes
BITMAP_UNUSED = 0
BITMAP_INSN_HEAD = 1
BITMAP_INSN_BODY = 2
BITMAP_CONFIRMED_DATA = 3

_memory = array('B', file_data[start_offset:end_offset])
_aflags = array('B', [BITMAP_UNUSED] * dis_len)

def translate_addr(addr):
	if addr < base_addr:
		raise IOError, "Trying to read below base address"
	elif addr > (base_addr + dis_len):
		raise IOError, "Trying to read above memory length"
	return addr - base_addr

def lookup_mem(addr):
	addr = translate_addr(addr)
	# 6 bytes is a full insn
	return _memory[addr:addr+6]

def lookup_flag(addr):
	return _aflags[translate_addr(addr)]

def set_flag(addr, flag):
	_aflags[translate_addr(addr)] = flag

def checkMemState(addr):
	flag = lookup_flag(addr)
	if flag == BITMAP_INSN_HEAD:
		return "FOUND"
		
	if flag == BITMAP_INSN_BODY:
		return "OVERLAP"

	return "NONE"




if (options.print_trace):
	print "Disassembly Trace:"
q = [entry_point]

c = 0
while q:
	pc = q.pop()
	c += 1
	#if (c % 100 == 0): print "@ %04x" % pc

	try:
		fetched_mem = lookup_mem(pc)
	except IOError:
		# If the generated addr is outside of mapped memory, skip it
		continue

	# HACK 6 repeated 0xFF's = uninited mem
	if all([i==0xFF for i in fetched_mem]):
		continue

	ms = checkMemState(pc)
	if (ms == "FOUND"):
		continue

	if (ms == "OVERLAP"):
		print "Error, jumping into the middle of an instruction @ %04x" % pc
		
	try:
		insn = decode(pc, fetched_mem)
	except NameError, q:
		print "%04x\tunimplemented opcode: %s [%02x]" % (pc,q, lookup_mem(pc)[0])
		exit(1)

	q.extend([i for i in insn.dests])

	insns[pc] = insn

	# Mark instruction bounds
	set_flag(pc, BITMAP_INSN_HEAD)
	for i in xrange(insn.length-1):
		set_flag(pc + i + 1, BITMAP_INSN_BODY)

	if (options.print_trace):
		print "%04x\t" % pc + str(insn.disasm)
	if type(insn.disasm) == str:
		print "Ran into string-type disassembly"
		exit()

if (options.print_trace):
	print "\n\nDisassembled Output:"
i=base_addr
while i < (base_addr+dis_len):
	try:
		decoding = str(insns[i].disasm)
		l = insns[i].length
	except KeyError:
		decoding = ".db %02x" % lookup_mem(i)[0]
		l=1
	print "%04x\t%s" % (i,decoding)
	i+=l

