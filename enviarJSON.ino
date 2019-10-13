#include "WiFi.h"
#include "ESPAsyncWebServer.h"
 
const char* ssid = "NJH";
const char* password =  "0811172901";


 
AsyncWebServer server(80);


const char* naipe = "copas";
const char* numero =  "7";

 
void setup(){
    Serial.begin(9600);
    delay(10);

    // We start by connecting to a WiFi network

    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());


  server.on("/info", HTTP_GET, [](AsyncWebServerRequest *request)
  {
    AsyncResponseStream *response = request->beginResponseStream("text/html");
    response-> printf("}\n");
    response-> printf("naipe: %s \n", naipe);
    response-> printf("numero: %s \n", numero);
    response-> printf("}\n");
    request->send(response);
  });
 
  server.begin();
}

void loop()
{  
}
