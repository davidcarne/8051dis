#!/usr/bin/python

import curses
import curses.ascii
import curses.textpad

import cursG.dialog

import traceback

from idis.datastore import DataStore
import idis.tools

COLOR_RED_ON_BLUE = 6
COLOR_RED_ON_WHITE = 6
COLOR_BLACK_ON_WHITE  = 5
COLOR_YELLOW_ON_BLUE  = 4
COLOR_GREEN_ON_BLUE  = 3
COLOR_CYAN_ON_BLUE  = 2
COLOR_WHITE_ON_BLUE = 1

from asmDisplayWindow import *



def takeInput(win, orig, lines=4):
	ns = { "altIsDown": False}


	curses.curs_set(1)
	width = 40
	y,x = win.getmaxyx()
	newwin = win.derwin(lines, 40, y/2-lines/2, (x-width)/2)
	newwin.clear()
	newwin.bkgd(' ', curses.color_pair(COLOR_BLACK_ON_WHITE))
	newwin.addstr(orig)
	tb = curses.textpad.Textbox(newwin)

	def inputValidator(ch):
		if (ch) == 27:
			ns["altIsDown"] = True
			return
	
		if ch == curses.ascii.DEL:
			if ns["altIsDown"]:
				newwin.erase()
			else:
				return curses.ascii.BS

		# enter terminates
		if ch == 10 and not ns["altIsDown"]:
			return curses.ascii.BEL

		ns["altIsDown"] = False
		return ch

	res = tb.edit(inputValidator).strip()
	curses.curs_set(0)
	return res


