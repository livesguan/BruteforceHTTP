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


# Split user list
# We don't want to split password because we will use all pass for each user
# spliting user is the only choice !
userlistFile = userlist
passlistFile = passlist
userlist = userlistFile.read().split('\n')
passlist = passlistFile.read().split('\n')
maxAccount = len(userlist) * len(passlist)
credentials = []

# on each brute force worker finished his job
def onBruteDone(id, creds):
	global credentials
	if len(creds) != 0:
		credentials.append(creds)

	if numThread == id:
		if len(credentials) == 0:
			utils.printf("Password not found!", "bad")
		else:
			utils.print_table(("Username", "Password"), *credentials)
		utils.printf("\nCompleted. Run time: %0.5s [s]\n" % (
	    time.time() - timeStarting), "good")
		sys.exit(0)

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
listSize = int(math.ceil(float(len(userlist)) / float(numThread)))
# array of users for each thread
# [['admin', 'hello'], ['hola', 'halo']] # 2 list for 2 thread each has 2 user
userlists = [userlist[x:x+listSize]
    for x in xrange(0, len(userlist), listSize)]
utils.printf("Number of workers: %s\n" % len(userlists))
utils.printf("Starting...\n")
utils.printf("Testing connection...\n")
readyWorkers = []
# loop through list of users
for i in xrange(len(userlists)):
	# get user list for current thread
	users = userlists[i]
	# create new thread
	bruteForceWorker = httpbrute.BruteForcing(
	    varTargetURL, users, passlist, (i + 1))
	bruteForceWorker.setOnEachBruteCallback(onEachBruteDone)
	bruteForceWorker.setCallback(onBruteDone)
	if bruteForceWorker.actTestConnection():
		# add thread to list
		bruteForceWorkers.append(bruteForceWorker)
		readyWorkers.append(str(i + 1))
		utils.prints("Worker [%s] ready!" % '-'.join(readyWorkers))
	else:
		sys.exit(0)

utils.printf("All %s workers ready!" % len(readyWorkers))
utils.printf("")
readyWorkers = None

for i in xrange(len(bruteForceWorkers)):
	# start all thread in list
	bruteForceWorkers[i].daemon = True
	bruteForceWorkers[i].start()

# keep main thread alive
while True:
	try:
		time.sleep(0.1)
	except KeyboardInterrupt, SystemExit:
		userlistFile.close()
		passlistFile.close()
		sys.exit(0)
sys.exit(0)