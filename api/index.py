# -*- coding: utf-8 -*-
import requests
import pickle
from geopandas import GeoDataFrame
from shapely.geometry import Point
from flask import Flask, jsonify

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


def geo_code_fun(row, one_point=False):
    # Geocode a location
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={row},israel"
    params = {
        "key": API_KEY,
    }

    response = requests.get(url, params=params)

    # Check the response status code
    if response.status_code == 200:
        # The request was successful
        data_coded = response.json()
        if one_point:
            return data_coded
        else:
            geocoding_data.append(data_coded)
    else:
        # The request failed
        print("Request failed")


@app.route('/kalpi/<address>')
def find_kalpi(address):
    try:
        res = geo_code_fun(address, True)
        if res == 'Request failed':
            return "Geo coding error."
        else:
            Y = res['results'][0]['geometry']['location']['lat']
            X = res['results'][0]['geometry']['location']['lng']

            crs_geo = 'EPSG:4326'
            nearby_ballot = GeoDataFrame(geometry=[Point(X, Y)], crs=crs_geo).sjoin(gdf_voroni)
            kalpiyot = pnt_voronoi.loc[nearby_ballot['index_right']][['address', 'location', 'symbol']]
            json_str = kalpiyot.to_json(force_ascii=False, orient='records').replace("\\", "")

    except:
        return ""
    # send it to the Vercel function
    try:
        requests.post("https://n0hkbszkewfd5scr.public.blob.vercel-storage.com/saveBlob-30gP8sWgozkg5EBOqiOeFTS3MXpwgN.js", json={"json_data": json_str})
    except:
        return json_str
    return json_str


@app.route('/')
def home():
    return '???'
