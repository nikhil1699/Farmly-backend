from flask import Flask,Blueprint, flash, g, redirect, render_template, request, session, url_for, Response,send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json

app = Flask(__name__)

CORS(app)

#Routes
@app.route('/',methods=['GET'])
def index():
	return '<h1>Farmly Backend</h1>'

