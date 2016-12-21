import json
import time
import threading
import paho.mqtt.client as mqtt
import ssl
import Adafruit_DHT
import os
import requests
from datetime import datetime

#thing, certs and mqtt connection
client_id = 'temperature-1'
aws_endpoint = 'abc123d4efghi.iot.us-west-2.amazonaws.com'     #add your AWS account specific custom end-point here
ca_filename = 'ca.pem.crt'
cert_filename = 'certificate.pem'
private_key_filename = 'private-key.pem'
mqtt_topic = 'topic/tempdata/temperature'


def onDisconnect(client, userdata, rc):
        print("Disconnected from AWS IoT")
def on_connect(client, userdata, flags, rc):
        print("Connected to AWS IoT with result code")

def getNow():
    localtime = time.localtime()
    return (time.strftime("%Y%m%d %H%M%S", localtime))


client = mqtt.Client(client_id=client_id)
client.tls_set(
    ca_filename,
    certfile=cert_filename,
    keyfile=private_key_filename,
    tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_connect = on_connect
client.on_disconnect = onDisconnect
client.connect(aws_endpoint, 8883, 70)

def getSensorread():
        cpuserial = "0000000000000000"
        try:
                f = open('/proc/cpuinfo', 'r')
                for line in f:
                        if line[0:6] == 'Serial':
                                cpuserial = line[10:26]
                f.close()
        except:
                cpuserial = "ERROR000000000"  
        print "serial no.%s" %cpuserial
        
        time.sleep(5)
        a = datetime.now().strftime('%Y-%m-%dT%H:%M:%S:%fZ')   #[:-3]
        print a
        humidity, temperature = Adafruit_DHT.read_retry(11,4)
        print ('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity) )
        return humidity, temperature, cpuserial, a
       
        

while True:
                now = getNow()
                humidity, temperature, cpuserial, a = getSensorread()
                payload = json.dumps(
                                   dict(
                                             Temperature=str(temperature), Humidity=str(humidity), RPISerialno=str(cpuserial) 
                                         )
                        )
                client.publish(mqtt_topic, payload)
                
                humidity, temperature, cpuserial, a = getSensorread()
                url = '<describe_your_endpoint_connection>'
                DATA = json.dumps (
                        dict (
                        DateTime=(a), Temperature=(temperature), Moisture=(humidity)
                        )
                )
                print DATA
                resp = requests.post(url, data=(DATA), headers={'content-type': 'application/json'})
                print (resp.status_code) 
        
client.loop_start()

                

time.sleep(5)
