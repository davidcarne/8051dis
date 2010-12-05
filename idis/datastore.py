import sqlite3
from cPickle import loads, dumps
import zlib
from dbtypes import *
from arch.shared_mem_types import *



class DataStore:
	def __init__(self, filename):
		self.updates = 0
		self.inserts = 0
		self.deletes = 0
		self.commits = 0
		self.meminfo_misses = 0
		self.meminfo_fetches = 0
		self.meminfo_failures = 0
		
		self.conn = sqlite3.connect(filename)
		self.conn.execute("PRAGMA synchronous = OFF")
		self.conn.execute("PRAGMA journal_mode = OFF")
		self.c = self.conn.cursor()
		self.createTables()

		self.memory_info_cache = {}
		self.memory_info_insert_queue = {}
		
		self.segments_cache = []
		self.__populateSegments()
		
		self.memory_info_insert_queue = []
		self.memory_info_insert_queue_ignore = set()

	
	def addrs(self):
		self.flushInsertQueue()

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
				(addr		INTEGER CONSTRAINT addr_pk PRIMARY KEY,
				 length		INTEGER,
				 typeclass	VARCHAR(100),
				 typename	VARCHAR(100),
				 obj		BLOB )''')

		self.c.execute('''
			CREATE TABLE IF NOT EXISTS segments
				(base_addr INTEGER CONSTRAINT base_addr_pk PRIMARY KEY,
				obj BLOB)''')

	def __iter__(self):
		self.flushInsertQueue()
		
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
		self.flushInsertQueue()

		row = self.c.execute('''SELECT addr, length
					FROM memory_info 
					WHERE addr <= ? ORDER BY addr DESC LIMIT 1''',
				  (addr,)).fetchone()
		
		#print row
		# If we got no results - this would be the first, and therefore there is a default for it
		if not row:
			try:
				self.readBytes(addr, 1)
				return True
			except IOError:
				return False
		
		
		if row[0] == addr:
			return True
			
		#print row[0], row[1], addr
		# There is a row before and if addr is within the previous opcode, row doesn't exist
		if row[0] + row[1] > addr:
			return False
		
			
		# There's a default
		
		try:
			self.readBytes(addr, 1)
			return True
		except IOError:
			return False



	def createDefault(self, addr):
		try:
			mi = MemoryInfo.createFromDecoding(decode_numeric(self, addr))
		except IOError:
			raise KeyError
			
		mi.typeclass = "default"
		self[addr] = mi
		return mi
	
	
	def __getitem__(self, addr):
		self.meminfo_fetches += 1
		# See if the object is already around
		try:
			obj = self.memory_info_cache[addr]
			if obj == None:
				raise KeyError
			return obj

		except KeyError:
			self.flushInsertQueue()
		
			# No, fetch from DB
			row = self.c.execute('''SELECT * 
					FROM memory_info 
					WHERE addr <= ? ORDER BY addr DESC LIMIT 1''',
				  (addr,)).fetchone()
			
			if not row: 
				self.meminfo_failures += 1
				return self.createDefault(addr)
			
				
			if row[0] != addr:
				if row[0] + row[1] > addr:
					raise KeyError
				return self.createDefault(addr)
				

				
			self.meminfo_misses += 1
			
			obj = MemoryInfo("key", row[0], row[1], row[2], row[3], ds=self)
			
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

		if addr in self.memory_info_insert_queue_ignore:
			self.flushInsertQueue()
			
		self.memory_info_cache[addr] = v

		is_default = v.typeclass == "default"
		if is_default:
			return
			
		self.__queue_insert(addr, v)
		
	def __queue_insert(self, addr, v):
		# Not in cache, so save new obj in cache
		self.memory_info_insert_queue.append(addr)
		
		
	def __delitem__(self, addr):
	
		is_default = self.memory_info_cache[addr].typeclass == "default"
		
		try:
			del self.memory_info_cache[addr]
		except KeyError:
			pass

		self.deletes += 1
		#print "DELETE: %d" % self.deletes

		if is_default:
			return
			
		self.memory_info_insert_queue_ignore.update([addr])
		self.c.execute('''DELETE FROM memory_info WHERE addr=?''',
		   	  (addr,))

	def __changed(self, addr, value):
		self.updates += 1
		self.flushInsertQueue()
		
		self.c.execute('''UPDATE memory_info SET length=?, typeclass=?, typename=? WHERE addr=?''',
		   	  (value.length, value.typeclass, value.typename, addr))
		pass

	def flushInsertQueue(self):
		params = []
		for addr in self.memory_info_insert_queue:
			if addr in self.memory_info_insert_queue_ignore:
				continue
			obj = self.memory_info_cache[addr]
			param_l = (obj.addr, obj.length, obj.typeclass, obj.typename, None)
			params.append(param_l)

		self.memory_info_insert_queue_ignore = set()
		self.memory_info_insert_queue = []
		
		self.inserts += len(params)

		self.conn.executemany('''INSERT INTO memory_info(addr, length, typeclass, typename, obj) VALUES 
			(?,?,?,?,?)''',
			params
			)
		
	def flush(self):
		self.commits += 1
		self.conn.commit()

	def __del__(self):
		self.flush()
