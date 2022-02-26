from aurorapy.client import AuroraError, AuroraTCPClient
import time
import paho.mqtt.client as mqtt
import json
from sun import IsSunUp

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("AuroraMQTT Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("ABBPowerOne", "7yPxtqtzHk8JP9ZDqJJNXgWa")
client.connect("192.168.1.10", 1883, 60)
client.loop_start()

c = AuroraTCPClient(ip='192.168.1.10', port=20108, address=2)

while True:

    try:
        if IsSunUp():
            c.connect()
            result = dict()

            product_number=c.pn()
            result["product_number"] = product_number

            serial_number=c.serial_number()
            result["serial_number"] = serial_number

            #OUTPUT POWER
            output_power = c.measure(3)
            result["output_power"] = output_power

            #ENERGY DAILY
            daily_energy = c.cumulated_energy(period=0) / 1000
            result["daily_energy"] = daily_energy

            #ENERGY WEEK
            energy_week = c.cumulated_energy(period=1) / 1000
            result["energy_week"] = energy_week

            #ENERGY MONTH
            energy_month = c.cumulated_energy(period=3) / 1000
            result["energy_month"] = energy_month

            #ENERGY YEAR
            year_energy = c.cumulated_energy(period=4) / 1000
            result["year_energy"] = year_energy

            #ENERGY TOTAL
            energy_total = c.cumulated_energy(period=5) / 1000
            result["energy_total"] = energy_total

            jsonRes = json.dumps(result)
            client.publish("/solar/1", jsonRes)

            c.close()

            time.sleep(2)
        
        else:
            print('Sun is down')
            time.sleep(300)

    except Exception as e:
        print(e)

    

