import grpc
import services_pb2
import services_pb2_grpc
from services_pb2 import PersonMessage, LocationMessage

# openinn a gRPC channel
channel = grpc.insecure_channel('localhost:5003')

# creating a gRPC stub 
stub = services_pb2_grpc.CallServiceStub(channel)

person = PersonMessage(first_name="bht" , last_name="kum", company_name="kub")
stub.create_person(person)
print("CALLLLLLLLLLLED gRPC services")
