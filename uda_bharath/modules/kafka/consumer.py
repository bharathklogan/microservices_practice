from __future__ import annotations
from kafka import KafkaConsumer
from dataclasses import dataclass
from datetime import datetime
from services_pb2 import PersonMessage, LocationMessage
import services_pb2
import services_pb2_grpc
import json
import ast
import grpc


def create_person(req):
    channel = grpc.insecure_channel('grpc-api:5003')
    stub = services_pb2_grpc.CallServiceStub(channel)
    person = PersonMessage(first_name=req["first_name"] , last_name=req["last_name"], company_name=req["company_name"])
    stub.create_person(person)


def create_location(req):
    channel = grpc.insecure_channel('grpc-api:5003')
    stub = services_pb2_grpc.CallServiceStub(channel)
    location = LocationMessage(person_id=req["person_id"], creation_time=req["creation_time"],latitude=req["latitude"],longitude=req["longitude"])
    stub.create_location(location)


consumer = KafkaConsumer('test',
     bootstrap_servers=['my-release-kafka.default.svc.cluster.local:9092'],
     value_deserializer=lambda m: json.dumps(m.decode('utf-8')))

for message in consumer:
    resp=eval(json.loads((message.value)))
    if "first_name" in resp:
        create_person(resp)
    elif "person_id" in resp:
        create_location(resp)
    else:
      print(resp)



