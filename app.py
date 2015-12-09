#!flask/bin/python
from flask import Flask, jsonify

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

def create():
	pass
def show():
	pass
def update():
	pass
def destroy():
	pass

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)