def main(args):
	ds = DataStore(args[0])

   	curses.init_pair(COLOR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_CYAN_ON_BLUE, curses.COLOR_CYAN, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_GREEN_ON_BLUE, curses.COLOR_GREEN, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_YELLOW_ON_BLUE, curses.COLOR_YELLOW, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
   	curses.init_pair(COLOR_RED_ON_WHITE, curses.COLOR_RED, curses.COLOR_WHITE)
   	curses.init_pair(COLOR_RED_ON_BLUE, curses.COLOR_RED, curses.COLOR_BLUE)
	
	curses.curs_set(0)

	cursG.dialog.bgattr = curses.color_pair(COLOR_WHITE_ON_BLUE)
	cursG.dialog.fldattr = curses.color_pair(COLOR_BLACK_ON_WHITE)
	cursG.dialog.badfldattr = curses.color_pair(COLOR_RED_ON_WHITE)| curses.A_REVERSE

	#(y,x) = 
	#asm_win = curses.newwin(

	
	colors_nohil = {

			IND_ADDR: (curses.color_pair(COLOR_CYAN_ON_BLUE)),
			IND_COMMENT: (curses.color_pair(COLOR_WHITE_ON_BLUE)),
			IND_LABEL: (curses.color_pair(COLOR_GREEN_ON_BLUE)) | curses.A_BOLD,
			IND_XREF: (curses.color_pair(COLOR_GREEN_ON_BLUE)),

			IND_DISASM_OPC: (curses.color_pair(COLOR_WHITE_ON_BLUE)),
			IND_DISASM_PUNC: (curses.color_pair(COLOR_CYAN_ON_BLUE)),
			IND_DISASM_CONSTANT: (curses.color_pair(COLOR_GREEN_ON_BLUE)),

			IND_SRCMARK:curses.color_pair(COLOR_RED_ON_BLUE) | curses.A_BOLD,
			IND_DSTMARK:curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD,
			}
	colors_hil = {
			IND_HSEL: curses.color_pair(COLOR_WHITE_ON_BLUE)  | curses.A_BOLD,

			IND_ADDR: (curses.color_pair(COLOR_CYAN_ON_BLUE) | curses.A_BOLD),
			IND_COMMENT: (curses.color_pair(COLOR_WHITE_ON_BLUE) | curses.A_BOLD),
			IND_LABEL: (curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD),
			IND_XREF: (curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD),

			
			IND_DISASM_OPC: (curses.color_pair(COLOR_WHITE_ON_BLUE)) | curses.A_BOLD,
			IND_DISASM_PUNC: (curses.color_pair(COLOR_WHITE_ON_BLUE)) | curses.A_BOLD,
			IND_DISASM_CONSTANT: (curses.color_pair(COLOR_GREEN_ON_BLUE)) | curses.A_BOLD,

			
			IND_SRCMARK:curses.color_pair(COLOR_RED_ON_BLUE) | curses.A_BOLD,
			IND_DSTMARK:curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD,
			}

	db = AssemblerDisplay(stdscr, ds, colors_nohil, colors_hil)

	while 1:
		ds.flush()

		db.redraw()

		# HACK
		try:
			while db.seladdr > db.last_displayed_addr:
				db.window_base += ds[db.window_base].length
				db.redraw()
		except AttributeError:
			pass

		stdscr.refresh()
		c=stdscr.getch()
		if 0<c<256:
			c=chr(c)
			# Q or q exits
			if c in 'Qq': break
			if c == 'A':
				def fileExistsValidator(f):
					try:
						open(f,"r")
					except IOError:
						return False
					return True
				
				res = cursG.dialog.doInputDialog(stdscr, [
							cursG.dialog.InputField("fname","FileName", validator=fileExistsValidator)
							],
							fld_w = 80
							)

				if (res != None):
					idis.tools.addIHex(ds, res["fname"])


			if c == 'a':
				def fileExistsValidator(f):
					try:
						open(f,"r")
					except IOError:
						return False
					return True
				def intOrBlankValidator(f):
					return f == "" or cursG.dialog.intValidator(f)

				res = cursG.dialog.doInputDialog(stdscr, [
							cursG.dialog.InputField("fname","FileName", validator=fileExistsValidator),
							cursG.dialog.InputField("base","Base Address", "0x0", validator = cursG.dialog.intValidator),
							cursG.dialog.InputField("startoffs","Start offset", "0x0", validator = cursG.dialog.intValidator),
							cursG.dialog.InputField("length","Length to load", "", validator = intOrBlankValidator),
							],
							fld_w = 80
							)
				if (res != None):
					if res["length"] == "": length = -1
					else:                   length = int(res["length"],0)
					
					idis.tools.addBinary(ds, res["fname"], int(res["base"],0), int(res["startoffs"],0), length)


				ds.flush()

			if c == 'X':
				idis.tools.xrefsPass(ds)
			if c == 'L':
				idis.tools.labelsPass(ds)

			# The following commands require the line to be in the datastore
			if db.seladdr in ds:
				if c == '\n':
					naddr = idis.tools.follow(ds,db.seladdr)
					if naddr != None:
						db.seladdr = naddr
						db.window_base = db.seladdr

				if c == 'c':
					idis.tools.codeFollow(ds, db.seladdr)

				if c == 'v':
					d = ds[db.seladdr].cdict
					fields = [ cursG.dialog.InputField(i[0], i[0], str(i[1])) for i in d.iteritems() ]
					cursG.dialog.doInputDialog(stdscr, fields)
				if c == ";":	
					ds[db.seladdr].comment = takeInput(stdscr, ds[db.seladdr].comment, 4)

				if c == "l":	
					lstr = ds[db.seladdr].label
					if not lstr: lstr = ""
					ds[db.seladdr].label = takeInput(stdscr, lstr, 1)
		else:
			db.doCommand(c)


		



if __name__ == '__main__':
	import sys
	try:
		stdscr = curses.initscr()
		curses.start_color()
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(1)

		main(sys.argv[1:])
		
		curses.nocbreak();
		stdscr.keypad(0)
		curses.echo()
		
		print
		curses.endwin()
	except:
		curses.nocbreak();
		stdscr.keypad(0)
		curses.echo()
		curses.endwin()
		traceback.print_exc()
