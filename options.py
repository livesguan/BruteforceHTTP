#!/usr/bin/python
# -*- coding:utf-8 -*-

import data
import sys
from core import actions, utils

URL = None
USER_LIST = "default"
PASS_LIST = "default"
THREADS = 1
KEY_FALSE = None
MODE = "--brute"
DEF_A_MODE = ("--brute", "--sqli", "--basic")
DEF_R_MODE = ("--verbose", "--log", "--proxy")
DEF_OPS = ("-u", "-U", "-p", "-t", "-k")

R_OPTIONS = {
    "--proxy": True,
    "--log": False,
    "--verbose": False
}


def check_option(url, options, r_options):
    global MODE

    final_option = {}
    try:
        final_option["threads"] = int(options["-t"])
    except Exception as ConvertError:
        utils.die("Invalid threads", ConvertError)

    if MODE == "--sqli":
        final_option["passlist"] = "MyP@ssW0rd"
        final_option["userlist"] = data.getSQL()

    else:
        final_option["passlist"] = data.getPass() if options["-p"] == "default" else actions.fread(options["-p"])
        if options["-U"]:
            final_option["userlist"] = actions.lread(options["-U"])
        else:
            final_option["userlist"] = data.getUser() if options["-u"] == "default" else actions.fread(options["-u"])

        final_option["falsekey"] = options["-k"]

    if "http" not in url:
        url = "http://%s" % url
    if url[-1] != "/":
        url += "/"

    if r_options["--proxy"]:
        r_options["--proxy"] = actions.getProxyList()

    return url, final_option, r_options


def get_user_options():
    global URL, USER_LIST, PASS_LIST, THREADS, KEY_FALSE, MODE, R_OPTIONS, DEF_A_MODE, DEF_R_MODE, DEF_OPS
    
    options = {
        "-u": USER_LIST,
        "-p": PASS_LIST,
        "-t": THREADS,
        "-k": KEY_FALSE,
        "-U": None,
    }

    if len(sys.argv) == 1:
        utils.print_help()
        sys.exit(0)

    idx = 1
    while idx < len(sys.argv):
        if sys.argv[idx] in ("-h", "--help", "help"):
            utils.print_help()
        else:
            if sys.argv[idx] in DEF_R_MODE:
                R_OPTIONS[sys.argv[idx]] = True

            elif sys.argv[idx] in DEF_A_MODE:
                MODE = sys.argv[idx]
                idx += 1

            elif sys.argv[idx] in DEF_OPS:
                options[sys.argv[idx]] = sys.argv[idx + 1]
                idx += 1

            else:
                URL = sys.argv[idx]
        idx += 1

    if not URL:
        utils.printf("An URL is required", "bad")
        sys.exit(1)
    else:
        utils.printf(craft_banner(URL, options, MODE, R_OPTIONS), "good")
        URL, options, R_OPTIONS = check_option(URL, options, R_OPTIONS)

        return URL, options, MODE, R_OPTIONS


def craft_banner(url, options, mode, R_OPTIONS):
    usr = options["-U"] if options["-U"] else options["-u"]

    banner = """
      =================================================================
    /  Target: %-56s \\
    |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
    |  Users: %-58s |
    |  Password: %-55s |
    |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
    |                                                                    |
    |      Attack mode: %-6s |   Using Proxy: %-6s |   Threads: %-4s |
    |                                                                    |
    |--------------------------------------------------------------------|
    |          Verbose: %-13s  |          Save Log: %-12s |
    |--------------------------------------------------------------------|
    \\  False keyword: %-49s /
      =================================================================
    """ % (url, usr, options["-p"], mode.replace("--", ""), 
           R_OPTIONS["--proxy"], options["-t"], R_OPTIONS["--verbose"], 
           R_OPTIONS["--log"], options["-k"])

    return banner.replace("\t", "  ")

