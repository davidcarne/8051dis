from dbtypes import *
from arch.shared_mem_types import *
	
def addBinary(ds, file, base_addr, start_offset, length):
	# Load the file
	file_data = [ord(i) for i in open(file).read()]

	if length == -1:
		end_offset = len(file_data)
		dis_len = len(file_data) - start_offset
	else:
		end_offset = start_offset + length
		dis_len = length

	seg = Segment(file_data[start_offset:end_offset], base_addr)
	ds.addSegment(seg)
	
def parseIhexLine(line):
	if line[0] != ':':
		print "Start char fail!"
		return
	bc = int(line[1:3], 16)
	addr = int(line[3:7], 16)
	rtype = int(line[7:9], 16)
	data = line[9:9 + 2 * bc]
	data = [int(data[i : i+2], 16) for i in xrange(0,len(data),2)] 
	ck = int(line[9 + 2 * bc: 9 + 2 * bc + 2], 16)

	if bc != len(data):
		print "data len fail!"
		return

	calcck = (0x100 - (sum([bc, addr & 0xFF, addr >> 8, rtype] + data) & 0xFF)) & 0xFF
	if calcck != ck:
		print data
		print "Checksum Fail, %02x = %02x!" % (calcck, ck)
		return

	return rtype, addr, data

def addIHex(ds, file):
	lines = open(file).readlines()

	recs = []
	for i in lines:
		record = parseIhexLine(i)
		if not record:
			print "Error parsing line %s" % i
		recs.append(record)
	
	addrs = [(addr, addr+len(data)) for rtype, addr, data in recs if rtype == 0x0]
	dmin = min([i[0] for i in addrs])
	dmax = max([i[1] for i in addrs])
	
	
	# build data array
	data = [0x0] * (dmax - dmin + 1)
	for rtype, addr, ldata in recs:
		if (rtype == 0x0):
			for offs, j in enumerate(ldata):
				data[offs + addr - dmin] = j
	
	seg = Segment(data, dmin)
	ds.addSegment(seg)

	createDefaults(ds, dmin, dmin + len(data))
