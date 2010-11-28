#!/usr/bin/python

################ PM hack #########################
import sys
def dbghook(type, value, tb):
	import traceback, pdb

	gui_instance.except_shutdown()
	
	traceback.print_exception(type, value, tb)

	print
	pdb.pm()
sys.excepthook = dbghook
############### END PM HACK ######################



import traceback
import sys
from idis.datastore import DataStore
import idis.tools


# HACK - differentiate gui types
import gui.curses_gui
gui_class = gui.curses_gui.CursesGui


# Handle args with optionparser
def main(args):
	global gui_instance
	filenames = args
	gui_instance = gui_class()


	# Run the gui
	gui_instance.startup()
	gui_instance.mainloop(filenames)
	gui_instance.shutdown()
		



if __name__ == '__main__':
	main(sys.argv[1:])
