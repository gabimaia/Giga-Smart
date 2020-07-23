import os
import time
import sys
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO

THINGSBOARD_HOST = os.popen("sed -n '1p' /usr/local/src/client-mqtt-tb").read().strip('\n')
ACCESS_TOKEN = os.popen("sed -n '2p' /usr/local/src/client-mqtt-tb").read().strip('\n')

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=5

GPIO.setwarnings(False)

gpio_state = {22: False, 24: False, 26: False}
porta_state = {'Porta_1': 'Fechada','Porta_2': 'Fechado' }

def on_connect(client, userdata, msg, *extra_params):
    # Subscribing to receive RPC requests
    #client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
    client.subscribe('v1/devices/me/rpc/request/+')
    # Sending current GPIO status
    client.publish('v1/devices/me/attributes', get_gpio_status(), 1)

def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    # Decode JSON request
    data = json.loads(msg.payload)
    client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
    # Check request method
    
    if data['method'] == 'getValue':
        print(gpio_state[24])
        client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
         # Reply with GPIO status

    elif data['method'] == 'setValue':
        # Update GPIO status and reply
        set_gpio_status2(24, data['params'])
        client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
        client.publish('v1/devices/me/attributes', get_gpio_status(),1)
        #Update Door status and publish
        if data['params'] == True:
            porta_state['Porta_2'] = 'Aberto'
            client.publish('v1/devices/me/telemetry', json.dumps(porta_state),0)

    elif data['method'] == 'setValue1':
        # Update GPIO status and reply
        set_gpio_status2(26, data['params'])
        client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
        client.publish('v1/devices/me/attributes', get_gpio_status(), 1)
        #Update rele status and publish
        if data['params'] == True:
            porta_state['Porta_1'] = 'Aberta'
            client.publish('v1/devices/me/telemetry', json.dumps(porta_state),0)

    elif data['method'] == 'setValue2':
        set_gpio_status(22, data['params'])
        client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
        client.publish('v1/devices/me/attributes', get_gpio_status(), 1)

def get_gpio_status():
    # Encode GPIOs state to json
    return json.dumps(gpio_state)

def set_gpio_status(pin, status):
    # Output GPIOs state
    GPIO.output(pin, GPIO.HIGH if status==True else GPIO.LOW)
    # Update GPIOs state
    gpio_state[pin] = status

def set_gpio_status2(pin, status):
    GPIO.output(pin, GPIO.LOW if status==True else GPIO.HIGH)
    gpio_state[pin] = status

# Using board GPIO layout
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)


next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()

try:
    while True:
        #GPIO status atualize
        gpio_state[26]=False
        gpio_state[24]=False
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        #atualize door status
        porta_state['Porta_1'] = 'Fechada'
        porta_state['Porta_2'] = 'Fechado'
        #publish status on attributes
        client.subscribe('v1/devices/me/rpc/request/+')
        client.publish('v1/devices/me/attributes', get_gpio_status(),1)
        client.publish('v1/devices/me/attributes', get_gpio_status(),1)
        #publish door status on telemetry
        client.publish('v1/devices/me/telemetry', json.dumps(porta_state),0)

        # Register connect callback
        client.on_connect = on_connect
        # Registed publish message callback
        client.on_message = on_message

        time.sleep(10)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
