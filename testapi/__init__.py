# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from flask import g, Flask, request, jsonify
from flask_cors import cross_origin

from . import db

__version__ = '201008.1'

logging.basicConfig()
_log = logging.getLogger('testapi')
_log.setLevel(logging.DEBUG)

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


# Converts an Ad DB object to a dict
def ad_to_dict(ad):
    return {
        'id': ad.uuid,
        'subject': ad.subject,
        'body': ad.body,
        'price': ad.price,
        'email': ad.email
    }


# Converts a dict (from JSON) to a Ad DB object
def ad_from_dict(ad_dict):
    ad = db.Ad()
    ad.subject = ad_dict['subject']
    ad.body = ad_dict['body']
    ad.price = ad_dict['price']
    ad.email = ad_dict['email']
    return ad


@app.route('/ads', methods=['GET', 'POST'])
@cross_origin()
def ads():
    if request.method == 'GET':
        db_ad_list = g.s.query(db.Ad)
        return_ad_list = list()
        for ad in db_ad_list:
            return_ad_list.append(ad_to_dict(ad))

        return jsonify(return_ad_list)
    elif request.method == 'POST':
        ad_dict = request.json
        ad = ad_from_dict(ad_dict)
        ad.uuid = uuid4()
        g.s.add(ad)
        g.s.commit()

        return jsonify(success=True), 201
