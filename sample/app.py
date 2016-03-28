#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for

from models.VocabMgmt import VocabTerm
from graphsession import Session
from graphdb import GraphInterface

app = Flask(__name__)
gi = GraphInterface()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.route('/rabdata/vocabmgmt/term/<rabid>', methods=['GET'])
def show_term(rabid):
	sh = Session(gi)
	term = VocabTerm.find("http://vivo.brown.edu/individual/" + rabid, sh)
	if not term:
		abort(404)
	else:
		return jsonify(term.to_dict())

@app.route('/rabdata/vocabmgmt/term/<rabid>', methods=['PUT'])
def update_term(rabid):
	sh = Session(gi)
	term = VocabTerm.find("http://vivo.brown.edu/individual/" + rabid, sh)
	data = request.json
	if term.update(data=data):
		term.save(sh)
		redirect(url_for('show_term', rabid=rabid))
	else:
		abort(400)

# @app.route('/rabdata/vocabmgmt/term/', methods=['POST'])
# def new_term(rabid):
# 	sh = Session(gi)
# 	term = VocabTerm.find(uri="http://vivo.brown.edu/individual/" + rabid, sh)
# 	data = request.json
# 	if term.update(data=data):
# 		term.save(sh)
# 		redirect(url_for(rabid))
# 	else:
# 		pass


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)