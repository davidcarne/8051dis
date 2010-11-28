from decutils import *

def decode_acall_ajmp(pc, opc, addrl):
	calc_addr = ((pc + 2) & 0xF800) + ((opc & 0xE0) << 3) + addrl
	wtype = "call" if opc & 0x10 else "jmp"

	return DictProxy(
				addr = pc,
				dests = [calc_addr, pc+2] if wtype == "call" else [calc_addr],
				disasm = AE("a%s" % wtype, a_PC(calc_addr)),
				length = 2,
				cycles = 2
			)

def decode_ret(pc, opc):
	return DictProxy(
				addr = pc,
				dests = [],
				disasm = AE("ret"),
				length = 1,
				cycles = 2
			)

def decode_reti(pc, opc):
	return DictProxy(
				addr = pc,
				dests = [],
				disasm = AE("reti"),
				length = 1,
				cycles = 2
			)

def decode_cjne_a_iram(pc, opc, iram, rel):
	newpc = pc + sb(rel) + 3
	return DictProxy(
				addr = pc,
				disasm = AE("cjne", a_A(), a_D(iram), a_PC(newpc)),
				dests = [newpc, pc + 3],
				length = 3,
				cycles = 2
			)

def decode_jnz(pc, opc, rel):
	newpc = pc + sb(rel) + 2
	return DictProxy(
				addr = pc,
				disasm = AE("jnz", a_PC(newpc)),
				dests = [newpc, pc + 2],
				length = 2,
				cycles = 2
			)

def decode_jmp(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = AE("jmp", a_PMAI(False)),
				dests = [],
				cycles = 2,
				length = 1
			)
			
def decode_ljmp(pc, opc, addrh, addrl):
	newpc = ((addrh << 8) | addrl)
	def runner(state):
		state.pc = newpc
	return DictProxy(
				addr = pc,
				disasm = AE("ljmp", a_PC(newpc)),
				dests = [newpc],
				cycles = 2,
				sim = runner,
				length = 3
			)

def decode_lcall(pc, opc, addrh, addrl):
	newpc = ((addrh << 8) | addrl)
	def runner(state):
		state.pc = newpc
	return DictProxy(
				addr = pc,
				disasm = AE("lcall", a_PC(newpc)),
				dests = [newpc, pc+3],
				cycles = 2,
				sim = runner,
				length = 3
			)
			
def decode_sjmp(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	def runner(state):
		state.pc = newpc
	return DictProxy(
				addr = pc,
				disasm = AE("sjmp", a_PC(newpc)),
				dests = [newpc],
				cycles = 2,
				sim = runner,
				length = 2
			)
					
def decode_djnz_reg(pc, opc, reladdr):
	newpc = (pc + 2 + sb(reladdr))
	return DictProxy(
				addr = pc,
				disasm = AE("djnz", a_R(opc&0x7), a_PC(newpc)),
				dests = [newpc, pc + 2],
				cycles = 2,
				length = 2
			)
def decode_djnz_iram(pc, opc, iram, reladdr):
	newpc = (pc + 2 + sb(reladdr))
	return DictProxy(
				addr = pc,
				disasm = AE("djnz", a_D(iram), a_PC(newpc)),
				dests = [newpc, pc + 4],
				cycles = 2,
				length = 3
			)			
def decode_jz(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jz", a_PC(newpc)),
			cycles = 2,
			length = 2,
			dests = [newpc, pc+2]
			)
			
def decode_jnc(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jnc", a_PC(newpc)),
			cycles = 2,
			length = 2,
			dests = [newpc, pc+2]
			)
						
def decode_jnb(pc, opc, bitaddr, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jnb", a_B(bitaddr), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)

def decode_jb(pc, opc, bitaddr, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jb", a_B(bitaddr), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)

def decode_jbc(pc, opc, bitaddr, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jbc", a_B(bitaddr), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)


def decode_nop(pc, op):
	return DictProxy(
			addr = pc,
			disasm = AE("nop"),
			cycles = 1,
			length = 1,
			dests = [pc + 1]
			)


def decode_jc(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("jc", a_PC(newpc)),
			cycles = 2,
			length = 2,
			dests = [newpc, pc+2]
			)
			
def decode_cjne_reg_imm(pc, opc, immediate, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("cjne", a_R(opc&7), a_I8(immediate), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)	

def decode_cjne_ind_imm(pc, opc, immediate, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("cjne", a_RI(opc&1), a_I8(immediate), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)
			
def decode_cjne_a_imm(pc, opc, immediate, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = AE("cjne", a_A(), a_I8(immediate), a_PC(newpc)),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)

def decode_push(pc, opc, addr):
	return DictProxy(
			addr = pc,
			disasm = AE("push", a_D(addr)),
			cycles = 2,
			length = 2,
			dests = [pc+2]
			)

def decode_pop(pc, opc, addr):
	return DictProxy(
			addr = pc,
			disasm = AE("pop", a_D(addr)),
			cycles = 2,
			length = 2,
			dests = [pc+2]
			)



