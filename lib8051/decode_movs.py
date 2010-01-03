from decutils import *

def decode_mov_a_iram(pc, opc, iram_addr):
	def runner(state):
		state.a = state.iram[iram_addr]
		
	return DictProxy(
				addr = pc,
				disasm = "mov a, %#02x" % iram_addr,
				cycles = 1,
				sim = runner,
				length = 2,
				dests = [pc + 2],
			)
			

def decode_mov_a_imm(pc, opc, immediate):
	def runner(state):
		state.a = immediate
		
	return DictProxy(
				addr = pc,
				disasm = "mov a, #%#02x" % immediate,
				cycles = 1,
				sim = runner,
				length = 2,
				dests = [pc + 2],
			)
			
									
def decode_mov_iram_ind(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				disasm = "mov %#02x, @r%x" % (iram_addr, opc & 0x1),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)
			

def decode_mov_iram_reg(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				disasm = "mov %#02x, r%x" % (iram_addr, opc & 0x7),
				cycles = 2,
				length = 2,
				dests = [pc + 2],
			)

def decode_mov_iram_a(pc, opc, iram_addr):
	return DictProxy(
				addr = pc,
				disasm = "mov %#02x, a" % (iram_addr),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)
			
def decode_mov_iram_imm(pc, opc, iram_addr, immediate):
	return DictProxy(
				addr = pc,
				disasm = "mov %#02x, #%#02x" % (iram_addr, immediate),
				cycles = 2,
				length = 3,
				dests = [pc + 3],
			)
			
def decode_mov_reg_imm(pc, opc, immediate):
	return DictProxy(
				addr = pc,
				disasm = "mov r%x, %#02x" % (opc & 0x7, immediate),
				cycles = 1,
				length = 2,
				dests = [pc + 2],
			)
			
def decode_mov_ind_a(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = "mov @r%x, a" % (opc & 0x1),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
			)
			
def decode_mov_dptr_imm16(pc, opc, dh, dl):
	return DictProxy(
				addr = pc,
				disasm = "mov dptr, #%#04x" %((dh << 8) | dl),
				cycles = 2,
				length = 3,
				dests = [pc+3],
				)
				
def decode_movc(pc, opc):
	reg = "dptr" if opc & 0x10 else "pc"
	return DictProxy(
				addr = pc,
				disasm = "movc a, @a + %s" % reg,
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)

def decode_mov_reg_a(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = "mov r%d, a" % (opc&0x7),
				cycles = 1,
				length = 1,
				dests = [pc + 1],
				)

def decode_movx_ind_a(pc, opc):
	reg = "r%d" % (opc&1) if opc & 0x2 else "dptr"
	return DictProxy(
				addr = pc,
				disasm = "movx @%s, a" % reg,
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)
				
def decode_movx_a_ind(pc, opc):
	reg = "r%d" % (opc&1) if opc & 0x2 else "dptr"
	return DictProxy(
				addr = pc,
				disasm = "movx a, @%s" % reg,
				cycles = 2,
				length = 1,
				dests = [pc + 1],
				)