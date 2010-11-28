from shared_opcode_types import *


def decode_ascii_string(ds, startaddr):
	
	str_buf = ""
	has_zero_term = False
	
	addr = startaddr
	while 1:
		# Make sure we don't run off the end of memory
		try:
			mem = ds.readBytes(addr, 1)[0]
		except IndexError:
			break
		
		# If that location already has data defined
		try:
			old_loc_data = ds[addr]
			if not old_loc_data.cdict["is_default"]:
				break
			if old_loc_data.label:
				break
				
		except IndexError:
			pass
		
		addr += 1
		
		if mem == 0x00:
			has_zero_term = True
			break
		
		str_buf += chr(mem)

	return { "addr": startaddr,
			 "length": addr - startaddr,
			 "disasm": AE((".str" if has_zero_term else ".strnoz"), StringOperand(str_buf)) }
			 
			 

decoderTypes = {
	"astring" : decode_ascii_string
	}
	
def getDecoder(dec_type):
	return decoderTypes[dec_type]