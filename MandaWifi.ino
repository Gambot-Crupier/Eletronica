#include "BluetoothSerial.h"
#include <WiFi.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

//Parte do bt
String NomeDaRede = "";
String SenhaDaRede = "";
char Letra;
int UsuarioSenha = 0;
int ContadorTimeOut = 0;
boolean Conectado = true;
boolean FinalizaBluetooth = true;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Gambot");
}

void loop() {

  ConectaNoWIFI();

  Serial.println('\n');
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());


  delay(1000);

}


void ConectaNoWIFI() {
  while (Conectado) {
    RecebeNomeESenhaDaRede();
    WiFi.begin((const char*)NomeDaRede.c_str(), (const char*)SenhaDaRede.c_str());
    Serial.print("Conectando em: ");
    Serial.print(NomeDaRede);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print('.');
      ContadorTimeOut++;
      if (ContadorTimeOut == 8) {
        Serial.print("Problema de conexao");
        NomeDaRede = "";
        SenhaDaRede = "";
        ContadorTimeOut = 0;
        break;
      }
    }
    if (WiFi.status() == WL_CONNECTED) {
      Conectado = false;
    }
  }
}


void RecebeNomeESenhaDaRede() {

  while (FinalizaBluetooth) {
    if (SerialBT.available()) {
      Letra = char(SerialBT.read());
      if (Letra != ',') {
        if (UsuarioSenha == 0) {
          NomeDaRede.concat(Letra);
        }
        if (UsuarioSenha == 1) {
          SenhaDaRede.concat(Letra);
        }
      }
      else {
        UsuarioSenha++;
        if (UsuarioSenha == 2) {
          FinalizaBluetooth = false;
        }
      }
    }
    delay(100);
  }
  UsuarioSenha = 0;
  FinalizaBluetooth = true;
}
