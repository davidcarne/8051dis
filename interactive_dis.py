#!/usr/bin/python

import curses
import curses.ascii
import curses.textpad

import traceback
import cPickle
import sqlite3

COLOR_BLACK_ON_WHITE  = 5
COLOR_YELLOW_ON_BLUE  = 4
COLOR_GREEN_ON_BLUE  = 3
COLOR_CYAN_ON_BLUE  = 2
COLOR_WHITE_ON_BLUE = 1



IND_ADDR = 0
IND_XREF = 1
IND_COMMENT = 2
IND_LABEL = 3

IND_DISASM_OPC = 4
IND_DISASM_PUNC = 5
IND_DISASM_CONSTANT = 6

IND_HSEL = 10

class MemoryInfo:
	def __init__(self, label, addr, length, disasm, comment = "", xrefs=[]):
		self.label = label
		self.addr = addr
		self.length = 3
		self.disasm = disasm
		self.comment = comment
		self.xrefs = xrefs

example_display = {
		0: MemoryInfo("_start", 0x0, 0x3, "mov\tdptr, 0x1234", "load 1234 into dptr\nThis is important",[1,2]),
		3: MemoryInfo(None, 0x3, 0x1, "movx\t@dptr, r0")
		}

class AssemblerDisplay:
	def __init__(self, scr, datasource):
		self.scr = scr
		self.datasource = datasource
		self.colors_nohil = {

				IND_ADDR: (curses.color_pair(COLOR_CYAN_ON_BLUE)),
				IND_COMMENT: (curses.color_pair(COLOR_WHITE_ON_BLUE)),
				IND_LABEL: (curses.color_pair(COLOR_GREEN_ON_BLUE)),
				IND_XREF: (curses.color_pair(COLOR_GREEN_ON_BLUE)),

				IND_DISASM_OPC: (curses.color_pair(COLOR_YELLOW_ON_BLUE)),
				IND_DISASM_OPC: (curses.color_pair(COLOR_WHITE_ON_BLUE)),
				IND_DISASM_OPC: (curses.color_pair(COLOR_GREEN_ON_BLUE)),
				}
		self.colors_hil = {
				IND_HSEL: curses.color_pair(COLOR_WHITE_ON_BLUE)  | curses.A_BOLD |curses.A_STANDOUT,

				IND_ADDR: (curses.color_pair(COLOR_CYAN_ON_BLUE) | curses.A_BOLD),
				IND_COMMENT: (curses.color_pair(COLOR_WHITE_ON_BLUE) | curses.A_BOLD),
				IND_LABEL: (curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD),
				IND_XREF: (curses.color_pair(COLOR_GREEN_ON_BLUE) | curses.A_BOLD),

				
				IND_DISASM_OPC: (curses.color_pair(COLOR_YELLOW_ON_BLUE)) | curses.A_BOLD,
				IND_DISASM_OPC: (curses.color_pair(COLOR_WHITE_ON_BLUE)) | curses.A_BOLD,
				IND_DISASM_OPC: (curses.color_pair(COLOR_GREEN_ON_BLUE)) | curses.A_BOLD,
				}

		self.scr.bkgd(' ', self.colors_nohil[IND_ADDR])

	addrCol = 2
	labelCol = 8
	disasmCol = 16
	commentCol = 60
	xrefCol = 40
	def drawMem(self, line, meminfo, selected, spaceLeft):
		# Structure
		#
		#
		# xxxx              xref
		# xxxx              xref
		# xxxx  label:      xref
		# xxxx     disassembly       ; comment
		# xxxx                       ; continued comment

		
		if not meminfo.comment:
			formatted_comment = []
		else:
			formatted_comment = meminfo.comment.strip().split('\n')

		linesNeeded = 1
		lengthOfComment = len(formatted_comment)
		labelLineNeeded = 1 if meminfo.label else 0
		xrefLines = len(meminfo.xrefs)
		if (lengthOfComment > 1): linesNeeded += lengthOfComment - 1
		linesNeeded += max(labelLineNeeded, xrefLines)
		
		
		y,x = self.scr.getmaxyx()
		lcol = self.colors_hil if selected else self.colors_nohil

		linesToDraw = min(spaceLeft, linesNeeded)

		# Draw the highlighted background
		if (selected):
			for i in xrange(linesToDraw):
				self.scr.addstr(line+i,1, " " * (x-2), lcol[IND_ADDR])
				self.scr.addch(line+i,1, '!', lcol[IND_HSEL])

		# Draw the address for each line
		for i in xrange(linesToDraw):
			self.scr.addstr(line+i,self.addrCol, "%04X" % meminfo.addr, lcol[IND_ADDR])

		if meminfo.xrefs:
			for lnum,xref in enumerate(meminfo.xrefs):
				if lnum > linesToDraw: break
				self.scr.addstr(line + lnum, self.xrefCol,"[xref %s]"%xref, lcol[IND_XREF])

		if meminfo.label:
			if meminfo.xrefs:
				lineToDrawLabelOn = len(meminfo.xrefs) - 1
			else:
				lineToDrawLabelOn = 0
			if lineToDrawLabelOn > linesToDraw: return linesToDraw
			
			self.scr.addstr(line + lineToDrawLabelOn, self.labelCol,"%s:" % meminfo.label , lcol[IND_LABEL])


		# Draw the disassembly
		disasmLine =  max(labelLineNeeded, xrefLines)
		if disasmLine > linesToDraw:
			return linesToDraw
		self.scr.addstr(line + disasmLine, self.disasmCol, meminfo.disasm , lcol[IND_DISASM_OPC])

		# Draw the comment
		for lnum, cline in enumerate(formatted_comment):
			lnum += disasmLine
			if lnum > linesToDraw: return linesToDraw
			self.scr.addstr(line + lnum, self.commentCol,"; %s" % cline , lcol[IND_COMMENT])

		return linesToDraw

	def redraw(self, seladdr):
		self.scr.erase()
		self.scr.border()
		y,x = self.scr.getmaxyx()
		i=1
		base_addr = 0

		addr = base_addr
		while i < y-1:
			if not addr in self.datasource: break
			i += self.drawMem(i, self.datasource[addr], addr == seladdr, y-1-i)
			addr += self.datasource[addr].length




