#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os.path
import re
import smtplib
import subprocess
import sys
import urllib2
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('/var/log/tv.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

TV_ID = "MAGIC MIRROR"

USERNAME = ""
PASSWORD = ""

FROM = ''
TO = [""]

SUBJECT = "new teamviewer id on {}".format(TV_ID)
TEXT = "Teamviwer istallation on {} has now id {}"

FILE_PATH = "~/old_tv_id"

def get_tv_id():
    tv_info = str(subprocess.check_output(['teamviewer','--info']))

    m = re.search(r"TeamViewer\ ID:.*\ ([0-9]{8,})", tv_info)
    id = None
    try:
        id = m.group(1)
        return id
    except IndexError:
        return None

def get_old_id():
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            id = file.read()
            file.close()
            return id
    else:
        return None

def write_new_id(id):
    with open(FILE_PATH, "w") as file:
        file.write(id)
        file.close()

def internet_on():
    try:
        response = urllib2.urlopen('http://www.google.de', timeout=5)
        return True
    except urllib2.URLError:
        return False

old_id = get_old_id()
id = get_tv_id()

if id is None or old_id == id:
    sys.exit(1)

logger.info("tv id is {}".format(id))
TEXT = TEXT.format(TV_ID, id)

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

logger.info("checking connection...")
on = False
for i in range(0, 10):
    if internet_on():
        on = True
        break
    else:
        logger.info("no connection sleep 5 seconds")
        time.sleep(5)

if on:
    logger.info("sending mail")
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(USERNAME, PASSWORD)
    server.sendmail(FROM, TO, message)
    server.quit()

    logger.info("write file")
    write_new_id(id)
