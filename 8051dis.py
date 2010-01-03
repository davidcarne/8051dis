#!/usr/bin/python

from lib8051 import decode
import sys

insns = {}

def checkMemState(addr):
	if k in insns:
		return "FOUND"
		
	for k,v in insns.iteritems():
		if k <= addr and k+v.length > addr:
			return "OVERLAP"

f = [ord(i) for i in open(sys.argv[1]).read()]
pc = 0

q = [0]

while q:
	pc = q.pop()
	try:
		insn = decode(pc, f[pc:])
	except NameError, q:
		print "%04x\tunimplemented opcode: %s [%02x]" % (pc,q, f[pc])
		break
	q.extend([i for i in insn.dests if i not in insns])
	insns[pc] = insn
	print "%04x\t" % pc + insn.disasm