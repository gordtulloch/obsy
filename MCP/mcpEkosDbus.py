#############################################################################################################
## E K O S D B U S                                                                                         ##
#############################################################################################################
# EkosDbus - functions to control the Ekos instance running on the local machine

# Set up logging
import logging
logger = logging.getLogger("mcpEkosDbus")

class EkosDbus():
	def __init__(self):
		# user login session
		self.session_bus = dbus.SessionBus()
		self.start_ekos_proxy = None
		self.start_ekos_iface = None
		self.ekos_proxy = None
		self.ekos_iface = None
		self.scheduler_proxy = None
		self.scheduler_iface = None
		self.is_ekos_running = None

	def setup_start_ekos_iface(self):
		try:
			# proxy object
			self.start_ekos_proxy = self.session_bus.get_object("org.kde.kstars",  # bus name
																"/kstars/MainWindow_1/actions/ekos"  # object path
																)
			# interface object
			self.start_ekos_iface = dbus.Interface(self.start_ekos_proxy, 'org.qtproject.Qt.QAction')
		except dbus.DBusException as dbe:
			logger.error("DBUS error starting Ekos: "+dbe)
			sys.exit(1)

	def setup_ekos_iface(self, verbose=True):
		# if self.start_ekos_iface is None:
		#     self.setup_start_ekos_iface()
		try:
			self.ekos_proxy = self.session_bus.get_object("org.kde.kstars",
														  "/KStars/Ekos"
														  )
			# ekos interface
			self.ekos_iface = dbus.Interface(self.ekos_proxy, 'org.kde.kstars.Ekos')
		except dbus.DBusException as dbe:
			logger.error("DBUS error getting Ekos interface: "+dbe)
			sys.exit(1)

	def setup_scheduler_iface(self, verbose=True):
		try:
			# https://api.kde.org/extragear-api/edu-apidocs/kstars/html/classEkos_1_1Scheduler.html
			self.scheduler_proxy = self.session_bus.get_object("org.kde.kstars",
															   "/KStars/Ekos/Scheduler"
															   )
			self.scheduler_iface = dbus.Interface(self.scheduler_proxy, "org.kde.kstars.Ekos.Scheduler")
		except dbus.DBusException as dbe:
			logger.error("DBUS error getting Ekos Scheduler interface: "+dbe)
			sys.exit(1)

	def start_ekos(self):
		logger.info("Start Ekos")
		if self.start_ekos_iface is None:
			self.setup_start_ekos_iface()
		self.start_ekos_iface.trigger()

	def stop_ekos(self):
		logger.info("Stop Ekos")
		if self.ekos_iface is None:
			self.setup_ekos_iface()
		self.ekos_iface.stop()

	# is_ekos_running does not work
	def is_ekos_running(self):
		if self.ekos_iface is None:
			self.setup_ekos_iface(verbose=False)
		sys.exit(0)

	def load_and_start_profile(self, profile):
		logger.info("Load {} profile".format(profile))
		if self.ekos_iface is None:
			self.setup_ekos_iface()
		self.ekos_iface.setProfile(profile)
		logger.info("Start {} profile".format(profile))
		self.ekos_iface.start()
		self.ekos_iface.connectDevices()
		logger.info("TODO Waiting for INDI devices...")
		time.sleep(5)

	def load_schedule(self, schedule):
		logger.info("Load {} schedule".format(schedule))
		if self.scheduler_iface is None:
			self.setup_scheduler_iface()
		self.scheduler_iface.loadScheduler(schedule)

	def start_scheduler(self):
		logger.info("Start scheduler")
		if self.scheduler_iface is None:
			self.setup_scheduler_iface()
		self.scheduler_iface.start()

	def stop_scheduler(self):
		logger.info("Stop scheduler")
		if self.scheduler_iface is None:
			self.setup_scheduler_iface()
		self.scheduler_iface.stop()

	def reset_scheduler(self):
		logger.info("Reset all jobs in the scheduler")
		if self.scheduler_iface is None:
			self.setup_scheduler_iface()
		self.scheduler_iface.resetAllJobs()

	# is_scheduler_running does not work
	def is_scheduler_running(self):
		if self.scheduler_iface is None:
			self.setup_scheduler_iface(verbose=False)
		sys.exit(0)