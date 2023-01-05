
import os, struct, array
from fcntl import ioctl
from inotify_simple import INotify, flags
import threading

# Event manager and handler in order to handle devices in Linux.

# Source: https://github.com/torvalds/linux/blob/master/arch/alpha/include/uapi/asm/ioctl.h
# Defines and structs: https://github.com/torvalds/linux/blob/master/include/uapi/linux/input.h
# Reading the data: https://github.com/gvalkov/python-evdev/blob/5adc2abf1ec8a02c05c80cb1b3e34ba1d4237803/evdev/input.c
# Defines and stuff: https://github.com/kdart/pycopia/blob/master/core/pycopia/OS/Linux/event.py
# Not used: https://github.com/kdart/pycopia/blob/master/core/pycopia/OS/Linux/Input.py

# From <linux/input.h>

INPUT_PROP_POINTER = 0x00
INPUT_PROP_DIRECT = 0x01
INPUT_PROP_BUTTONPAD = 0x02
INPUT_PROP_SEMI_MT = 0x03
INPUT_PROP_TOPBUTTONPAD = 0x04
INPUT_PROP_POINTING_STICK = 0x05
INPUT_PROP_ACCELEROMETER = 0x06

class EventTypes:
	EV_SYN = 0x00
	EV_KEY = 0x01
	EV_REL = 0x02
	EV_ABS = 0x03
	EV_MSC = 0x04
	EV_SW = 0x05
	EV_LED = 0x11
	EV_SND = 0x12
	EV_REP = 0x14
	EV_FF = 0x15
	EV_PWR = 0x16
	EV_FF_STATUS = 0x17
	EV_MAX = 0x1f

