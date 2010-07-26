from decutils import *

def decode_generic_rotate(pc, opc):
	direction_left = opc & 0x20
	dirchar = "l" if direction_left else "r"
	carry = "c" if opc & 0x10 else ""

	opcode = "r%s%s" %(direction_left, carry)
	
	return DictProxy(
		addr = pc,
		disasm = AE(opcode, a_A()),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)

def decode_anl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = AE("anl", a_A(), a_I8(immediate)),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
			
def decode_anl_a_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("anl", a_A(), a_RI(opc&0x1)),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
			
def decode_xrl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = AE("xrl", a_A(), a_I8(immediate)),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
					
def decode_orl_a_imm(pc, opc, immediate):
	return DictProxy(
		addr = pc,
		disasm = AE("orl", a_A(), a_I8(immediate)),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)
			
def decode_orl_a_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("orl", a_A(), a_RI(opc&0x1)),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)


def decode_clr_a(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("clr", a_A()),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
def decode_clr_c(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("clr", a_C()),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)
			
def decode_clr_bit(pc, opc, bitaddr):
	return DictProxy(
		addr = pc,
		disasm = AE("clr", a_B(bitaddr)),
		cycles = 1,
		length = 2,
		dests = [pc + 2],
		)

def decode_xch_reg(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("xch", a_A(), a_R(opc&0x7)),
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)

def decode_xch_iram(pc, opc, iram_addr):
	return DictProxy(
		addr = pc,
		disasm = AE("xch", a_A(), a_D(iram_addr)),
		dests = [pc + 2],
		cycles = 1,
		length = 2
		) 

		
def decode_swap(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("swap", a_A()),
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)

def decode_setb_c(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("setb", a_C()),
		length = 1,
		cycles = 1,
		dests = [pc + 1]
		)
		
def decode_setb_bitaddr(pc, opc, bitaddr):
	return DictProxy(
		addr = pc,
		disasm = AE("setb", a_B(bitaddr)),
		length = 2,
		cycles = 1,
		dests = [pc + 2]
		)
