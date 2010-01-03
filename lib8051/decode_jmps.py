from decutils import *

def decode_jmp(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = "jmp @a + dptr",
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
				disasm = "ljmp %#04x" % newpc,
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
				disasm = "ljmp %#04x" % newpc,
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
				disasm = "sjmp %#04x" % newpc,
				dests = [newpc],
				cycles = 2,
				sim = runner,
				length = 2
			)
					
def decode_djnz_reg(pc, opc, reladdr):
	newpc = (pc + 2 + sb(reladdr))
	return DictProxy(
				addr = pc,
				disasm = "djnz r%d, %#04x" % (opc&0x7, newpc),
				dests = [newpc, pc + 2],
				cycles = 2,
				length = 2
			)
			
def decode_jz(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = "jz %#04x" % (newpc),
			cycles = 2,
			length = 2,
			dests = [newpc, pc+2]
			)
			
			
def decode_jnb(pc, opc, bitaddr, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = "jnb %02x.%d, %#04x" % (bitaddr>>3, bitaddr&7, newpc),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)

def decode_jc(pc, opc, reladdr):
	newpc = pc + 2 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = "jc %#04x" % (newpc),
			cycles = 2,
			length = 2,
			dests = [newpc, pc+2]
			)
			
			
def decode_cjne_ind_imm(pc, opc, immediate, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = "cjne @r%d, #%#02x, %#04x" % (opc&1, immediate, newpc),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)
			
def decode_cjne_a_imm(pc, opc, immediate, reladdr):
	newpc = pc + 3 + sb(reladdr)
	return DictProxy(
			addr = pc,
			disasm = "cjne a, #%#02x, %#04x" % (immediate, newpc),
			cycles = 2,
			length = 3,
			dests = [newpc, pc+3]
			)