class EventCodes:
	KEY_RESERVED = 0
	KEY_ESC = 1
	KEY_1 = 2
	KEY_2 = 3
	KEY_3 = 4
	KEY_4 = 5
	KEY_5 = 6
	KEY_6 = 7
	KEY_7 = 8
	KEY_8 = 9
	KEY_9 = 10
	KEY_0 = 11
	KEY_MINUS = 12
	KEY_EQUAL = 13
	KEY_BACKSPACE = 14
	KEY_TAB = 15
	KEY_Q = 16
	KEY_W = 17
	KEY_E = 18
	KEY_R = 19
	KEY_T = 20
	KEY_Y = 21
	KEY_U = 22
	KEY_I = 23
	KEY_O = 24
	KEY_P = 25
	KEY_LEFTBRACE = 26
	KEY_RIGHTBRACE = 27
	KEY_ENTER = 28
	KEY_LEFTCTRL = 29
	KEY_A = 30
	KEY_S = 31
	KEY_D = 32
	KEY_F = 33
	KEY_G = 34
	KEY_H = 35
	KEY_J = 36
	KEY_K = 37
	KEY_L = 38
	KEY_SEMICOLON = 39
	KEY_APOSTROPHE = 40
	KEY_GRAVE = 41
	KEY_LEFTSHIFT = 42
	KEY_BACKSLASH = 43
	KEY_Z = 44
	KEY_X = 45
	KEY_C = 46
	KEY_V = 47
	KEY_B = 48
	KEY_N = 49
	KEY_M = 50
	KEY_COMMA = 51
	KEY_DOT = 52
	KEY_SLASH = 53
	KEY_RIGHTSHIFT = 54
	KEY_KPASTERISK = 55
	KEY_LEFTALT = 56
	KEY_SPACE = 57
	KEY_CAPSLOCK = 58
	KEY_F1 = 59
	KEY_F2 = 60
	KEY_F3 = 61
	KEY_F4 = 62
	KEY_F5 = 63
	KEY_F6 = 64
	KEY_F7 = 65
	KEY_F8 = 66
	KEY_F9 = 67
	KEY_F10 = 68
	KEY_NUMLOCK = 69
	KEY_SCROLLLOCK = 70
	KEY_KP7 = 71
	KEY_KP8 = 72
	KEY_KP9 = 73
	KEY_KPMINUS = 74
	KEY_KP4 = 75
	KEY_KP5 = 76
	KEY_KP6 = 77
	KEY_KPPLUS = 78
	KEY_KP1 = 79
	KEY_KP2 = 80
	KEY_KP3 = 81
	KEY_KP0 = 82
	KEY_KPDOT = 83
	KEY_103RD = 84

	KEY_ZENKAKUHANKAKU = 85
	KEY_102ND = 86
	KEY_F11 = 87
	KEY_F12 = 88
	KEY_RO = 89
	KEY_KATAKANA = 90
	KEY_HIRAGANA = 91
	KEY_HENKAN = 92
	KEY_KATAKANAHIRAGANA = 93
	KEY_MUHENKAN = 94
	KEY_KPJPCOMMA = 95
	KEY_KPENTER = 96
	KEY_RIGHTCTRL = 97
	KEY_KPSLASH = 98
	KEY_SYSRQ = 99
	KEY_RIGHTALT = 100
	KEY_LINEFEED = 101
	KEY_HOME = 102
	KEY_UP = 103
	KEY_PAGEUP = 104
	KEY_LEFT = 105
	KEY_RIGHT = 106
	KEY_END = 107
	KEY_DOWN = 108
	KEY_PAGEDOWN = 109
	KEY_INSERT = 110
	KEY_DELETE = 111
	KEY_MACRO = 112
	KEY_MUTE = 113
	KEY_VOLUMEDOWN = 114
	KEY_VOLUMEUP = 115
	KEY_POWER = 116
	KEY_KPEQUAL = 117
	KEY_KPPLUSMINUS = 118
	KEY_PAUSE = 119

	KEY_KPCOMMA = 121
	KEY_HANGUEL = 122
	KEY_HANJA = 123
	KEY_YEN = 124
	KEY_LEFTMETA = 125
	KEY_RIGHTMETA = 126
	KEY_COMPOSE = 127

	KEY_STOP = 128
	KEY_AGAIN = 129
	KEY_PROPS = 130
	KEY_UNDO = 131
	KEY_FRONT = 132
	KEY_COPY = 133
	KEY_OPEN = 134
	KEY_PASTE = 135
	KEY_FIND = 136
	KEY_CUT = 137
	KEY_HELP = 138
	KEY_MENU = 139
	KEY_CALC = 140
	KEY_SETUP = 141
	KEY_SLEEP = 142
	KEY_WAKEUP = 143
	KEY_FILE = 144
	KEY_SENDFILE = 145
	KEY_DELETEFILE = 146
	KEY_XFER = 147
	KEY_PROG1 = 148
	KEY_PROG2 = 149
	KEY_WWW = 150
	KEY_MSDOS = 151
	KEY_COFFEE = 152
	KEY_DIRECTION = 153
	KEY_CYCLEWINDOWS = 154
	KEY_MAIL = 155
	KEY_BOOKMARKS = 156
	KEY_COMPUTER = 157
	KEY_BACK = 158
	KEY_FORWARD = 159
	KEY_CLOSECD = 160
	KEY_EJECTCD = 161
	KEY_EJECTCLOSECD = 162
	KEY_NEXTSONG = 163
	KEY_PLAYPAUSE = 164
	KEY_PREVIOUSSONG = 165
	KEY_STOPCD = 166
	KEY_RECORD = 167
	KEY_REWIND = 168
	KEY_PHONE = 169
	KEY_ISO = 170
	KEY_CONFIG = 171
	KEY_HOMEPAGE = 172
	KEY_REFRESH = 173
	KEY_EXIT = 174
	KEY_MOVE = 175
	KEY_EDIT = 176
	KEY_SCROLLUP = 177
	KEY_SCROLLDOWN = 178
	KEY_KPLEFTPAREN = 179
	KEY_KPRIGHTPAREN = 180

	KEY_F13 = 183
	KEY_F14 = 184
	KEY_F15 = 185
	KEY_F16 = 186
	KEY_F17 = 187
	KEY_F18 = 188
	KEY_F19 = 189
	KEY_F20 = 190
	KEY_F21 = 191
	KEY_F22 = 192
	KEY_F23 = 193
	KEY_F24 = 194

	KEY_PLAYCD = 200
	KEY_PAUSECD = 201
	KEY_PROG3 = 202
	KEY_PROG4 = 203
	KEY_SUSPEND = 205
	KEY_CLOSE = 206
	KEY_PLAY = 207
	KEY_FASTFORWARD = 208
	KEY_BASSBOOST = 209
	KEY_PRINT = 210
	KEY_HP = 211
	KEY_CAMERA = 212
	KEY_SOUND = 213
	KEY_QUESTION = 214
	KEY_EMAIL = 215
	KEY_CHAT = 216
	KEY_SEARCH = 217
	KEY_CONNECT = 218
	KEY_FINANCE = 219
	KEY_SPORT = 220
	KEY_SHOP = 221
	KEY_ALTERASE = 222
	KEY_CANCEL = 223
	KEY_BRIGHTNESSDOWN = 224
	KEY_BRIGHTNESSUP = 225
	KEY_MEDIA = 226
	KEY_SWITCHVIDEOMODE = 227
	KEY_KBDILLUMTOGGLE = 228
	KEY_KBDILLUMDOWN = 229
	KEY_KBDILLUMUP = 230
	KEY_SEND = 231
	KEY_REPLY = 232
	KEY_FORWARDMAIL = 233
	KEY_SAVE = 234
	KEY_DOCUMENTS = 235
	KEY_BATTERY = 236

	KEY_UNKNOWN = 240

	BTN_MISC = 0x100
	BTN_0 = 0x100
	BTN_1 = 0x101
	BTN_2 = 0x102
	BTN_3 = 0x103
	BTN_4 = 0x104
	BTN_5 = 0x105
	BTN_6 = 0x106
	BTN_7 = 0x107
	BTN_8 = 0x108
	BTN_9 = 0x109

	BTN_MOUSE = 0x110
	BTN_LEFT = 0x110
	BTN_RIGHT = 0x111
	BTN_MIDDLE = 0x112
	BTN_SIDE = 0x113
	BTN_EXTRA = 0x114
	BTN_FORWARD = 0x115
	BTN_BACK = 0x116
	BTN_TASK = 0x117

	BTN_JOYSTICK = 0x120
	BTN_TRIGGER = 0x120
	BTN_THUMB = 0x121
	BTN_THUMB2 = 0x122
	BTN_TOP = 0x123
	BTN_TOP2 = 0x124
	BTN_PINKIE = 0x125
	BTN_BASE = 0x126
	BTN_BASE2 = 0x127
	BTN_BASE3 = 0x128
	BTN_BASE4 = 0x129
	BTN_BASE5 = 0x12a
	BTN_BASE6 = 0x12b
	BTN_DEAD = 0x12f

	BTN_GAMEPAD = 0x130
	BTN_A = 0x130
	BTN_B = 0x131
	BTN_C = 0x132
	BTN_X = 0x133
	BTN_Y = 0x134
	BTN_Z = 0x135
	BTN_TL = 0x136
	BTN_TR = 0x137
	BTN_TL2 = 0x138
	BTN_TR2 = 0x139
	BTN_SELECT = 0x13a
	BTN_START = 0x13b
	BTN_MODE = 0x13c
	BTN_THUMBL = 0x13d
	BTN_THUMBR = 0x13e

	BTN_DIGI = 0x140
	BTN_TOOL_PEN = 0x140
	BTN_TOOL_RUBBER = 0x141
	BTN_TOOL_BRUSH = 0x142
	BTN_TOOL_PENCIL = 0x143
	BTN_TOOL_AIRBRUSH = 0x144
	BTN_TOOL_FINGER = 0x145
	BTN_TOOL_MOUSE = 0x146
	BTN_TOOL_LENS = 0x147
	BTN_TOUCH = 0x14a
	BTN_STYLUS = 0x14b
	BTN_STYLUS2 = 0x14c
	BTN_TOOL_DOUBLETAP = 0x14d
	BTN_TOOL_TRIPLETAP = 0x14e

	BTN_WHEEL = 0x150
	BTN_GEAR_DOWN = 0x150
	BTN_GEAR_UP = 0x151

	KEY_OK = 0x160
	KEY_SELECT  = 0x161
	KEY_GOTO = 0x162
	KEY_CLEAR = 0x163
	KEY_POWER2 = 0x164
	KEY_OPTION = 0x165
	KEY_INFO = 0x166
	KEY_TIME = 0x167
	KEY_VENDOR = 0x168
	KEY_ARCHIVE = 0x169
	KEY_PROGRAM = 0x16a
	KEY_CHANNEL = 0x16b
	KEY_FAVORITES = 0x16c
	KEY_EPG = 0x16d
	KEY_PVR = 0x16e
	KEY_MHP = 0x16f
	KEY_LANGUAGE = 0x170
	KEY_TITLE = 0x171
	KEY_SUBTITLE = 0x172
	KEY_ANGLE = 0x173
	KEY_ZOOM = 0x174
	KEY_MODE = 0x175
	KEY_KEYBOARD = 0x176
	KEY_SCREEN = 0x177
	KEY_PC = 0x178
	KEY_TV = 0x179
	KEY_TV2 = 0x17a
	KEY_VCR = 0x17b
	KEY_VCR2 = 0x17c
	KEY_SAT = 0x17d
	KEY_SAT2 = 0x17e
	KEY_CD = 0x17f
	KEY_TAPE = 0x180
	KEY_RADIO = 0x181
	KEY_TUNER = 0x182
	KEY_PLAYER = 0x183
	KEY_TEXT = 0x184
	KEY_DVD = 0x185
	KEY_AUX = 0x186
	KEY_MP3 = 0x187
	KEY_AUDIO = 0x188
	KEY_VIDEO = 0x189
	KEY_DIRECTORY = 0x18a
	KEY_LIST = 0x18b
	KEY_MEMO = 0x18c
	KEY_CALENDAR = 0x18d
	KEY_RED = 0x18e
	KEY_GREEN = 0x18f
	KEY_YELLOW = 0x190
	KEY_BLUE = 0x191
	KEY_CHANNELUP = 0x192
	KEY_CHANNELDOWN = 0x193
	KEY_FIRST = 0x194
	KEY_LAST = 0x195
	KEY_AB = 0x196
	KEY_NEXT = 0x197
	KEY_RESTART = 0x198
	KEY_SLOW = 0x199
	KEY_SHUFFLE = 0x19a
	KEY_BREAK = 0x19b
	KEY_PREVIOUS = 0x19c
	KEY_DIGITS = 0x19d
	KEY_TEEN = 0x19e
	KEY_TWEN = 0x19f

	KEY_DEL_EOL = 0x1c0
	KEY_DEL_EOS = 0x1c1
	KEY_INS_LINE = 0x1c2
	KEY_DEL_LINE = 0x1c3

	KEY_FN = 0x1d0
	KEY_FN_ESC = 0x1d1
	KEY_FN_F1 = 0x1d2
	KEY_FN_F2 = 0x1d3
	KEY_FN_F3 = 0x1d4
	KEY_FN_F4 = 0x1d5
	KEY_FN_F5 = 0x1d6
	KEY_FN_F6 = 0x1d7
	KEY_FN_F7 = 0x1d8
	KEY_FN_F8 = 0x1d9
	KEY_FN_F9 = 0x1da
	KEY_FN_F10 = 0x1db
	KEY_FN_F11 = 0x1dc
	KEY_FN_F12 = 0x1dd
	KEY_FN_1 = 0x1de
	KEY_FN_2 = 0x1df
	KEY_FN_D = 0x1e0
	KEY_FN_E = 0x1e1
	KEY_FN_F = 0x1e2
	KEY_FN_S = 0x1e3
	KEY_FN_B = 0x1e4

	KEY_MAX = 0x1ff

	REL_X = 0x00
	REL_Y = 0x01
	REL_Z = 0x02
	REL_RX = 0x03
	REL_RY = 0x04
	REL_RZ = 0x05
	REL_HWHEEL = 0x06
	REL_DIAL = 0x07
	REL_WHEEL = 0x08
	REL_MISC = 0x09
	REL_MAX = 0x0f

	ABS_X = 0x00
	ABS_Y = 0x01
	ABS_Z = 0x02
	ABS_RX = 0x03
	ABS_RY = 0x04
	ABS_RZ = 0x05
	ABS_THROTTLE = 0x06
	ABS_RUDDER = 0x07
	ABS_WHEEL = 0x08
	ABS_GAS = 0x09
	ABS_BRAKE = 0x0a
	ABS_HAT0X = 0x10
	ABS_HAT0Y = 0x11
	ABS_HAT1X = 0x12
	ABS_HAT1Y = 0x13
	ABS_HAT2X = 0x14
	ABS_HAT2Y = 0x15
	ABS_HAT3X = 0x16
	ABS_HAT3Y = 0x17
	ABS_PRESSURE = 0x18
	ABS_DISTANCE = 0x19
	ABS_TILT_X = 0x1a
	ABS_TILT_Y = 0x1b
	ABS_TOOL_WIDTH = 0x1c
	ABS_VOLUME = 0x20
	ABS_MISC = 0x28
	ABS_MAX = 0x3f

