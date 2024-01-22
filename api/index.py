# -*- coding: utf-8 -*-
import requests
import pickle
from geopandas import GeoDataFrame
from shapely.geometry import Point
from flask import Flask, jsonify
from urllib.parse import urlparse
import json


import os

ASSETS_FOLDER = 'assets'
VORNOI_GDF = os.path.join(ASSETS_FOLDER, 'gdf_voroni.pkl')
VORNOI_PNTS = os.path.join(ASSETS_FOLDER, 'voroni_pnts.pkl')

with open(VORNOI_GDF, "rb") as f:
    gdf_voroni = pickle.load(f)
with open(VORNOI_PNTS, "rb") as f:
    pnt_voronoi = pickle.load(f)

app = Flask(__name__)

geocoding_data = []
API_KEY = os.environ["GOOGLE_API"]  #


def geo_code_fun(row):
    # Geocode a location
    params = {
        "key": API_KEY,
    }
    if ',' in row:
        list_str = row.split(',')
        list_str.reverse()
        row = ','.join(list_str)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={row},israel"
    response = requests.get(url, params=params)

    # Check the response status code
    if response.status_code == 200:
        # The request was successful
        data_coded = response.json()
        return data_coded

    else:
        # The request failed
        print("Request failed")


@app.route('/kalpi/<address>')
def find_kalpi(address):
    try:
        res,lang = geo_code_fun(address)
        if res == 'Request failed':
            return "Geo coding error."
        else:
            Y = res['results'][0]['geometry']['location']['lat']
            X = res['results'][0]['geometry']['location']['lng']
            pnt_x_y = Point(X, Y)
            crs_geo = 'EPSG:4326'
            nearby_ballot = GeoDataFrame(geometry=[pnt_x_y], crs=crs_geo).sjoin(gdf_voroni)
            kalpiyot = pnt_voronoi.loc[nearby_ballot['index_right']][['address', 'location', 'symbol']]
            json_str = kalpiyot.to_json(force_ascii=False, orient='records')

    except:
        return "No Kalpi"
    return json_str


@app.route('/')
def home():
    return '???'
