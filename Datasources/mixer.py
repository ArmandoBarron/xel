from HandlerDB import *
import requests
import configparser
from time import sleep
import json
import numpy as np 
import pandas as pd



class mixer():

	def __init__ (self,datasources):
		self.keys = []
		self.datasources = dict()
		for key,value in datasources.items():
			self.keys.append(key)
			self.datasources[key] = pd.DataFrame.from_records(value) #load dataframes
			numeric_columns = self.getNumericColumns(key)
			self.datasources[key][numeric_columns] = self.datasources[key][numeric_columns].apply(pd.to_numeric, errors='coerce')
			if key == "EMAS": 
				dropcol = "id_60m"
			if key == "MERRA": 
				dropcol = "id_merra"

			self.datasources[key]= self.datasources[key].drop(columns=dropcol)

	def group(self):
		for key,value in self.datasources.items():
			groupbyVariable = self.getKEY(key)
			numeric_columns = self.getNumericColumns(key)
			self.datasources[key]= self.datasources[key].groupby(groupbyVariable).mean().reset_index()
			print(self.datasources[key])

	def getdata(self):
		datasources = dict()
		for key,value in self.datasources.items():
			datasources[key] = self.datasources[key].to_json(orient='records')
		return datasources

	def merge_data(self):
		sizek = len(self.keys)
		datasink = self.datasources[self.keys[0]] #obtenemos los primeros datos
		if sizek > 1: #si hay mas
			for x in range(1,sizek):
				df = self.datasources[self.keys[x]] 
				keygroup1 = self.getKEY(self.keys[0])
				keygroup2 = self.getKEY(self.keys[x])
				datasink = pd.merge(datasink, df, how='left', left_on=keygroup1, right_on=keygroup2)
				#format latitudes
				datasink = datasink.rename(columns = {'latitud_x':'latitud','longitud_x':'longitud'})
				datasink=datasink.drop(columns=['latitud_y','longitud_y'])

		return datasink.to_json(orient='records')

	def getKEY(self,key):
		if key == "EMAS": 
			att = ["codigo","fecha"]
		if key == "MERRA": 
			att = ["station_code","fecha"]

		return att
	
	def getNumericColumns(self,key):
		if key == "EMAS": 
			numeric_columns = ['dir_rafaga','dir_viento','vel_rafaga','vel_viento','temperatura','humedad','presion_barometrica','precipitacion','radiacion_solar']
		if key == "MERRA": 
			numeric_columns = ['temp_max','temp_min','temp_mean','prec_max']
		return numeric_columns