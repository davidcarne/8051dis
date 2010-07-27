import curses

bgattr = 0
fldattr = 0
badfldattr = 0

def intValidator(x):
	try:
		int(x,0)
	except ValueError:
		return False
	return True

class InputField:
	def __init__(self, destname, caption, default = "", validator = None):
		self.destname = destname
		self.caption = caption
		self.validator = validator
		self.valuestr = default

		if (validator):
			self.isValid = validator(default)
		else:
			self.isValid = True
	
	def update(self, value):
		self.valuestr = value
		if (self.validator):
			self.isValid = self.validator(self.valuestr)

def createInputField(a):
	if type(a) == tuple:
		return InputField(a[0], a[1])
	return a

FLD_SUBMIT = -1
FLD_CANCEL = -2
class InputDialog:
	def __init__(self, pwnd, attrs, desired_w = -1, desired_h = None, fld_w=30):
		self.attrs = [createInputField(i) for i in attrs]
		self.bgattr = bgattr
		self.fldattr = fldattr
		self.badfldattr = badfldattr
		self.fld_w = fld_w 

		self.lines = lines = len(attrs)+4
		if (desired_h != -1):
			lines = min(lines, desired_h)
		
		self.caption_width = max([len(i.caption) for i in self.attrs])

		width = self.caption_width + 5 + fld_w
		width = max(width,23)
		
		self.btnOffset = width - 20

		y,x = pwnd.getmaxyx()
		self.newwin = pwnd.derwin(lines, width, y/2-lines/2, (x-width)/2)
		self.newwin.bkgd(bgattr)
		self.newwin.keypad(1)

		
		self.fld_offs = 3 + self.caption_width

		self.cursor_fld = 0
		self.cursor_x = 0

	def redraw(self):
		
		self.newwin.border()
		
		for line,attr in enumerate(self.attrs):
			self.newwin.addstr(line+1,2, "%*s" % (self.caption_width, attr.caption))
			self.newwin.addstr(line+1,self.fld_offs, "%-*s" %(self.fld_w, attr.valuestr), self.fldattr if attr.isValid else self.badfldattr)

		
		self.newwin.addstr(self.lines - 2, self.btnOffset, "[cancel]", self.fldattr if self.cursor_fld == FLD_CANCEL else self.bgattr)
		self.newwin.addstr(self.lines - 2, self.btnOffset+9, "[submit]", self.fldattr if self.cursor_fld == FLD_SUBMIT else self.bgattr)
		self.newwin.refresh()
		
		self.updateCursor()

	def updateCursor(self):
		if self.cursor_fld < 0:		
			curses.curs_set(0)
			return
		
		if self.cursor_x > len(self.attrs[self.cursor_fld].valuestr):
			self.cursor_x = len(self.attrs[self.cursor_fld].valuestr)

		curses.curs_set(1)
		cy = self.cursor_fld + 1

		#print "Cursor at %d %d" % (cy,cx)
		self.newwin.move(cy,self.cursor_x + self.fld_offs)

	def runloop(self):
		
		curses.curs_set(1)
		self.updateCursor()
		while 1:
			self.redraw()

			c = self.newwin.getch()

			if c == 0x7F: c = curses.ascii.BS

			#print c,
			if 0 < c < 256:
				if c == 10 and self.cursor_fld == FLD_CANCEL:
					self.cancelled = True
					return
				
				if c == 10 and self.cursor_fld == FLD_SUBMIT:
					self.cancelled = False
					return
				
				if c == curses.ascii.ESC:
					self.cancelled = True
					return
				
				if c == curses.ascii.BS:
					if self.cursor_x > 0 :
						self.cursor_x -= 1
						self.attrs[self.cursor_fld].update(self.attrs[self.cursor_fld].valuestr[:self.cursor_x] + \
							self.attrs[self.cursor_fld].valuestr[self.cursor_x+1:])

				elif c == curses.ascii.TAB:
					
					if (self.cursor_fld == FLD_SUBMIT):
						self.cursor_fld = FLD_CANCEL
					elif (self.cursor_fld == FLD_CANCEL):
						self.cursor_fld = 0
					else:
						self.cursor_fld += 1

					if (self.cursor_fld == len(self.attrs)):
						self.cursor_fld = FLD_SUBMIT

				elif curses.ascii.isprint(c):
					self.attrs[self.cursor_fld].update(self.attrs[self.cursor_fld].valuestr[:self.cursor_x] + \
						chr(c) + self.attrs[self.cursor_fld].valuestr[self.cursor_x+1:])
					if self.cursor_x < self.fld_w - 1:
						self.cursor_x += 1
					
			elif c == curses.KEY_LEFT:
				if (self.cursor_fld == FLD_SUBMIT):
					self.cursor_fld = FLD_CANCEL
				elif self.cursor_x > 0 :
					self.cursor_x -= 1

			elif c == curses.KEY_RIGHT:
				if self.cursor_fld == FLD_CANCEL:
					self.cursor_fld = FLD_SUBMIT
				elif self.cursor_x < self.fld_w - 1:
					self.cursor_x += 1

			elif c == curses.KEY_UP:
				#print "UP",
				if (self.cursor_fld < 0):
					self.cursor_fld = len(self.attrs) - 1
				elif self.cursor_fld == 0:
					self.cursor_fld = FLD_SUBMIT
				else:
					self.cursor_fld -= 1
			elif c == curses.KEY_DOWN:
				#print "DOWN",
				if (self.cursor_fld == FLD_SUBMIT):
					self.cursor_fld = 0
				else:
					self.cursor_fld += 1

				if (self.cursor_fld == len(self.attrs)):
					self.cursor_fld = FLD_SUBMIT
		
		curses.curs_set(0)




def doInputDialog(pwnd, attrs, desired_w = -1, desired_h = -1, fld_w=30):
	d = InputDialog(pwnd, attrs, desired_w, desired_h, fld_w)
	d.runloop()

	if d.cancelled:
		return None
	return dict( [ (a.destname, a.valuestr) for a in d.attrs ] )


