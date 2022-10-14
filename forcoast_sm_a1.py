#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
# --------------------------------------------------------------------
#  Copyright 2022 Maretec
#   Francisco Campuzano
#
#   campuzanofj.maretec@tecnico.ulisboa.pt
#
#    This work is licenced under a Creative Commons Attribution 4.0 
#	 International License.
#
#
#        https://creativecommons.org/licenses/by/4.0/
# --------------------------------------------------------------------

import os
import xarray as xr 
from ftplib import FTP
import sys
import datetime as dt
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
from numpy import ma
from datetime import datetime
import os
import pytz
from pandas.tseries.frequencies import to_offset
# import telegram
import matplotlib
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pandas.tseries.frequencies import to_offset
import argparse
import a1_data_thredds
from matplotlib.ticker import FormatStrFormatter
import a1_data_geoserver
import math
# import datetime

# Get input from command line arguments

parser = argparse.ArgumentParser(description = "Description for my parser")
parser.add_argument("-p", "--pilot", help = "Set pilot area", required = True, default = "sado_estuary")
parser.add_argument("-T", "--T0", help = "Set reference time", required = True, default = "2021-09-26")
parser.add_argument("-lat", "--lati", help = "Latitude", required = True, default = "38.7229344")
parser.add_argument("-lon", "--loni", help = "Longitude", required = True, default = "-9.0917642")
parser.add_argument("-lim", "--TIDETHRESHOLD", help = "Workability threshold", required = True, default = "1.9")

argument = parser.parse_args()

lati = float(argument.lati)
loni = float(argument.loni)
TIDETHRESHOLD = float(argument.TIDETHRESHOLD)
t_start = argument.T0

# t_start = "2021-09-26"
period = 3
# TIDETHRESHOLD = 1.9

# Portugal (Tagus)
# loni = -9.0917642
# lati =38.7229344

print("pilot")
print(argument.pilot)

t_start_datetime = dt.datetime.strptime(str(t_start),"%Y-%m-%d")

def is_dst(dttime,timeZone):
   aware_dt = timeZone.localize(dttime)
   return aware_dt.dst() != dt.timedelta(0,0)

timeZone = pytz.timezone("Europe/Lisbon")
CORRECT_FOR_SUMMERTIME = is_dst(t_start_datetime,timeZone)

dataRange = range(1,period)
dataRangeData = range(0,period)	

# Read data from THREDDS service

if argument.pilot == "sado_estuary":
	all_data=a1_data_thredds.a1_data_thredds(t_start_datetime,period,dt,lati,loni)
elif argument.pilot == "limfjord":
	all_data=a1_data_geoserver.a1_data_geoserver_process(lati,loni,t_start,period)


if CORRECT_FOR_SUMMERTIME:
	all_data.index = all_data.index + dt.timedelta(hours=1)

## get api data from sunrise/sunset api
sunrise = []
sunset = []
for day in dataRange:
	print("day:")
	print(day)
	dateAPI = (t_start_datetime+dt.timedelta(days=day)).strftime("%Y-%m-%d")
	resp = requests.get(f"https://api.sunrise-sunset.org/json?lat={lati}&lng={loni}&date={dateAPI}", verify=False)
	sunrise.append(datetime.strptime(dateAPI + 'T' +resp.json()["results"]["sunrise"], '%Y-%m-%dT%I:%M:%S %p'))
	sunset.append(datetime.strptime(dateAPI + 'T'+ resp.json()["results"]["sunset"], '%Y-%m-%dT%I:%M:%S %p'))
	
	
if CORRECT_FOR_SUMMERTIME:	
	for idx in range(len(sunrise)):
		sunrise[idx] = sunrise[idx] + dt.timedelta(hours=1)
	for idx in range(len(sunset)):
		sunset[idx] = sunset[idx] + dt.timedelta(hours=1)

#calculate high and low tides
tides = all_data["water_level"].values
times = all_data["water_level"].index

f_prime = np.gradient(tides) # differential approximation
indices = np.where(np.diff(np.sign (f_prime)))[0] # Find the inflection point.
#sometimes there are minor oscilations around the min and max tide. if that happens within one hour take the first one
#a = np.append(np.diff(indices)>10,True)
#indices = indices[a]
print("indices:")
print(indices)

