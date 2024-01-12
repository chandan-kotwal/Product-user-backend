from flask import Flask, jsonify, request
from flask_basicauth import BasicAuth
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
import os


app = Flask(__name__)

DB_USERNAME = 'root'
DB_PASSWORD = 'password'
DB_HOST = os.getenv("DB_Host","localhost")
DB_PORT = '3306'
DB_NAME = 'productuser'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
ES_HOSTANME=os.getenv("ES_Host","localhost")
es = Elasticsearch([{'host': ES_HOSTANME, 'port': 9200,'scheme':"http"}])
index_name = 'item'



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


def check_credentials(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return True
    else:
        return False


basic_auth.check_credentials = check_credentials

@app.route("/health")
@basic_auth.required
def health():
    return jsonify(success=True), 200


@app.route("/api/v1/user")
@basic_auth.required
def get_users():
    users = User.query.all()
    return jsonify([{'username': user.username, 'password': user.password} for user in users])


@app.route("/api/v1/user/<username>")
@basic_auth.required
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'username': user.username, 'password': user.password})
    return jsonify({'message': 'User not found'}), 404


@app.route("/api/v1/user", methods=['POST'])
@basic_auth.required
def create_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route("/api/v1/item", methods=['GET'])
@basic_auth.required
def list_item():
    result = es.search(index=index_name, body={
        'query': {
            'match_all': {}
        }
    })
   
    if "error" in result:
            return jsonify({'error': "error in listing the items "}), 500

    hits = result.get('hits', {}).get('hits', [])

    response = {'index_content': []}
    for hit in hits:
        response['index_content'].append(hit['_source'])

    return jsonify(response)    

@app.route('/api/v1/item', methods=['POST'])
@basic_auth.required
def index_document():
    data = request.get_json()

    document_body = data

    es.index(index=index_name, body=document_body)

    return jsonify({'message': 'Document indexed successfully'}), 201






PORT = 3000

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=PORT,host="0.0.0.0")
