#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        serialized_campers = [camper.to_dict(rules=('-activities', '-signups')) for camper in campers]
        for dicts in serialized_campers:
            dicts.pop('created_at')
            dicts.pop('updated_at')
        return serialized_campers
    elif request.method == 'POST':
        new_camper = Camper(
            name = request.get_json()["name"],
            age = request.get_json()["age"]
        )
        db.session.add(new_camper)
        db.session.commit()

        return make_response(jsonify(new_camper.to_dict()), 201)
    return {'error': '400: Validation Error'}, 400

@app.route('/campers/<int:id>')
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        serialized_camper = camper.to_dict()
        serialized_camper.pop('created_at')
        serialized_camper.pop('updated_at')
        serialized_camper.update({"activities": serialized_camper["signups"]})
        serialized_camper.pop('signups')
        return make_response(jsonify(serialized_camper), 200)
    return {'error': '404: Camper not found'}, 404

@app.route('/activities')
def activities():
    activities = Activity.query.all()
    serialized_acts = [activity.to_dict() for activity in activities]
    for acts in serialized_acts:
        acts.pop('created_at')
        acts.pop('updated_at')
        acts.pop('signups')
    response = make_response(jsonify(serialized_acts), 200)
    return response

@app.route('/activities/<int:id>', methods=["DELETE"])
def delete_activity(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()

        return make_response('', 204)
    
    return "404: Activity Not Found", 404

@app.route('/signups', methods=['POST'])
def create_signup():
    new_signup = Signup(
        time = request.get_json()["time"],
        camper_id = request.get_json()["camper_id"],
        activity_id = request.get_json()["activity_id"]
    )
    if new_signup:
        db.session.add(new_signup)
        db.session.commit()
        return make_response(jsonify(new_signup.to_dict()), 201)
    return {'error': '400: Validation Error'}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
