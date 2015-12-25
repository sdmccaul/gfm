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
	fisFacultyList = access.all(FisFaculty)
	return jsonify(fisFacultyList)

@app.route('/rabdata/api/v0.1/fisfeed/faculty/', methods=['POST'])
def create(params):
	credential = Credential.new(params)
	if credential.save():
		redirect(url_for('credentials'))
	else:
		pass

@app.route('/rabdata/api/v0.1/fisfeed/faculty/<rabid>', methods=['GET'])
def show(rabid=None):
	if rabid is None:
        raise Exception("No rabid provided")
	credential = Credential.find(rabid=rabid)
	return jsonify(credential)


@app.route('/rabdata/api/v0.1/fisfeed/faculty/<rabid>', methods=['PATCH'])
def update(params):
	credential = Credential.find(params['rabid'])
	if credential.update():
		redirect(url_for(credential))
	else:
		pass

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)