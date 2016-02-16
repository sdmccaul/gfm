#!flask/bin/python
from flask import Flask, jsonify
from models import FisFaculty

from sparqldb import SparqlInterface
from triplemanager import SessionGraph

app = Flask(__name__)
db = SparqlInterface()
access = SessionGraph(db)


#@app.route('/rabdata/api/v0.1/fisfeed/faculty/', methods=['GET'])
def index():
	allFisFac = FisFaculty.all()
	return jsonify(allFisFac)

@app.route('/rabdata/api/v0.1/fisfeed/faculty/', methods=['POST'])
def create(params):
	fisFac = FisFaculty.new(params)
	if fisFac.save():
		redirect(url_for('faculty'))
	else:
		pass

@app.route('/rabdata/api/v0.1/fisfeed/faculty/<rabid>', methods=['GET'])
def show(rabid=None):
	if rabid is None:
        raise Exception("No rabid provided")
	fisFac = FisFaculty.find(rabid=rabid)
	return jsonify(fisfac)


@app.route('/rabdata/api/v0.1/fisfeed/faculty/<rabid>', methods=['PUT'])
def update(params):
	fisFac = FisFaculty.find(rabid=rabid)
	if fisFac.update(params=params):
		redirect(url_for(rabid))
	else:
		pass

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)