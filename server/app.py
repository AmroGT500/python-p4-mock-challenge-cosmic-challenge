from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource, reqparse
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Home route
@app.route('/')
def home():
    return 'Home'

# Scientist list resource
class ScientistListResource(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [scientist.to_dict() for scientist in scientists]

    def post(self):
        # Parse the request data
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be empty.')
        parser.add_argument('field_of_study', type=str, required=True, help='Field of study cannot be empty.')
        args = parser.parse_args()

        # Create the new scientist
        scientist = Scientist(name=args['name'], field_of_study=args['field_of_study'])
        db.session.add(scientist)
        db.session.commit()

        # Return the new scientist data
        return scientist.to_dict(), 201

# Scientist resource
class ScientistResource(Resource):
    def get(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        return scientist.to_dict()

    def patch(self, id):
        # Find the scientist by ID
        scientist = Scientist.query.get(id)
        if not scientist:
            return {'error': 'Scientist not found'}, 404

        # Parse the request data
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('field_of_study', type=str)
        args = parser.parse_args()

        # Update the scientist data
        if args['name']:
            scientist.name = args['name']
        if args['field_of_study']:
            scientist.field_of_study = args['field_of_study']
        db.session.commit()

        # Return the updated scientist data
        return scientist.to_dict(), 202
    
    def delete(self, id):
        # Find the scientist by ID
        scientist = Scientist.query.get(id)
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        
        # Delete associated missions
        missions = Mission.query.filter_by(scientist_id=id).all()
        for mission in missions:
            db.session.delete(mission)

        # Delete the scientist
        db.session.delete(scientist)
        db.session.commit()

        # Return empty response
        return '', 204

# Add resources to the API
api.add_resource(ScientistListResource, '/scientists')
api.add_resource(ScientistResource, '/scientists/<int:id>')

# Planet list resource
class PlanetListResource(Resource):
    def get(self):
        planets = Planet.query.all()
        return [planet.to_dict() for planet in planets]

# Add resource to the API
api.add_resource(PlanetListResource, '/planets')

# Missions resource
class MissionsResource(Resource):
    def post(self):
        # Parse the request data
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be empty.')
        parser.add_argument('scientist_id', type=int, required=True, help='Scientist ID cannot be empty.')
        parser.add_argument('planet_id', type=int, required=True, help='Planet ID cannot be empty.')
        args = parser.parse_args()

        # Check if scientist and planet exist
        scientist = Scientist.query.get(args['scientist_id'])
        planet = Planet.query.get(args['planet_id'])
        if not scientist or not planet:
            return {'error': 'Invalid scientist or planet ID'}, 400

        # Create the new mission
        mission = Mission(name=args['name'], scientist_id=args['scientist_id'], planet_id=args['planet_id'])
        db.session.add(mission)
        db.session.commit()

        # Return the new mission data
        return mission.to_dict(), 201

# Add resource to the API
api.add_resource(MissionsResource, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
