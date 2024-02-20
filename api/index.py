# -*- coding: utf-8 -*-
import requests
import pickle
from geopandas import GeoDataFrame
from shapely.geometry import Point
from flask import Flask, jsonify
import json
import urllib.parse

import os
from os.path import join as jn

def find_en_name(my_str):
  # This function know how to find the city from google api address
  format_s = my_str.split(',')
  comma_count = my_str.count(',')
  return format_s[0] if comma_count==0 or comma_count==1 else format_s[1]

# folder that store the database for the algorithm
main_folder = 'assets'
# Read data form the assets
with open(jn(main_folder,'gdf_voroni.pkl'), "rb") as f:
    poly_voroni= pickle.load(f)
with open(jn(main_folder,'voroni_pnts.pkl'), "rb") as f:
    pnt_voronoi= pickle.load(f)

with open(jn(main_folder,'gdf_voroni_local.pkl'), "rb") as f:
    poly_voroni_local= pickle.load(f)
with open(jn(main_folder,'voroni_pnts_local.pkl'), "rb") as f:
    pnt_voronoi_local= pickle.load(f)

with open(jn(main_folder,'places_dic.pkl'), "rb") as f:
    places_dic2= pickle.load(f)

app = Flask(__name__)

API_KEY = os.environ["GOOGLE_API"]  

def geo_code_fun(row):
    # Geocode a location
    params = {
        "key": API_KEY,
    }
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={row},israel"
    response = requests.get(url, params=params)

    # Check the response status code
    if response.status_code == 200:
        # The request was successful
        return response.json()
    else:
        # The request failed
        print("Request failed")

def add_in_data(is_in_data,area_eb,res=False):
  "This function find the relevant kalpi/s"
  # no kalpi
  if is_in_data.iloc[0]['is_minimum']==0:
    return False
  # at least one kalpi, pull out the relevant kalpis to choose from
  temp_data_pnts= pnt_voronoi_local[pnt_voronoi_local['reg']==area_eb]
  # if there is only one kalpi
  if is_in_data.iloc[0]['is_minimum']==1:
    return temp_data_pnts
  # there are more than one ballot, make sure if we need to to geo-coding
  if not res:
    res  = geo_code_fun(address)
  # Create new point from the geocoding
  Y = res['results'][0]['geometry']['location']['lat']
  X = res['results'][0]['geometry']['location']['lng']
  point2 = Point(X,Y)
  # if there are  two points, find the closet one
  if is_in_data.iloc[0]['is_minimum']==2:
    groups =  pnt_voronoi_local[pnt_voronoi_local['reg']==area].groupby(level=0)
    dis_1 = groups.get_group(-2).iloc[0].geometry.distance(point2)
    dis_2 = groups.get_group(-3).iloc[0].geometry.distance(point2)
    if dis_1 <dis_2:
      return groups.get_group(-2)
    else:
      return groups.get_group(-3)
  # if there are more than two - find the relevant polygons 
  temp_data_polys= poly_voroni_local[poly_voroni_local['reg']==area_eb]
  # find the relevant polygons that intersect the new point
  nearby_ballot = GeoDataFrame(geometry=[point2],crs='EPSG:4326').sjoin(temp_data_polys)
  # drop_duplicates is when our code includes same location with a different ballot symbol
  return temp_data_pnts.loc[nearby_ballot['index_right']]



@app.route('/kalpi/<address>')
def find_kalpi(address):
  # First- clean up the data
  address= address.replace('"', '').replace("'", '').replace("-", ' ').strip()
  # Decode the URL-encoded text
  address = urllib.parse.unquote(address)
  area= address.split(',')[0]
  return area
  is_in_data = places_dic2[(places_dic2['location']==area) | (places_dic2['name_en']==area.lower())]
  return is_in_data.to_json(force_ascii=False,orient='records')
  # if len(is_in_data)>0:
  #     area_eb = is_in_data.iloc[0]['area']
  #     kalpiyot= add_in_data(is_in_data,area_eb)
  # else:
  #     res  = geo_code_fun(address)
  #     name = find_en_name(res['results'][0]['formatted_address']).strip().lower()
  #     is_in_data = places_dic2[places_dic2['name_en']== name]
  #     if len(is_in_data)>0:
  #         area_eb = is_in_data.iloc[0]['area']
  #         kalpiyot= add_in_data(is_in_data,area_eb,res)
  #     else:
  #         Y = res['results'][0]['geometry']['location']['lat']
  #         X = res['results'][0]['geometry']['location']['lng']
  #         point2 = Point(X,Y)
  #         nearby_ballot = GeoDataFrame(geometry=[point2],crs='EPSG:4326').sjoin(poly_voroni)
  #         # drop_duplicates is when our code includes same location with a different ballot symbol
  #         kalpiyot = pnt_voronoi.loc[nearby_ballot['index_right']]
  # if kalpiyot is False:
  #   return "No Kalpi"
  # else:
  #   kalpiyot[['address','location']]= kalpiyot[['address','location']].apply(lambda x:x.str.replace("'",'').str.replace('"',''))
  #   return kalpiyot[['address','location','symbol']].to_json(force_ascii=False,orient='records')
@app.route('/')
def home():
    return '???'
