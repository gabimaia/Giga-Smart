import os
import time

arq_energy1 = open('/usr/local/src/coletas/tensao', 'r')
arq_energy2 = open('/usr/local/src/coletas/corrente', 'r')
arq_energy3 = open('/usr/local/src/coletas/potencia', 'r')

conteudo1 = arq_energy1.readlines()
conteudo2 = arq_energy2.readlines() 
conteudo3 = arq_energy3.readlines() 

try:
	while True:

		tensao = os.popen('timeout 2s mosquitto_sub -C 1 -t testeP8').read()
		corrente = os.popen('timeout 2s mosquitto_sub -C 1 -t testeSCT').read()
		potencia = os.popen('timeout 2s mosquitto_sub -C 1 -t testepower').read()

		if tensao == '' : tensao = (str(0.0) + '\n')
		if corrente  == '' : corrente = (str(0.0) + '\n')
		if potencia == '' : potencia = (str(0.0) + '\n')

		conteudo1.append(str(tensao))
		conteudo2.append(str(corrente))
		conteudo3.append(str(potencia))

		arq_energy1 = open('/usr/local/src/coletas/tensao', 'w')
		arq_energy2 = open('/usr/local/src/coletas/corrente', 'w')
		arq_energy3 = open('/usr/local/src/coletas/potencia', 'w')

		arq_energy1.writelines(conteudo1)
		arq_energy2.writelines(conteudo2)
		arq_energy3.writelines(conteudo3)

		time.sleep(5)

except KeyboardInterrupt:
    pass