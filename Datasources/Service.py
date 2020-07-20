#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for,jsonify
from bins import *
from mixer import mixer
import json

app = Flask(__name__)

@app.route('/')
def prueba():
    return "Meteorological microservice"

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


@app.route('/getDS', methods=['POST'])
def byClust():

    puntos = request.get_json()

    fuentes = puntos['fuentes'].split(",") #fuentes de datos separadas por ,

    sources =dict()
    #obtener los datos de las fuentes
    for fuente in fuentes:
        sources[fuente]= GetSource(puntos['polygon'],puntos['inicio'],puntos['fin'],fuente)
    tool = mixer(sources)
    tool.group()
    data = json.loads(tool.merge_data())
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200,debug = True)
    #ssl_context=('Certificados/cert.pem', 'Certificados/key.pem')