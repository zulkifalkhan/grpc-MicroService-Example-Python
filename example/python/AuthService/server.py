# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
from email import message
from locale import currency
import logging
import hashlib
import grpc
import AuthService_pb2
import AuthService_pb2_grpc

from staff_pb2_grpc import StaffManagerStub
import staff_pb2

from RecordService_pb2_grpc import RecordServiceStub
import RecordService_pb2
from pymongo import MongoClient # to make connection with mongoDB

#Databases Schemas
class TestUser:
    def __init__(self,name,email,password,birthDate,gender):
        self.name=name
        self.email=email
        self.password=password
        self.gender=gender
        self.birthDate=birthDate
UserDB={}  #global datbase to store user data.

class TestEmploy:
    def __init__(self,EmpId,Name,BirthDate,Gender,Qualification,Fees,DeptID,Role,Password):
        self.EmpId=EmpId
        self.Name=Name
        self.BirthDate=BirthDate
        self.Gender=Gender
        self.Qualification=Qualification
        self.Fees=Fees
        self.DeptID=DeptID
        self.Role=Role
        self.Password=Password
EmpDB={}

class SecretClass:
    def __init__(self,token,role):
        self.token=token
        self.role=role
TokenDB={}  #to make token

# Schemas for DB end here

globalClient=None
def mongo():
    global globalClient #to use it as the global variable
    if(globalClient==None):
        cluster = ""
        client = MongoClient(cluster)
        # print(client.list_database_names())
        db = client.myFirstDatabase
        globalClient=client
        return globalClient
    else:
        return globalClient
# my global working space act as db

# ---------------------------------------------------------------Databases functions
def isUserPresent(email):
    client = mongo()
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Users"]
    dbResponse=mycol.find_one({"UserID":email})
    print(dbResponse)
    if(dbResponse==None):
        return False
    else:
        return True

def DBStoreUser(UserData):    
    client = mongo()
    print(client.list_database_names())
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Users"]
    if(isUserPresent(UserData.email)==True):
        return False
    currRecord = {"UserID":UserData.email,"Name":UserData.name,"BirthDate":UserData.birthDate,"Password":UserData.password,"Gender":UserData.gender}
    x = mycol.insert_one(currRecord)
    return True

def DBauthUser(email,password):
    client = mongo()
    print(client.list_database_names())
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Users"]
    dbResponse=mycol.find_one({"UserID":email})
    if(dbResponse==None):
        return False
    if(dbResponse["Password"]!=password):
        return False
    return True

def isEmpPresent(email):
    client = mongo()
    print(client.list_database_names())
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Emp"]
    dbResponse=mycol.find_one({"EmpID":email})
    print(dbResponse)
    if(dbResponse==None):
        return False
    else:
        return True

def DBstoreEmp(EmpData):
    client = mongo()
    print(client.list_database_names())
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Emp"]
    if(isEmpPresent(EmpData.EmpId)==True):
        return False
    currRecord = {"EmpID":EmpData.EmpId,"Name":EmpData.Name,"BirthDate":EmpData.BirthDate,"Password":EmpData.Password,"Gender":EmpData.Gender,"Qualification":EmpData.Qualification,"DeptID":EmpData.DeptID,"Role":EmpData.Role,"Fees":EmpData.Fees}
    x = mycol.insert_one(currRecord)
    return True

def DBauthEmp(email,password):
    client = mongo()
    print(client.list_database_names())
    mydb = client["myFirstDatabase"]        
    mycol = mydb["Emp"]
    dbResponse=mycol.find_one({"EmpID":email})
    if(dbResponse==None):
        return False,None
    if(dbResponse["Password"]!=password):
        return False,None
    return True,dbResponse["Role"]
    
