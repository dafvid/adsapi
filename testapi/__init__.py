# -*- coding: utf-8 -*-
import json
import logging
from uuid import uuid4

from email_validator import validate_email, EmailNotValidError
from flask import g, Flask, request, jsonify, abort
from flask_cors import cross_origin
from sqlalchemy import desc
from werkzeug.exceptions import HTTPException

from . import db

__version__ = '201008.1'

logging.basicConfig()
_log = logging.getLogger('testapi')
_log.setLevel(logging.DEBUG)

app = Flask(__name__)

adb = db.DB()
# create database it doesn't exist
if not adb.exists():
    adb.create()


# add the database session to the request context
@app.before_request
def before_request():
    g.s = adb.get_session()


# closes the connection after the request
@app.teardown_appcontext
def teardown_appcontext(error):
    if hasattr(g, 's'):
        g.s.close()


# wraps HTTPExceptions in JSON
# from https://flask.palletsprojects.com/en/master/errorhandling/
@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


# the index(root) route just returns the API version string
@app.route('/')
def index():
    return 'Ad API v0.1'


# serve the specification from the root rather than from /static
@app.route('/openapi.yaml')
@cross_origin()
def openapi():
    return app.send_static_file('openapi.yaml')


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
    if 'price' in ad_dict:
        ad.price = ad_dict['price']
    ad.email = ad_dict['email']
    return ad


# route to list all ads or add a new ad
@app.route('/ads', methods=['GET', 'POST'])
@cross_origin()
def ads():
    client_errors = list()
    # GET verb returns a list of ads
    if request.method == 'GET':
        # check for invalid parameters
        for k in request.args.keys():
            if k not in ['sort', 'order']:
                client_errors.append("parameter '{}' not allowed".format(k))
        sort = request.args.get('sort', 'created')
        # check for invalid sort parameter values
        if sort not in ['created', 'price']:
            client_errors.append("sort parameter must be 'created' or 'price'")
        order = request.args.get('order', 'desc')
        # check for invalid order parameter values
        if order not in ['asc', 'desc']:
            client_errors.append("order parameter must be 'asc' or 'desc'")

        # raise client error if any client errors
        if client_errors:
            return abort(400, ', '.join(client_errors))

        # query all ads from the db
        db_ad_list = g.s.query(db.Ad)

        # sort the ads by the sort and order parameters
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
        # convert all items to dicts for JSON-conversion
        for ad in db_ad_list.all():
            return_ad_list.append(ad_to_dict(ad))

        # return the list as JSON
        return jsonify(return_ad_list)
    # POST verb create a new ad
    elif request.method == 'POST':
        client_errors = list()
        ad_dict = request.json

        # check for required keys
        keys = ['subject', 'body', 'email']
        for k in keys:
            if k not in ad_dict:
                client_errors.append("Missing '{}' in body".format(k))

        # validate email
        try:
            validate_email(ad_dict['email'])
        except EmailNotValidError as e:
            client_errors.append(str(e))

        # if price is set then it has to be > 0
        if 'price' in ad_dict:
            if ad_dict['price'] < 0:
                client_errors.append('price must be positive or zero')

        # abort with code 400 if any errors
        if client_errors:
            abort(400, ', '.join(client_errors))

        # convert JSON dict to DB Ad
        ad = ad_from_dict(ad_dict)
        ad.uuid = uuid4()  # generate UUID
        g.s.add(ad)
        g.s.commit()

        return jsonify(success=True), 201


# get a specific ad or delete one
@app.route('/ads/<ad_id>', methods=['GET', 'DELETE'])
@cross_origin()
def ads_id(ad_id):
    if request.method == 'GET':
        # query db for Ad based on UUID
        ad = g.s.query(db.Ad).filter(db.Ad.uuid == ad_id).one()

        return jsonify(ad_to_dict(ad))
    elif request.method == 'DELETE':
        # delete Ad from DB based on UUID
        g.s.query(db.Ad).filter_by(uuid=ad_id).delete()
        g.s.commit()

        return jsonify(success=True), 204
