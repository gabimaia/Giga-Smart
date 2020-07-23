import os
import time
import datetime
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO

THINGSBOARD_HOST = os.popen("sed -n '1p' /usr/local/src/client-mqtt-tb").read().strip('\n')
ACCESS_TOKEN = os.popen("sed -n '2p' /usr/local/src/client-mqtt-tb").read().strip('\n')

client = mqtt.Client()
# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)
# Set access token
client.username_pw_set(ACCESS_TOKEN)

client.loop_start()

GPIO.setwarnings(False)

sensor_data = {'data': '', 'temperature': 0, 'humidity': 0, 'Agua': 0, 'Chamas': 0, 'Fumaca': 0, 'Porta': 0, 'Tensao': 0, 'Corrente': 0, 'Potencia':0, 'rele_porta': 'Off', 'rele_2': 'Off','rele_ar': 'Off'} 
gpio_state = {22: False, 24: False, 26: False}

# Setando o modo que cada pino vai trabalhar
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

def on_message(client, userdata, msg):
#    print('Topic: ' + msg.topic  + 'Message: ' + str(msg.payload)) #Remover
    # Decode JSON request
    data = json.loads(msg.payload)

    if data['method'] == 'getgpio22':
        client.publish(msg.topic.replace('request', 'response'), json.dumps(gpio_state[22]))
    elif data['method'] == 'getgpio24':
        client.publish(msg.topic.replace('request', 'response'), json.dumps(gpio_state[24]))
    elif data['method'] == 'getgpio26':
        client.publish(msg.topic.replace('request', 'response'), json.dumps(gpio_state[26]))

    elif data['method'] == 'setgpio22':
        # Acionamento Ar condicionado
        set_gpio_status(22, data['params'], 'high')
        client.publish('v1/devices/me/attributes', get_gpio_status(),1)
        if data['params'] == True:
            sensor_data['rele_ar'] = 'On'
        elif data['params'] == False:
            sensor_data['rele_ar'] = 'Off'

    elif data['method'] == 'setgpio24':
        # Acionamento rele 1 - porta do rack
        set_gpio_status(24, data['params'], 'low')
        client.publish('v1/devices/me/attributes', get_gpio_status(), 1)
        if data['params'] == True:
            sensor_data['rele_porta'] = 'On'
        elif data['params'] == False:
            sensor_data['rele_porta'] = 'Off'

    elif data['method'] == 'setgpio26':
        # Acionamento rele 2 
        set_gpio_status(26, data['params'], 'low')
        client.publish('v1/devices/me/attributes', get_gpio_status(), 1)
        if data['params'] == True:
            sensor_data['rele_2'] = 'On'
        elif data['params'] == False:
            sensor_data['rele_2'] = 'Off'

def get_gpio_status():
    # Encode GPIOs state to json
    return json.dumps(gpio_state)

def set_gpio_status(pin, status, mode):

        if mode == 'high': # Acionamento do ar
            GPIO.output(pin, GPIO.HIGH if status==True else GPIO.LOW)
            gpio_state[pin] = status

        elif mode == 'low': #Acionamento do modulo rele
            GPIO.output(pin, GPIO.LOW if status==True else GPIO.HIGH)
            gpio_state[pin] = status

# Armazenando o log 
arq_log = open('/usr/local/src/log/gigapop-monitor.log', 'r')
conteudo_log = arq_log.readlines()

try:
    while True:

	# Coletando os dados dos sensores        
        data = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        last_value_temperature = os.popen('sudo tail -n 1 /usr/local/src/coletas/temperatura').read().strip('\n')
        last_value_humidity = os.popen('sudo tail -n 1 /usr/local/src/coletas/umidade').read().strip('\n')
        Agua = os.popen('sudo cat /sys/class/gpio/gpio26/value').read().strip('\n')
        Chamas = os.popen('sudo cat /sys/class/gpio/gpio16/value').read().strip('\n')
        Fumaca = os.popen('sudo cat /sys/class/gpio/gpio21/value').read().strip('\n')
        Porta = os.popen('sudo cat /sys/class/gpio/gpio20/value').read().strip('\n')
        Tensao = os.popen('tail -n 1 /usr/local/src/coletas/tensao').read().strip('\n')
        Corrente = os.popen('tail -n 1 /usr/local/src/coletas/corrente').read().strip('\n')
        Potencia = os.popen('tail -n 1 /usr/local/src/coletas/potencia').read().strip('\n')

        if Chamas == '0': Chamas = 'Ausente'
        else: Chamas = 'detectado'

        if Agua == '1': Agua = 'Ausente'
        else: Agua = 'detectado'

        if Fumaca == '1': Fumaca = 'Ausente'
        else: Fumaca = 'detectado'
 
        if Porta == '0': Porta = 'Fechada'
        else: Porta = 'Aberta'

        # Atribuindo os dados aos parametros que sao enviados para o Thingsboard
        sensor_data['temperature'] = last_value_temperature
        sensor_data['humidity'] = last_value_humidity
        sensor_data['Agua'] = Agua
        sensor_data['Chamas'] = Chamas
        sensor_data['Fumaca'] = Fumaca
        sensor_data['Porta'] = Porta
        sensor_data['Tensao'] = Tensao
        sensor_data['Corrente'] = Corrente
        sensor_data['Potencia'] = Potencia
        sensor_data['data'] = data

 #       print(sensor_data)        
        #publish status on attributes
        client.subscribe('v1/devices/me/rpc/request/+')
        client.publish('v1/devices/me/attributes', get_gpio_status(),1)
        #publish status on telemetry
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data),0)

        # Registed publish message callback
        client.on_message = on_message

        arq_log = open('/usr/local/src/log/gigapop-monitor.log', 'w')
        conteudo_log.append(str(sensor_data) + '\n')
        arq_log.writelines(conteudo_log)

        sensor_data['rele_porta'] = 'Off'
        sensor_data['rele_2'] = 'Off'
        #GPIO status atualize
        gpio_state[24]=False
        gpio_state[26]=False
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(26, GPIO.HIGH)

        time.sleep(10)

except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()