for x, res in enumerate(indices): 
	if abs(f_prime[res]) > abs(f_prime[res+1]):
		indices[x] = res+1
		if f_prime[res] < 0 and f_prime[res+1] > 0:
			f_prime[res+1] = -f_prime[res+1]
		elif f_prime[res] > 0 and f_prime[res+1] < 0:
			f_prime[res+1] = -f_prime[res+1]

print("indice (update):")
print(indices)
print("f_prime[indices]")
print(f_prime[indices])

maxTideTimes = times[indices[f_prime[indices]>0]]
minTideTimes = times[indices[f_prime[indices]<0]]
maxTides = tides[indices[f_prime[indices]>0]]
minTides = tides[indices[f_prime[indices]<0]]

print("Debug tides:")
print(tides)
print("f_prime:")
print(f_prime)
print("maxTideTimes:")
print(maxTideTimes)
print("minTideTimes:")
print(minTideTimes)
print("maxTides:")
print(maxTides)
print("minTides:")
print(minTides)

print("Debug sunrise:")
print(sunrise)
print(sunset)

YELLOW = "#f6c56d"
ORANGE = "#fda03f"
ORANGERED = "#ff5b30"
GREEN = "#08695d"
BLUE = "#36b5b1"
RED = "#ff0000"

nsubplots = 1
nrows = len(dataRange)/nsubplots

def pos_from_time(time, day):
	
	#defines poisiton in plot from time
	pos = float(datetime.strftime(time,'%H'))/(nrows*24) \
		+ float(datetime.strftime(time,'%M'))/60/(nrows*24) \
		+ day/(nrows) 
	return pos + 0.018

def get_color_patch_wind(value):
	#color for wind values
	if value>24:
		return "#ff0000"
	elif value>20:
		return "#f6c56d"
	else:
		return "#25A24E"

def get_color_patch_precipitation(value):
	#according to https://www.ipma.pt/pt/educativa/faq/meteorologia/previsao/faqdetail.html?f=/pt/educativa/faq/meteorologia/previsao/faq_0033.html
	#color for precipitation values
	if value>4:
		return "#7F00FF"
	elif value>0.5:
		return "#9999FF"
	else:
		return "#ffffff"
	

tidePlot = plt.figure(figsize=(30,7))
#tidePlot.subplots_adjust(hspace=1)

