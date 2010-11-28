
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