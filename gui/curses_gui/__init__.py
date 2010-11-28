# This file is ugly - just a pile of hacks to maintain the old gui while I shift to the new one

COLOR_RED_ON_BLUE = 6
COLOR_RED_ON_WHITE = 6
COLOR_BLACK_ON_WHITE  = 5
COLOR_YELLOW_ON_BLUE  = 4
COLOR_GREEN_ON_BLUE  = 3
COLOR_CYAN_ON_BLUE  = 2
COLOR_WHITE_ON_BLUE = 1


import idis.tools
from idis.datastore import DataStore


import curses
import curses.ascii
import curses.textpad
from asmDisplayWindow import *
import cursG.dialog

import arch
# TODO: HACK: get architecture from doc / on startup
runtime_arch = arch.architectureFactory('8051')


canChangeCursorVisibility = False
def curses_set_cursor(vis):
	# TODO - query the cursor visibility at startup
	try:
		if canChangeCursorVisibility:
			curses.curs_set(vis)
	except:
		canChangeCursorVisibility = False

# yech - inject this
cursG.dialog.curses_set_cursor = curses_set_cursor


def takeInput(win, orig, lines=4):
	ns = { "altIsDown": False}
	
	curses_set_cursor(1)
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
	curses_set_cursor(0)
	return res



class CursesGui(object):

	def __init__(self):
		self.needs_cleanup = False
		pass
	
	def __graceful_cleanup(self):
		if self.needs_cleanup:
			curses.nocbreak();
			self.stdscr.keypad(0)
			curses.echo()
			curses.endwin()
			self.needs_cleanup = False
		raise
		
	def startup(self):
		try:
			self.needs_cleanup = True;
			self.stdscr = curses.initscr()
			curses.start_color()
			curses.noecho()
			curses.cbreak()
			self.stdscr.keypad(1)
		
			curses.init_pair(COLOR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
			curses.init_pair(COLOR_CYAN_ON_BLUE, curses.COLOR_CYAN, curses.COLOR_BLUE)
			curses.init_pair(COLOR_GREEN_ON_BLUE, curses.COLOR_GREEN, curses.COLOR_BLUE)
			curses.init_pair(COLOR_YELLOW_ON_BLUE, curses.COLOR_YELLOW, curses.COLOR_BLUE)
			curses.init_pair(COLOR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
			curses.init_pair(COLOR_RED_ON_WHITE, curses.COLOR_RED, curses.COLOR_WHITE)
			curses.init_pair(COLOR_RED_ON_BLUE, curses.COLOR_RED, curses.COLOR_BLUE)
			
		except:
			self.__graceful_cleanup()
			
	def mainloop(self, filenames):
		if (len(filenames) < 1):
			self.shutdown()
			print "usage: idis filename"
			return
			
		ds = DataStore(filenames[0])
		try:
			# Setup a few more params [move to init?]
			curses_set_cursor(0)
			cursG.dialog.bgattr = curses.color_pair(COLOR_WHITE_ON_BLUE)
			cursG.dialog.fldattr = curses.color_pair(COLOR_BLACK_ON_WHITE)
			cursG.dialog.badfldattr = curses.color_pair(COLOR_RED_ON_WHITE)| curses.A_REVERSE

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
			
			display_win = AssemblerDisplay(self.stdscr, ds, colors_nohil, colors_hil)
			locations = []

			while 1:
				ds.flush()
				display_win.redraw()

				# HACK
				try:
					while display_win.seladdr > display_win.last_displayed_addr:
						display_win.window_base += ds[display_win.window_base].length
						display_win.redraw()
				except AttributeError:
					pass

				self.stdscr.refresh()
				c=self.stdscr.getch()
				if 0<c<256:
					c_h = c
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
						
						res = cursG.dialog.doInputDialog(self.stdscr, [
									cursG.dialog.InputField("fname","FileName", validator=fileExistsValidator)
									],
									fld_w = 80
									)

						if (res != None):
							idis.tools.addIHex(ds, res["fname"])

					

					if c == 'r':
						idis.tools.rebuild(ds, runtime_arch)
						
					if c == 'R':
						idis.tools.clean(ds)
					
					if c == 'g':
						
						res = cursG.dialog.doInputDialog(self.stdscr, [
									cursG.dialog.InputField("addr","Address", "0x%04x" % display_win.seladdr, validator=cursG.dialog.intValidator) ] )

						if res:	
							loc = int(res["addr"], 0)
							locations.append((display_win.seladdr, display_win.window_base))
							display_win.seladdr = loc
							display_win.window_base = loc

					if c_h == 0x7f:
						try:
							(display_win.seladdr, display_win.window_base) = locations.pop()
						except IndexError: pass

					if c == 'a':
						def fileExistsValidator(f):
							try:
								open(f,"r")
							except IOError:
								return False
							return True
						def intOrBlankValidator(f):
							return f == "" or cursG.dialog.intValidator(f)

						res = cursG.dialog.doInputDialog(self.stdscr, [
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
					if display_win.seladdr != None and display_win.seladdr in ds:
						if c == '\n':
							naddr = idis.tools.follow(ds,display_win.seladdr)
							if naddr != None:
								locations.append((display_win.seladdr, display_win.window_base))
								display_win.seladdr = naddr
								display_win.window_base = display_win.seladdr
						if c == 'u':
							idis.tools.undefine(ds, display_win.seladdr)

						if c == 'c':
							idis.tools.codeFollow(ds, runtime_arch, display_win.seladdr)

						if c == 's':
							idis.tools.decodeAs(ds, "astring", display_win.seladdr)
							
						if c == 'v':
							d = ds[display_win.seladdr].cdict

							#fields = [ cursG.dialog.InputField(i[0], i[0], str(i[1])) for i in d.iteritems() ]
							#cursG.dialog.doInputDialog(self.stdscr, fields)
							#takeInput(stdscr, ds[display_win.seladdr].comment, 4)

						if c == ";":	
							ds[display_win.seladdr].comment = takeInput(self.stdscr, ds[display_win.seladdr].comment, 4)

						if c == "l":	
							lstr = ds[display_win.seladdr].label
							if not lstr: lstr = ""
							ds[display_win.seladdr].label = takeInput(self.stdscr, lstr, 1)
				else:
					display_win.doCommand(c)

		except:
			self.__graceful_cleanup()
	
	
	def shutdown(self):
		if self.needs_cleanup:
			curses.nocbreak();
			self.stdscr.keypad(0)
			curses.echo()
			curses.endwin()
			self.needs_cleanup = False
			
	except_shutdown = shutdown	