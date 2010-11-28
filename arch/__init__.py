import shared_opcode_types
import shared_mem_types
from lib8051 import Arch8051

architecture_list = {
	'8051': Arch8051
}

def architectureFactory(archname):
	return architecture_list[archname]()

def architectureNames():
	return architecture_list.names()
