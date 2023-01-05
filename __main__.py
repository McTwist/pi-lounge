#!/usr/bin/env python3
"""
This project started to make it possible to
interact with the terminal with a controller.
When that was done, it escalated to Bluetooth.
Then it went bananas over Storage and WiFi.
"""

from queue import Queue
import subprocess

from .event import GeneralEventManager, EventTypes, EventCodes
from .remote import Remote, KeyCodes as RemoteCodes
from .menu import Menu
from .bluetooth import Bluetooth
from .wifi import WiFi
from .storage import Storage

class Runner:
	"""A wrapper around a boolean value in order to make it callable."""
	def __init__(self, b=True):
		self.__run = b

	def __call__(self, b=False):
		self.__run = b

	def __bool__(self):
		return self.__run

class Input:
	"""Handle input events."""
	DELTA_PRESS = 0.6
	DELTA_RELEASE = 0.5
	ENTER = [EventCodes.BTN_A, EventCodes.KEY_ENTER, EventCodes.BTN_LEFT]
	BACK = [EventCodes.BTN_B, EventCodes.KEY_ESC, EventCodes.BTN_RIGHT]
	def __init__(self):
		self.queue = Queue()
		self.ldir = 0

	def get(self):
		return self.queue.get()

	def reset(self):
		with self.queue.mutex:
			self.queue.queue.clear()

	def up(self):
		self.queue.put((0, -1))

	def down(self):
		self.queue.put((0, 1))

	def enter(self):
		self.queue.put((1, True))

	def back(self):
		self.queue.put((2, True))

	def _direction(self, value):
		if value > 0:
			self.down()
		elif value < 0:
			self.up()

	def update(self, ctrl, evtype, code, value):
		if evtype == EventTypes.EV_KEY:
			if code in self.ENTER:
				if value:
					self.enter()
			elif code in self.BACK:
				if value:
					self.back()
			elif code == EventCodes.KEY_DOWN:
				if value:
					self.down()
			elif code == EventCodes.KEY_UP:
				if value:
					self.up()
		elif evtype == EventTypes.EV_REL:
			if code == EventCodes.REL_WHEEL:
				self._direction(value)
		elif evtype == EventTypes.EV_ABS:
			if code == EventCodes.ABS_HAT0Y:
				self._direction(value)
			elif code in [EventCodes.ABS_Y, EventCodes.ABS_RZ]:
				if evtype in ctrl.capabilities and code in ctrl.capabilities[evtype]:
					capability = ctrl.capabilities[evtype][code]
					# According to the documentation, this is needed to be done as there
					# are no such modification within the kernel
					value = max(capability.minimum, min(value, capability.maximum))
					half = (capability.maximum - capability.minimum) / 2.0
					value = (value if capability.minimum < 0 else value - half) / half
				if value > self.DELTA_PRESS:
					if self.ldir <= 0:
						self.ldir = 1
						self.down()
				elif value < -self.DELTA_PRESS:
					if self.ldir >= 0:
						self.ldir = -1
						self.up()
				# Center
				elif self.DELTA_RELEASE > value > -self.DELTA_RELEASE:
					self.ldir = 0

	def update_remote(self, code, value):
		if code == RemoteCodes.KEY_OK:
			if value:
				self.enter()
		elif code == RemoteCodes.KEY_BACK:
			if value:
				self.back()
		elif code == RemoteCodes.KEY_DOWN:
			if value:
				self.down()
		elif code == RemoteCodes.KEY_UP:
			if value:
				self.up()

class InteractiveMenu:
	"""An interactive menu shell."""
	def __init__(self, menu, input_ctrl):
		self._runner = Runner()
		self.input_ctrl = input_ctrl
		self.menu = menu

	def __call__(self):
		self._runner(True)

		self.draw()

		while self._runner:
			vec = 0
			select = False
			action, value = self.input_ctrl.get()
			if action == 0:
				vec = value
			elif action == 1:
				select = True
			elif action == 2:
				self.exit()
			update = False
			if vec != 0:
				self.menu.jump(vec)
				update = True
			if select:
				self.menu.execute()
				update = True
			if update:
				self.draw()

	def draw(self):
		self.menu.draw()

	def exit(self):
		self.menu.execute(self._runner)

	@property
	def runner(self):
		return self._runner

