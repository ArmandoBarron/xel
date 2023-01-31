#!/usr/bin/python3
from flask import Flask, jsonify, request
from flask_api import status
import subprocess
import os
# import requests
# import simplejson as json
from config import Config, ProductionConfig, DevelopmentConfig


app = Flask(__name__)
app.config.from_object(Config())
if app.config.get('ENV') == 'production':
  app.config.from_object(ProductionConfig())
if app.config.get('ENV') == 'development':
  app.config.from_object(DevelopmentConfig())


@app.route('/', methods=['GET'])
def h():
  return jsonify({'msg': 'Deployer'}), status.HTTP_200_OK

@app.route('/stacks/deploy', methods=['POST'])
def deploy():
  s = status.HTTP_400_BAD_REQUEST
  res = {'msg': 'Error'}
  rj = request.json
  print(rj, flush=True)
  if not rj.get('wf_name'):
    return jsonify(res), s
  c = os.sep.join([os.getcwd(), 'cfg-files', rj.get('wf_name') + '.cfg'])
  args = './puzzlemesh/puzzlemesh -c '+c+' -m ' + rj.get('deployment_mode')
  print(args, flush=True)
  sp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
  sp.wait()
  if sp.returncode == 0:
    s = status.HTTP_200_OK
    res['msg'] = 'deployed'
  stdouterr, _ = sp.communicate()
  stdouterr = stdouterr.decode("utf-8")
  res['out'] = stdouterr
  return jsonify(res), s

@app.route('/stacks/run', methods=['POST'])
def run():
  s = status.HTTP_400_BAD_REQUEST
  res = {'msg': 'Error'}
  rj = request.json
  if not rj.get('wf_name'):
    return jsonify(res), s
  c = os.sep.join([os.getcwd(), 'cfg-files', rj.get('wf_name') + '.cfg'])
  args = './puzzlemesh/puzzlemesh -c '+c+' -m ' + rj.get('deployment_mode') + " -exec T -api " + rj.get('apikey') + " -access " + rj.get('access_token')+ " -token " + rj.get('tokenuser')
  print(args, flush=True)
  sp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
  sp.wait()
  if sp.returncode == 0:
    s = status.HTTP_200_OK
    res['msg'] = 'executed'
  stdouterr, _ = sp.communicate()
  stdouterr = stdouterr.decode("utf-8")
  res['out'] = stdouterr
  res['code'] = sp.returncode
  return jsonify(res), s

@app.route('/stacks/remove', methods=['POST'])
def remove():
  pass
  # TODO: docker stack rm <stack>

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)