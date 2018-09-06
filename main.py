#!/usr/bin/python
# -*- coding:utf-8 -*-

from core import actions
import httpbrute
import options
import os
import sys


def main(target_url, options_value, mode, run_options):
    # TODO mode 利用
    print target_url, options_value, run_options
    user_list, pass_list = options_value.values()
    set_proxy, set_verbose, set_log = run_options.values()
    user_list = user_list.split('\n')
    pass_list = pass_list.split('\n')
    httpbrute.handle(target_url, user_list, pass_list, set_proxy)

if __name__ == '__main__':
    current_dir = actions.get_root_dir(sys.argv[0])
    if current_dir:
        os.chdir(current_dir)
    main(*options.get_user_options())
