from datetime import datetime
import os
import json
import pandas as pd
import socketio
import configparser
import time
import logging
import requests
from logging.handlers import RotatingFileHandler
import pyodbc

log_file = "test.log"
max_size = 20 * 1024 * 1024
backup_count = 10000


#  Create a logger
logger = logging.getLogger("RotationalLogger")
logger.setLevel(logging.DEBUG)

#  Create a rotating file handler
handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# database Connection details
server = '26041\\SQLEXPRESS1'      # e.g., 'localhost\\SQLEXPRESS' or '192.168.1.100'
database = 'maindata'  # e.g., 'TestDB'
# Connection string
conn_str = f"""
    Driver={{ODBC Driver 17 for SQL Server}};
    Server={server};
    Database={database};
    Trusted_Connection=yes;
    """


try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        print("Database Connection successful!")

except Exception as e:
        print("Error:", e) 


def update_to_database(intrumentid, bid_size, bid_price, ask_size, ask_price):
     
        cursor = conn.cursor()
      #  query = "INSERT INTO [44668] ([intrumentid], [bid_qty], [bid_price], [ask_price], [ask_qty]) VALUES ('44668',22,1.05,1.1,25)"
        query = "INSERT INTO ["+ intrumentid +"] ([intrumentid], [bid_qty], [bid_price], [ask_price], [ask_qty]) VALUES ('" + intrumentid +"',"+ bid_size +"," + bid_price +","+ ask_price +","+ ask_size +")"
        cursor.execute(query)
        conn.commit()


##############################   Inputs   ############################################
API_KEY = "6d3d294e0e38a655729848"
API_SECRET = "Ufdt021#c2"
source = "WEBAPI"
url = "https://xts2.nirmalbang.com"
xtsMessageCode = [1501]

Instruments = [
   
            {"exchangeSegment": 2, "exchangeInstrumentID": 44668},
        {"exchangeSegment": 2, "exchangeInstrumentID": 44713},
        {"exchangeSegment": 2, "exchangeInstrumentID": 44730},
        {"exchangeSegment": 2, "exchangeInstrumentID": 44639},
        {"exchangeSegment": 2, "exchangeInstrumentID": 44661},
        {"exchangeSegment": 2, "exchangeInstrumentID": 44687}
]

broadcastMode = 'Full'
#####################################################################################


def login():
    loginurl = url + '/apimarketdata/auth/login'
    data = {
        "secretKey": API_SECRET,
        "appKey": API_KEY,
        "source": source
    }
    headers = {'Content': 'application/json'}
    response = requests.post(loginurl, json=data, headers=headers, verify=False)
    return response.json()

def subscribeInstruments(Instruments, xtsMessageCode):
    sub_url = url + '/apimarketdata/instruments/subscription'
    sub_data = {
        "instruments": Instruments,
        "xtsMessageCode": xtsMessageCode
    }
    sub_headers = {'Content': 'application/json', 'Authorization': set_marketDataToken}
    response = requests.post(sub_url, json=sub_data, headers=sub_headers, verify=False)
    return response.json()

