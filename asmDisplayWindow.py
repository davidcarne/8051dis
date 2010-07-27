import curses
from  lib8051.decutils import PCJmpDestination

IND_ADDR = 0
IND_XREF = 1
IND_COMMENT = 2
IND_LABEL = 3

IND_DISASM_OPC = 4
IND_DISASM_PUNC = 5
IND_DISASM_CONSTANT = 6

IND_SRCMARK =11
IND_DSTMARK =12

IND_HSEL = 10


class AssemblerDisplay:
	def __init__(self, scr, datasource, colors_nohil, colors_hil):
		self.scr = scr
		self.datasource = datasource
		self.colors_nohil = colors_nohil
		self.colors_hil = colors_hil

		self.scr.bkgd(' ', self.colors_nohil[IND_ADDR])
		self.seladdr = None
		self.window_base = None

	addrCol = 2
	labelCol = 8
	opcodeCol = 16
	operandCol = 25
	commentCol = 60
	xrefCol = 40

	def doCommand(self, c):
		if c == curses.KEY_RESIZE:
			pass
		elif c == curses.KEY_DOWN:
			try:
				next_addr = self.datasource[self.seladdr].length + self.seladdr
				if next_addr in self.datasource:
					self.seladdr = next_addr

				if (self.seladdr > self.last_displayed_addr):
					self.window_base += self.datasource[self.window_base].length

			except KeyError: pass
		elif c == curses.KEY_UP:
			i = self.seladdr - 1
			while i >= 0:
				if i in self.datasource:
					self.seladdr = i
					break
				i -= 1
			
			if self.seladdr < self.window_base: self.window_base = self.seladdr
	
	def drawMem(self, line, meminfo, selected, src, dst, spaceLeft):
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
		labelLineNeeded = 2 if meminfo.label else 0
		xrefLines = len(meminfo.xrefs)
		if (xrefLines): xrefLines += 1

		if (lengthOfComment > 1): linesNeeded += lengthOfComment - 1
		linesNeeded += max(labelLineNeeded, xrefLines)
		
		
		y,x = self.scr.getmaxyx()
		lcol = self.colors_hil if selected else self.colors_nohil

		linesToDraw = min(spaceLeft, linesNeeded)

		# Draw the highlighted background
		if (selected):
			for i in xrange(linesToDraw):
				self.scr.addstr(line+i,1, " " * (x-2), lcol[IND_ADDR])
		
		for i in xrange(linesToDraw):
			if (selected): self.scr.addch(line+i,1, '!', lcol[IND_HSEL])
			elif (src): self.scr.addch(line+i,1, '-', lcol[IND_SRCMARK])
			elif (dst): self.scr.addch(line+i,1, '+', lcol[IND_DSTMARK])

		# Draw the address for each line
		for i in xrange(linesToDraw):
			self.scr.addstr(line+i,self.addrCol, "%04X" % meminfo.addr, lcol[IND_ADDR])

		if meminfo.xrefs:
			for lnum,xref in enumerate(meminfo.xrefs):
				if lnum > linesToDraw: break
				self.scr.addstr(line + lnum+1, self.xrefCol,"[xref %04x]"%xref, lcol[IND_XREF])

		if meminfo.label:
			if meminfo.xrefs:
				lineToDrawLabelOn = len(meminfo.xrefs) - 1 + 1
			else:
				lineToDrawLabelOn = 1
			if lineToDrawLabelOn > linesToDraw: return linesToDraw
			
			self.scr.addstr(line + lineToDrawLabelOn, self.labelCol,"%s:" % meminfo.label , lcol[IND_LABEL])


		# Draw the disassembly
		disasmLine =  max(labelLineNeeded, xrefLines)
		if disasmLine >= linesToDraw:
			return linesToDraw

		if type(meminfo.disasm) == str:
			raise ValueError, meminfo.disasm

		self.scr.addstr(line + disasmLine, self.opcodeCol, meminfo.disasm.opcode, lcol[IND_DISASM_OPC])

		cpos = self.operandCol
		first = True
		for i in meminfo.disasm.operands:
			if not first:
				self.scr.addstr(line + disasmLine, cpos, "," , lcol[IND_DISASM_PUNC])
				cpos += 2
			first = False


			toDraw = str(i)
			
			draw_col = lcol[IND_DISASM_OPC]

			if isinstance(i, PCJmpDestination):
				try:
					l = self.datasource[i.addr].label
					draw_col = lcol[IND_LABEL]
					if l: toDraw = l
				except KeyError: pass

			self.scr.addstr(line + disasmLine, cpos, toDraw , draw_col)

			cpos += len(toDraw)

		# Draw the comment
		for lnum, cline in enumerate(formatted_comment):
			lnum += disasmLine
			if lnum > linesToDraw: return linesToDraw
			self.scr.addstr(line + lnum, self.commentCol,"; %s" % cline , lcol[IND_COMMENT])
		return linesToDraw

	def redraw(self):
		self.scr.erase()
		self.scr.border()
		y,x = self.scr.getmaxyx()
		i=1

		try:
			seg = self.datasource.segments[0]
		except IndexError:
			return

		if self.window_base == None:
			self.window_base = seg.base_addr
			self.seladdr = self.window_base

		addr = self.window_base

		while i < y-1:
			try:
				line_data = self.datasource[addr]
			except:
				i += 1
				addr += 1
				continue
			sel = addr == self.seladdr

			try:
				src = addr in self.datasource[self.seladdr].xrefs
			except KeyError:
				src = False
			
			try:
				dst = addr in self.datasource[self.seladdr].cdict["insn"].dests
			except KeyError:
				dst = False
			
			i += self.drawMem(i, line_data, sel,src,dst, y-1-i)
			self.last_displayed_addr = addr
			addr += self.datasource[addr].length

