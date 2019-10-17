TaskHandle_t Task1;

#include "BluetoothSerial.h"
#include <WiFi.h>
#include <Ultrasonic.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define TRIGGER_PIN  27
#define ECHO_PIN     35
#define DIRECTION_PIN 32
#define STEP_PIN 33

BluetoothSerial SerialBT;
Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

//Motor e sensor distancia
int salvaposicao[] = {0, 0, 0, 0, 0, 0, 0, 0};
int posicaocartasnamesa[] = {0, 0, 0, 0, 0};
int contador = 0;
int contaPassos = 1;
int numerodejogadores = 3;
int posicao = 0;
int somadospassos = 0;
int IdentificaPessoa = 0;
long microsec;
float DISTANCE;
boolean identificando = true;
boolean ConfirmacaoJogador = true;
//Motor e sensor distancia

// BT e WIFI
String NomeDaRede = "";
String SenhaDaRede = "";
char Letra;
int UsuarioSenha = 0;
int ContadorTimeOut = 0;
boolean Conectado = true;
boolean FinalizaBluetooth = true;
// BT e WIFI

void setup() {
  Serial.begin(115200);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  SerialBT.begin("Gambot");

}


void loop() {

  // ConectaNoWIFI();

  SerialBT.print("Conectado");
  Serial.println('\n');
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());

  delay(1000);

  ChamaIdentificaPessoas();

  while (identificando) {
    LeituradoSensorDeDistancia();
  }

  delay(1000);

  DistribuiCartas();

  delay(10000);
}


void pulso() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(1000);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(1000);
}

void ConectaNoWIFI() {
  while (Conectado) {
    RecebeNomeESenhaDaRede();
    WiFi.begin((const char*)NomeDaRede.c_str(), (const char*)SenhaDaRede.c_str());
    Serial.print("Conectando em: ");
    Serial.print(NomeDaRede);
    Serial.print("//");
    Serial.print(SenhaDaRede);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print('.');
      ContadorTimeOut++;
      if (ContadorTimeOut == 4) {
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


void LeituradoSensorDeDistancia() {
  microsec = ultrasonic.timing();
  DISTANCE = ultrasonic.convert(microsec, Ultrasonic::CM);
  Serial.print("CM: ");
  Serial.println(DISTANCE);
  delay(20);

  if (DISTANCE != 0 && DISTANCE <= 8.0 && IdentificaPessoa == 0) {
    IdentificaPessoa = 1;
    salvaposicao[contador] = contaPassos;
    contaPassos = 1;
    Serial.println("Identificou");
    Serial.println(salvaposicao[contador]);
    contador++;
    Serial.println("Saiu");
  }

}

void ChamaIdentificaPessoas() {
  xTaskCreatePinnedToCore(
    IdentificaPessoas,   /* Task function. */
    "Task1",     /* name of task. */
    10000,       /* Stack size of task */
    NULL,        /* parameter of the task */
    1,           /* priority of the task */
    &Task1,      /* Task handle to keep track of created task */
    0);          /* pin task to core 0 */
}
void IdentificaPessoas( void * pvParameters ) {

  digitalWrite(DIRECTION_PIN, HIGH);

  for (int x = 0; x < 2300; x++) { // 200 passos é uma volta, tá 2300 pq o passo está em 1/8
    pulso();
    contaPassos = contaPassos + 1;
    if (IdentificaPessoa == 1) {
      while (ConfirmacaoJogador) {
        //LEITURA DO JSON
        delay(3000);
        ConfirmacaoJogador = false;
      }
      IdentificaPessoa = 0;
      ConfirmacaoJogador = true;
    }
  }

  delay(1000);


  digitalWrite(DIRECTION_PIN, LOW);
  for (int x = 0; x < 2300; x++) {
    pulso();
  }

  identificando = false;

  vTaskDelay(100 / portTICK_PERIOD_MS);
  vTaskSuspend(NULL);
}

void DistribuiCartas() {
  digitalWrite(DIRECTION_PIN, HIGH);
  posicao = 0;
  for (int x = 0; x < numerodejogadores; x++) {
    for (int x = 0; x < salvaposicao[posicao]; x++) {
      pulso();
    }
    posicao++;
    somadospassos = salvaposicao[x] + somadospassos;
    delay(1000);

    for (int x = 0; x < 2; x++) {
      //FUNCAO POSICIONA
      //FUNCAO TIRAFOTO
      //FUNCAO LANCAO
    }
  }

  for (int x = numerodejogadores; x < 8; x++) {
    salvaposicao[x] = 0;
  }
  for (int x = 0; x < (2300 - somadospassos); x++) {
    pulso();
  }
  
  posicaocartasnamesa[0] = salvaposicao[0];
  
  for (int x = 1; x < 5; x++) {
    posicaocartasnamesa[x] = 160;
  }
  posicao = 0;
  
  delay(1000);
  digitalWrite(DIRECTION_PIN, LOW);
  for (int x = 0; x < 2300; x++) {
    pulso();
  }
  
  digitalWrite(DIRECTION_PIN, HIGH);
  
  for (int x = 0; x < 5; x++) {
    for (int x = 0; x < posicaocartasnamesa[posicao]; x++) {
      pulso();
    }
    posicao++;
    delay(1000);

    for (int x = 0; x < 2; x++) {
      //FUNCAO POSICIONA
      //FUNCAO TIRAFOTO
      //FUNCAO LANCAO
    }
  }

  digitalWrite(DIRECTION_PIN, LOW);
  for (int x = 0; x < posicaocartasnamesa[0] + 640; x++) {
    pulso();
  }
  
  posicao = 0;

}
