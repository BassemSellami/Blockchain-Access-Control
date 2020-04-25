#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
A simple flask server that gives some random sensor like data
'''

import random

from flask import Flask

APP = Flask(__name__)

@APP.route("/data")
def data():
    return f"{random.randint(0, 20)}ms", 200

@APP.route("/add")
def add():
    return f"You may now access this data", 200
