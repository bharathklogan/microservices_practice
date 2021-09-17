import grpc
import services_pb2
import services_pb2_grpc
import os
import json
import time
import ast

from geoalchemy2.shape import to_shape
from shapely.geometry.point import Point
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from geoalchemy2.types import Geometry as GeometryType
from marshmallow import Schema, fields
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from concurrent import futures
from sqlalchemy import create_engine
from marshmallow_sqlalchemy.convert import ModelConverter as BaseModelConverter
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, String

base = declarative_base()

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

class Person(base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)


class Location(base):
    __tablename__ = "location"

    id = Column(BigInteger, primary_key=True)
    person_id = Column(Integer, ForeignKey(Person.id), nullable=False)
    coordinate = Column(Geometry("POINT"), nullable=False)
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    _wkt_shape: str = None

    @property
    def wkt_shape(self) -> str:
        # Persist binary form into readable text
        if not self._wkt_shape:
            point: Point = to_shape(self.coordinate)
            # normalize WKT returned by to_wkt() from shapely and ST_AsText() from DB
            self._wkt_shape = point.to_wkt().replace("POINT ", "ST_POINT")
        return self._wkt_shape

    @wkt_shape.setter
    def wkt_shape(self, v: str) -> None:
        self._wkt_shape = v

    def set_wkt_with_coords(self, lat: str, long: str) -> str:
        self._wkt_shape = f"ST_POINT({lat} {long})"
        return self._wkt_shape

    @hybrid_property
    def longitude(self) -> str:
        coord_text = self.wkt_shape
        return coord_text[coord_text.find(" ") + 1 : coord_text.find(")")]

    @hybrid_property
    def latitude(self) -> str:
        coord_text = self.wkt_shape
        return coord_text[coord_text.find("(") + 1 : coord_text.find(" ")]
        
        
class PersonSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    company_name = fields.String()

    class Meta:
        model = Person

class LocationSchema(Schema):
    id = fields.Integer()
    person_id = fields.Integer()
    longitude = fields.String(attribute="longitude")
    latitude = fields.String(attribute="latitude")
    creation_time = fields.DateTime()

    class Meta:
        model = Location





class CallServicer(services_pb2_grpc.CallServiceServicer):

    def create_person(self, request, context):
    
        print("Insideeeeeeeeeeeeeeeeeeeeeee grpc person")
        person_new = Person()
        person_new.first_name = request.first_name
        person_new.last_name = request.last_name
        person_new.company_name = request.company_name
        
        print("Initializinggggggggggggggggg the db")
        db_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        db = create_engine(db_string)
        Session = sessionmaker(bind=db)
        session = Session()
        query = session.query(func.max(Person.id).label("max_id"))
        person_new.id = (query.one().max_id) + 1
        session.add(person_new)
        session.commit()
        print("Committeddddddde and added the newwwwwwwwwwwwwwwwwwwwwwww person to the db")
        response = services_pb2.Person()
        print("NEwwwwwwwwwwwwwwwwwwwwwwwww Person is", person_new)
        
        response.person = True
        
        return response

    def create_location(self, request, context):
  
        print("Insssssssssssssssssssssssssssss loccccccccccccccccccccccccccccccccccc")
        new_location = Location()
        new_location.person_id = request.person_id
        if request.creation_time:
            new_location.creation_time = request.creation_time
        else:
            new_location.creation_time = datetime.now()
        new_location.coordinate = ST_Point(request.latitude, request.longitude)

        print("Initializinggggggggggggggggg the db")
        db_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        db = create_engine(db_string)   
        Session = sessionmaker(bind=db)
        session = Session()

        session.add(new_location)
        session.commit()
        print("Committeddddddde and added the newwwwwwwwwwwwwwwwwwwwwwww loccccccccccccccccccccccccccc to the db")

        response = services_pb2.Location()
        response.location = True
        print("NEwwwwwwwwwwwwwwwwwwwwwwwww LOCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA is", new_location)

        return response


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

services_pb2_grpc.add_CallServiceServicer_to_server(
	CallServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 5003.')
server.add_insecure_port('[::]:5003')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
	while True:
		time.sleep(86400)
except KeyboardInterrupt:
	server.stop(0)