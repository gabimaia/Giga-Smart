import RPi.GPIO as GPIO
import time
import datetime
import sys 
sys.path.insert(0, "/usr/local/src/DHT11_Python/")
import dht11

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# read data using pin 12
instance = dht11.DHT11(pin=12)

condicao=True
count = 0

arquivo1 = open('/usr/local/src/coletas/temp-zabbix', 'r')
arquivo2 = open('/usr/local/src/coletas/umid-zabbix', 'r')
conteudo1 = arquivo1.readlines()
conteudo2 = arquivo2.readlines() 

try:
        while(condicao):
                result = instance.read()
                if result.is_valid():
#                       print("Last valid input: " + str(datetime.datetime.now()))
                        conteudo1.append(str(result.temperature) + '\n')
                        conteudo2.append(str(result.humidity) + '\n')
                        count = 0
                elif count == 120:
                        conteudo1.append(str(0.0) + '\n')
                        conteudo2.append(str(0.0) + '\n')
                        count = 0
                else:
                        count += 1

                arquivo1 = open('/usr/local/src/coletas/temp-zabbix', 'w')
                arquivo2 = open('/usr/local/src/coletas/umid-zabbix', 'w')
                arquivo1.writelines(conteudo1)
                arquivo2.writelines(conteudo2)
                time.sleep(2)
                        
except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()

