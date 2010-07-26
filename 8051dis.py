#!/usr/bin/python

from lib8051 import decode
import sys

from array import array

import psyco
psyco.full()


insns = {}




# Load the file
f = [ord(i) for i in open(sys.argv[1]).read()]

# Create a bitmap to mark used bytes
BITMAP_UNUSED = 0
BITMAP_INSN_HEAD = 1
BITMAP_INSN_BODY = 2
BITMAP_CONFIRMED_DATA = 3
aflags = array('B', [BITMAP_UNUSED] * len(f))



def checkMemState(addr):
	if aflags[addr] == BITMAP_INSN_HEAD:
		return "FOUND"
		
	if aflags[addr] == BITMAP_INSN_BODY:
		return "OVERLAP"

	return "NONE"



pc = 0

q = [0]

c = 0
while q:
	pc = q.pop()
	c += 1
	#if (c % 100 == 0): print "@ %04x" % pc

	# HACK 6 repeated 0xFF's = uninited mem
	if f[pc:pc+6] == [0xFF] * 6:
		continue

	ms = checkMemState(pc)
	if (ms == "FOUND"):
		continue
	if (ms == "OVERLAP"):
		print "Error, jumping into the middle of an instruction @ %04x" % pc
		break;

	try:
		insn = decode(pc, f[pc:])
	except NameError, q:
		print "%04x\tunimplemented opcode: %s [%02x]" % (pc,q, f[pc])
		exit(1)
	q.extend([i for i in insn.dests])

	insns[pc] = insn

	aflags[pc] = 1
	for i in xrange(insn.length-1):
		aflags[pc+i+1] = 2
	print "%04x\t" % pc + str(insn.disasm)
	if type(insn.disasm) == str:
		exit()

i=0
while i < len(f):
	try:
		decoding = str(insns[i].disasm)
		l = insns[i].length
	except KeyError:
		decoding = ".db %02x" % f[i]
		l=1
	print "%04x\t%s" % (i,decoding)
	i+=l

