import threading
from subprocess import Popen, PIPE
import re


class Bluetooth:
	"""
	Handle bluetooth devices.
	"""
	thread = None

	def scan(self, callback):
		self.callback = callback
		self.runner = True
		if self.thread == None:
			self.thread = threading.Thread(target=self.loop, daemon=True)
			self.thread.start()

	def cancel(self):
		self.runner = False

	def loop(self):
		p = self.bluetoothctl()
		p.stdout.readline() # Skip first
		p.stdin.write(b"scan on\n")
		p.stdin.flush()
		while self.runner:
			line = p.stdout.readline().strip().decode()
			if not self.runner:
				break
			# Only take in new devices
			if '\x1b[K[\x1b[0;92mNEW\x1b[0m]' in line:
				m = re.findall(r'Device (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}) (.*)', line)[0]
				self.callback(m[0], m[-1])
		self.thread = None

	def get_devices(self):
		p = self.bluetoothctl("devices")
		p.wait()
		return self.devices_to_list(p.stdout.readlines())

	def get_paired(self):
		p = self.bluetoothctl("paired-devices")
		p.wait()
		return self.devices_to_list(p.stdout.readlines())

	def device_info(self, mac):
		p = self.bluetoothctl("info", mac)
		p.wait()
		info = {}
		def value(line):
			return line.split(' ', 1)[1]
		for line in p.stdout.readlines():
			line = line.decode('utf-8').strip()
			if line.startswith("Name"):
				info["name"] = value(line)
			elif line.startswith("Paired"):
				info["paired"] = value(line) == "yes"
			elif line.startswith("Trusted"):
				info["trusted"] = value(line) == "yes"
			elif line.startswith("Connected"):
				info["connected"] = value(line) == "yes"
		return info

	def trust_device(self, mac):
		p = self.bluetoothctl("trust", mac)
		p.wait()
		print(p.stdout.readlines())
		import time
		time.sleep(5)
		self.bluetoothctl("connect", mac).wait()

	def remove_device(self, mac):
		self.bluetoothctl("untrust", mac).wait()
		self.bluetoothctl("remove", mac).wait()

	@staticmethod
	def devices_to_list(data):
		data = list(data)
		devs = []
		for datum in data:
			datum = datum.decode('utf-8').strip()
			if datum.startswith("Device"):
				devs.append(tuple(datum[7:].split(' ', 1)))
		return devs

	@staticmethod
	def bluetoothctl(*args, **kwargs):
		return Popen(["bluetoothctl", *args], stdin=PIPE, stdout=PIPE, bufsize=1, **kwargs)
