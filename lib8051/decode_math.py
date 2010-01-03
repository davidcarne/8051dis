from decutils import *

def decode_inc_dptr(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = "inc dptr",
				dests = [pc + 1],
				cycles = 2,
				length = 1
			)
			
def decode_inc_reg(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = "inc r%d" % (opc&0x7),
				dests = [pc + 1],
				cycles = 1,
				length = 1
			)

def decode_add_a_iram(pc, opc, iram_addr):
	return DictProxy(
			addr = pc,
			disasm = "add a, %#02x" % iram_addr,
			dests = [pc + 2],
			cycles = 1,
			length = 2
			)
			
def decode_add_a_reg(pc, opc):
	return DictProxy(
			addr = pc,
			disasm = "add a,r%d" % (opc&7),
			dests = [pc + 1],
			cycles = 1,
			length = 1
			)		
				
def decode_add_a_imm(pc, opc, immediate):
	return DictProxy(
			addr = pc,
			disasm = "add a, #%#02x" % immediate,
			dests = [pc + 2],
			cycles = 1,
			length = 2
			)
			
def decode_cpl_a(pc, opc):
	return DictProxy(
			addr = pc,
			disasm = "cpl a",
			dests = [pc + 1],
			cycles = 1,
			length = 1
			)