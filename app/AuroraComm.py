from dotenv import load_dotenv
import os
import time
import paho.mqtt.client as mqtt
import json
from sun import IsSunUp
from waiting import wait, TimeoutExpired
from GetFromPowerOne import PowerOne
from aurorapy.client import AuroraError, AuroraTCPClient
from HassAutodiscovery import Advertise


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):    
    print("AuroraMQTT Connected with result code "+str(rc))
    Advertise(client, PowerOne(0), os.getenv('MQTT_TOPIC'))
    client.publish(os.getenv('MQTT_TOPIC')+"/status",payload="online", qos=0, retain=True)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

load_dotenv()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(os.getenv('MQTT_USERNAME'), os.getenv('MQTT_PASSWORD'))
client.will_set(os.getenv('MQTT_TOPIC')+"/status", payload="offline", qos=0, retain=True)
client.connect(os.getenv('MQTT_BROKER_HOST'), int(os.getenv('MQTT_BROKER_PORT')), 60)
time.sleep(5)
client.loop_start()

sunup = 0

while True:

    if IsSunUp():
        if sunup < 1:
            print('Sun is up, starting polling every two seconds\n')
            client.loop_start()
            sunup = sunup + 1           

        jsonRes = json.dumps(PowerOne(1))
        client.publish(os.getenv('MQTT_TOPIC'), jsonRes)

        time.sleep(2)
    
    else:
        print('Sun is down, stopping polling until tomorrow\n')
        jsonRes = json.dumps(PowerOne(0))
        client.publish(os.getenv('MQTT_TOPIC'), jsonRes, retain=True)
        client.loop_stop()
        wait(lambda: IsSunUp(), sleep_seconds=300)
        sunup = 0

    


