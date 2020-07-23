import os
import time
import sys
#import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = os.popen("sed -n '1p' /usr/local/src/client-mqtt-tb").read().strip('\n')
ACCESS_TOKEN = os.popen("sed -n '2p' /usr/local/src/client-mqtt-tb").read().strip('\n')


# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=2

#sensor_data = {'corrente': 0, 'tensao': 0, 'potencia': 0}

sensor_data2 = {'corrente': 0, 'tensao': 0, 'potencia': 0}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 10)

client.loop_start()

try:
    while True:
        corrente = os.popen('sudo mosquitto_sub -C 1 -u aluno -P alunopop -t testeSCT').read()
        tensao = os.popen('sudo mosquitto_sub -C 1 -u aluno -P alunopop -t testeP8').read()
        potencia = os.popen('sudo mosquitto_sub -C 1 -u aluno -P alunopop -t testepower').read()
        
        sensor_data2['corrente'] = corrente
        sensor_data2['tensao'] = tensao
        sensor_data2['potencia'] = potencia

        # Sending humidity and temperature data to ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data2),0)
        time.sleep(10)

except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
