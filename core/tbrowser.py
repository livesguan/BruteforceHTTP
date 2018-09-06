#!/usr/bin/python
# -*- coding:utf-8 -*-


import actions
import data
import mechanize
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def start_browser():
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.set_handle_referer(True)
    browser.set_handle_redirect(True)
    browser.set_handle_equiv(True)
    return browser


def get_login_form(browser_form):
    ret_form_id = 0
    text_field = r"TextControl\W(.*)="
    pass_field = r"PasswordControl\W(.*)="

    for form in browser_form:
        try:
            reg_text_field = re.findall(text_field, str(form), re.MULTILINE)[0]
            reg_pass_field = re.findall(pass_field, str(form), re.MULTILINE)[0]
            return ret_form_id, reg_text_field, reg_pass_field
        except:
            ret_form_id += 1
    return None


def user_agent():
    agents = data.get_agent()
    return actions.randomFromList(agents.split("\n"))

