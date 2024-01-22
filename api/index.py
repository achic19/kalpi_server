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


def geo_code_fun(row, one_point=False):
    # Geocode a location
    try:
        json_object = json.loads(row)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={json_object['street']},{json_object['city']},israel"
    except json.JSONDecodeError:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={row},israel"
    params = {
        "key": API_KEY,
    }
    # url = f"https://maps.googleapis.com/maps/api/geocode/json?address={row},israel"
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
# def write_post(sorce,ballot):
#     # 1.  Connect to PostgreSQL
#     db_url = os.getenv("postgres://default:ISE3lKgq6kfe@ep-wispy-limit-89580954-"
#                        "pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb")
#     # Use the environment variable for database URL
#     parsed_url = urlparse(db_url)
#     connection = psycopg2.connect(
#         host=parsed_url.hostname,
#         port=parsed_url.port,
#         database=parsed_url.path[1:],
#         user=parsed_url.username,
#         password=parsed_url.password
#     )
#
#     # Create a cursor
#     cursor = connection.cursor()
#
#     # Define a table and column (replace 'your_table' and 'column_name' with your actual table and column names)
#     table_name = 'sp'
#     # Insert JSON data into the table
#     cursor.execute(f'INSERT INTO SP (Adr, Ballot) VALUES ({sorce},{ballot} )')
#
#     # Commit the transaction
#     connection.commit()
#
#     # Close the cursor and connection
#     cursor.close()
#     connection.close()


@app.route('/kalpi/<address>')
def find_kalpi(address):
    try:
        res = geo_code_fun(address, True)
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
        return 'Error to find the closet calpi'
    # try:
    #     write_post(str(pnt_x_y),str(nearby_ballot.loc[0].geometry))
    # except:
    #     return json_str
    return json_str


@app.route('/')
def home():
    return '???'