class MainMenu(InteractiveMenu):
	"""The main menu."""
	def __init__(self, menu, input_ctrl):
		super().__init__(menu.sub_menu(), input_ctrl)
		self.menu.add("0", "Shutdown", create_cmd_input("sudo shutdown now"))
		self.menu.add("1", "Steamlink", create_cmd_input("steamlink"), True)
		self.menu.add("2", "RetroPie", create_cmd_input("emulationstation"))
		self.menu.add("3", "Bluetooth", BluetoothMenu(menu.sub_menu(), input_ctrl))
		self.menu.add("4", "WiFi", WiFiMenu(menu.sub_menu(), input_ctrl))
		self.menu.add("5", "Storage", StorageMenu(menu.sub_menu(), input_ctrl))

	def exit(self):
		pass # Disable

class BluetoothMenu(InteractiveMenu):
	"""Managing bluetooth devices."""
	def __init__(self, menu, input_ctrl):
		super().__init__(menu, input_ctrl)
		self.bt = Bluetooth()
		self.paired = self.bt.get_paired()
		self.pair_exist = lambda dev: dev in [pair[0] for pair in self.paired]
		self.fpair = lambda dev: "*" if self.pair_exist(dev) else " "

	def __call__(self):
		self.load_menu()
		self.menu.draw()

		self.bt.scan(self.add_device)
		super().__call__()
		self.bt.cancel()

	def handle_device(self, dev):
		if self.pair_exist(dev):
			print("Removing device...")
			self.bt.remove_device(dev)
		else:
			print("Connecting device...")
			self.bt.trust_device(dev)
		# Refresh list
		self.paired = self.bt.get_paired()
		# TODO: Make smarter, don't update the whole list
		self.load_menu()
		self.menu.draw()

	def load_menu(self, draw=False):
		self.menu.clear()
		self.menu.add("X", "Back", self.runner)
		devs = self.bt.get_devices()
		devs.sort(key=lambda pair: pair[1])
		for pair in devs:
			self.add_device(*pair, draw)

	def add_device(self, address, name, draw=True):
		self.menu.add(self.fpair(address), name, lambda: self.handle_device(address))
		if draw:
			self.menu.draw()

class WiFiMenu(InteractiveMenu):
	"""Managing WiFi connection."""
	def __init__(self, menu, input_ctrl):
		super().__init__(menu, input_ctrl)
		self.wifi = WiFi()

	def __call__(self):
		self.menu.clear()

		self.menu.add("Abort", "Scanning proximity...", self.runner)
		self.menu.draw()

		networks = self.wifi.get_networks()

		self.menu.update(0, key="X", text="Back")

		for network in networks:
			self.menu.add("*" if network["in-use"] else " ", network["ssid"], lambda: self.connect(network))

		super().__call__()

	def connect(self, network):
		self.wifi.connect(network["bssid"])

class StorageMenu(InteractiveMenu):
	"""
	Managing the storage for the ROMS.
	- Local backup of favorites
	- VPN
	- Manual mounting
	"""
	def __init__(self, menu, input_ctrl):
		super().__init__(menu, input_ctrl)
		self.storage = Storage()
		self.menu.add("X", "Back", self.runner)
		self.menu.add(" ", "Mounted", self.storage.connect)
		self.menu.add(" ", "VPN", self.vpn)

	def draw(self):
		self.menu.update(1, key="*" if self.storage.mounted() else " ")
		self.menu.update(2, key="*" if self.storage.uses_vpn() else " ")
		super().draw()

	def vpn(self):
		if self.storage.uses_vpn():
			self.storage.stop_vpn()
		else:
			self.storage.start_vpn()

def create_cmd(cmd, pre=None, post=None):
	def _ret():
		if pre:
			pre()
		try:
			subprocess.run(cmd, shell=True)
		except KeyboardInterrupt:
			pass
		if post:
			post()
	return _ret

# TODO: Move this into Input instead
def input_pause():
	input_manager.pause()
	remote.pause()
	menu.pause()

def input_resume():
	input_ctrl.reset()
	menu.resume()
	remote.resume()
	input_manager.resume()

create_cmd_input = lambda cmd: create_cmd(cmd, input_pause, input_resume)

input_ctrl = Input()
input_manager = GeneralEventManager(input_ctrl.update)
remote = Remote(input_ctrl.update_remote)

menu = Menu()

def main():
	with menu:
		MainMenu(menu, input_ctrl)()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass

