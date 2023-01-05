
from .event import EventHandler, EventManager, EvenTypes, EventCodes

class Joystick(EventHandler):
	"""
	Keeps track of a joystick.
	"""
	def __init__(self, dev, callback):
		self.callback = callback
		super().__init__(dev)

	def event(self, tv_sec, tv_usec, evtype, code, value):
		if evtype == EventTypes.EV_KEY or evtype == EventTypes.EV_ABS:
			if (code >= EventCodes.BTN_JOYSTICK and code < EventCodes.KEY_OK) or
				(code >= EventCodes.ABS_X and code <= EventCodes.ABS_MAX):
				self.callback(code, value)

class JoystickManager(EventManager):
	"""
	Keeps track of joysticks.
	"""
	def __init__(self, callback):
		super().__init__(lambda dev: Joystick(dev, callback))

	def is_device(self, dev):
		# Note: Read the device data in order to determine if it is a controller
		return dev.startswidth("event")

	def get_path(self):
		return "/dev/input"
