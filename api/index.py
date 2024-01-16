# -*- coding: utf-8 -*-
import requests
import pickle
from geopandas import GeoDataFrame
from shapely.geometry import Point
from flask import Flask, jsonify
# from @vercel/blob import put
from http import HTTPStatus

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


def handler(request):
    try:
        # Extract data from the request body
        data_to_write = request.json().get('data')

        # Write data to the Blob store
        blob_url = write_to_blob(data_to_write)

        # Respond with the URL where the data is stored
        return {
            'statusCode': HTTPStatus.OK,
            'body': {'url': blob_url},
        }
    except Exception as e:
        # Handle errors
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': {'error': str(e)},
        }

def write_to_blob(data_to_write):
    # Generate a unique filename or use a specific one
    filename = 'example.txt'

    # Save the data to the Blob store
    blob_url = put(filename, data_to_write, {'access': 'public'}).url

    return blob_url

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
            json_str = kalpiyot.to_json(force_ascii=False, orient='records')

    except:
        return 'Error to find the closet calpi'
    # send it to the Vercel function
    data_to_write = {'content': 'This is the content of the file.'}
    # Make a POST request to the create_and_write function
    # requests.post('https://kalpi-server.vercel.app/', json={'data': data_to_write})
    requests.post\
        ("https://n0hkbszkewfd5scr.public.blob.vercel-storage.com/saveBlob-p098JuUz1T8tQ9rozz1oJ5upFdGEBK.js",
                  data=str(kalpiyot['symbol']))
    return json_str


@app.route('/')
def home():
    return '???'







