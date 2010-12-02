from arch.shared_opcode_types import *
from arch.shared_mem_types import *

class DictProxy(dict):
	def __init__(self,**args):
		if __debug__ and "length" in args and "dests" in args and "pc" in args:
			for x in args["dests"]:
				assert not ( x > args["pc"] and x < args["pc"] + args["length"])
			
		dict.__init__(self, args)
		self["typeclass"] = "code"
		self["typename"] = "8051"
		
		# Kill off the simulator
		try:
			del self["sim"]
		except KeyError: pass
		
	#def __repr__(self):
	#	return str(dict( [(i,self.__dict__[i]) for i in self.d if i in self.__dict__ ]  ))


def sb(x):
	if x >= 128:
		return x - 256
	return x

class ProgramMemoryIndirectAddressingOperand(Operand):
	def __init__(self, from_pc=True):
		self.from_pc = from_pc
	def render(self, ds=None):
		return "@a + %s" % ({False: "dptr", True: "pc"}[self.from_pc]), TYPE_UNSPEC
		
class DptrOperand(Operand):
	def render(self, ds=None):
		return "dptr", TYPE_UNSPEC

class PCOperand(Operand):
	def render(self, ds=None):
		return "pc", TYPE_UNSPEC

class DptrIndirectAddressingOperand(Operand):
	def render(self, ds=None):
		return "@dptr", TYPE_UNSPEC

class RegisterOperand(Operand):
	def __init__(self, Rn):
		assert Rn >=0 and Rn <= 7
		self.Rn = Rn
		Operand.__init__(self)
		
	def render(self, ds=None):
		return "R%d" % self.Rn, TYPE_UNSPEC

class RegisterIndirectAddressingOperand(Operand):
	def __init__(self, Rn):
		assert Rn in [0,1]
		self.Rn = Rn

	def render(self, ds=None):
		return "@R%d" % self.Rn, TYPE_UNSPEC

class DirectAddressingOperand(Operand):
	def __init__(self, direct):
		assert direct < 256 and direct >= 0
		self.direct = direct

	def render(self, ds=None):
		return "(%#02x)" % self.direct, TYPE_UNSPEC

class ImmediateOperand8(Operand):
	def __init__(self, constant):
		assert constant >= 0 and constant < 256
		self.constant = constant
	def render(self, ds=None):
		return "#0x%02x" % self.constant, TYPE_UNSPEC

class ImmediateOperand16(Operand):
	def __init__(self, constant):
		assert constant >= 0 and constant < 65536
		self.constant = constant
	def render(self, ds=None):
		return "#0x%04x" % self.constant, TYPE_UNSPEC

class BitOperand(Operand):
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

	def render(self, ds=None):
		return "%s(%#02x.%d)" % ("/" if self.invflag else "", self.addr, self.bit), TYPE_UNSPEC

class AccumulatorOperand(Operand):
	def render(self, ds=None):
		return "a", TYPE_UNSPEC

class ABOperand(Operand):
	def render(self, ds=None):
		return "ab", TYPE_UNSPEC

class CarryFlagOperand(Operand):
	def render(self, ds=None):
		return "c", TYPE_UNSPEC

class PCJmpDestination(Operand):
	def __init__(self, calculated_addr):
		self.addr = calculated_addr
	def render(self, ds=None):
		typecode = TYPE_UNSPEC
		if ds:
			try:
				if ds[self.addr].label:
					return ds[self.addr].label, TYPE_SYMBOLIC
			except IndexError:
				typecode = TYPE_DEST_INVALID
			except KeyError:
				pass
		return "%#04x" % self.addr, typecode
		
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

