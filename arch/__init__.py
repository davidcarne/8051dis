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

def getDecoder(dec_type):
	try:
		return shared_mem_types.decoderTypes[dec_type]
	except KeyError:
		return architectureFactory(dec_type).decode