class EventLed:
	LED_NUML = 0x00
	LED_CAPSL = 0x01
	LED_SCROLLL = 0x02
	LED_COMPOSE = 0x03
	LED_KANA = 0x04
	LED_SLEEP = 0x05
	LED_SUSPEND = 0x06
	LED_MUTE = 0x07
	LED_MISC = 0x08
	LED_MAIL = 0x09
	LED_CHARGING = 0x0a
	LED_MAX = 0x0f

class EventBus:
	BUS_PCI = 0x01
	BUS_ISAPNP = 0x02
	BUS_USB = 0x03
	BUS_HIL = 0x04
	BUS_BLUETOOTH = 0x05

	BUS_ISA = 0x10
	BUS_I8042 = 0x11
	BUS_XTKBD = 0x12
	BUS_RS232 = 0x13
	BUS_GAMEPORT = 0x14
	BUS_PARPORT = 0x15
	BUS_AMIGA = 0x16
	BUS_ADB = 0x17
	BUS_I2C = 0x18
	BUS_HOST = 0x19
	BUS_GSC = 0x1A

class ForceFeedback:
	FF_RUMBLE = 0x50
	FF_PERIODIC = 0x51
	FF_CONSTANT = 0x52
	FF_SPRING = 0x53
	FF_FRICTION = 0x54
	FF_DAMPER = 0x55
	FF_INERTIA = 0x56
	FF_RAMP = 0x57
	FF_EFFECT_MIN = 0x50
	FF_EFFECT_MAX = 0x57

	FF_SQUARE = 0x58
	FF_TRIANGLE = 0x59
	FF_SINE = 0x5a
	FF_SAW_UP = 0x5b
	FF_SAW_DOWN = 0x5c
	FF_CUSTOM = 0x5d
	FF_WAVEFORM_MIN = 0x58
	FF_WAVEFORM_MAX = 0x5d

	FF_GAIN = 0x60
	FF_AUTOCENTER = 0x61

	FF_MAX_EFFEECTS = 0x60
	FF_MAX = 0x7f

