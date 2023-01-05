
from .event import EventHandler, EventManager, EventTypes

# Note: Only used for gaming locally

class Keyboard(EventHandler):
	"""
	Keeps track of a keyboard.
	"""
	def __init__(self, dev, callback):
		self.callback = callback
		super().__init__(dev)

	def event(self, tv_sec, tv_usec, evtype, code, value):
		if evtype == EventTypes.EV_KEY:
			self.callback(code, value)
			print("Key: {}, {}".format(code, value))

class KeyboardManager(EventManager):
	"""
	Keeps track of keyboards.
	"""
	def __init__(self, callback):
		super().__init__(lambda dev: Keyboard(dev, callback))

	def is_device(self, dev):
		return dev.endswith("-event-kbd")

	def get_path(self):
		return "/dev/input/by-path"

# Tests
if __name__ == "__main__":
	import time
	def kbd_event(code, value):
		print("Keyboard: {} = {}".format(code, value))
	kbd_mngr = KeyboardManager(kbd_event)
	while True:
		time.sleep(10)
