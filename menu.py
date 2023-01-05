
import threading
import curses

class Menu:
	"""
	Keep track of the menu.
	"""
	def __init__(self):
		self.menu = {}
		self.curr = 0

	def __enter__(self):
		self.screen = curses.initscr()
		# Create colors
		curses.start_color()
		curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
		self.start()
		self.screen.keypad(True)

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.runner = False
		self.stop()
		self.screen.keypad(0)
		curses.endwin()

	def start(self):
		# Remove odd behavior
		self.screen.refresh()
		# Set flags
		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)

	def stop(self):
		curses.curs_set(1)
		curses.nocbreak()
		curses.echo()

	def sub_menu(self):
		return SubMenu(self)

	def pause(self):
		self.stop()

	def resume(self):
		self.start()
		self.screen.clear()
		self.screen.refresh()

class SubMenu:
	def __init__(self, parent):
		self.menu = []
		self.curr = 0
		self.parent = parent

	def get_parent(self):
		return self.parent

	def add(self, key, text, fn, default=False):
		if default:
			self.curr = len(self.menu)
		self.menu.append({
			"key": key,
			"text": text,
			"fn": fn
		})

	def update(self, i=None, key=None, text=None, fn=None):
		if key == None and text == None and fn == None:
			return
		if i == None or i < 0 or i >= len(self.menu):
			i = self.curr
		item = self.menu[i]
		if key:
			item["key"] = key
		if text:
			item["text"] = text
		if fn:
			item["fn"] = fn

	def clear(self):
		self.menu = []
		self.curr = 0

	def execute(self, fn=None):
		self.parent.screen.clear()
		self.parent.screen.refresh()
		(fn if fn else self.menu[self.curr]["fn"])()
		self.parent.screen.clear()

	def jump(self, dir):
		self.curr += dir
		self.curr = (self.curr + len(self.menu)) % len(self.menu)

	def next(self):
		self.jump(1)

	def prev(self):
		self.jump(-1)

	def draw(self):
		curses.curs_set(1) # Enable
		curses.curs_set(0) # Disable
		for i, item in enumerate(self.menu):
			key = item["key"]
			clr = 2 if i == self.curr else 1
			self.parent.screen.addstr(i, 0, "{}".format(key), curses.color_pair(clr))
			if item['text']:
				self.parent.screen.addstr(i, len(key), ": {}\n".format(item["text"]))
		self.parent.screen.refresh()
