#!/usr/bin/python

import unittest
from idis.datastore import DataStore
from idis.dbtypes import Segment
from idis.tools import *

class basicSectionTestCase(unittest.TestCase):

	def test_notInDS(self):
		ds = DataStore(":memory:")
		self.assertEqual(False, 0 in ds)
		self.assertEqual(False, 1 in ds)
		self.assertEqual(False, -1 in ds)

	def test_inBasicDS(self):
		ds = DataStore(":memory:")
		seg = Segment([0,1,2,3,4,5,6,7], 0x0)
		ds.addSegment(seg)
		
		
		self.assertEqual(False, -1 in ds)
		self.assertEqual(True, 0 in ds)
		self.assertEqual(True, 1 in ds)
		self.assertEqual(True, 2 in ds)
		self.assertEqual(True, 3 in ds)
		self.assertEqual(True, 4 in ds)
		self.assertEqual(True, 5 in ds)
		self.assertEqual(True, 6 in ds)
		self.assertEqual(True, 7 in ds)
		self.assertEqual(False, 8 in ds)

	def test_inBasicDS(self):
		ds = DataStore(":memory:")
		seg = Segment([0,1,2,3,4,5,6,7], 0x0)
		ds.addSegment(seg)
		
		def fakeCallable():
			ds[-1]
		self.assertRaises(KeyError, fakeCallable)
		
		for i in xrange(0,8):
			ds[i]
			
		def fakeCallable():
			ds[8]
		self.assertRaises(KeyError, fakeCallable)
		

	def testUndefine(self):
		ds = DataStore(":memory:")
		seg = Segment([0,1,2,3,4,5,6,7], 0x0)
		ds.addSegment(seg)
		
		undefine(ds, 0)
		
					
if __name__ == '__main__':
	unittest.main()
