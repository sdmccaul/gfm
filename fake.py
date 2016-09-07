#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.cors import CORS

from models.VocabMgmt import VocabTerm
from models.RDFResource import RDFResource
from graphsession import Session
from graphdb import GraphInterface

app = Flask(__name__)
CORS(app)
gi = GraphInterface()


@app.route('/rabdata/fisfeed/faculty/', methods=['GET'])
def index():
	try:
		allFisFaculty = FisFaculty.search()
	except:
		return 404
	return json.dumps(allFisFaculty)


@app.route('/rabdata/fisfeed/faculty/', methods=['POST'])
def create():
	try:
		new = FisFaculty.create(json.loads(resp.body))
	except:
		return 400
	return response(code=201, body=new)

@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['GET'])
def retrieve(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	data = json.dumps(fisfac)
	return response(code=200, body=data)

@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['PUT'])
def replace(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	if fisfac.ETag == req.headers["If-Match"]:
		try:
			updated = FisFaculty.overwrite(fisfac, json.loads(req.body))
		except:
			return 400
		return response(code=201, body=updated)
	else:
		return 409


@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['DELETE'])
def destroy(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	if fisfac.ETag == req.headers["If-Match"]:
		try:
			fisfac.remove()
		except:
			return 403
		return 204
	else:
		return 409

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)