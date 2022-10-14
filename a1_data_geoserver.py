#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
# --------------------------------------------------------------------
#  Copyright 2022 Deltares
#   Daniel Twigt
#
#   daniel.twigt@deltares.nl
#
#    This work is licenced under a Creative Commons Attribution 4.0 
#	 International License.
#
#
#        https://creativecommons.org/licenses/by/4.0/
# --------------------------------------------------------------------

import os
import tempfile
from owslib.wcs import WebCoverageService
from owslib.wms import WebMapService
import datetime
import rasterio as rio
import pandas as pd
import numpy as np
import math
from urllib.request import urlopen
import json

def a1_data_geoserver(store,coverage,lat,lon,T0,period):

	# store="forcoast"
	# coverage="limfjord_elev"
	# lat=56.9404
	# lon=9.0434
	# T0 = "2021-11-28"
	# period = 2

	url = 'https://forecoast.apps.k.terrasigna.com/geoserver/ows?'
	wcs = WebCoverageService(url,version='2.0.1')
	#print(wcs.contents)

	# Read time positions from WMS getCapabilities, as these seem unavailable from WCS API
	wms = WebMapService(url, version='1.3.0')

	wms_layer = store + ":" + coverage
	wcs_layer = store + "__" + coverage
	data = wms[wms_layer]
	available_times = data.timepositions

	#lat_subset = ('Lat', lat)
	#long_subset = ('Long', lon)

	T0_start = datetime.datetime.strptime(str(T0),"%Y-%m-%d")
	T0_stop  = datetime.datetime.strptime(str(T0),"%Y-%m-%d") + datetime.timedelta(days=period)
	#delta = datetime.timedelta(hours=1)

	timeseries=[]
	times=[]

	#while T0_start <= T0_stop:

	for time in available_times:

		datetime_wms = datetime.datetime.strptime(time[0:-5], '%Y-%m-%dT%H:%M:%S')

		# If desired time is within avialable times, read data
		if datetime_wms >= T0_start and datetime_wms <= T0_stop:

			######## Old piece of code requesting a wcs-coverage, right now, a wms-request in made instead
			######## Leaving it here just in case - Gido
			#time_subset = ("time", time)
			#response = wcs.getCoverage(identifier=[wcs_layer], format='GeoTIFF', crs='EPSG:4326', subsets=[long_subset, lat_subset, time_subset])

			# print(response)

			# Dump to output file and read value
			# tmpdir = '.'
			# fn = os.path.join(tmpdir,'temp.tif')
			# f = open(fn,'wb')
			# f.write(response.read())
			# f.close()

			# src = rio.open('temp.tif')
			# array = src.read(1)			
			
			bbox="{},{},{},{}".format(lon-0.1,lat-0.1,lon+0.1,lat+0.1)
			url = f"https://forecoast.apps.k.terrasigna.com/geoserver/ows?service=WMS&version=1.1.1&request=GetFeatureInfo&crs=EPSG:4326&transparent=true&bbox={bbox}&x=50&y=50&feature_count=1&layers={wms_layer}&query_layers={wms_layer}&time={time}&width=101&height=101&format=image/png&info_format=application/json"
			response = urlopen(url)
			data_json = json.loads(response.read())
			data_value = data_json['features'][0]['properties']['GRAY_INDEX']

			print(data_value)

			timeseries.append(data_value)
			times.append(datetime_wms)

	df_times = pd.Series(times, dtype="string")
	df_values = pd.Series(timeseries, dtype="float")
	df_timeseries = pd.concat([df_times,df_values], axis=1)

	return df_timeseries

def a1_data_geoserver_process(lat,lon,T0,period):

	df_timeseries=a1_data_geoserver("forcoast","limfjord_elev",lat,lon,T0,period)

	time_hydro = df_timeseries[0]
	ssh = df_timeseries[1]

	u = pd.Series(np.zeros_like(ssh[:].values), dtype="float")
	v = pd.Series(np.zeros_like(ssh[:].values), dtype="float")
	vm = pd.Series(np.zeros_like(ssh[:].values), dtype="float")

	df_hydro = pd.concat([u,v,vm,ssh,time_hydro], axis=1)
	df_hydro.columns = ["velocity_U","velocity_V","velocity_modulus","water_level", "time"]
	df_hydro["time"] = pd.to_datetime(time_hydro, format='%Y-%m-%d %H:00:00')
	df_hydro = df_hydro.set_index("time")

	df_timeseries=a1_data_geoserver("forcoast","limfjord_uwind",lat,lon,T0,period)

	time_meteo = df_timeseries[0]
	x_wind= df_timeseries[1]

	df_timeseries=a1_data_geoserver("forcoast","limfjord_vwind",lat,lon,T0,period)

	y_wind= df_timeseries[1]

	wind_modulus = (x_wind**2+y_wind**2)**(1/2)

	wind_modulus_df = pd.Series(wind_modulus, dtype="float")

	precip = pd.Series(np.zeros_like(y_wind[:].values), dtype="float")
	air_temperature = pd.Series(np.zeros_like(y_wind[:].values), dtype="float")

	df_meteo = pd.concat([air_temperature,precip,wind_modulus_df,x_wind,y_wind,time_meteo], axis=1)
	df_meteo.columns = ["air_temperature","precipitation","wind_modulus","wind_velocity_X","wind_velocity_Y", "time"]
	df_meteo["time"] = pd.to_datetime(time_meteo, format='%Y-%m-%d %H:00:00')
	df_meteo = df_meteo.set_index("time")

	all_data = df_hydro.join(df_meteo)
	all_data = all_data[~all_data.index.duplicated(keep='first')]

	print(all_data)

	return all_data

# a1_data_geoserver_process(56.9404,9.0434,"2021-11-26",2)

