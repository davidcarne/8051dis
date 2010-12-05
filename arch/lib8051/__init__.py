import opcode_8051

def hack_8051_decode(ds, addr, saved_params={}):
	return opcode_8051.decode(addr, ds.readBytes(addr, 5))
	
class Arch8051(object):
	maxInsnLength = 6
	decode = staticmethod(hack_8051_decode)