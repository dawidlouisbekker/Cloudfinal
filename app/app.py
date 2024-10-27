from flask import Flask, request, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
from pymongo import MongoClient

#from redis import Redisf
import secrets
import random
import string
import hashlib
import os




app = Flask(__name__)

mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = int(os.getenv('MONGO_PORT', 27017))
client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")

topiccollections = client["projects"]

collection = topiccollections["project"]

@app.route("/get")

@app.route("/gettopiccollections")
def topiccollections():
    pass
    

# Create a new document
@app.route('/addToTopic', methods=['POST'])
def create_document():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 201


@app.route('/read', methods=['GET'])
def read_documents():
    documents = list(collection.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])  
    return jsonify(documents)


@app.route('/update/<id>', methods=['PUT'])
def update_document(id):
    data = request.json
    result = collection.update_one({"_id": id}, {"$set": data})
    return jsonify({"modified_count": result.modified_count}), 200

@app.route('/delete/<id>', methods=['DELETE'])
def delete_document(id):
    result = collection.delete_one({"_id": id})
    return jsonify({"deleted_count": result.deleted_count}), 200






app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{os.getenv("POSTGRES_USER")}:'f'{os.getenv("POSTGRES_PASSWORD")}@'f'{os.getenv("POSTGRES_HOST")}/'f'{os.getenv("POSTGRES_DB")}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app=app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    token = db.Column(db.String(65), unique=False, nullable=True)
    online = db.Column(db.Boolean, nullable=True ) 
    
    def json(self):
        return {'id' : self.id, 'username' : self.username , 'token' : self.token}
'''class Topics(db.Model):
    name = db.Column(db.String(150), primary_key=True)
    owner = db.Column(db.String(150), unique=False, nullable=False)
    collectionsID = db.Column(db.String(150), unique=True, nullable=False)'''

class Questionaires(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), unique=True, nullable = False)
    answer = db.Column(db.String(500))
    
 
with app.app_context():
    db.create_all()

key = "23908jowknw9n4wijnice"

@app.route("/test" ,methods = ["GET"])
def test():
    return make_response(jsonify({'message' : 'test route'}), 200)

def AESDecrypt(input, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pad(input.encode(),AES.block_size)
    

@app.route("/", methods = ["GET"])
async def verify():
    IV = GenerateIV()
    app.config["IV"] = IV
    hashobject = hashlib.md5(IV)
    app.config["Key"] = hashobject.hexdigest()
    print(app.config["Key"])
    print(IV)
    return IV

@app.route("/uploadquestionaire",methods = ["POST"] )
def UploadQuestionaire():
    data = request.get_json()
    print(data)
    question = data.get('question')
    answer = data.get('answer')
    new_user = Questionaires(Question = question, Answer = answer)
    return make_response("succes",200)
       
@app.route("/GetQuestionaire", methods = ["POST"])
def getQuestionaire():
    data = request.get_json()
    id = int(data)
    questions= Questionaires.query.filter_by(id=id).first()
    request_data = {
        'id' : f'{id}',
        'question' : f'{questions.question}',
        'answer' : f'{questions.answer}'
    }
    return make_response(jsonify(request_data), 200)


@app.route("/ez",methods = ["GET"] )
def GetQuestionaireWeb():
    questoinaires = Questionaires.query.all()
    jsonQuestion = {"questionaires" : [question.json() for question in questoinaires]}
    return make_response(([question.json() for question in questoinaires]), 200)
        


@app.route("/salt", methods=["POST"])
def GiveSalt():
    data = request.get_data()
    
    print(data.decode('utf-8'))
    a = secrets.choice(string.digits)
    b = secrets.choice(string.digits)
    c= secrets.choice(string.digits)
    x = secrets.choice(string.digits)
    context = random.randint(0,3)
    jsonvar = { "1": a,"2" : b,"3" : c, "4" : x, "5" : context} 
    return jsonify(jsonvar)


    
def GenerateIV():
    IV = get_random_bytes(16)
    return IV

@app.route("/login", methods=["POST"])
def login():
    credentials = request.get_json()
    username = credentials.get("username")
    password = credentials.get("password")
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            token = "".join(random.choices(string.ascii_letters + string.digits,k=64))
            user.token = token
            user.online = True
            return make_response(jsonify({"token" : token, "ID" : user.id}),200)
        
    return make_response("",401)

@app.route("/logout", methods = ["POST"])
def logout():
    data = request.get_json()
    user = User.query.filter_by(id=id).first()
    return make_response(200)
    

@app.route("/user/add", methods= ["POST"])
def create_user():
    data = request.get_json()
    username = data["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        return make_response("user exists",500)
    
    try:
        temptoken = "".join(random.choices(string.ascii_letters + string.digits,k=64))
        new_user = User(username=data["username"], password=data['password'], token=temptoken, online=True)
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"token" : temptoken}),200)#make_response(jsonify({'message' : "user created"}),201)
    except:
        return make_response("error creating",500) 

@app.route("/users", methods = ["GET"])
def get_user():
    try:
        users = User.query.all()
        #if len(users):
        return make_response(jsonify({"users" : [user.json() for user in users]}), 200)
        #return make_response(jsonify({'message' : 'no user found'}), 404)
    except:
        return make_response(jsonify({'message' : 'error getting users'}), 500)
    
@app.route("/users/<int:id>", methods = ["GET"])
def UpdateUser(id):
    try:
        data = request.get_json()
        user = User.query.filter_by(id=id).first()
        if user:
            user.username = data["username"]
            db.session.commit()
        return make_response(jsonify({'user': "user updated"}),200)
    except:
        return "error"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)