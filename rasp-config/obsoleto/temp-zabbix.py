import RPi.GPIO as GPIO
import time
import datetime
import sys 
sys.path.insert(0, "/usr/local/src/DHT11_Python/")
import dht11


# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# read data using pin 25
instance = dht11.DHT11(pin=12)

result = instance.read()
temp = result.temperature
temp = float(temp)
print (temp)


