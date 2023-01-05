from subprocess import Popen, PIPE
import re

class WiFi:
	"""
	Keep track of the available Wi-Fi:s.
	"""
	def get_networks(self):
		p = self.nmcli("-g", "in-use,bssid,ssid,chan,signal", "dev", "wifi", "list")
		p.wait()
		data = list(p.stdout.readlines())
		networks = []
		for datum in data:
			datum = datum.decode('utf-8').rstrip()
			inuse, bssid, ssid, channel, signal = re.split(r'(?<!\\):', datum)
			networks.append({
				"in-use": inuse == '*',
				"bssid": bssid.replace('\\', ''),
				"ssid": ssid,
				"channel": int(channel),
				"signal": int(signal)
			})
		return networks

	def connect(self, ssid, password=None):
		"""Connect with (b)ssid with or without password"""
		if password == True:
			password = input("Password: ")
		if password:
			self.nmcli("dev", "wifi", "connect", ssid, "password", password).wait()
		else:
			# TODO: Check if it works, otherwise request password
			self.nmcli("con", "up", ssid).wait()

	@classmethod
	def is_online(cls):
		p = cls.nmcli("-g", "state", "g")
		p.wait()
		return p.readline().decode('utf-8').strip() == "connected"


	@staticmethod
	def nmcli(*args, **kwargs):
		return Popen(["nmcli", "-c", "no", *args], stdin=PIPE, stdout=PIPE, bufsize=1, **kwargs)

