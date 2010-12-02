# Operands that follow after an instruction / pseudo op
#
# Some of the 8051 specific ones need to be pushed here / subclassed in the 8051 code

TYPE_UNSPEC = 0
TYPE_SYMBOLIC = 1
TYPE_DEST_INVALID = 2

class Operand(object):
	def __init__(self):
		pass

	def __str__(self):
		return self.render(None)[0]

# Numeric constant of arbitrary size and representation
# Some 8051 operands should be made subclasses of this to allow format to be changed

class ArbitraryNumeric(Operand):
	def __init__(self, vals, fmt):
		width = fmt["width"]
		signed = fmt["signed"]
		
		# TODO - justifys?
		assert width % 8 == 0
		assert width > 0
		assert len(vals) == width / 8
		
		ordered_bytes = vals
		if not fmt["big_endian"]:
			ordered_bytes = vals[::-1]
		
		# calculate the value
		numeric_val = reduce(lambda acc, byte: (acc<<8) | byte, ordered_bytes)
		
		if signed == "TWOSCOMP":
			if numeric_val & (1<<(width-1)):
				numeric_val -= 1<<width
		elif signed == "ONESCOMP":
			if numeric_val & (1<<(width-1)):
				numeric_val = -(numeric_val ^ ((1<<width) - 1))
		
		self.value = numeric_val
	
	def render(self, ds=None):
		return "%#x" % self.value, TYPE_UNSPEC
		
# Only used as argument to directives
class StringOperand(Operand):
	def __init__(self, val):
		self.val = val
		
	def render(self, ds=None):
		return "\"%s\"" % self.val, TYPE_UNSPEC
		
class AssemblyEncoding(Operand):
	def __init__(self, opcode, *operands):
		self.opcode = opcode
		self.operands = operands

	def render(self, ds=None):
		return "%s\t%s" % (self.opcode, ", ".join([str(i) for i in self.operands])), TYPE_UNSPEC


AE = AssemblyEncoding
