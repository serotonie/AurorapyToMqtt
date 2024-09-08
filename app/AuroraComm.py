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

load_dotenv()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print("AuroraMQTT Connected with result code "+str(reason_code))
    client.publish(os.getenv('MQTT_TOPIC')+"/status",
                   payload="online", qos=0, retain=True)

if 'MQTT_USERNAME_FILE' in os.environ:
    MQTT_USERNAME = open(os.getenv('MQTT_USERNAME_FILE'), 'r').readline()
else:
    MQTT_USERNAME = os.getenv('MQTT_USERNAME')
    
if os.getenv('DEBUG', False) == "True":
    print(MQTT_USERNAME)

if 'MQTT_PASSWORD_FILE' in os.environ:
    MQTT_PASSWORD = open(os.getenv('MQTT_PASSWORD_FILE'), 'r').readline()
else:
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

if os.getenv('DEBUG', False) == "True":
    print(MQTT_PASSWORD)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.will_set(os.getenv('MQTT_TOPIC')+"/status",
                payload="offline", qos=0, retain=True)
client.connect(os.getenv('MQTT_BROKER_HOST'),
               int(os.getenv('MQTT_BROKER_PORT')), 30)
client.loop_start()

sunup = 0

while True:

    if IsSunUp():
        if sunup < 1:
            print('Sun is up, starting polling every two seconds\n')
            # client.loop_start()
            sunup = sunup + 1

            resPowerOne = PowerOne(1)
            if resPowerOne is not None:
                Advertise(client, resPowerOne, os.getenv('MQTT_TOPIC'))

                jsonRes = json.dumps(resPowerOne)
                client.publish(os.getenv('MQTT_TOPIC'), jsonRes)

        else:
            resPowerOne = PowerOne(1)

            if resPowerOne is not None:

                jsonRes = json.dumps(resPowerOne)
                client.publish(os.getenv('MQTT_TOPIC'), jsonRes)

        time.sleep(2)

    else:
        print('Sun is down, stopping polling until tomorrow\n')

        resPowerOne = PowerOne(0)

        if resPowerOne.get("serial_number") is not None:
            Advertise(client, resPowerOne, os.getenv('MQTT_TOPIC'))

            jsonRes = json.dumps(resPowerOne)
            client.publish(os.getenv('MQTT_TOPIC'), jsonRes, retain=True)

        # client.loop_stop()

        wait(lambda: IsSunUp(), sleep_seconds=300)

        sunup = 0
