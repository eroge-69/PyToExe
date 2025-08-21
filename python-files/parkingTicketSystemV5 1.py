from flask import Flask,jsonify,request,redirect
from cryptography.fernet import Fernet
from flask_cors import CORS
from datetime import datetime
import random
import os
from gevent.pywsgi import WSGIServer
from datetime import date
import json
import string
import datetime as dt
import base64
from io import BytesIO
import re
import pandas as pd
from configparser import ConfigParser
import pyodbc as odbc
from tkinter import ttk,messagebox
import logging
from wsgilog import log

app=Flask(__name__)

def parkingConfig():
    config=ConfigParser()
    config.read("config.ini")
    return config

logging.basicConfig(filename="parkingTicketSystemLogs.log", format='%(asctime)s %(name)s %(levelname)s %(message)s ', filemode='a',level=logging.DEBUG) # Create the file logger
logger=logging.getLogger()
logger.propagate = True

key=b'i3vVJAiA2-e6JIBoTBwvmQNmTXvVhbr60p5jOYVRVws='

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def database():
    config=parkingConfig()
    print(config)
    db = odbc.connect(f"DRIVER={{{str(config['databaseConfiguration']['driverName'])}}};SERVER={str(config['databaseConfiguration']['serverName'])};DATABASE={str(config['databaseConfiguration']['databaseName'])};Trust_Connection=yes;User ID={str(config['databaseConfiguration']['username'])};Password={str(config['databaseConfiguration']['password'])}",autocommit=True)
    cursor=db.cursor()
    return db,cursor

def validateAuthToken(token):
    token=bytes(token, 'utf-8')
    f = Fernet(key)
    token = f.decrypt(token)
    token=token.decode("utf-8")
    db,cursor = database()
    query=f"select user from user_access_token where token='{token}' and status='active'"
    cursor.execute(query)
    result=cursor.fetchone()
    if result:return 'valid',result[0]
    else:return 'invalid',""

def checkDataFields(data,*argv):
    status=True
    invalidField=[]
    for field in argv:
        try:
            if data[field] and data[field]!="":pass
            else:
                invalidField.append({field:"invalid"})
                status=False
        except:
            invalidField.append({field:"invalid"})
            status=False
    return status,invalidField

def validateTicketNumber(db,cursor,ticketNumber):
    query=f"select top 1 id from parking_token where tokenNumber='{ticketNumber}'"
    cursor.execute(query)
    result=cursor.fetchone()
    if result:return False
    else:return True

def generateTicketNumber(db,cursor,config):
    ticketNumber=str(config["parkingTicketConfiguration"]["companyId"])+"S"+str(config["parkingTicketConfiguration"]["siteId"])+"Y"+str(int(str(datetime.now().year)[1:]))
    query="select top 1 id from parking_token order by id desc"
    cursor.execute(query)
    result=cursor.fetchone()
    if result:recentId=int(result[0])
    else:recentId=0
    recentId+=1
    ticketNumber=ticketNumber+str(str(recentId).zfill(6))
    status=validateTicketNumber(db,cursor,ticketNumber)
    if status:return ticketNumber
    else:generateTicketNumber(db,cursor,config)

def validateParam(params):
    invalidParam={}
    status=True
    for param in params:
        value=request.args.get(param)
        if value:pass
        else:
            invalidParam[param]="invalid"
            status=False
    return status,invalidParam

def getParkingMinutes(checkInDate,checkInTime,checkOutDate,checkOutTime):
    checkInDateTemp=checkInDate.split("-")
    checkInTimeTemp=checkInTime.split(":")
    checkOutDateTemp=checkOutDate.split("-")
    checkOutTimeTemp=checkOutTime.split(":")
    print(checkInDateTemp,checkInTimeTemp,checkOutDateTemp,checkOutTimeTemp)
    # datetime(year, month, day, hour, minute, second)
    a = dt.datetime(int(checkInDateTemp[0]), int(checkInDateTemp[1]), int(checkInDateTemp[2]), int(checkInTimeTemp[0]), int(checkInTimeTemp[1]), int(checkInTimeTemp[2]))
    b = dt.datetime(int(checkOutDateTemp[0]), int(checkOutDateTemp[1]), int(checkOutDateTemp[2]), int(checkOutTimeTemp[0]), int(checkOutTimeTemp[1]), int(checkOutTimeTemp[2]))
    # returns a timedelta object
    print(a)
    print(b)
    c = b-a
    print('Difference: ', c)
    minutes = c.total_seconds() / 60
    #print('Total difference in minutes: ', minutes)
    # returns the difference of the time of the day
    #minutes = c.seconds / 60
    print('Difference in minutes: ', minutes)
    return round(minutes),c

@app.route("/api/v1/parkingSystem/generateTicket/",methods=["GET"])
def generateTicket():  
    app.logger.info(f"{request.remote_addr}---------{request.url}")
    try:
        headers = request.headers                                                                                   
        bearer = headers.get('Authorization')
        if bearer:                                                                       
            token = bearer.split()[1]
            status,userId=validateAuthToken(token)
            if status=="valid":
                db,cursor = database()  
                config=parkingConfig()  
                laneId=request.args.get("laneId")
                siteId=request.args.get("siteId")
                carNo=request.args.get("carNo")
                status2,invalidParam=validateParam(["laneId","siteId","carNo"])
                if status2:
                    ticketNumber=generateTicketNumber(db,cursor,config)
                    query = f"""
                        INSERT INTO parking_token
                        (tokenNumber, site, status, hardware, lot, customer, vehicleType, siteIdRealPark, entryLaneId, carNo)
                        VALUES ('{ticketNumber}', {config['parkingTicketConfiguration']['siteId']}, 'active', 
                        {config['hardwareConfiguration']['hardwareId']}, 0, 0, 1, {siteId}, {laneId}, '{carNo}')
                    """
                    cursor.execute(query)
                    db.commit()
                    app.logger.info({"response":"success","ticketNumber":ticketNumber,"block":"Unspecified","lot":"Unspecified"})
                    return jsonify({"response":"success","ticketNumber":ticketNumber,"block":"Unspecified","lot":"Unspecified"}),200
                else:
                    app.logger.error({"message":"Invalid Arguments!","errors":invalidParam,"response":"failed"})
                    return jsonify({"message":"Invalid Arguments!","errors":invalidParam,"response":"failed"}),422
            else:
                app.logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
                return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403
        else:
            app.logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
            return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403 
    except:
        app.logger.error({"message":"Internal Server Error"})
        return jsonify({"message":"Internal Server Error"}),500