class MDSocket_io(socketio.Client):
    def __init__(self, token, userID, reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=True,
                 **kwargs):
        super().__init__(logger=False, engineio_logger=False, ssl_verify=False)
        self.token = token
        self.userID = userID
        self.port = url
        self.broadcastMode = broadcastMode
        self.connection_url = f'{self.port}/?token={token}&userID={userID}&publishFormat=JSON&broadcastMode={self.broadcastMode}'
        # print("Connection URL-->", self.connection_url)
        self.on('connect', self.on_connect)
        self.on('joined', self.on_joined)
        self.on('message', self.on_message)
        self.on('1501-json-full', self.on_message1501_json_full)
        self.on('1501-json-partial', self.on_message1501_json_partial)
        self.on('1502-json-full', self.on_message1502_json_full)
        self.on('1502-json-partial', self.on_message1502_json_partial)
        self.on('1505-json-full', self.on_message1505_json_full)
        self.on('1505-json-partial', self.on_message1505_json_partial)
        self.on('1510-json-full', self.on_message1510_json_full)
        self.on('1510-json-partial', self.on_message1510_json_partial)
        self.on('1512-json-full', self.on_message1512_json_full)
        self.on('1512-json-partial', self.on_message1512_json_partial)
        self.on('disconnect', self.on_disconnect)
        self.on('error', self.on_error)

    def connect(self, headers={}, transports='websocket', namespaces=None, socketio_path='/apimarketdata/socket.io',
                verify=False):
        super().connect(self.connection_url, headers=headers, transports=transports, namespaces=namespaces, socketio_path=socketio_path)
        self.wait()

    def on_connect(self):
        print('Market Data Socket connected successfully!')
        logger.info('Market Data Socket connected successfully!')

    def on_message(self, data):
        # print('message ' + data)
        logger.info('message %s', data)
    
    def on_joined(self, data):
        print('ws joined' + data)
        logger.info('ws joined %s', data)

    def on_message1501_json_full(self, data):
        # logger.info("1501_data:- %s",data)
        
        y = json.loads(data)
        
        instrument_id = y['ExchangeInstrumentID']
        bid_size = y['Touchline']['BidInfo']['Size']
        ask_size = y['Touchline']['AskInfo']['Size']
        bid_price = y['Touchline']['BidInfo']['Price']
        ask_price = y['Touchline']['AskInfo']['Price']

        print('I received a 1501 full Touchline message!' + '------ Bid : ' +str(bid_size) +' | ' + str(bid_price) + ' : ' + str(ask_price) +' | ' +str(ask_size))  

        update_to_database(str(instrument_id), str(bid_size), str(bid_price), str(ask_size), str(ask_price) )

     #   print("1501_data", data)

    def on_message1502_json_full(self, data):
        # print('1502_json_full' + data)
        logger.info('1502_data:- %s', data)

    def on_message1505_json_full(self, data):
        # print(datetime.now(), '1505_json_full' + data)
        logger.info('1505_data:- %s', data)
    
    def on_message1510_json_full(self, data):
        # print(datetime.now(),'1510_json_full' + data)
        logger.info('1510_data:- %s', data)

    def on_message1512_json_full(self, data):
        # print(datetime.now(),'1512_json_full' + data)
        logger.info('1512_data:- %s', data)

    def on_message1501_json_partial(self, data):
        # print('1501_json_partial', data)
        logger.info('1501_json_partial:- %s', data)

    def on_message1502_json_partial(self, data):
        # print('1502_json_partial' + data)
        logger.info('1502_json_partial:- %s', data)

    def on_message1510_json_partial(self, data):
        # print('1510_json_partial' + data)
        logger.info('1510_json_partial:- %s', data)

    def on_message1505_json_partial(self, data):
        # print('1505_json_partial' + data)
        logger.info('1505_json_partial:- %s', data)

    def on_message1512_json_partial(self, data):
        # print('1512_json_partial' + data)
        logger.info('1512_json_partial:- %s', data)

    def on_disconnect(self):
        print('Market Data Socket disconnected!')
        logger.info('Market Data Socket disconnected!')

    def on_error(self, data):
        print('Market Data Error', data)
        logger.error('Market Data Error %s', data)


if __name__ == "__main__":

    
    login_response = login()
    # print("Login Response:", login_response)
    set_marketDataToken = login_response['result']['token']
    set_muserID = login_response['result']['userID']
    print("Market Data Token:", set_marketDataToken)
    for i in xtsMessageCode:
        print("Subscribing to Message Code:", i)
        sub_response = subscribeInstruments(Instruments, i)
        # print("Subscription Response:", sub_response)

    soc = MDSocket_io(set_marketDataToken, set_muserID)
    soc.connect()