# -----------------------------------------------------------------------Databases functions
class AuthServiceClass(AuthService_pb2_grpc.AuthServiceServicer):

    # -----------------------------------MC3
    def MakeAppointment3(self, request, context):
        with grpc.insecure_channel('localhost:50054') as channel: #for another grpc call
            stub = RecordServiceStub(channel)
            response = stub.makeAppointment(RecordService_pb2.MKAppRequest(UserId=request.UserId,EmpId=request.EmpId,Date=request.Date,Status="false"))
        return RecordService_pb2.MKAppResponse(message=response.message)

    def CompleteAppointment3(self, request, context):
        print(request.UserId)
        with grpc.insecure_channel('localhost:50054') as channel:
            stub=RecordServiceStub(channel)
            response=stub.CompleteAppointment(RecordService_pb2.CompleteApp(UserId=request.UserId,EmpId=request.EmpId,Date=request.Date))
        return RecordService_pb2.CompleteAppReply(message=response.message)
    
    def GetAllAppointment(self,request,context):
        array=[]
        with grpc.insecure_channel('localhost:50054') as channel: #for another grpc call
            stub = RecordServiceStub(channel)
            response = stub.CompleteAppointment(RecordService_pb2.getApp())
            print("\n\n-------------OK-------------\n\n")
            print("Wokring inside:",response)
            print("Main type is:",type(response))
            for x in response.message:  #to covert particular into array(main bug)
                print(x)
                array.append(x)
        return RecordService_pb2.getAppReply(message=array)

    def ListOfAllDept(self, request, context):
        array=[]
        with grpc.insecure_channel('localhost:50053') as channel: #for another grpc call
            stub = StaffManagerStub(channel)
            response = stub.ListDepart(staff_pb2.listDept())
            print("\n\n-------------OK-------------\n\n")
            print("Wokring inside:",response)
            print("Main type is:",type(response))
            for x in response.message:  #to covert particular into array(main bug)
                print(x)
                array.append(x)
        return staff_pb2.listDeptReply(message=array)
    
    def ListOfAllDoctor(self, request, context):
        array=[]
        with grpc.insecure_channel('localhost:50053') as channel: #for another grpc call
            stub = StaffManagerStub(channel)
            response = stub.ListDoctor(staff_pb2.listDoc(deptId=request.deptId))
            for x in response.message:
                array.append(x)
        return staff_pb2.listDocReply(message=array)
    
    def AddDepartment(self, request, context):
        with grpc.insecure_channel('localhost:50053') as channel: #for another grpc call
            stub = StaffManagerStub(channel)
            response = stub.AddDepart(staff_pb2.AddDept(name=request.name))
        return staff_pb2.AddDeptReply(message=response.message)

    def SayHelloAgain(self, request, context):
        return AuthService_pb2.HelloReply(message='Hello Again, %s!' % request.name) 

    def RegisterUser(self,request,context):
        retmsg="Not Successful"
        currUser=TestUser(request.Name,request.UserID,request.Password,request.BirthDate,request.Gender)
        dbResponse=DBStoreUser(currUser)
        if(dbResponse==True):
            retmsg="Successful"
        print("\n-----------Inside User Registeration----------\n")
        return AuthService_pb2.UserRegisterationResponse(response=retmsg)
    
    def AuthenticateUser(self, request, context):
        retMsg="Not Successful"
        generatedToken="Null"
        if(DBauthUser(request.UserID,request.Password)==True):
            retMsg="Successful"
            generatedToken=hashlib.sha256(request.UserID.encode("utf-8")).hexdigest()
            TokenDB[request.UserID]=SecretClass(generatedToken,"user")
        return AuthService_pb2.UserAuthenticationResponse(response=retMsg,secretKey=generatedToken)
    
    def RegisterEmploy(self,request,context):
        retMsg="Not Successful"
        currEmp=TestEmploy(request.EmpID,request.Name,request.BirthDate,request.Gender,request.Qualification,request.Fees,request.DeptID,request.role,request.Password)
        if(DBstoreEmp(currEmp)==True):
            retMsg="Successful"
        return AuthService_pb2.EmployRegisterationResponse(response=retMsg)
    
    def AuthenticateEmploy(self,request,context):
        retMsg="Not Successful"
        generatedToken="Null"
        flag,responseRole=DBauthEmp(request.EmpID,request.Password)
        if(flag==True):
            retMsg="Successful"
            generatedToken=hashlib.sha256(request.EmpID.encode("utf-8")).hexdigest()
            print("CurrentRole:",responseRole)
            TokenDB[request.EmpID]=SecretClass(generatedToken,responseRole)
        return AuthService_pb2.EmployAuthenticationResponse(response=retMsg,secretKey=generatedToken)
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    AuthService_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceClass(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
