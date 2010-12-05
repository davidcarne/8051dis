#!/usr/bin/python


import os
import os.path
import sys
import time

sys.path += [
		os.path.dirname(sys.path[0]) 
			]



import idis
import idis.tools
from idis.datastore import DataStore
import arch

testfile = '/tmp/basic_test_name'
try:
	os.unlink(testfile)
except OSError: pass

ds = DataStore(testfile)

my_dir = os.path.dirname(sys.argv[0])

testfile_path = my_dir + "/src/8051_flash_trunc.bin"


startTime = time.time()
print "Starting tests at time %f" % startTime

idis.tools.addBinary(ds, testfile_path, 0x0, 0x8000, 0x7E00)

ds.flush()

midTime = time.time()
print "Loading binary took %f seconds" % (midTime - startTime)


runtime_arch = arch.architectureFactory('8051')
idis.tools.codeFollow(ds, runtime_arch, 0x0)

ds.flush()

endTime = time.time()

print "Time taken: %f seconds" % (endTime - startTime)
print """Updates: %d
Inserts: %d
Deletes: %d
Commits: %d
Meminfo fetches: %d
         misses: %d (%f)
       failures: %d (%f)""" % (ds.updates, ds.inserts, ds.deletes, ds.commits, ds.meminfo_fetches,
	ds.meminfo_misses, float(ds.meminfo_misses) / ds.meminfo_fetches,
	ds.meminfo_failures, float(ds.meminfo_failures) / ds.meminfo_fetches)

print str(ds[0].disasm)