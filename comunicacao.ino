#include "WiFi.h"
#include "ESPAsyncWebServer.h"
 
const char* ssid = "NJH";
const char* password =  "0811172901";
 
AsyncWebServer server(80);

int led = 2;


int i = i;

 
void setup(){
  Serial.begin(9600);
  pinMode (led, OUTPUT);
  digitalWrite(led, LOW);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
 
  Serial.println(WiFi.localIP());
  Serial.println(i);
 
  server.on("/on", HTTP_GET, [](AsyncWebServerRequest *request){
    AsyncResponseStream *response = request->beginResponseStream("text/html");
    response-> printf("Hello World");
    request->send(response);
    digitalWrite(led, HIGH);
  });
  server.on("/off", HTTP_GET, [](AsyncWebServerRequest *request){
    AsyncResponseStream *response = request->beginResponseStream("text/html");
    response-> printf("Bye World");
    request->send(response);
    digitalWrite(led, LOW);
  });

  server.on("/jogador", HTTP_GET, [](AsyncWebServerRequest *request)
  {
    AsyncResponseStream *response = request->beginResponseStream("text/html");
    response-> printf("Jogador: 45 e jogador numero %d", i);
    i++;
    request->send(response);
  });
 
  server.begin();
}
 
void loop(){}
