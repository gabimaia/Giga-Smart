#include "EspMQTTClient.h"
#include "EmonLib.h"
int enableA = D0;
int enableB = D1;
int enableC = D2;

float tensao;
float aRef = 3.3;
float relacao = 76.2;

float lixotensao = 3.44;
float lixocorrente = 0.01;

#define AMOSTRAS 12

EnergyMonitor emon1;


EspMQTTClient client(
  "PoP-RN",
  "PoP-RN@t3cnic0",
  "172.20.32.1",  // MQTT Broker server ip
  1883,                   // MQTT broker port
  "aluno",              // MQTT username
  "alunopop",             // MQTT password
  "test",                 // Client name
  true,                   // Enable web updater
  true                    // Enable debug messages
);

void setup() {
   
  Serial.begin(115200);
  emon1.current(A0,29);
  pinMode(enableA, OUTPUT);
  pinMode(enableB, OUTPUT);
  pinMode(enableC, OUTPUT);

}

void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("teste", [](const String & payload) {
    Serial.println(payload);
  });
}

float lePorta(uint8_t portaAnalogica) {
  float total=0;  
  for (int i=0; i<AMOSTRAS; i++) {
    total += 1.0 * analogRead(portaAnalogica);
    delay(5);
  }
  return (((total / (float)AMOSTRAS)*aRef)/ 1024.0)*(relacao);
}  
void loop() {
  
  digitalWrite(enableA, HIGH);
  digitalWrite(enableB, LOW);
  digitalWrite(enableC, LOW);
  
  delay(500);
  
  tensao = lePorta(A0);
  tensao = tensao - lixotensao;
  if (tensao < 0)
  {tensao = 0;}
  String V = String(tensao);
  client.publish("testeP8", V);

  digitalWrite(enableC, HIGH);
  digitalWrite(enableA, LOW);
  delay(500);
  
  double Irms = emon1.calcIrms(1480);
  Irms = Irms - lixocorrente;
  if (Irms < 0)
  {Irms = 0;}
  String c = String(Irms);
  client.publish("testeSCT", c);
  
  
  float potencia = tensao * Irms;;
  String P = String(potencia);
  client.publish("testepower", P);

  
  client.loop();
  
  delay(500);
}
