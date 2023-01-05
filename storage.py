import os
from pathlib import Path
from subprocess import Popen
import signal
import re
from xml.dom import minidom
import glob

class Storage:
	"""
	Handle the storage for Retro Pie
	- Make sure that ~/RetroPie/roms is mounted.
	- Open up VPN if the mount does not exist.
	- Various other nifty behaviors.
	"""
	def __init__(self):
		self._vpn = None

	def mounted(self):
		return self.retropie_roms().is_mount()

	def connect(self):
		if self.mounted():
			return
		# Just a slight network hickup
		self.mount_net()
		if self.mounted():
			return
		# Another network
		self.start_vpn()
		self.mount_net()
		if self.mounted():
			return
		# Offline usage
		self.mount_local()

	def mount_net(self):
		p = Popen(["mount", "-a"], stdin=PIPE, stdout=PIPE, bufsiz=1)
		p.wait()

	def mount_local(self):
		p = Popen(["mount", "-o", "bind", str(self.local_roms()), str(self.retropie_roms())], stdin=PIPE, stdout=PIPE, bufsiz=1)
		p.wait()

	def start_vpn(self):
		"""open up a connection to the VPN."""
		vpn_path = Path.home() / "vpn"
		openvpn_config = str(vpn_path / "auto_rhubarb-pie_server.ovpn")
		self._log = open(str(vpn_path / "vpn.log"), "a")
		self._vpn = Popen(["sudo", "openvpn", "--config", openvpn_config], stdout=subprocess.PIPE, stderr=self._log)
		while True:
			line = self._vpn.stdout.readline()
			if not line:
				break
			if re.search("Initialization Sequence Completed", line):
				break

	def stop_vpn(self):
		"""Close the connection to the VPN."""
		self._vpn.send_signal(signal.SIGINT)
		self._vpn.wait()
		self._log.flush()
		self._log.close()
		self._vpn = None
		self._log = None

	def uses_vpn(self):
		return self._vpn != None

	def load_favorites(self):
		"""
		Go through the favorites from emulationstation and store
		them locally for offline usage.
		- Go through .emulationstation/gamelists/*/gamelist.xml
		  in search for the tag "favorite" with the value "true".
		  gameList.game.favorite=true
		  gameList.game.path
		"""
		def getText(nodes):
			return ''.join([node.data for node in nodes if node.nodeType == node.TEXT_NODE])

		consoles = {}

		for gamelist in glob.glob(str(self.emulationstation() / "gamelists" / "*" / "gamelist.xml")):
			console = os.path.basename(os.path.dirname(gamelist))
			paths = []
			dom = minidom.parse(gamelist)
			for favorite in dom.getElementsByTagName("favorite"):
				if getText(favorite.childNodes) != "true":
					continue
				path = getText(favorite.parentNode.getElementsByTagName("path")[0].childNodes).lstrip('./')
				paths.append(path)
			consoles[console] = paths
			# TODO: Copy the necessary files
			# Problem 1: What files should be copied?
			# Problem 1a: Only the file specified? Will miss DOSBox files.
			# Problem 1b: The whole folder they contain? May get all files available.
			# Fix 1: Depends.
			# Fix 1a: If not DosBox, copy only one file.
			# Fix 1b: If it's DosBox, copy whole folder.
			# Note: Also copy save files (srm)
			# Note: Sync both ways depending on modified file

	def save_favorites(self):
		"""
		Put back the local storage of games and put them back on
		the network storage.
		"""
		# TODO: Copy back all from the specific folder
		for game in glob.glob(str(self.local_roms() / "*" / "*")):
			console = os.path.basename(os.path.dirname(gamelist))
			source = os.path.basename(game)

	@staticmethod
	def retropie_roms():
		return Path.home() / "RetroPie" / "roms"

	@staticmethod
	def local_roms():
		return Path.home() / "RetroPie" / "local_roms"

	@staticmethod
	def emulationstation():
		return Path.home() / ".emulationstation"

#storage = Storage()
#storage.load_favorites()
