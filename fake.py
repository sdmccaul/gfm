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

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify( { 'error': 'Not found' } ), 404)

# @app.errorhandler(400)
# def not_found(error):
#     return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# @app.route('/rabdata/vocabmgmt/term/<rabid>', methods=['GET'])
# def show_term(rabid):
# 	sh = Session(gi)
# 	term = VocabTerm.find(
# 		"<http://vivo.brown.edu/individual/{0}>".format(rabid), sh)
# 	neighborProps = [
# 		"<http://www.w3.org/2004/02/skos/core#broader>",
# 		"<http://www.w3.org/2004/02/skos/core#narrower>",
# 		"<http://www.w3.org/2004/02/skos/core#related>"
# 	]
# 	neighbors = {}
# 	neighborURIs = []
# 	for p in neighborProps:
# 		neighborURIs.extend(term[p])
# 	if neighborURIs:
# 		for uri in neighborURIs:
# 			nbor = RDFResource.find(uri, sh).to_dict()
# 			neighbors[nbor['@id']] = {
# 					'display': nbor['<http://www.w3.org/2000/01/rdf-schema#label>'][0]
# 				}
# 	if not term:
# 		abort(404)
# 	else:
# 		resp = term.to_dict()
# 		resp['neighbors'] = neighbors
# 		return jsonify(resp)

# @app.route('/rabdata/vocabmgmt/term/<rabid>', methods=['PUT'])
# def update_term(rabid):
# 	sh = Session(gi)
# 	term = VocabTerm.find("http://vivo.brown.edu/individual/" + rabid, sh)
# 	data = request.json
# 	if term.update(data=data):
# 		term.save(sh)
# 		redirect(url_for('show_term', rabid=rabid))
# 	else:
# 		abort(400)

@app.route('/rabdata/fisfeed/faculty/', methods=['GET'])
def index():
	try:
		allFisFaculty = FisFaculty.all()
	except:
		return 404
	return json.dumps(allFisFaculty)


@app.route('/rabdata/fisfeed/faculty/', methods=['POST'])
def create():
	try:
		new = FisFaculty.create(resp.body)
	except:
		return 400
	new.save()
	return 201

@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['GET'])
def retrieve(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	data = json.dumps(fisfac)
	return data

@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['PUT'])
def update(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	if fisfac.ETag == req.headers["If-Match"]:
		resp = fisfac.overwrite(req.body)
		if resp == 200:
			return 200
		else:
			return resp
	else:
		return 409


@app.route('/rabdata/fisfeed/faculty/<rabid>', methods=['DELETE'])
def destroy(rabid):
	try:
		fisfac = FisFaculty.find(rabid=rabid)
	except:
		return 404
	if fisfac.ETag == req.ETag:
		fisfac.remove()
		return 204
	else:
		return 409

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)