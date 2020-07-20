import psycopg2
import psycopg2.extras
from datetime import datetime
from datetime import timedelta

import configparser

class HandlerDB:

	def __init__(self):
		config = configparser.ConfigParser()
		config.read('config.ini')

		host=config['Database']['host']
		user= config['Database']['user']
		pw=config['Database']['pass']
		DB= config['Database']['DB']
		puerto= config['Database']['port']

		self.state= config['Database']['state']

		self.mydb = psycopg2.connect(
		host=host,
		user=user,
		password=pw,
		database=DB,
		port = int(puerto)
		)
		self.mycursor = self.mydb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

	def GetFont(self,poligono,inicio,fin,font):
		if font == "EMAS":
			query = "select * from data_60m where \
					polygon(%s) @> point(''||data_60m.longitud||','||data_60m.latitud||'') and \
					to_date(data_60m.fecha,'DD-MM-YYYY') >= to_date(%s,'DD-MM-YYYY') and \
					to_date(data_60m.fecha,'DD-MM-YYYY') <= to_date(%s,'DD-MM-YYYY')"			 	
			self.mycursor.execute(query, (poligono,inicio,fin,))
			result = self.mycursor.fetchall()
			return result
		if font == "EMAS10":
			pass
		if font == "EMAS10":
			pass	
		if font == "MERRA":
			query = "select * from merra where \
					polygon(%s) @> point(''||merra.longitud||','||merra.latitud||'') and \
					to_date(merra.fecha,'DD-MM-YYYY') >= to_date(%s,'DD-MM-YYYY') and \
					to_date(merra.fecha,'DD-MM-YYYY') <= to_date(%s,'DD-MM-YYYY')"			 	
			self.mycursor.execute(query, (poligono,inicio,fin,))
			result = self.mycursor.fetchall()
			return result


	def commit(self):
		self.mydb.commit()

	def CerrarConexion(self):
		self.mycursor.close()
		self.mydb.close()

	def InsertarFilas(self,row):
		self.mycursor.execute('INSERT INTO merra_year(año,station_code,latitud, \
					longitud, temp_max,temp_min, temp_mean) \
					VALUES(%s, %s, %s, %s, %s, %s, %s)', 
					row)