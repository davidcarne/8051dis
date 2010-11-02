from decutils import *

def decode_mov_a_reg(pc, opc):
	return DictProxy(
				addr = pc,
				#disasm = "mov a, r%x" % (opc & 0x7),
				disasm = AE("mov", a_A(), a_R(opc & 0x7)),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
			)
			

def decode_mov_a_iram(pc, opc, iram):

	return DictProxy(
				addr = pc,
				#disasm = "mov a, %#04x" % iram,
				disasm = AE("mov", a_A(), a_D(iram)),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)
			

def decode_mov_a_imm(pc, opc, immediate):
	def runner(state):
		state.a = immediate
		
	return DictProxy(
				addr = pc,
				#disasm = "mov a, #%#02x" % immediate,
				disasm = AE("mov", a_A(), a_I8(immediate)),
				cycles = 1,
				sim = runner,
				length = 2,
				dests = [pc + 2],
			)

def decode_mov_ind_imm(pc, opc, immediate):	
	return DictProxy(
				addr = pc,
				#disasm = "mov a, #%#02x" % immediate,
				disasm = AE("mov", a_RI(opc & 0x1), a_I8(immediate)),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)

def decode_mov_ind_iram(pc, opc, iram):	
	return DictProxy(
				addr = pc,
				#disasm = "mov a, #%#02x" % immediate,
				disasm = AE("mov", a_RI(opc & 0x1), a_D(iram)),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)
def decode_mov_a_ind(pc, opc):	
	return DictProxy(
				addr = pc,
				#disasm = "mov a, #%#02x" % immediate,
				disasm = AE("mov", a_A(), a_RI(opc & 0x1)),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
			)

def decode_mov_iram_iram(pc, opc, iram_1_addr, iram_2_addr):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_D(iram_2_addr), a_D(iram_1_addr)),
				cycles = 2,
				length = 3,
				dests = [pc + 3],
			)

def decode_mov_iram_ind(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				#disasm = "mov %#02x, @r%x" % (iram_addr, opc & 0x1),
				disasm = AE("mov", a_D(iram_addr), a_RI(opc & 0x1)),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)
			

def decode_mov_iram_reg(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				#disasm = "mov %#02x, r%x" % (iram_addr, opc & 0x7),
				disasm = AE("mov", a_D(iram_addr), a_R(opc & 0x7)),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)

def decode_mov_reg_iram(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				#disasm = "mov %#02x, r%x" % (iram_addr, opc & 0x7),
				disasm = AE("mov", a_R(opc & 0x7), a_D(iram_addr)),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)

def decode_mov_iram_a(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				#disasm = "mov %#02x, a" % (iram_addr),
				disasm = AE("mov", a_D(iram_addr), a_A()),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)
			
def decode_mov_iram_imm(pc, opc, iram_addr, immediate):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_D(iram_addr), a_I8(immediate)),
				cycles = 2,
				length = 3,
				dests = [pc + 3],
			)
			
def decode_mov_reg_imm(pc, opc, immediate):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_R(opc& 0x7), a_I8(immediate)),
				#"mov r%x, %#02x" % (opc & 0x7, immediate),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)
			
def decode_mov_ind_a(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_RI(opc & 0x1), a_A()),
				#disasm = "mov @r%x, a" % (opc & 0x1),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
			)
			
def decode_mov_dptr_imm16(pc, opc, dh, dl):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_DPTR(), a_I16((dh << 8) | dl)),
				#disasm = "mov dptr, #%#04x" %((dh << 8) | dl),
				cycles = 2,
				length = 3,
				dests = [pc+3],
				)
				
def decode_movc(pc, opc):
	reg_is_pc = False if opc & 0x10 else True

	return DictProxy(
				addr = pc,
				#disasm = "movc a, @a + %s" % reg",
				disasm = AE("movc", a_A(), a_PMAI(reg_is_pc)),
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)

def decode_mov_reg_a(pc, opc):
	return DictProxy(
				addr = pc,
				#disasm = "mov r%d, a" % (opc&0x7),
				disasm = AE("mov", a_R(opc & 0x7), a_A()),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
				)

def decode_movx_ind_a(pc, opc):
	regdest = a_RI(opc&1) if opc & 0x2 else a_DPTRI()
	return DictProxy(
				addr = pc,
				disasm = AE("movx", regdest, a_A()),
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)
				
def decode_movx_a_ind(pc, opc):
	regsrc = a_RI(opc&1) if opc & 0x2 else a_DPTRI()
	return DictProxy(
				addr = pc,
				disasm = AE("movx", a_A(), regsrc),
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)

def decode_mov_c_bitaddr(pc, opc, bitaddr):
	return DictProxy(
				addr = pc,
				disasm = AE("mov", a_C(), a_B(bitaddr)),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
				)

def decode_mov_bitaddr_c(pc, opc, bitaddr):
	return DictProxy(
				addr = pc,
				disasm = AE("mov",  a_B(bitaddr), a_C()),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
				)
