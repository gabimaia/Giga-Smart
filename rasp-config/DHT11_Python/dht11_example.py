import RPi.GPIO as GPIO
import dht11
import time
import datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = dht11.DHT11(pin=12)

condicao=True
try:
	while(condicao):
		result = instance.read()
		if result.is_valid():
			condicao = False
#	        print("Last valid input: " + str(datetime.datetime.now()))
			print(result.temperature)
			print(result.humidity)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
