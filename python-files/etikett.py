import mysql.connector
import usb.core
import usb.util
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs

import time

mydb = mysql.connector.connect(
  host="localhost",
  user="teewelt",
  password="quasi",
  database="etiketten"
)

mycursor = mydb.cursor()

hostName = "localhost"
serverPort = 8080

# DARJEELING FTGFOP1 TYP "Tukdah"  ** 
# Benannt nach dem Lepcha Wort "Takdah" - Tal der Tiger. Die ersten Pflanzungen gehen auf das Jahr 1864 zurück und ist wunderbar eingebettet in Magnolien, Orchideen und Koniferen. Eine späte, fein abgestimmte first flush Pflückung.
# Das Blatt ist helles Braun, oliv-schimmernd, gleichmäßig, die Tasse gold-gelb, brillant und der Charakter frisch, aromatisch, blumig.  ** 
# Schwarztee First Flush  ** 
# 12 g auf 1 Liter, 100°C, 2 Minuten ziehen lassen.  ** 
# 5  ** 
# tee  ** 
# 1000  ** 
#   ** 
#   ** 
#   ** 
#   ** 
#   ** 
#   ** 
#   ** 
#   ** 
class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        # first, let's check the device
        if device.bDeviceClass == self._class:
            return True
        # ok, transverse all devices to find an
        # interface that matches our class
        for cfg in device:
            # find_descriptor: what's it?
            intf = usb.util.find_descriptor(
                                        cfg,
                                        bInterfaceClass=self._class
                                )
            if intf is not None:
                return True

        return False
    
class MyServer(BaseHTTPRequestHandler):

    
    def printArticle(self,myresult):
        
   
        print (len(myresult))
        bez=myresult[0]
        etext=myresult[1]
        ebez=myresult[2]
        zub=myresult[3]
        kat=myresult[4]
        output=myresult[5]
        aid=myresult[6]
        herkunft=myresult[7]
        brennwert=myresult[8]
        fett=myresult[9]
        fettsaure=myresult[10]
        kohlenhydrate=myresult[11]
        zucker=myresult[12]
        eiweiss=myresult[13]
        salz=myresult[14]
        
        for value in myresult:
           print ("#",value, " ** ")
        
    def do_GET(self):

        parsed_url = urlparse(self.path)
        print(parsed_url.query.encode('utf-8'))
        res=(parse_qs(parsed_url.query))
       


        if 'itemID' in res:
            id=(res['itemID'][0])
            print(id)
            query="Select distinct Bez,Etikettentext, EtikettenBez,Zubereitung, Kat,Output,Art_ID, Herkunft,Brennwert,Fett,Fettsaeuren,Kohlenhydrate,Zucker,Eiweiss,Salz from t_artikel2 where Art_ID='"+id+"'";
            mycursor.execute(query)
            myresult = mycursor.fetchone()
            try:
                
                len(myresult)>0
                self.printArticle(myresult)
            except:
                print ("Wrong id")
        self.send_response(200)
       

        self.send_header("Content-type", "text/html")
        self.end_headers()
        f = open("/home/alf/python/path/etikletten/form.html")
        page=f.read()
        self.wfile.write(bytes(page,"utf-8"))


if __name__ == "__main__":        
    
   

    printers = usb.core.find(find_all=1, custom_match=find_class(7))
    
    
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

                     


