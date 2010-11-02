from decutils import *

def decode_generic_rotate(pc, opc):
	direction_left = opc & 0x20
	dirchar = "l" if direction_left else "r"
	carry = "c" if opc & 0x10 else ""

	opcode = "r%s%s" %(dirchar, carry)
	
	return DictProxy(
		addr = pc,
		disasm = AE(opcode, a_A()),
		cycles = 1,
		length = 1,
		dests = [pc + 1],
		)


def generic_logical_a_imm(text):
	def decode_x_a_imm(pc, opc, immediate):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_A(), a_I8(immediate)),
			cycles = 1,
			length = 2,
			dests = [pc + 2],
			)

	return decode_x_a_imm


def generic_logical_iram_imm(text):
	def decode_x_iram_imm(pc, opc, iram, immediate):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_D(iram), a_I8(immediate)),
			cycles = 2,
			length = 3,
			dests = [pc + 3],
			)
	return decode_x_iram_imm

def generic_logical_iram_a(text):
	def decode_x_iram_a(pc, opc, iram):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_D(iram), a_A()),
			cycles = 1,
			length = 2,
			dests = [pc + 2],
		)
	return decode_x_iram_a


def generic_logical_a_iram(text):
	def decode_x_a_iram(pc, opc, iram):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_A(), a_D(iram)),
			cycles = 1,
			length = 2,
			dests = [pc + 2],
			)
	return decode_x_a_iram

def generic_logical_a_reg(text):
	def decode_x_a_reg(pc, opc):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_A(), a_R(opc&0x7)),
			cycles = 1,
			length = 1,
			dests = [pc + 1],
			)
	return decode_x_a_reg

def generic_logical_a_ind(text):
	def decode_x_a_ind(pc, opc):
		return DictProxy(
			addr = pc,
			disasm = AE(text, a_A(), a_RI(opc&0x1)),
			cycles = 1,
			length = 1,
			dests = [pc + 1],
		)
	return decode_x_a_ind


# Hack to generate all ANL / ORL / XRL operands
for opc in ["xrl", "orl", "anl"]:
	for mode in ["a_reg", "a_iram", "a_ind", "a_imm", "iram_a", "iram_imm"]:
		# Hack - anyone know a better way?
		exec("decode_%s_%s = generic_logical_%s('%s')" % (opc, mode, mode, opc))


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

def decode_xch_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("xch", a_A(), a_RI(opc&0x1)),
		dests = [pc + 1],
		cycles = 1,
		length = 1
		)

def decode_xchd_ind(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("xchd", a_A(), a_RI(opc&0x1)),
		dests = [pc + 1],
		cycles = 1,
		length = 1
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

def decode_cpl_c(pc, opc):
	return DictProxy(
		addr = pc,
		disasm = AE("cpl", a_C()),
		length = 1,
		cycles = 1,
		dests = [pc + 1]
		)

def decode_cpl_bit(pc, opc, bitaddr):
	return DictProxy(
		addr = pc,
		disasm = AE("cpl", a_B(bitaddr)),
		length = 2,
		cycles = 1,
		dests = [pc + 2]
		)


	
def decode_anl_c(pc, opc, bitaddr):
	inv = (opc == 0xB0)
	return DictProxy(
		addr = pc,
		disasm = AE("anl", a_C(), a_B(bitaddr, inv)),
		length = 2,
		cycles = 2,
		dests = [pc + 2]
		)

def decode_orl_c(pc, opc, bitaddr):
	inv = (opc == 0xA0)
	return DictProxy(
		addr = pc,
		disasm = AE("orl", a_C(), a_B(bitaddr, inv)),
		length = 2,
		cycles = 2,
		dests = [pc + 2]
		)
