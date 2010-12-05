import sys

from idis.datastore import DataStore


ds = DataStore(sys.argv[1])

location = ds[int(sys.argv[2], 0)]

print """
Address: %04x
length: %d
TypeClass: %s
TypeName: %s""" % (location.addr, location.length, location.typeclass, location.typename)
