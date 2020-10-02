from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
from helpers import schedule_delivery, get_distance
import requests
import json
import datetime

app = Flask(__name__)

CORS(app)

# Mongo Setup
uri = 'mongodb+srv://'
client = MongoClient(uri,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=None,
                     socketKeepAlive=True)

db = client.Farmly


# json bs
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# Homepage
@app.route('/', methods=['GET'])
def index():
    return '<h1>Farmly Backend</h1>'


# Order Routes
@app.route('/add-order', methods=['POST'])
def add_order():
    # Adds order to DB after payment is processed
    try:
        order = request.get_json()
        order['idealDeliveryDate'] = datetime.datetime.strptime(order['idealDeliveryDate'], "%Y-%m-%d")
        # add order to delivery
        delivery_scheduled = schedule_delivery(order)
        if delivery_scheduled:
            order['deliveryStatus'] = 'scheduled'
            order_inserted = db.orders.insert(order)
            return Response(json.dumps({"message": "Delivery Scheduled", "orderId": str(order['_id']),
                                        "deliveryDate": str(delivery_scheduled)}), status=200,
                            mimetype='application/json')
        else:
            order['deliveryStatus'] = 'pending'
            order_inserted = db.orders.insert(order)
            return Response(json.dumps({"message": "Couldn't schedule delivery"}), status=409,
                            mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"message": "Couldn't add order", "error": e}), status=404,
                        mimetype='application/json')


@app.route('/cancel-order/<orderid>', methods=['PATCH'])
def cancel_order():
    # Cancels order, may need to issue refund
    pass


# Truck Routes
@app.route('/add-truck', methods=['POST'])
def add_truck():
    # Adds a truck that will deal with deliveries
    try:
        truck = request.get_json()
        print(truck)  # remove after
        if truck:
            truck_inserted = db.trucks.insert_one(truck)
            if truck_inserted:
                return Response(json.dumps({"message": "Truck Added"}), status=200, mimetype='application/json')
        return Response(json.dumps({"message": "Couldn't add truck, try again"}), status=400,
                        mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"message": "Couldn't add order", "error": e}), status=404,
                        mimetype='application/json')


@app.route('/get-trucks/', methods=['GET'])
def get_trucks():
    try:
        trucks = list(db.trucks.find({}))
        if trucks:
            return Response(
                json.dumps({"message": "{} trucks".format(len(trucks)), "data": trucks}, default=json_util.default),
                status=200, mimetype="application/json")
        else:
            return Response(json.dumps({"message": "No trucks"}), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"message": "Couldn't retrieve trucks", "error": e}, default=json_util.default()),
                        status=404, mimetype='application/json')


