# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from flask import g, Flask, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import desc

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
        'email': ad.email,
        'created': ad.created.isoformat(timespec='seconds')+'Z'  # timezonehack
    }


# Converts a dict (from JSON) to an Ad DB object
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
        sort = request.args.get('sort', 'created')
        assert sort in ['created', 'price']
        order = request.args.get('order', 'desc')
        assert order in ['asc', 'desc']
        db_ad_list = g.s.query(db.Ad)
        if sort == 'created':
            if order == 'asc':
                db_ad_list = db_ad_list.order_by(db.Ad.created)
            else:
                db_ad_list = db_ad_list.order_by(desc(db.Ad.created))
        elif sort == 'price':
            if order == 'asc':
                db_ad_list = db_ad_list.order_by(db.Ad.price)
            else:
                db_ad_list = db_ad_list.order_by(desc(db.Ad.price))

        return_ad_list = list()
        for ad in db_ad_list.all():
            return_ad_list.append(ad_to_dict(ad))

        return jsonify(return_ad_list)
    elif request.method == 'POST':
        ad_dict = request.json
        ad = ad_from_dict(ad_dict)
        ad.uuid = uuid4()
        g.s.add(ad)
        g.s.commit()

        return jsonify(success=True), 201


@app.route('/ads/<ad_id>', methods=['GET', 'DELETE'])
@cross_origin()
def ads_id(ad_id):
    if request.method == 'GET':
        ad = g.s.query(db.Ad).filter(db.Ad.uuid == ad_id).one()

        return jsonify(ad_to_dict(ad))
    elif request.method == 'DELETE':
        g.s.query(db.Ad).filter_by(uuid=ad_id).delete()
        g.s.commit()

        return jsonify(success=True), 201
