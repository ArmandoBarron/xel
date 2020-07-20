from HandlerDB import *
import requests
import configparser
from time import sleep
import json
import numpy as np 
import pandas as pd



def GetSource(puntos,inicio,fin,source):
	conexion = HandlerDB()
	poly = format_polygon(puntos)
	DS = conexion.GetFont(poly,inicio,fin,source) #EMASMAX
	conexion.CerrarConexion()
	return DS


# --------------- UTILS (FUNCIONES DE UTILERIA) ---------------------


def format_polygon(poligono):
	poly ="("
	for i in range(1,len(poligono)+1):
		poly = poly+"("+str(poligono[str(i)]['lon'])+","+str(poligono[str(i)]['lat'])+"),"
	poly = poly[:-1] +")" 
	return poly