@app.route("/api/v1/parkingSystem/updateTicketStatus/",methods=["GET"])
def updateTicketStatus():
    app.logger.info(f"{request.remote_addr}---------{request.url}")
    if True:                                                                                                                                                                                          
        headers = request.headers                                                                                   
        bearer = headers.get('Authorization')     
        if bearer:                                                                  
            token = bearer.split()[1]
            status,userId=validateAuthToken(token)
            if status=="valid":
                db,cursor = database()  
                config=parkingConfig() 
                ticketNumber=request.args.get("ticketNumber")
                laneId=request.args.get("laneId")
                paymentMethod=request.args.get("paymentMethod")
                status2,invalidParam=validateParam(["ticketNumber","laneId","paymentMethod"])
                if status2:
                    query=f"select top 1 id from parking_token where tokenNumber='{str(ticketNumber)}' and status='active'"
                    cursor.execute(query)
                    result=cursor.fetchone()
                    if result:
                        query=f"update parking_token set status='expired',exitLaneId={str(laneId)},checkOutDateTime=GETDATE(),paymentMethod={str(paymentMethod)} where id={result[0]}"
                        cursor.execute(query)
                        db.commit()
                        app.logger.info({"response":"success","message":"Status Update Success!"})
                        return jsonify({"response":"success","message":"Status Update Success!"}),200
                    else:
                        app.logger.error({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"})
                        return jsonify({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"}),401
                else:
                    app.logger.error({"message":"Invalid Arguments!","errors":invalidParam,"response":"failed"})
                    return jsonify({"message":"Invalid Arguments!","errors":invalidParam,"response":"failed"}),422
            else:
                app.logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
                return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403
        else:
            app.logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
            return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403  
    #except:
    #    app.logger.error({"message":"Internal Server Error"})
    #    return jsonify({"message":"Internal Server Error"}),500

@app.route("/api/v1/parkingSystem/getParkingAmount/",methods=["GET"])
def getParkingAmount():
    app.logger.info(f"{request.remote_addr}---------{request.url}")
    try:                                                                                                                                                                                          
        headers = request.headers                                                                                   
        bearer = headers.get('Authorization')
        if bearer:                                                                       
            token = bearer.split()[1]
            status,userId=validateAuthToken(token)
            if status=="valid":
                db,cursor = database()  
                config=parkingConfig()  
                ticketNumber=request.args.get("ticketNumber")
                if ticketNumber:
                    query=f"select top 1 id,status,CAST(checkInDateTime AS DATE) AS checkInDate,CAST(checkInDateTime AS TIME) AS checkInTime,CAST(checkOutDateTime AS DATE) AS checkOutDate,CAST(checkOutDateTime AS TIME) AS checkOutTime from parking_token where tokenNumber='{str(ticketNumber)}'"
                    cursor.execute(query)
                    result=cursor.fetchone()
                    if result:
                        if result[1]=='active':
                            duration,c=getParkingMinutes(str(result[2]),str(result[3]),str(result[4]),str(result[5]))
                            if int(duration)<=10:
                                logger.error({"response":"success","message":"Amount Calculated Successfully!","amount":0})
                                return jsonify({"response":"success","message":"Amount Calculated Successfully!","amount":0}),200
                            else:
                                logger.error({"response":"success","message":"Amount Calculated Successfully!","amount":100})
                                return jsonify({"response":"success","message":"Amount Calculated Successfully!","amount":100}),200
                        elif result[1]=='expired':
                            logger.info({"response":"success","message":"Amount Calculated Successfully!","amount":0})
                            return jsonify({"response":"success","message":"Amount Calculated Successfully!","amount":0}),200
                        else:
                            logger.error({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"})
                            return jsonify({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"}),401
                    else:
                        logger.error({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"})
                        return jsonify({"message":"Invalid Ticket Number!","errors":{"ticketNumber":"invalid"},"response":"failed"}),401
                else:
                    logger.error({"message":"Invalid Arguments!","errors":{"ticketNumber":"invalid"},"response":"failed"})
                    return jsonify({"message":"Invalid Arguments!","errors":{"ticketNumber":"invalid"},"response":"failed"}),422
            else:
                logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
                return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403 
        else:
            logger.error({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"})
            return jsonify({"message":"Invalid Access Token","response":"failed","errors":"Token Expired"}),403 
    except:
        logger.error({"message":"Internal Server Error"})
        return jsonify({"message":"Internal Server Error"}),500

if __name__=="__main__":
    #app.run(port=7700,host='0.0.0.0',debug=True)
    secret_key="cdaParkingCustomerApp"
    app.secret_key = secret_key
    app.config['SESSION_TYPE'] = 'filesystem'
    http_server = WSGIServer(('0.0.0.0', 7000), app)
    app.logger.info(f"{str(datetime.now())}-------------------Ticket Server Started Successfully!")
    http_server.serve_forever()