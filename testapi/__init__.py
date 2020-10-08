# -*- coding: utf-8 -*-
from flask import Flask

from . import db

__version__ = '201008.1'

app = Flask(__name__)

adb = db.DB()
if not adb.exists():
    adb.create()
