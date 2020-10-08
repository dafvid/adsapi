# -*- coding: utf-8 -*-
from flask import g, Flask, request, jsonify

from . import db

__version__ = '201008.1'

app = Flask(__name__)

adb = db.DB()
if not adb.exists():
    adb.create()


@app.before_request
def before_request():
    g.s = adb.get_session()


@app.route('/')
def index():
    return 'Ad API v0.1'


def ad_to_dict(ad):
    return {
        'id': ad.uuid,
        'subject': ad.subject,
        'body': ad.body,
        'price': ad.price,
        'email': ad.email
    }


@app.route('/ads', methods=['GET', 'POST'])
def ads():
    if request.method == 'GET':
        db_ad_list = g.s.query(db.Ad)
        return_ad_list = list()
        for ad in db_ad_list:
            return_ad_list.append(ad_to_dict(ad))
        return jsonify(return_ad_list)

