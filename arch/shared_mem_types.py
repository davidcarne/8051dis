from shared_opcode_types import *

def decode_numeric(ds, addr, saved_params = None, width=8, big_endian=False, signed="UNSIGNED"):
	assert signed in ["UNSIGNED", "TWOSCOMP", "ONESCOMP"]
	
	if width == 8:
		big_endian = False

	# Some of the saved_params need to be pushed down to the operand level
	# For example - signed is a property of the representation, not the memory location		
	if not saved_params:
		saved_params = {
			"width": width,
			"big_endian": big_endian,
			"signed": signed
			}
		
	bytecount = width/8
	try:
		mem = ds.readBytes(addr, bytecount)
	except IndexError:
		return None
	
	directive_specialcases = {
		(8,  False, False):	".db",
		(8,  False, True):	".db"
		}
		
	try:
		dirname = directive_specialcases[(width, big_endian, signed)]
	except KeyError:
		dirname = ".d%s%d%s" % ( ("s" if signed else "u"), width, ("be" if big_endian else ""))
		
	return { "addr": addr,
			 "length": bytecount,
			 "disasm": AE(dirname, ArbitraryNumeric(mem, saved_params)),
			 "suggested_label": "d%x" % addr,
			 "typeclass" : "data",
			 "typename": "numeric",
			 "saved_params": saved_params }
		
	
def decode_ascii_string(ds, startaddr, saved_params={}):
	
	
	str_buf = ""
	has_zero_term = False
	
	addr = startaddr
	if not saved_params:
		while 1:
			# Make sure we don't run off the end of memory
			try:
				mem = ds.readBytes(addr, 1)[0]
			except IOError:
				break
			
			# If that location already has data defined
			try:
				old_loc_data = ds[addr]
				if not old_loc_data.typeclass == "default":
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

	else:
		# restore the params the string was created with
		addr = end_addr = saved_params["end_addr"]
		has_zero_term = saved_params["has_zero_term"]
		
		# read the string from memory
		calc_end = end_addr - 1 if has_zero_term else end_addr
		str_buf = "".join([chr(i) for i in ds.readBytes(startaddr, calc_end-startaddr)])
	

	def charFilter(a):
		return a.isalnum() or a in "_"
		
	lab = "".join([i for i in str_buf if charFilter(i)])
	saved_params = {
		"end_addr": addr,
		"has_zero_term": has_zero_term
	}
	
	return { "addr": startaddr,
			 "length": addr - startaddr,
			 "disasm": AE((".str" if has_zero_term else ".strnoz"), StringOperand(str_buf)),
			 "suggested_label": "a%s" % lab,
			 "typeclass" : "data",
			 "typename": "astring",
			 "saved_params": saved_params }
			 
decoderTypes = {
	"astring" : decode_ascii_string
	}
	