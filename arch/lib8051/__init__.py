import opcode_8051

class Arch8051(object):
	maxInsnLength = 6
	decode = staticmethod(opcode_8051.decode)