class EventHandler:
	"""
	Keeps track of an event.
	"""
	def __init__(self, dev):
		self._dev = dev
		self._fd = open(dev, 'rb')
		self._input = struct.Struct('llHHi')
		# Start input thread
		self._wait = threading.Event()
		self._wait.set()
		self._runner = True
		self._thread = threading.Thread(target=self.loop, daemon=True)
		self._thread.start()

	@property
	def dev(self):
		return self._dev

	def close(self):
		self._runner = False
		self._wait.set()
		self._fd.close()
		self._thread.join()

	def pause(self):
		self._wait.clear()

	def resume(self):
		self._wait.set()

	def loop(self):
		try:
			with self._fd:
				self.get_info()
				while self._runner:
					self.read()
					self._wait.wait()
		except OSError:
			# Disconnected
			self._fd.close()

	def read(self):
		evbuf = self._fd.read(self._input.size)
		if not self._wait.is_set():
			return
		if not evbuf:
			return
		self.event(*self._input.unpack(evbuf))

	def event(self, tv_sec, tv_usec, evtype, code, value):
		pass

	def is_connected(self):
		return self._thread.is_alive()

	def get_info(self):
		"""
		Retrieves the information and stores it within the object.
		Normally should only be called once.
		Left out for performance reasons.
		"""
		### ioctl ###
		# Note: For Raspberry Pi, this is how it works
		# From kernel <uapi/linux/ioctl.h>
		_ioc_nrbits = 8
		_ioc_typebits = 8
		_ioc_sizebits = 14 # 13 in source, but libraries uses this one
		_ioc_dirbits = 2 # 3 in source, but libraries...

		_ioc_nrshift = 0
		_ioc_typeshift = _ioc_nrshift+_ioc_nrbits
		_ioc_sizeshift = _ioc_typeshift+_ioc_typebits
		_ioc_dirshift = _ioc_sizeshift+_ioc_sizebits

		# Other libraries starts at 0
		_ioc_none = 1
		_ioc_read = 2
		_ioc_write = 3

		_ioc = lambda dir, type, nr, size: (
			(dir << _ioc_dirshift) |
			(ord(type) << _ioc_typeshift) |
			(nr << _ioc_nrshift) |
			(size << _ioc_sizeshift))
		_ior = lambda type, nr, size: _ioc(_ioc_read, type, nr, size)
		_iow = lambda type, nr, size: _ioc(_ioc_write, type, nr, size)

		eviocgversion = _ior('E', 0x01, 4)
		eviocgid = _ior('E', 0x02, 8)
		eviocgrep = _ior('E', 0x03, 8)
		eviocsrep = _iow('E', 0x04, 8)
		eviocgname = lambda len: _ioc(_ioc_read, 'E', 0x06, len)
		eviocgphys = lambda len: _ioc(_ioc_read, 'E', 0x07, len)
		eviocguniq = lambda len: _ioc(_ioc_read, 'E', 0x08, len)
		eviocgprop = lambda len: _ioc(_ioc_read, 'E', 0x09, len)
		eviocgbit = lambda ev, len: _ioc(_ioc_read, 'E', 0x20 + (ev), len)
		eviocgabs = lambda abs: _ior('E', 0x40 + abs, 48)
		eviocsff = _iow('E', 0x80, 38)
		eviocrmff = _iow('E', 0x81, 4)
		eviocgeffects = _ior('E', 0x84, 4)
		eviocgrab = _iow('E', 0x90, 4)
		eviocrevoke = _iow('E', 0x91, 4)

		test_bit = lambda bitmask, bit: bitmask[bit//8] & (1 << (bit % 8))
		class AbsValues:
			minimum = 0
			maximum = 0
			fuzz = 0
			flat = 0
			resolution = 0
			def __init__(self, t):
				_, self.minimum, self.maximum, self.fuzz, self.flat, self.resolution = t
			def __repr__(self):
				return "({}, {}, {}, {}, {})".format(self.minimum, self.maximum, self.fuzz, self.flat, self.resolution)

		### Device info ###

		buf = array.array('H', [0] * 4)
		try:
			ioctl(self._fd, eviocgid, buf)
			self.bustype, self.vendor, self.product, self.version = buf
		except:
			self.bustype = 0
			self.vendor = 0
			self.product = 0
			self.version = 0
		buf = array.array('B', [0] * 256)
		try:
			ioctl(self._fd, eviocgname(256), buf)
			self.name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
		except:
			self.name = "Device {}".format(self.product)
		buf = array.array('B', [0] * 256)
		try:
			ioctl(self._fd, eviocgphys(256), buf)
			self.phys = buf.tobytes().rstrip(b'\x00').decode('utf-8')
		except:
			self.phys = ""
		buf = array.array('B', [0] * 256)
		try:
			ioctl(self._fd, eviocguniq(256), buf)
			self.uniq = buf.tobytes().rstrip(b'\x00').decode('utf-8')
		except:
			self.uniq = ""
		buf = array.array('i', [0])
		try:
			ioctl(self._fd, eviocgversion, buf)
			self.driver = buf[0]
		except:
			self.driver = 0

		### Properties ###

		input_prop_max = 0x1f
		count = (input_prop_max+7)//8
		buf = array.array('B', [0] * count)
		self.properties = []
		try:
			ioctl(self._fd, eviocgprop(count), buf)
		except:
			pass
		else:
			for i in range(input_prop_max):
				if test_bit(buf, i):
					self.properties.append(i)
		buf = array.array('i', [0])
		try:
			ioctl(self._fd, eviocgeffects, buf)
			self.num_effects = buf[0]
		except:
			self.num_effects = 0

		### Capabilities ###

		ev_size = EventTypes.EV_MAX // 8 + 1
		key_size = EventCodes.KEY_MAX // 8 + 1
		ev_bits = array.array('B', [0] * ev_size)
		self.capabilities = {}
		try:
			ioctl(self._fd, eviocgbit(0, ev_size), ev_bits)
		except:
			pass
		else:
			for ev_type in range(EventTypes.EV_MAX):
				if not test_bit(ev_bits, ev_type):
					continue
				capability = ev_type
				eventcodes = {}
				code_bits = array.array('B', [0] * key_size)
				try:
					ioctl(self._fd, eviocgbit(ev_type, key_size), code_bits)
				except:
					continue
				for ev_code in range(EventCodes.KEY_MAX):
					if not test_bit(code_bits, ev_code):
						continue
					if ev_type == EventTypes.EV_ABS:
						absinfo = array.array('i', [0] * 6)
						try:
							ioctl(self._fd, eviocgabs(ev_code), absinfo)
							absinfo = AbsValues(absinfo)
						except:
							continue
						eventcodes[ev_code] = absinfo
					else:
						eventcodes[ev_code] = True
				self.capabilities[capability] = eventcodes

		### Effects ###

		if EventTypes.EV_FF in self.capabilities:
			# https://www.kernel.org/doc/html/v4.14/input/ff.html
			def upload_effect(etype, eid, direction, trigger, replay, effect):
				if etype not in self.capabilities[EventTypes.EV_FF]:
					return -1
				buf = array.array('H', [0] * 50) # TODO: Calculate max size
				# type
				# id
				# direction
				# - button
				#   interval
				# - length
				#   delay
				struct.pack_into('HhHHHHH', buf, 0, etype, eid, direction, *trigger, *replay)
				if etype == FF_RUMBLE:
					# strong_magnitude
					# weak_magnitude
					struct.pack_info('HH', buf, 14, *effect)
				elif etype == FF_PERIODIC:
					# waveform
					# period
					# magnitude
					# offset
					# phase
					# - attack_length
					#   attack_level
					#   fade_length
					#   fade_level
					# custom_len
					# custom_data (pointer, research)
					struct.pack_info('HHhhHHHHHIh', buf, 14, *effect)
				elif etype == FF_CONSTANT:
					# level
					# - attack_length
					#   attack_level
					#   fade_length
					#   fade_level
					struct.pack_info('hHHHH', buf, 14, *effect)
				# Condition
				elif etype in [FF_SPRING, FF_FRICTION, FF_DAMPER, FF_INERTIA]:
					# right_saturation
					# left_saturation
					# right_coeff
					# left_coeff
					# deadband
					# center
					# * x2
					struct.pack_info('HHhhHh' * 2, buf, 14, *effect)
				elif etype == FF_RAMP:
					# start_level
					# end_level
					# - attack_length
					#   attack_level
					#   fade_length
					#   fade_level
					struct.pack_info('hhHHHH', buf, 14, *effect)
				return ioctl(self._fd, eviocsff, buf)

			def remove_effect(eid):
				buf = struct.pack('h', eid)
				ioctl(self._fd, eviocrmff, buf)

			def fd_write(evtype, code, value):
				# - usec
				#   sec
				# type
				# code
				# value
				buf = struct.pack('llHHi', 0, 0, evtype, code, value)
				self._fd.write(buf)

			def play_effect(eid, value):
				fd_write(EventTypes.EV_FF, eid, value)

			def set_gain(gain):
				fd_write(EventTypes.EV_FF, ForceFeedback.FF_GAIN, 0xFFFF * gain // 100)

			def set_autocenter(on=True):
				fd_write(EventTypes.EV_FF, ForceFeedback.FF_AUTOCENTER, 0xFFFF * autocenter // 100)

			self.upload_effect = upload_effect
			self.remove_effect = remove_effect
			self.play_effect = play_effect
			self.set_gain = set_gain
			self.set_autocenter = set_autocenter


class EventManager:
	"""
	Keeps track of events.
	"""
	def __init__(self, create_event):
		self._create_event = create_event
		self._devices = self.get_all()
		# Watchers
		self._inotify = INotify()
		self._wd = self._inotify.add_watch(self.get_path(), flags.CREATE | flags.ATTRIB | flags.DELETE)
		self._wait = threading.Event()
		self._wait.set()
		self._runner = True
		self._thread = threading.Thread(target=self._loop, daemon=True)
		self._thread.start()

	@property
	def devices(self):
		return self._devices

	def is_device(self, dev):
		return dev.startswith("event") or "-event-" in dev

	def get_path(self):
		return "/dev/input"

	def _loop(self):
		import time
		while self._runner:
			create = []
			for event in self._inotify.read(timeout=100, read_delay=10):
				if not self._wait.is_set():
					break
				if not self.is_device(event.name):
					continue
				if event.mask & flags.CREATE:
					create.append(event.name)
				if event.mask & flags.ATTRIB and event.name in create:
					create.remove(event.name)
					# Retry until success
					while True:
						try:
							with open("{}/{}".format(self.get_path(), event.name), 'rb'):
								break
						except:
							time.sleep(0.1)
					self.update_state()
				if event.mask & flags.DELETE:
					self.update_state()
			self._wait.wait()

	def close(self):
		self._runner = False
		self._wait.set()
		self._inotify.rm_watch(self._wd)
		self._thread.join()

	def pause(self):
		self._wait.clear()
		for device in self._devices:
			device.pause()

	def resume(self):
		for device in self._devices:
			device.resume()
		self.update_state()
		self._wait.set()

	@staticmethod
	def is_valid_dev(dev):
		try:
			with open(dev, 'rb'):
				return True
		except:
			return False

	def cur_devs(self):
		return ['{}/{}'.format(self.get_path(), fn) for fn in os.listdir(self.get_path()) if self.is_device(fn)]

	def get_all(self):
		return [self._create_event(dev) for dev in self.cur_devs()]

	def update_state(self):
		rem_devices = [device for device in self._devices if not device.is_connected()]
		self._devices = [device for device in self._devices if device.is_connected()]
		[device.close() for device in rem_devices]
		cur_devs = self.cur_devs()
		old_devs = [device.dev for device in self._devices]
		new_devs = [dev for dev in cur_devs if dev not in old_devs]
		self._devices.extend([self._create_event(dev) for dev in new_devs if self.is_valid_dev(dev)])
		return self.devices

class GeneralEvent(EventHandler):
	"""
	General event handler.
	"""
	def __init__(self, dev, callback):
		self.callback = callback
		super().__init__(dev)

	def event(self, tv_sec, tv_usec, evtype, code, value):
		self.callback(self, evtype, code, value)

class GeneralEventManager(EventManager):
	"""
	General event manager.
	"""
	def __init__(self, callback):
		super().__init__(lambda dev: GeneralEvent(dev, callback))


class DebugEvent(GeneralEvent):
	"""
	Debug event for a device.
	Retrieves a lot of data from the device, but can
	also send data.
	Currently used to experiment device interface.
	"""
	def __init__(self, dev, callback):
		super().__init__(dev, callback)

		self.get_info()


if __name__ == "__main__":
	# Debugging all devices
	nil = lambda ctrl, evtype, code, value: None
	import glob
	for dev in glob.glob("/dev/input/event*"):
		try:
			event = DebugEvent(dev, nil)
		except Exception as e:
			print(str(e))
		else:
			print("{}, {}, {}, {}".format(hex(event.bustype), hex(event.vendor), hex(event.product), hex(event.version)))
			print("{}, {}, {}, {}".format(event.name, event.phys, event.uniq, event.driver))
			print(event.capabilities)
			print(event.properties)

