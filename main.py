#!/usr/bin/python

import sys, time, os#, itertools
	
try:
	import mechanize, re, ssl
except ImportError as error:
	print(error)
	_, missing_moudle, _ = str(error).split("'")
	sys.exit("Try: sudo apt install python-%s" %(missing_moudle))
	
try:
	from core import actions, utils
	import httpbrute, options
except ImportError as error:
	print(error)
	sys.exit("Missing core module!")
	
	
########################## SSL 
#	https://stackoverflow.com/a/35960702
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
########################## End ssl

def main(setTargetURL, setUserlist, setPasslist,  setProxy):

	try:
		sizePasslist = actions.getObjectSize(setPasslist)

	except:
		#utils.printf("Can not get size of passlist", "bad")
		pass

	timeStarting = time.time()
	credentials = []

	try:
		
		usePasslist = setPasslist.readlines()

		result = httpbrute.handle(setTargetURL, setUserlist, setPasslist, sizePasslist, setProxy)
		if result:
			credentials.append(result)
	#except (KeyboardInterrupt, SystemExit):
	except KeyboardInterrupt:# as error:
		# for worker in workers:
		# 	worker.join()
		utils.die("Terminated by user!", "KeyboardInterrupt")
		
	except SystemExit:# as error
		utils.die("Terminated by system!", "SystemExit")

	except Exception as error:
		utils.die("Error while running", error)

	finally:
		# try:
		# 	for worker in workers:
		# 		worker.join()
		# except:
		# 	pass
		############################################
		#	Get result
		#
		############################################

		try:
		
			#	check result
			if len(credentials) == 0:
				utils.printf("Password not found!", "bad")
			else:
				utils.printf("")
				utils.print_table(("Username", "Password"), *credentials)
		except Exception as error:
			utils.printf(error, "bad")
			pass

		utils.printf("\nCompleted. Run time: %0.5s [s]\n" %(time.time() - timeStarting))

		########################################
		#	Clear resources
		#
		########################################

		try:
			setPasslist.close()
		except:
			pass
		try:
			setUserlist.close()
		except:
			pass

		sys.exit(0)

if __name__ == "__main__":
	current_dir = actions.getProjectRootDirectory(sys.argv[0])
	if current_dir:
		os.chdir(current_dir)
	setTargetURL, setUserlist, setPasslist, setProxy = options.getUserOptions()
	main(setTargetURL, setUserlist, setPasslist, setProxy)