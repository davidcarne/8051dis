
class ArbitraryNumeric(object):
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
	
	def __str__(self):
		return "%#x" % self.value
		
# Only used as argument to directives
class StringOperand(object):
	def __init__(self, val):
		self.val = val
		
	def __str__(self):
		return "\"%s\"" % self.val
		
class AssemblyEncoding(object):
	def __init__(self, opcode, *operands):
		self.opcode = opcode
		self.operands = operands

	def __str__(self):
		return "%s\t%s" % (self.opcode, ", ".join([str(i) for i in self.operands]))


AE = AssemblyEncoding