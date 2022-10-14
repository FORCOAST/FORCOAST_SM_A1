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

import xarray as xr 
import pandas as pd
import numpy as np
import datetime
import requests

def exists(path):
  
    r = requests.head(path,timeout=10)
    # Status code 200 = OK
    if r.status_code == requests.codes.ok:
        code = 200
        status = True
        return code, status
    # Status code 404 = not found
    if r.status_code == 404:
        code = 404
        status = False
        return code, status
    if r.status_code == 999:
        code = 999
        status = False
        return code, status
    # Anything else = assume something wrong with server
    if r.status_code != 200 & r.status_code != 404:
        code = r.status_code
        status = False
        return code, status

def a1_data_thredds(t_start_datetime,period,dt,lati,loni):

	# Check latest available time

	t_latest_hydro = t_start_datetime
	t_latest_meteo = t_start_datetime

	check = False
	while check == False:

		code, status = exists("http://thredds.maretec.org/thredds/fileServer/IST_MOHID_BIO_DATA/LISOCEAN_0.003DEG_50L_3H/FORECAST/" + t_latest_hydro.strftime("%Y%m%d%H") + "_Surface.nc")

		if status == True:
			check = True

		print(check)
		t_latest_hydro = t_latest_hydro - datetime.timedelta(days=1)

	t_start_hydro = t_latest_hydro + datetime.timedelta(days=1)

	check = False
	while check == False:

		code, status = exists("http://thredds.maretec.org/thredds/fileServer/WRF/TAGUS_3KM_1L_1H/FORECAST/" + t_latest_meteo.strftime("%Y%m%d%H") + ".nc")
			
		if status == True:
			check = True

		print(check)
		t_latest_meteo = t_latest_meteo - datetime.timedelta(days=1)

	t_start_meteo = t_latest_meteo + datetime.timedelta(days=1)

	for pp in range(period):

		print(pp)

		time_hydro = t_start_hydro + dt.timedelta(days=pp)
		time_meteo = t_start_meteo + dt.timedelta(days=pp)

		url_hydro = "http://thredds.maretec.org/thredds/dodsC/IST_MOHID_BIO_DATA/LISOCEAN_0.003DEG_50L_3H/FORECAST/" + time_hydro.strftime("%Y%m%d%H") + "_Surface.nc"
		url_meteo = "http://thredds.maretec.org/thredds/dodsC/WRF/TAGUS_3KM_1L_1H/FORECAST/" + time_meteo.strftime("%Y%m%d%H") + ".nc"

		print(url_hydro)
		print(url_meteo)

		# First day of data should be there, following check we did with "exists"
		if pp == 0:

			hydro = xr.open_dataset(url_hydro)

			ssh = hydro['ssh'].sel(lon=loni, lat=lati, method='nearest')
			u = hydro['u'].sel(lon=loni, lat=lati, depth=1, method='nearest')
			v = hydro['v'].sel(lon=loni, lat=lati, depth=1, method='nearest')
			vm = hydro['vm'].sel(lon=loni, lat=lati, depth=1, method='nearest')

			meteo = xr.open_dataset(url_meteo)

			air_temperature = meteo['air_temperature'].sel(lon=loni, lat=lati, method='nearest')
			wind_modulus = meteo['wind_modulus'].sel(lon=loni, lat=lati, method='nearest')
			x_wind = meteo['x_wind'].sel(lon=loni, lat=lati, method='nearest')
			y_wind = meteo['y_wind'].sel(lon=loni, lat=lati, method='nearest')	

		if pp != 0:

			# Subsequent days unsure, hence use try
			try:

				hydro = xr.open_dataset(url_hydro)

				ssh = xr.concat([ssh, hydro['ssh'].sel(lon=loni, lat=lati, method='nearest')], dim="time")
				u = xr.concat([u, hydro['u'].sel(lon=loni, lat=lati, depth=1, method='nearest')], dim="time")
				v = xr.concat([v, hydro['v'].sel(lon=loni, lat=lati, depth=1, method='nearest')], dim="time")
				vm = xr.concat([vm, hydro['vm'].sel(lon=loni, lat=lati, depth=1, method='nearest')], dim="time")

			except:

				print('No data for ' + url_hydro)

			try:

				meteo = xr.open_dataset(url_meteo)

				air_temperature = xr.concat([air_temperature, meteo['air_temperature'].sel(lon=loni, lat=lati, method='nearest')], dim="time")
				wind_modulus = xr.concat([wind_modulus, meteo['wind_modulus'].sel(lon=loni, lat=lati, method='nearest')], dim="time")
				x_wind = xr.concat([x_wind, meteo['x_wind'].sel(lon=loni, lat=lati, method='nearest')], dim="time")
				y_wind = xr.concat([y_wind, meteo['y_wind'].sel(lon=loni, lat=lati, method='nearest')], dim="time")

			except:

				print('No data for ' + url_meteo)

		## MAKE HYDRO DATAFRAME

	time_hydro = pd.Series(ssh.time.values, dtype="string")
	ssh = pd.Series(ssh[:].values, dtype="float")
	u = pd.Series(u[:].values, dtype="float")
	v = pd.Series(v[:].values, dtype="float")
	vm = pd.Series(vm[:].values, dtype="float")
	df_hydro = pd.concat([u,v,vm,ssh,time_hydro], axis=1)

	df_hydro.columns = ["velocity_U","velocity_V","velocity_modulus","water_level", "time"]
	df_hydro["time"] = pd.to_datetime(time_hydro, format='%Y-%m-%dT%H:00:00.000000000')
	df_hydro = df_hydro.set_index("time")
	print(df_hydro)

	df_hydro.to_csv('./output/hydro_combined.csv')

	## MAKE METEO DATAFRAME

	time_meteo = pd.Series(air_temperature.time.values, dtype="string")
	air_temperature = pd.Series(air_temperature[:].values, dtype="float")
	wind_modulus = pd.Series(wind_modulus[:].values, dtype="float")
	x_wind = pd.Series(x_wind[:].values, dtype="float")
	y_wind = pd.Series(y_wind[:].values, dtype="float")
	precip = pd.Series(np.zeros_like(y_wind[:].values), dtype="float")
	df_meteo = pd.concat([air_temperature,precip,wind_modulus,x_wind,y_wind,time_meteo], axis=1)

	df_meteo.columns = ["air_temperature","precipitation","wind_modulus","wind_velocity_X","wind_velocity_Y", "time"]
	df_meteo["time"] = pd.to_datetime(time_meteo, format='%Y-%m-%dT%H:00:00.000000000')
	df_meteo = df_meteo.set_index("time")
	print(df_meteo)

	df_meteo.to_csv('./output/meteo_combined.csv')

	all_data = df_hydro.join(df_meteo)
	all_data = all_data[~all_data.index.duplicated(keep='first')]
	
	return all_data

