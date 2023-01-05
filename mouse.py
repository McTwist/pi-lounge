
from .event import EventHandler, EventManager, EventTypes

class Mouse(EventHandler):
	"""
	Keeps track of a mouse.
	"""
	def __init__(self, dev, callback):
		self.callback = callback
		super().__init__(dev)

	def event(self, tv_sec, tv_usec, evtype, code, value):
		if evtype == EventTypes.EV_KEY or evtype == EventTypes.EV_REL:
			self.callback(code, value)

class MiceManager(EventManager):
	"""
	Keep track of mice.
	"""
	def __init__(self, callback):
		super().__init__(lambda dev: Mouse(dev, callback))

	def is_device(self, dev):
		return dev.endswith("-event-mouse")

	def get_path(self):
		return "/dev/input/by-path"
