import sqlite3
from cPickle import loads, dumps
import zlib
from dbtypes import *
from arch.shared_mem_types import *


class CommentList(object):
	def __init__(self, connection, table):
		self.conn = connection
		
	def __len__(self):
		return self.conn.execute('''SELECT COUNT(*) FROM comments''' % table).fetchall()[0]

	# Objects are only temporary, don't keep around
	def getComments(self, addr, position=None):
		if position == None:
			return self.conn.execute('''SELECT text, position FROM comments WHERE addr = ?''', (addr,)).fetchall()
		return self.conn.execute('''SELECT text FROM comments WHERE addr = ? AND position = ?''', (addr, position)).fetchone()
	
	def setComment(self, addr, text, position):
		self.conn.execute('''DELETE FROM comments WHERE addr=? AND position=?''',
		   	  (addr,position))
			  
		if text:
			self.conn.execute('''INSERT INTO comments (addr, text, position) VALUES (?,?,?)''',
				(addr,text,position))
				
class SymbolList(object):
	def __init__(self, connection, table):
		self.conn = connection
		
	def __len__(self):
		return self.conn.execute('''SELECT COUNT(*) FROM symbols''' % table).fetchall()[0]

	# Objects are only temporary, don't keep around
	def getSymbol(self, addr):
		try:
			return str(self.conn.execute('''SELECT name FROM symbols WHERE addr = ?''', (addr,)).fetchall()[0][0])
		except IndexError:
			return None
	
	def setSymbol(self, addr, text):
		self.conn.execute('''DELETE FROM symbols WHERE addr=?''',
		   	  (addr,))
			  
		if text:
			self.conn.execute('''INSERT INTO symbols (addr, name) VALUES (?,?)''',
				(addr,text))
			  
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
		self.c = self.conn.cursor()
		self.createTables()

		self.memory_info_cache = {}
		self.memory_info_insert_queue = {}
		
		self.segments_cache = []
		self.__populateSegments()
		
		self.memory_info_insert_queue = []
		self.memory_info_insert_queue_ignore = set()

		self.symbols = SymbolList(self.conn, "symbols")
		self.comments = CommentList(self.conn, "comments")
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
		# Attrs/obj is a dumped representation of a dict
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

		self.c.execute('''
			CREATE TABLE IF NOT EXISTS symbols
				(addr INTEGER CONSTRAINT base_addr_pk PRIMARY KEY,
				name VARCHAR(100),
				type INTEGER,
				attrs BLOB
				)''')
		
		
		self.c.execute('''
			CREATE TABLE IF NOT EXISTS comments
				(addr INTEGER,
				text VARCHAR(100),
				position INTEGER,
				CONSTRAINT pk PRIMARY KEY (addr,position)
				)''')

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
		mi.ds = self
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
			row = self.c.execute('''SELECT addr,length,typeclass,typename,obj 
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
			
			obj = MemoryInfo("key", row[0], row[1], row[2], row[3], persist_attribs=loads(str(row[4])), ds=self)
			
			obj.ds_link = self.__changed
			obj.ds = self
			
			self.memory_info_cache[addr] = obj
			assert obj.addr == addr
			return obj

	def __setitem__(self, addr, v):
		v.ds = self
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
		
		self.c.execute('''UPDATE memory_info SET length=?, typeclass=?, typename=?, obj=? WHERE addr=?''',
		   	  (value.length, value.typeclass, value.typename, dumps(value.persist_attribs), addr))
		pass

	def flushInsertQueue(self):
		params = []
		for addr in self.memory_info_insert_queue:
			if addr in self.memory_info_insert_queue_ignore:
				continue
			obj = self.memory_info_cache[addr]
			param_l = (obj.addr, obj.length, obj.typeclass, obj.typename, dumps(obj.persist_attribs))
			params.append(param_l)

		self.memory_info_insert_queue_ignore = set()
		self.memory_info_insert_queue = []
		
		self.inserts += len(params)

		self.conn.executemany('''INSERT INTO memory_info(addr, length, typeclass, typename, obj) VALUES 
			(?,?,?,?,?)''',
			params
			)
		
	def flush(self):
		self.flushInsertQueue()
		self.commits += 1
		self.conn.commit()

	def __del__(self):
		self.flush()
