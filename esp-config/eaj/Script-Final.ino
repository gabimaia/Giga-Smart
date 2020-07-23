#include "EspMQTTClient.h"
#include "EmonLib.h"
int enableA = D0;
int enableB = D1;
int enableC = D2;

float tensao;
float aRef = 3.3;
float relacao = 76.2;

#define AMOSTRAS 12

EnergyMonitor emon1;


EspMQTTClient client(
  "PoP-RN",
  "PoP-RN@t3cnic0",
  "172.20.23.1",  // MQTT Broker server ip
  "aluno",   // Can be omitted if not needed
  "alunopop",   // Can be omitted if not needed
  "TestClient",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

void setup() {
   
  Serial.begin(115200);
  emon1.current(A0,29);
  pinMode(enableA, OUTPUT);
  pinMode(enableB, OUTPUT);
  pinMode(enableC, OUTPUT);
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("TestClient/lastwill", "I am going offline");  // You can activate the retain flag by setting the third parameter to true

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
  String V = String(tensao);
  client.publish("testeP8", V);

  digitalWrite(enableC, HIGH);
  digitalWrite(enableA, LOW);
  digitalWrite(enableB, LOW);
  delay(500);
  
  double Irms = emon1.calcIrms(1480);
  String c = String(Irms);
  client.publish("testeSCT", c);
  
  
  float potencia = tensao * Irms;;
  String P = String(potencia);
  client.publish("testepower", P);

  
  client.loop();
  
  delay(500);
}
