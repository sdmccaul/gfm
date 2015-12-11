#!flask/bin/python
from flask import Flask, jsonify
from models import Credential

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/rabdata/api/v0.1/credentials', methods=['GET'])
def index():
	credentials = Credential.all()
	return jsonify(credentials)

@app.route('/rabdata/api/v0.1/credentials/<rabid>', methods=['GET'])
def show(rabid=None):
	if rabid is None:
        raise Exception("No rabid provided")
	credential = Credential.find(rabid=rabid)
	return jsonify(credential)

def create(params):
	credential = Credential.new(params)
	if credential.save():
		redirect(url_for('credentials'))
	else:
		pass

def update(params):
	credential = Credential.find(params['rabid'])
	if credential.update():
		redirect(url_for(credential))
	else:
		pass

def destroy(params):
	Credential.find(params['rabid']).destroy()
	redirect(url_for('credentials'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)