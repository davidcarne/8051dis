from arch.shared_opcode_types import *
from arch.shared_mem_types import *

class DictProxy(object):
	def __init__(self,**args):
		if "length" in args and "dests" in args and "pc" in args:
			for x in args["dests"]:
				if x > args["pc"] and x < args["pc"] + args["length"]:
					print "INVALID DEST!!!"
					exit(1)
		self.d = args.keys()
		self.__dict__.update(args)

	def __repr__(self):
		return str(dict( [(i,self.__dict__[i]) for i in self.d if i in self.__dict__ ]  ))


def sb(x):
	if x >= 128:
		return x - 256
	return x

class ProgramMemoryIndirectAddressingOperand:
	def __init__(self, from_pc=True):
		self.from_pc = from_pc
	def __str__(self):
		return "@a + %s" % ({False: "dptr", True: "pc"}[self.from_pc])
		
class DptrOperand:
	def __str__(self):
		return "dptr"

class PCOperand:
	def __str__(self):
		return "pc"

class DptrIndirectAddressingOperand:
	def __str__(self):
		return "@dptr"

class RegisterOperand:
	def __init__(self, Rn):
		assert Rn >=0 and Rn <= 7
		self.Rn = Rn

	def __str__(self):
		return "R%d" % self.Rn

class RegisterIndirectAddressingOperand:
	def __init__(self, Rn):
		assert Rn in [0,1]
		self.Rn = Rn

	def __str__(self):
		return "@R%d" % self.Rn

class DirectAddressingOperand:
	def __init__(self, direct):
		assert direct < 256 and direct >= 0
		self.direct = direct

	def __str__(self):
		return "(%#02x)" % self.direct

class ImmediateOperand8:
	def __init__(self, constant):
		assert constant >= 0 and constant < 256
		self.constant = constant
	def __str__(self):
		return "#0x%02x" % self.constant

class ImmediateOperand16:
	def __init__(self, constant):
		assert constant >= 0 and constant < 65536
		self.constant = constant
	def __str__(self):
		return "#0x%04x" % self.constant

class BitOperand:
	def __init__(self, bit_and_addr, inv=False):
		bit = bit_and_addr & 0x7
		byte = bit_and_addr & 0xF8
		if (byte < 0x80):
			addr = 0x20 + byte/8
		else:
			addr = byte

		self.addr = addr
		self.bit = bit
		self.invflag = inv

	def __str__(self):
		return "%s(%#02x.%d)" % ("/" if self.invflag else "", self.addr, self.bit)

class AccumulatorOperand:
	def __str__(self):
		return "a"

class ABOperand:
	def __str__(self):
		return "ab"

class CarryFlagOperand:
	def __str__(self):
		return "c"

class PCJmpDestination:
	def __init__(self, calculated_addr):
		self.addr = calculated_addr
	def __str__(self):
		return "%#04x" % self.addr

a_R = RegisterOperand
a_RI = RegisterIndirectAddressingOperand
a_D = DirectAddressingOperand
a_A = AccumulatorOperand
a_AB = ABOperand
a_C = CarryFlagOperand
a_B = BitOperand
a_DPTR = DptrOperand
#a_PC = PCOperand
a_DPTRI = DptrIndirectAddressingOperand
a_I8 = ImmediateOperand8
a_I16 = ImmediateOperand16
a_PMAI = ProgramMemoryIndirectAddressingOperand

a_PC = PCJmpDestination

