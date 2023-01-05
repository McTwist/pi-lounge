
# CEC library
# https://github.com/trainman419/python-cec
try:
	import cec
except ImportError:
	cec = None
import threading

# Function requires a library
def require(lib, ret=None):
	def init(func):
		def f(*args, **kwargs):
			if not lib:
				return ret
			return func(*args, **kwargs)
		return f
	return init

# Finlux remote
# No idea if standard, and many keys are missing or blocked
class KeyCodes:
	KEY_OK = 0
	KEY_UP = 1
	KEY_DOWN = 2
	KEY_LEFT = 3
	KEY_RIGHT = 4
	KEY_MEDIA = 9
	KEY_MENU = 10
	KEY_TEXT = 11
	KEY_BACK = 13
	KEY_0 = 32
	KEY_1 = 33
	KEY_2 = 34
	KEY_3 = 35
	KEY_4 = 36
	KEY_5 = 37
	KEY_6 = 38
	KEY_7 = 39
	KEY_8 = 40
	KEY_9 = 41
	KEY_P_NEXT = 48
	KEY_P_PREV = 49
	KEY_SOURCE = 52
	KEY_INFO = 53
	KEY_PLAY = 68
	KEY_STOP = 69
	KEY_PAUSE = 70
	KEY_RECORD = 71
	KEY_REW = 72
	KEY_FORWARD = 73
	KEY_BLUE = 113
	KEY_RED = 114
	KEY_GREEN = 115
	KEY_YELLOW = 116

class Remote:
	"""
	Handle remote via CEC from HDMI.
	"""
	def __init__(self, callback):
		self.callback = callback
		self.__pause = False
		# Put in a thread to reduce boot time.
		# It takes time for the user to react anyway.
		@require(cec)
		def init():
			cec.init()
			cec.add_callback(self.keypress, cec.EVENT_KEYPRESS)
		threading.Thread(target=init).start()

	def pause(self):
		self.__pause = True
	def resume(self):
		self.__pause = False

	def keypress(self, event, keycode, duration):
		if self.__pause:
			return
		self.callback(keycode, duration == 0)

	def log(self, event, level, time, msg):
		pass

	def command(self, event, cmd_event, cmd):
		pass

	@require(cec)
	def is_on(self):
		dev = cec.Device(cec.CECDEVICE_TV)
		if dev:
			dev.is_on()
	@require(cec)
	def power_on(self):
		dev = cec.Device(cec.CECDEVICE_TV)
		if dev:
			dev.power_on()
	@require(cec)
	def standby(self):
		dev = cec.Device(cec.CECDEVICE_TV)
		if dev:
			dev.standby()

if __name__ == "__main__":
	def debug(keycode, value):
		print(keycode, value)
	remote = Remote(debug)
	while True:
		import time
		time.sleep(1)