def takeInput(win, orig, lines=4):
	ns = { "altIsDown": False}


	curses.curs_set(1)
	width = 40
	y,x = win.getmaxyx()
	newwin = win.derwin(lines, 40, y/2-lines/2, (x-width)/2)
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


def main():
	ds = example_display
   	curses.init_pair(COLOR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_CYAN_ON_BLUE, curses.COLOR_CYAN, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_GREEN_ON_BLUE, curses.COLOR_GREEN, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_YELLOW_ON_BLUE, curses.COLOR_YELLOW, curses.COLOR_BLUE)
   	curses.init_pair(COLOR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
	
	curses.curs_set(0)

	#(y,x) = 
	#asm_win = curses.newwin(
	db = AssemblerDisplay(stdscr, ds)

	seladdr = 0
	while 1:
		db.redraw(seladdr)
		stdscr.refresh()
		c=stdscr.getch()
		if 0<c<256:
			c=chr(c)
			# Q or q exits
			if c in 'Qq': break

			if c == ";":	
				ds[seladdr].comment = takeInput(stdscr, ds[seladdr].comment, 4)

			if c == "l":	
				lstr = ds[seladdr].label
				if not lstr: lstr = ""
				ds[seladdr].label = takeInput(stdscr, lstr, 1)

		elif c == curses.KEY_RESIZE:
			pass
		elif c == curses.KEY_DOWN:
			next_addr = ds[seladdr].length + seladdr
			if next_addr in ds:
				seladdr = next_addr
		elif c == curses.KEY_UP:
			i = seladdr - 1
			while i >= 0:
				if i in ds:
					seladdr = i
					break
				i -= 1

		


if __name__ == '__main__':
	try:
		stdscr = curses.initscr()
		curses.start_color()
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(1)

		main()
		
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
