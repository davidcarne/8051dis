from decutils import *

def decode_rrc(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "rrc a",
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)

def decode_rr(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "rr a",
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
def decode_anl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = "anl a, %#02x" % (immediate),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
			
def decode_anl_a_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "anl a, r%d" % (opc&0x1),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
			
def decode_xrl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = "xrl a, %#02x" % (immediate),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
					
def decode_orl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = "orl a, %#02x" % (immediate),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
			
def decode_orl_a_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "orl a, r%d" % (opc&0x1),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)


def decode_clr_a(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "clr a",
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
def decode_clr_c(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "clr c",
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
def decode_clr_bit(pc, opc, bitaddr):
	return DictProxy(
		addr = pc,
		disasm = "clr %#02x.%d" %(bitaddr>>3, bitaddr & 7),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)

def decode_xch_reg(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "xch a, r%d" % (opc&0x7),
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)

def decode_xch_iram(pc, opc, iram_addr):
	return DictProxy(
		addr = pc,
		disasm = "xch a, %#02x" % (iram_addr),
		dests = [pc + 2],
		cycles = 1,
		length = 2
		) 
			
def decode_rlc(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "rlc a",
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)
		
def decode_swap(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "swap a",
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)

def decode_setb_c(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = "setb c",
		length = 1,
		cycles = 1,
		dests = [pc + 1]
		)
		
def decode_setb_bitaddr(pc, opc, bitaddr):
	return DictProxy(
		addr = pc,
		disasm = "setb %#02x.%d" %(bitaddr >>3, bitaddr & 0x7),
		length = 2,
		cycles = 1,
		dests = [pc + 2]
		)
