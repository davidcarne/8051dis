import sqlite3
from cPickle import loads, dumps
import zlib

class DataStore:
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)
		self.c = self.conn.cursor()
		self.createTables()

		self.memory_info_cache = {}

		self.segments_cache = []
		self.__populateSegments()

	
	def addrs(self):
		addrs = self.c.execute('''SELECT addr FROM memory_info ORDER BY addr ASC''').fetchall()
		return (i[0] for i in addrs)

	def __getSegments(self):
		return self.segments_cache

	segments = property(__getSegments)
	
	def __populateSegments(self):
		for i in self.c.execute('''SELECT obj  FROM segments'''):
			self.segments_cache.append(loads(zlib.decompress(i[0])))

	def addSegment(self, segment):
		self.segments_cache.append(segment)
		dbstr = sqlite3.Binary(zlib.compress(dumps(segment)))
		self.c.execute('''INSERT INTO segments (base_addr, obj) VALUES (?,?)''',
		   	  (segment.base_addr,dbstr))

	def readBytes(self, addr, length = 1):
		for i in self.segments_cache:
			try:
				return i.readBytes(addr, length)
			except IOError:
				pass
		raise IOError, "no segment could handle the requested read"

	def createTables(self):
		self.c.execute('''
			CREATE TABLE IF NOT EXISTS memory_info
				(addr INTEGER CONSTRAINT addr_pk PRIMARY KEY,
				obj BLOB)''')

		self.c.execute('''
			CREATE TABLE IF NOT EXISTS segments
				(base_addr INTEGER CONSTRAINT base_addr_pk PRIMARY KEY,
				obj BLOB)''')

	def __iter__(self):
		addrs = self.c.execute('''SELECT addr 
					FROM memory_info''').fetchall()
		addrs = [i[0] for i in addrs]

		class DataStoreIterator:
			def __init__(self, src, addrs):
				self.src = src
				self.addrs = addrs
			def next(self):
				if not self.addrs:
					raise StopIteration

				v = self.src[self.addrs[0]]
				self.addrs = self.addrs[1:]
				return v

		return DataStoreIterator(self, addrs)

	def __contains__(self, addr):
		if addr in self.memory_info_cache:
			return self.memory_info_cache[addr] != None

		row = self.c.execute('''SELECT COUNT(*) 
					FROM memory_info 
					WHERE addr = ?''',
				  (addr,)).fetchone()
		result = bool(row[0])

		if not result:
			self.memory_info_cache[addr] = None

		return result

	def __getitem__(self, addr):
		# See if the object is already around
		try:
			obj = self.memory_info_cache[addr]
			if obj == None:
				raise KeyError
			return obj

		except KeyError:
			# No, fetch from DB
			row = self.c.execute('''SELECT obj 
					FROM memory_info 
					WHERE addr = ?''',
				  (addr,)).fetchone()

			# Still no obj? can't get it
			if not row: raise KeyError

			# unpickle the object, and save in cache
			obj = loads(zlib.decompress(row[0]))
			obj.ds_link = self.__changed

			self.memory_info_cache[addr] = obj
			assert obj.addr == addr
			return obj

	def __setitem__(self, addr, v):
		v.ds_link = self.__changed
		assert v.addr == addr
		try:
			# If the object is in cache, and its the same object, skip write to DB
			existing_obj = self.memory_info_cache[addr]
			if existing_obj == v: return

			# Evict the current entry from the cache
			del self.memory_info_cache[addr]
		except KeyError:
			pass

		# Not in cache, so save new obj in cache
		self.memory_info_cache[addr] = v
		dbstr = sqlite3.Binary(zlib.compress(dumps(v)))
		self.c.execute('''INSERT INTO memory_info(addr, obj) VALUES (?,?)''',
		   	  (addr,dbstr))

	def __delitem__(self, addr):
		try:
			del self.memory_info_cache[addr]
		except KeyError:
			pass

		self.c.execute('''DELETE FROM memory_info WHERE addr=?''',
		   	  (addr,))

	def __changed(self, addr, value):
		
		try:
			dbstr = sqlite3.Binary(zlib.compress(dumps(value)))
		except TypeError as excpt:
			raise TypeError, "Obj was %x %s %s" %(value.addr, value.disasm, value.cdict["insn"])

		self.c.execute('''UPDATE memory_info SET obj=? WHERE addr=?''',
		   	  (dbstr,addr))
		pass

	def flush(self):
		self.conn.commit()

	def __del__(self):
		self.flush()