for row in range(nsubplots):

	maxPlot = max(maxTides) + .9*(max(maxTides)-min(minTides))
	if TIDETHRESHOLD >= maxPlot:
		maxPlot = TIDETHRESHOLD + max(maxTides) + .9*(max(maxTides)-min(minTides))
	minPlot = min(minTides) - .9*(max(maxTides)-min(minTides))
	if TIDETHRESHOLD <= minPlot:
		minPlot = TIDETHRESHOLD - min(minTides) - .9*(max(maxTides)-min(minTides))
	plotRange = maxPlot - minPlot
	positionMultiplication = 2
	
	plt.subplot(nsubplots,1,row+1)
	dateInitial = (t_start_datetime+dt.timedelta(days=dataRange[(row)*2])).strftime("%Y-%m-%d")  
	dateFinal = (t_start_datetime+dt.timedelta(days=dataRange[(row)*2+1])).strftime("%Y-%m-%d") 
	plt.plot(times,tides, color=BLUE, linewidth=8)
	plt.box(on=None)
	ax = plt.gca()
	start_plot= datetime.combine(t_start_datetime+dt.timedelta(days=dataRange[row*2]), datetime.min.time())
	if row ==0:
		xposition= start_plot + dt.timedelta(hours=35)
		axins = ax.inset_axes([pos_from_time(xposition,1), 1 , .23, 1.1])
		im = plt.imread(os.path.join(os.getcwd(), "icons","colab_logo.png"))
		axins.imshow(im)
		axins.axis("off")
		
		plt.text(start_plot+dt.timedelta(hours=1), maxPlot+plotRange/positionMultiplication, \
				 "Night tide", fontsize=20, c=GREEN, zorder=200, ha='left',clip_on=False , va='center')
		plt.text(start_plot+dt.timedelta(hours=7), maxPlot+plotRange/positionMultiplication, \
				 "Optimal tide", fontsize=20, c= BLUE  , zorder=200,clip_on=False, ha='left', va='center')
		plt.text(start_plot+dt.timedelta(hours=13), maxPlot+plotRange/positionMultiplication, \
				 "Work Threshold", fontsize=20, c="#ff0000", \
				 clip_on=False,zorder=200, ha='left', va='center')
		plt.axhline(y = maxPlot+plotRange/positionMultiplication-plotRange/20, xmin=pos_from_time(start_plot+dt.timedelta(hours=0.1),0),   \
					xmax=pos_from_time(start_plot+dt.timedelta(hours=5),0), \
					color=GREEN,zorder=5000, linewidth=3,clip_on=False )
		
		plt.axhline(y = maxPlot+plotRange/positionMultiplication-plotRange/20, xmin=pos_from_time(start_plot+dt.timedelta(hours=6),0),   \
					xmax=pos_from_time(start_plot+dt.timedelta(hours=11),0), \
					color=BLUE,zorder=5000, linewidth=3,clip_on=False )
		plt.axhline(y = maxPlot+plotRange/positionMultiplication-plotRange/20, xmin=pos_from_time(start_plot+dt.timedelta(hours=12),0),   \
					xmax=pos_from_time(start_plot+dt.timedelta(hours=23),0), \
					color="#ff0000",zorder=5000, linewidth=3,clip_on=False )

		position_text = str(round(lati, 3)) + "N, " + str(round(loni, 3)) + "W"		
		
		plt.text(start_plot+dt.timedelta(hours=26), maxPlot+plotRange/positionMultiplication+plotRange/60, \
				 position_text, fontsize=20, fontweight="bold",c="#000000", zorder=200, ha='left',clip_on=False , va='center')
	
	plt.xlim([datetime.strptime(dateInitial + "T00:00", '%Y-%m-%dT%H:%M'), datetime.strptime(dateFinal + "T23:59", '%Y-%m-%dT%H:%M')])
	# Y-AXIS
	ax.yaxis.set_label_coords(-0.02,0.96)
	ax.yaxis.get_majorticklabels()[2].set_x(-0.03)
	for ylabeltick in ax.yaxis.get_majorticklabels():
		ylabeltick.set_x(-0.03)
	for line in ax.yaxis.get_ticklines():
		line.set_data([-.025, 0])	
	ax.yaxis.set_tick_params(width=4, length=30, color="#d3d3d3")
	#plt.yticks(np.arange(0, tides.max(), step=1), fontsize=22)
	plt.yticks(np.arange(minPlot, maxPlot, step=plotRange/6), fontsize=22)
	ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
	plt.ylabel("Water level (m)", loc='top', fontsize = 22,rotation=0)

	# X-AXIS
	for xlabeltick in ax.xaxis.get_majorticklabels():
		xlabeltick.set_y(-0.02)
	ax.xaxis.set_major_locator(mdates.HourLocator(interval=3)) 
	myFmt = mdates.DateFormatter('%H')
	ax.xaxis.set_major_formatter(myFmt)
	plt.xticks(fontsize=22)
	
	## PLOT LIMITS
	
	plt.ylim([minPlot, maxPlot])
	
	print(start_plot)
	plt.text(start_plot-dt.timedelta(hours=4), minPlot-plotRange/3.2,\
				 "Wind\n (km/h)", fontsize=22, c="000000", zorder=200, ha='center', va='center')
	plt.text(start_plot-dt.timedelta(hours=4), minPlot-plotRange/3.2*1.5, \
				 "Precipitation\n (mm/h)", fontsize=22, c="000000", zorder=200, ha='center', va='center')
	plt.text(start_plot-dt.timedelta(hours=4), minPlot-plotRange/7, \
			 "Time", fontsize=22, c="000000", zorder=200, ha='center', va='center')
	plt.text(start_plot-dt.timedelta(hours=0),\
			 TIDETHRESHOLD+plotRange/20, "lim= {}m".format(TIDETHRESHOLD), fontsize=20, c="#ff0000",zorder=1000, ha='left', va='center')

	ax.add_patch(matplotlib.patches.Rectangle((start_plot, TIDETHRESHOLD), \
			 dt.timedelta(hours=48), maxPlot-TIDETHRESHOLD, fc = "#ffffff", lw = 10,alpha=0.75,zorder=10))
	
	for idx_day,day in enumerate(dataRange[(row)*2:(row)*2+2]):
		
		# X-AXIS
		for xlabeltick in ax.xaxis.get_majorticklabels():
			xlabeltick.set_y(-0.02)
		ax.xaxis.set_major_locator(mdates.HourLocator(interval=3)) 
		myFmt = mdates.DateFormatter('%H')
		ax.xaxis.set_major_formatter(myFmt)
		plt.xticks(fontsize=22)

		
		## DAY AND NIGHT
		nday = day-dataRange[0]
		date = (t_start_datetime+dt.timedelta(days=day)).strftime("%Y-%m-%d")  
		print("date:")
		print(date)
		start = mdates.date2num(datetime.strptime(date + "T00:00", '%Y-%m-%dT%H:%M'))
		print("start:")		
		print(start)

		print("nday:")		
		print(nday)

		width = mdates.date2num(sunrise[nday]) - start 
		print("width:")
		print(width)
		
		ax.add_patch(matplotlib.patches.Rectangle((start, minPlot), width, maxPlot-minPlot, 
								fc = GREEN, lw = 10, alpha=0.7,zorder=100))
		start = mdates.date2num(sunset[nday])
		width = mdates.date2num(datetime.strptime(date + "T23:59", '%Y-%m-%dT%H:%M')) - start+0.001
		ax.add_patch(matplotlib.patches.Rectangle((start, minPlot), width, maxPlot-minPlot, 
								fc = GREEN, lw = 10,alpha=0.7,zorder=100))


		if nday !=0 and nday!=dataRange[-1]:
			start = mdates.date2num(sunrise[nday])
			width = dt.timedelta(minutes = 45)


		## WORKING HOURS
		
		time_min_work = times[(tides>=TIDETHRESHOLD) & (times>sunrise[nday]) & (times<sunset[nday])].min()
		time_max_work = times[(tides<=TIDETHRESHOLD) & (times>sunrise[nday]) & (times<sunset[nday]) \
							 & (times>time_min_work)].min()
		ax.add_patch(matplotlib.patches.Rectangle((sunrise[nday], TIDETHRESHOLD), \
							sunset[nday]- sunrise[nday], maxPlot-TIDETHRESHOLD, 
								fc = "#ffffff", lw = 10,alpha=0.9,zorder=10))
		
		daytimeTides = tides[(times>sunrise[nday]) & (times<sunset[nday])]
		dayTimes = times[(times>sunrise[nday]) & (times<sunset[nday])]
		workingSpots = dayTimes[np.argwhere(np.diff(np.sign(daytimeTides - TIDETHRESHOLD))).flatten()]
		
		for spot in workingSpots:
			plt.text(spot-dt.timedelta(minutes=0), minPlot+plotRange/10, spot.strftime("%Hh%M"),\
				fontsize=26,  c="#ff0000", ha='center', va='center',zorder=3000)
			plt.axvline(x=spot, ymin=0.12, \
				ymax=(TIDETHRESHOLD-minPlot)/(maxPlot-minPlot), color="#ff0000", ls="--", zorder=200)
		
		
		
		ax.axhline(y=TIDETHRESHOLD, color="#ff0000",zorder=50, alpha=1, linewidth=3)
		y_scale_im = 0.065
		## SUNRISE/SUNSET INDICATORS
		axins = ax.inset_axes([pos_from_time(sunset[nday],idx_day)-0.05, 1 , y_scale_im, .2])
		im = plt.imread(os.path.join(os.getcwd(), "icons","sunset.png"))
		axins.imshow(im)
		axins.axis("off")
		plt.text(sunset[nday]-dt.timedelta(minutes=0), maxPlot+plotRange/positionMultiplication/2, sunset[nday].strftime("%Hh%M"),\
				 fontsize=26,  c="000000", ha='center', va='center')
		axins = ax.inset_axes([pos_from_time(sunrise[nday],idx_day)-0.05, 1 , y_scale_im, .2])
		im = plt.imread(os.path.join(os.getcwd(), "icons","sunrise.png"))
		axins.imshow(im)
		axins.axis("off")
		plt.text(sunrise[nday]-dt.timedelta(minutes=0), maxPlot+plotRange/positionMultiplication/2, sunrise[nday].strftime("%Hh%M"), \
				 fontsize=26, c="000000", ha='center', va='center')
		sun_noon = sunrise[nday] + (sunset[nday]-sunrise[nday])/2
		weekday = sunrise[nday].strftime("%a %d/%m").replace("Mon", "Monday").replace("Tue","Tuesday").replace("Wed","Wednesday").replace("Thu","Thursday").replace("Fri","Friday").replace("Sat","Saturday").replace("Sun","Sunday")
		plt.text(sun_noon-dt.timedelta(minutes=0), maxPlot+plotRange/positionMultiplication-plotRange/positionMultiplication/3, \
				 weekday, \
				 fontsize=26, c="000000",zorder=1000, ha='center', va='center')
		
		
		
		start = datetime.strptime(date + "T00:00", '%Y-%m-%dT%H:%M')
		plt.axhline(y = maxPlot+plotRange/positionMultiplication-plotRange/positionMultiplication/3, xmin=pos_from_time(start+dt.timedelta(hours=.05),idx_day)-0.02,   \
					xmax=pos_from_time(start+dt.timedelta(hours=8),idx_day), \
					color="#7E7E7E",zorder=5000, linewidth=3,clip_on=False )
		plt.axhline(y = maxPlot+plotRange/positionMultiplication-plotRange/positionMultiplication/3, xmin=pos_from_time(start+dt.timedelta(hours=16),idx_day),\
					xmax=pos_from_time(start+dt.timedelta(hours=23),idx_day),\
					color="#7E7E7E",zorder=5000, linewidth=3,clip_on=False )
		
		
		## TIDE INDICATORS
		high_tides = maxTideTimes[(maxTideTimes>sunrise[nday]) & (maxTideTimes<sunset[nday])]
		for idx_tide,high_tide in enumerate(high_tides):
			high_tide_pos=pos_from_time(high_tide.to_pydatetime(),idx_day)-0.05
			yimagepos=0.21#(TIDETHRESHOLD-plotRange/5-minPlot)/(maxPlot-minPlot)
			axins = ax.inset_axes([high_tide_pos, yimagepos , y_scale_im, .2], zorder=200)
			im = plt.imread(os.path.join(os.getcwd(), "icons","high_tide.png"))
			axins.imshow(im)
			axins.axis("off")
			high_tide_time = maxTideTimes[(maxTideTimes>sunrise[nday]) & (maxTideTimes<sunset[nday])][idx_tide].to_pydatetime()
			plt.axvline(x=high_tide_time, ymin=yimagepos, \
						ymax=maxTides[(maxTideTimes>sunrise[nday]) & (maxTideTimes<sunset[nday])][idx_tide]/maxPlot, color=BLUE, ls="--", zorder=200)
			plt.text(high_tide_time-dt.timedelta(minutes=0),minPlot + plotRange/6 ,\
			maxTideTimes[(maxTideTimes>sunrise[nday]) & (maxTideTimes<sunset[nday])][idx_tide].to_pydatetime().strftime("%Hh%M"),\
					 fontsize=28, c="000000", zorder=200, ha='center', va='center')
			plt.text(high_tide_time-dt.timedelta(minutes=0), minPlot + plotRange/10, \
					 "{:.1f} m".format(maxTides[(maxTideTimes>sunrise[nday]) & (maxTideTimes<sunset[nday])][idx_tide]), \
					 fontsize=24, c="000000", zorder=200, ha='center', va='center')

		low_tides = minTideTimes[(minTideTimes>sunrise[nday]) & (minTideTimes<sunset[nday])]
		for idx_tide,low_tide in enumerate(low_tides):
			low_tide_pos = pos_from_time(minTideTimes[(minTideTimes>sunrise[nday]) & \
									(minTideTimes<sunset[nday])][idx_tide].to_pydatetime(), idx_day)-0.05
			yimagepos=0.63#(TIDETHRESHOLD+plotRange/10-minPlot)/(maxPlot-minPlot)
			axins = ax.inset_axes([low_tide_pos, yimagepos , y_scale_im, .2], zorder=200)
			
			im = plt.imread(os.path.join(os.getcwd(), "icons","low_tide.png"))
			axins.imshow(im)
			axins.axis("off")
			low_tide_time = minTideTimes[(minTideTimes>sunrise[nday]) & (minTideTimes<sunset[nday])][idx_tide].to_pydatetime()
			plt.axvline(x=low_tide_time,\
						ymin=(minTides[(minTideTimes>sunrise[nday]) & (minTideTimes<sunset[nday])][idx_tide]-minPlot)/(maxPlot-minPlot), \
										ymax=yimagepos, color=BLUE, ls="--", zorder=200)
			plt.text(low_tide_time-dt.timedelta(minutes=0), minPlot + 9.2*plotRange/10, \
					 minTideTimes[(minTideTimes>sunrise[nday]) & (minTideTimes<sunset[nday])][idx_tide].to_pydatetime().strftime("%Hh%M"), \
					 fontsize=28, c="000000", zorder=200, ha='center', va='center')
			plt.text(low_tide_time-dt.timedelta(minutes=0), minPlot + 5.1*plotRange/6, \
					 "{:.1f} m".format(minTides[(minTideTimes>sunrise[nday]) & (minTideTimes<sunset[nday])][idx_tide]),\
					 fontsize=24, c="000000", zorder=200, ha='center', va='center')


		## HOUR TICKS
		for hour in range(0,24+1,3):
			initial_y = -0.16
			end_y =-0.14
			plt.axvline(x=start+dt.timedelta(hours=hour), ymin=initial_y, 
					   ymax=(end_y+0.03), color="#000000", lw=4, zorder=200, clip_on=False)
			if hour>0:
				plt.axvline(x=start+dt.timedelta(hours=hour-1), ymin=initial_y, 
							ymax=end_y, color="#8f8f8f", lw=4, zorder=200, clip_on=False)
			if hour<24:
				plt.axvline(x=start+dt.timedelta(hours=hour+1), ymin=initial_y, 
						ymax=end_y, color="#8f8f8f", lw=4, zorder=200, clip_on=False)
		## WIND TABLE
		start = datetime.strptime(date + "T00:00", '%Y-%m-%dT%H:%M')

		start_day = (t_start_datetime+dt.timedelta(days=day)).strftime("%Y-%m-%d") 
		end_day = (t_start_datetime+dt.timedelta(days=day+1)).strftime("%Y-%m-%d") 
		
		all_data["wind_modulus_kmh"] = all_data["wind_modulus"]*3.6

		grouped_all_data = all_data.resample('3H', offset="-1H").mean()
		grouped_all_data.index = grouped_all_data.index + to_offset("H")
		grouped_all_data["angle"] = np.arctan2(grouped_all_data["wind_velocity_Y"],grouped_all_data["wind_velocity_X"])

		mask = (grouped_all_data.index >= start_day) & (grouped_all_data.index <= end_day)

		
		for index, row in grouped_all_data[mask].iterrows():
			#print(index,row['wind_modulus'])
		
			y0 = minPlot-plotRange/3.2
			x0 = index
			plt.text(x0-dt.timedelta(minutes=70), y0-plotRange/9/2,
					 "{:.0f}".format(row['wind_modulus_kmh']) , fontsize=22, c="000000", zorder=500)
			ax.add_patch(matplotlib.patches.Rectangle((x0-dt.timedelta(minutes=90),
							y0-plotRange/9/(nsubplots+0.2)), dt.timedelta(hours=3), 1/(nsubplots+0.4)*plotRange/5, 
							fc = get_color_patch_wind(row['wind_modulus_kmh']), lw = .5,alpha=1,zorder=400, clip_on=False,\
													 edgecolor='#d3d3d3'))
			y0_arrow = y0 -plotRange/25
			x0_arrow = x0 + dt.timedelta(minutes=15) if len("{:.0f}".format(row['wind_modulus_kmh']))==1 else x0 + dt.timedelta(minutes=30)
			scale_y = plotRange/11#.9/(nsubplots+.5)
			
			if math.isnan(row['angle']) == False:
				arrow = mpatches.FancyArrowPatch((x0_arrow-np.cos(row['angle'])/2*dt.timedelta(minutes=60), \
												  y0_arrow-np.sin(row['angle'])/2*scale_y),
												 (x0_arrow + np.cos(row['angle'])/2*dt.timedelta(minutes=60), 
												  y0_arrow+ np.sin(row['angle'])/2*scale_y),\
										 clip_on=False, zorder=500,mutation_scale=20, color="black")
				ax.add_patch(arrow)
				
			y0 =minPlot-plotRange/3.2*1.5
			plt.text(x0-dt.timedelta(minutes=35), y0-plotRange/9/2,
					 "{:.1f}".format(abs(row['precipitation'])) , fontsize=22, c="000000", zorder=500)
			ax.add_patch(matplotlib.patches.Rectangle((x0-dt.timedelta(minutes=90),
							y0-plotRange/9/(nsubplots+0.2)), dt.timedelta(hours=3), 1/(nsubplots+0.4)*plotRange/5, 
							fc = get_color_patch_precipitation(row['precipitation']), lw = .5,alpha=1,\
									zorder=400, clip_on=False, edgecolor='#d3d3d3'))
		

dayToday = datetime.today().strftime("%d%m%y")
tidePlot.savefig(os.path.join(os.getcwd(), "output",f"forcoast_a1_bulletin_temp.png"), bbox_inches='tight', dpi=96)
