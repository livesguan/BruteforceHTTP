#!/usr/bin/python

###############################################
#	Parse user's options from Argv
#	Create Brute forcing object
#	Start method
#	Clear object
#	Print result
#
##############################################

import sys
import actions
import httpbrute
import utils
import time
import threading
import math

##############################################
#	Create default options
#
############################################

srcUsrList = 'userlist.txt'
srcPassList = 'passlist.txt'
varTargetURL = ''
numThread = 1
numAccount = 0
isRunning = True

infUserOptions = '''
Target: TARGETURL
userlist: DEFAULT
passlist: DEFAULT
'''

################################
#	Get user's options
#
################################


if len(sys.argv) == 1:
	##############################
	#	If there is no options:
	#	print help and show how to use this script
	##############################

	utils.print_help()
	sys.exit(0)

elif len(sys.argv) == 2:
	############################################
	#	if 1 option only:
	#		calling help
	#	else:
	#		run process with default options
	#
	############################################

	if sys.argv[1] == '-h' or sys.argv[1] == '--help':
		utils.print_help()
		sys.exit(0)
	else:
		varTargetURL = sys.argv[1]
		#############################################
		#	open file here -> no delay for print help
		#############################################
		userlist = actions.actionGetFileData(srcUsrList)
		passlist = actions.actionGetFileData(srcPassList)

else:
	###########################################
	#	Get user options
	#	Replace default options
	#	**NEED IMPROVE**
	#
	###########################################

	userlist = actions.actionGetFileData(srcUsrList)
	passlist = actions.actionGetFileData(srcPassList)
	try:
		idxArgOpt = 1
		while idxArgOpt < len(sys.argv):

			#	Choose custom username
			if sys.argv[idxArgOpt] == '-U':
				userlist = actions.actionGetListData(sys.argv[idxArgOpt + 1])
				infUserOptions = infUserOptions.replace(
				    "userlist: DEFAULT", "userlist: %s" % (userlist))
				idxArgOpt += 1

			#	Choose custom userlist
			elif sys.argv[idxArgOpt] == '-u':
				userlist = actions.actionGetFileData(sys.argv[idxArgOpt + 1])
				infUserOptions = infUserOptions.replace(
				    "userlist: DEFAULT", "userlist: %s" % (sys.argv[idxArgOpt + 1]))
				idxArgOpt += 1

			#	Choose custom passlist
			elif sys.argv[idxArgOpt] == '-p':
				infUserOptions = infUserOptions.replace(
				    "passlist: DEFAULT", "passlist: %s" % (sys.argv[idxArgOpt + 1]))
				passlist = actions.actionGetFileData(sys.argv[idxArgOpt + 1])
				idxArgOpt += 1

			elif sys.argv[idxArgOpt] == '-w':
				numThread = int(sys.argv[idxArgOpt + 1])
				idxArgOpt += 1
			#	Possible URL
			else:
				varTargetURL = sys.argv[idxArgOpt]
			idxArgOpt += 1

	except:
		sys.exit(utils.craft_msg("Parsing arguments error", "bad"))

##########################
#	CHECK REQUIRED OPTIONS
#
##########################

if not varTargetURL:
	sys.exit(utils.craft_msg("An URL is required", "bad"))
else:
	infUserOptions = infUserOptions.replace('TARGETURL', varTargetURL)


###########################################
#	print option information before running
#
###########################################

print(infUserOptions)

timeStarting = time.time()
bruteForceWorkers = []
numUser = 0
numPass = 0

for i in userlist:
	numUser += 1
for i in passlist:
	numPass += 1

maxAccount = numUser * numPass
credentials = []
numThreadDone = 0

# on each brute force worker finished his job
def onBruteDone(id, creds):
	global credentials
	global numThreadDone
	global isRunning
	numThreadDone += 1
	if len(creds) != 0:
		credentials.append(creds)

	if numThreadDone == len(bruteForceWorkers):
		if len(credentials) == 0:
			utils.printf("Password not found!", "bad")
		else:
			utils.print_table(("Username", "Password"), *credentials)
		utils.printf("\nCompleted. Run time: %0.5s [s]\n" % (time.time() - timeStarting), "good")
		# Stop the whole program
		isRunning = False

# on each account that a bruteforce worker finished
def onEachBruteDone():
	global numAccount
	numAccount += 1
	percentage = numAccount * 100 / maxAccount
	processBarLength = 40
	currentProcessLength = percentage * processBarLength / 100
	process = '#' * (currentProcessLength) + ' ' * \
	                 (processBarLength - currentProcessLength)
	utils.prints("")
	utils.prints("%s / %s accounts [%s] (%s %%)" %
	             (numAccount, maxAccount, process, percentage))


# list size for userlist
# if we has 8 user in list and run with 4 thread
# then the list size will be 8 / 4 = 2 users
# which means each thread brute 2 users
listSize = int(math.ceil(float(numUser) / float(numThread)))
utils.printf("Starting...\n")
utils.printf("Testing connection...\n")
readyWorkers = []
currentWorkerId = 1
# loop through list of users
for i in xrange(0, numUser, listSize):
	# create new thread
	bruteForceWorker = httpbrute.BruteForcing(
	    varTargetURL, userlist, passlist, currentWorkerId, listSize)
	bruteForceWorker.setOnEachBruteCallback(onEachBruteDone)
	bruteForceWorker.setCallback(onBruteDone)
	if bruteForceWorker.actTestConnection():
		# add thread to list
		bruteForceWorkers.append(bruteForceWorker)
		readyWorkers.append(str(currentWorkerId))
		utils.prints("Worker [%s] connected!" % "-".join(readyWorkers))
	else:
		sys.exit(0)
	
	currentWorkerId += 1

utils.printf("All %s workers ready!" % len(readyWorkers), "good")
utils.printf("")
readyWorkers = None

for i in xrange(len(bruteForceWorkers)):
	# start all thread in list
	bruteForceWorkers[i].daemon = True
	bruteForceWorkers[i].start()

# keep main thread alive
while isRunning:
	try:
		time.sleep(0.1)
	except KeyboardInterrupt, SystemExit:
		try:
			userlist.close()
			passlist.close()
		except:
			pass
		sys.exit(0)