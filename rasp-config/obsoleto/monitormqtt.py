import os
import time
import datetime
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = os.popen("sed -n '1p' /usr/local/src/client-mqtt-tb").read().strip('\n')
ACCESS_TOKEN = os.popen("sed -n '2p' /usr/local/src/client-mqtt-tb").read().strip('\n')

sensor_data = {'data': '', 'temperature': 0, 'humidity': 0, 'Agua': 0, 'Chamas': 0, 'Fumaca': 0, 'Porta': 0, 'Tensao': 0, 'Corrente': 0, 'Potencia':0}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 10)

client.loop_start()

GPIO.setmode(GPIO.BCM)

arq_log = open('/usr/local/src/log/gigapop-monitor.log', 'r')
conteudo_log = arq_log.readlines()

try:
	while True:

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

		data = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Sending humidity and temperature data to ThingsBoard
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
		print(sensor_data)

		arq_log = open('/usr/local/src/log/gigapop-monitor.log', 'w')
		conteudo_log.append(str(sensor_data) + '\n')
		arq_log.writelines(conteudo_log)
	#publish data read
		client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
		time.sleep(5)

except KeyboardInterrupt:
    pass
    GPIO.cleanup()

client.loop_stop()
client.disconnect()

