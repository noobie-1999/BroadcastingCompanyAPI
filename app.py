from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

class Subscriptions(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    channel  =db.Column(db.Integer, db.ForeignKey('channel.channel_id'))

    def __init__(self,person, channel):
        self.sub_id = db.session.query(db.func.count(Subscriptions.sub_id)).all()[0][0]+1
        self.person = person
        self.channel = channel
    
    def __repr__(self):
        return "PersonID:"+str(self.person)+" ChannelID:"+str(self.channel)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    channels = db.relationship("Channel", secondary='subscriptions')

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
    
    def __repr__(self):
        return "UserID:"+str(self.user_id)

class Channel(db.Model):
    channel_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    subscribers = db.relationship("User", secondary='subscriptions')

    def __init__(self, channel_id, name):
        self.channel_id = channel_id
        self.name = name
    
    def __repr__(self):
        return "ChannelID:"+str(self.channel_id)

@app.route('/')
def home():
    return "Hello World"

@app.route('/adduser', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        user = User(data['user_id'], data['name'])
        print(user)
        db.session.add(user)
        db.session.commit()
        return jsonify({"status":"success"})
    except:
        return jsonify({"status":"failure"})

@app.route('/getusers', methods=['GET'])
def get_users():
    try:
        users = db.session.query(User).all()
        user_dict = OrderedDict()
        for user in users:
            temp_dict = {}
            temp_dict['user_id'] = user.user_id
            temp_dict['name'] = user.name
            user_dict[user.user_id] = temp_dict
        print(user_dict)
        return jsonify(user_dict)
    except:
        return "Hello"

@app.route('/addsubscription', methods=['POST'])
def add_subscription():
    try:
        data = request.get_json()
        sub = Subscriptions(data['person_id'], data['channel_id'])
        db.session.add(sub)
        db.session.commit()
        return jsonify({"status":"success"})
    except:
        return jsonify({"status":"failure"})

@app.route('/getchannelsbyuser/<int:user_id>', methods=['POST'])
def get_channels_by_user(user_id):
    try:
        data = request.get_json()
        channels = db.session.query(User).filter(User.user_id==user_id).all()[0].channels
        channel_dict = OrderedDict()
        key = 1
        for channel in channels:
            channel_dict[key] = channel.name
            key = key+1
        print(channel_dict)
        return jsonify(channel_dict)
    except:
        return jsonify({"status":"failure"})

if(__name__=='__main__'):
    app.run(debug=True)
