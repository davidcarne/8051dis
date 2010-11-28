from decode_jmps import *
from decode_movs import *
from decode_logical import *
from decode_math import *
def decode(pc, bytes):
	opc = bytes[0]
	# 2 byte ACALL
	if opc & 0x1F == 0x11:
		return decode_acall_ajmp(pc, opc, bytes[1])

	if opc == 0x26 or opc == 0x27:
		return decode_add_a_ind(pc, opc)
	if opc >= 0x28 and opc <= 0x2F:
		return decode_add_a_reg(pc, opc)
	if opc == 0x24:
		return decode_add_a_imm(pc, opc, bytes[1])
	if opc == 0x25:
		return decode_add_a_iram(pc, opc, bytes[1])
		
	if opc == 0x36 or opc == 0x37:
		return decode_add_a_ind(pc, opc, carry=True)
	if opc >= 0x38 and opc <= 0x3F:
		return decode_add_a_reg(pc, opc, carry=True)
	if opc == 0x34:
		return decode_add_a_imm(pc, opc, bytes[1], carry=True)
	if opc == 0x35:
		return decode_add_a_iram(pc, opc, bytes[1], carry=True)
		
		
	# 2 byte AJMP
	if opc & 0x1F == 0x01:
		return decode_acall_ajmp(pc, opc, bytes[1])
		
	if opc == 0x52:
		return decode_anl_iram_a(pc, opc, bytes[1])
	if opc == 0x53:
		return decode_anl_iram_imm(pc, opc, bytes[1], bytes[2])
	if opc == 0x54:
		return decode_anl_a_imm(pc, opc, bytes[1])
	if opc == 0x55:
		return decode_anl_a_iram(pc, opc, bytes[1])
	if opc >= 0x56 and opc <= 0x57:
		return decode_anl_a_ind(pc, opc)
	if opc >= 0x58 and opc <= 0x5F:
		return decode_anl_a_reg(pc, opc)
	if opc == 0x82 or opc == 0xB0:
		return decode_anl_c(pc, opc, bytes[1])
		
	if opc == 0xb4:
		return decode_cjne_a_imm(pc, opc, bytes[1], bytes[2])
	if opc == 0xb5:
		return decode_cjne_a_iram(pc, opc, bytes[1], bytes[2])
	if opc == 0xb6 or opc == 0xb7:
		return decode_cjne_ind_imm(pc, opc, bytes[1], bytes[2])
	if opc >= 0xb8 and opc <= 0xbf:
		return decode_cjne_reg_imm(pc, opc, bytes[1], bytes[2])
	
	if opc == 0xC2:
		return decode_clr_bit(pc, opc, bytes[1])
	if opc == 0xC3:
		return decode_clr_c(pc, opc)
	if opc == 0xE4:
		return decode_clr_a(pc, opc)
	
	if opc == 0xF4:
		return decode_cpl_a(pc, opc)
	if opc == 0xB3:
		return decode_cpl_c(pc, opc)
	if opc == 0xB2:
		return decode_cpl_bit(pc, opc, bytes[1])
	
	if opc == 0xD4:
		return decode_da(pc, opc)
	
	if opc == 0x14:
		return decode_dec_a(pc, opc)
	if opc >= 0x16 and opc <= 0x17:
		return decode_dec_ind(pc, opc)
	if opc >= 0x18 and opc <= 0x1F:
		return decode_dec_reg(pc, opc)
	if opc == 0x15:
		return decode_dec_iram(pc, opc, bytes[1])
	if opc == 0x84:
		return decode_div(pc, opc)
	if opc == 0xD5:
		return decode_djnz_iram(pc, opc, bytes[1], bytes[2])
	if opc >= 0xD8 and opc <= 0xDF:
		return decode_djnz_reg(pc, opc, bytes[1])
		
	if opc == 0x04:
		return decode_inc_a(pc, opc)
	if opc >= 0x06 and opc <= 0x07:
		return decode_inc_ind(pc, opc)
	if opc >= 0x08 and opc <= 0x0F:
		return decode_inc_reg(pc, opc)
	if opc == 0x05:
		return decode_inc_iram(pc, opc, bytes[1])
	if opc == 0xA3:
		return decode_inc_dptr(pc, opc)
	if opc == 0x20:
		return decode_jb(pc, opc, bytes[1], bytes[2])
	if opc == 0x10:
		return decode_jbc(pc, opc, bytes[1], bytes[2])
	if opc == 0x40:
		return decode_jc(pc, opc, bytes[1])
	if opc == 0x73:
		return decode_jmp(pc, opc)
	if opc == 0x30:
		return decode_jnb(pc, opc, bytes[1], bytes[2])
	if opc == 0x50:
		return decode_jnc(pc, opc, bytes[1])
	if opc == 0x70:
		return decode_jnz(pc, opc, bytes[1])
	if opc == 0x60:
		return decode_jz(pc, opc, bytes[1])
	if opc == 0x12:
		return decode_lcall(pc, opc, bytes[1], bytes[2])
	if opc == 0x02:
		return decode_ljmp(pc, opc, bytes[1], bytes[2])
	if opc == 0x90:
		return decode_mov_dptr_imm16(pc, opc, bytes[1], bytes[2])
	if opc == 0x75:
		return decode_mov_iram_imm(pc, opc, bytes[1], bytes[2])
	if opc == 0x85:
		return decode_mov_iram_iram(pc, opc, bytes[1], bytes[2])
	if opc == 0x76 or opc == 0x77:
		return decode_mov_ind_imm(pc, opc, bytes[1])
	if opc == 0xF6 or opc == 0xF7:
		return decode_mov_ind_a(pc, opc)
	if opc == 0xA6 or opc == 0xA7:
		return decode_mov_ind_iram(pc, opc, bytes[1])
	if opc == 0x74:
		return decode_mov_a_imm(pc, opc, bytes[1])
	if opc >= 0xE6 and opc <= 0xE7:
		return decode_mov_a_ind(pc, opc)
	if opc >= 0xE8 and opc <= 0xEF:
		return decode_mov_a_reg(pc, opc)
	if opc == 0xE5:
		return decode_mov_a_iram(pc, opc, bytes[1])
	if opc == 0xA2:
		return decode_mov_c_bitaddr(pc, opc, bytes[1])
	if opc >=0x78 and opc <= 0x7F:
		return decode_mov_reg_imm(pc, opc, bytes[1])
	if opc >= 0xF8 and opc <= 0xFF:
		return decode_mov_reg_a(pc, opc)
	if opc >= 0xA8 and opc <= 0xAF:
		return decode_mov_reg_iram(pc, opc, bytes[1])
	if opc == 0x92:
		return decode_mov_bitaddr_c(pc, opc, bytes[1])
	if opc >= 0x86 and opc <= 0x87:
		return decode_mov_iram_ind(pc, opc, bytes[1])
	if opc >= 0x88 and opc <= 0x8F:
		return decode_mov_iram_reg(pc, opc, bytes[1])
	if opc == 0xF5:
		return decode_mov_iram_a(pc, opc, bytes[1])
	if opc == 0x93 or opc == 0x83:
		return decode_movc(pc, opc)
		
	if opc >= 0xF0 and opc <= 0xF3:
		return decode_movx_ind_a(pc, opc)
	if opc >= 0xE0 and opc <= 0xE3:
		return decode_movx_a_ind(pc, opc)
		
	if opc == 0xA4:
		return decode_mul(pc, opc)
	if opc == 0x00:
		return decode_nop(pc, opc)
	if opc == 0x42:
		return decode_orl_iram_a(pc, opc, bytes[1])
	if opc == 0x43:
		return decode_orl_iram_imm(pc, opc, bytes[1], bytes[2])
	if opc == 0x44:
		return decode_orl_a_imm(pc, opc, bytes[1])
	if opc == 0x45:
		return decode_orl_a_iram(pc, opc, bytes[1])
	if opc >= 0x46 and opc <= 0x47:
		return decode_orl_a_ind(pc, opc)
	if opc >= 0x48 and opc <= 0x4F:
		return decode_orl_a_reg(pc, opc)
	if opc == 0x72 or opc == 0xA0:
		return decode_orl_c(pc, opc, bytes[1])
	if opc == 0xC0:
		return decode_push(pc, opc, bytes[1])
	if opc == 0xD0:
		return decode_pop(pc, opc, bytes[1])
	if opc == 0x22:
		return decode_ret(pc, opc)
	if opc == 0x32:
		return decode_reti(pc, opc)
	if opc == 0x23:
		return decode_generic_rotate(pc, opc)
	if opc == 0x33:
		return decode_generic_rotate(pc, opc)
	if opc == 0x03:
		return decode_generic_rotate(pc, opc)
	if opc == 0x13:
		return decode_generic_rotate(pc, opc)
	if opc == 0xD3:
		return decode_setb_c(pc, opc)
	if opc == 0xD2:
		return decode_setb_bitaddr(pc, opc, bytes[1])
	if opc == 0x80:
		return decode_sjmp(pc, opc, bytes[1])
	if opc == 0x94:
		return decode_subb_imm(pc, opc, bytes[1])
	if opc == 0x95:
		return decode_subb_iram(pc, opc, bytes[1])
	if opc >= 0x96 and opc <= 0x97:
		return decode_subb_ind(pc, opc)
	if opc >= 0x98 and opc <= 0x9F:
		return decode_subb_reg(pc, opc)
	if opc == 0xC4:
		return decode_swap(pc, opc)
	if opc == 0xA5:
		return None
	if opc >= 0xC6 and opc <= 0xC7:
		return decode_xch_ind(pc, opc)
	if opc >= 0xC8 and opc <= 0xCF:
		return decode_xch_reg(pc, opc)
	if opc == 0xC5:
		return decode_xch_iram(pc, opc, bytes[1])
	if opc == 0xD6 or opc == 0xD7:
		return decode_xchd_ind(pc, opc)
	if opc == 0x62:
		return decode_xrl_iram_a(pc, opc, bytes[1])
	if opc == 0x63:
		return decode_xrl_iram_imm(pc, opc, bytes[1], bytes[2])
	if opc == 0x64:
		return decode_xrl_a_imm(pc, opc, bytes[1])
	if opc == 0x65:
		return decode_xrl_a_iram(pc, opc, bytes[1])
	if opc >= 0x66 and opc <= 0x67:
		return decode_xrl_a_ind(pc, opc)
	if opc >= 0x68 and opc <= 0x6F:
		return decode_xrl_a_reg(pc, opc)

	raise NotImplementedError, "Opcode %02x" % opc
