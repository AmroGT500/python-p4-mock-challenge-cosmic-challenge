from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship: A Planet has many Scientists through Missions
    scientists = db.relationship('Scientist', secondary='missions', back_populates='planets')

    # Add relationship: A Planet has many Missions
    missions = db.relationship('Mission', back_populates='planet')

    # Add serialization rules
    serialize_rules = ('-missions.planet', '-scientists.missions',)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship: A Scientist has many Planets through Missions
    planets = db.relationship('Planet', secondary='missions', back_populates='scientists')
    
    # Add relationship: A Scientist has many Missions
    missions = db.relationship('Mission', back_populates='scientist')

    # Add serialization rules
    serialize_rules = ('-missions.scientist', '-planets.missions', '-missions.planet', '-planets.scientists',)

    # Add validation for name and field_of_study
    @validates('name')
    def validate_name(self, key, name):
        # custom validation logic
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        # custom validation logic
        if not field_of_study.strip():
            raise ValueError("Field of study cannot be empty.")
        return field_of_study

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id', ondelete='CASCADE'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id', ondelete='CASCADE'), nullable=False)
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    # Add serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions', '-planet.id', '-scientist.planets',)

    # Add validation for name, scientist_id, and planet_id
    @validates('name')
    def validate_name(self, key, name):
        # custom validation logic
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        return name

    @validates('scientist_id', 'planet_id')
    def validate_foreign_key(self, key, value):
        # custom validation logic
        if not value:
            raise ValueError(f"{key.replace('_id', '').title()} cannot be empty.")
        return value

# add any models you may need.