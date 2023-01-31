from flask import Flask, jsonify, request, json
from exe import execute
from exe2 import remove
#from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
#CORS(app)

with open('conf.json', 'r') as f:
    conf = json.load(f)['server']
f.close()

@app.route("/start_services", methods=['POST'])
def start_services():
    data = request.get_json()
    data = json.loads(data)
    success, data = execute(data)
    if(success):
        return jsonify({conf['create_services_response_field']:conf['create_services_success_response'], conf['create_services_id_field']:data})
    return jsonify({conf['create_services_response_field']:conf['create_services_error_response'], conf['create_services_error_cause_field']:data})

@app.route("/remove_services", methods=['POST','GET'])
def remove_services():
    id = request.args.get(conf['remove_services_id_name'])
    if(remove(id)):
        return jsonify({conf['remove_services_response_field']:conf['remove_services_success_response']})
    return jsonify({conf['remove_services_response_field']:conf['remove_services_error_response']})

if __name__=="__main__":
    #app.run(host=conf['server_ip'], port=conf['server_port'], debug=True,  use_reloader=True)
    serve(app, host=conf['server_ip'], port=conf['server_port'], threads=4)