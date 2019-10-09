TaskHandle_t Task1;
TaskHandle_t Task2;

#include <Ultrasonic.h>
#define TRIGGER_PIN  27
#define ECHO_PIN     35
#define DIRECTION_PIN 32
#define STEP_PIN 33

Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

int salvaposicao[] = {0, 0, 0, 0, 0, 0, 0, 0};
int contador = 0;
int contaPassos = 1;
int numerodejogadores = 2;
int posicao = 0;
int somadospassos = 0;
int IdentificaPessoa = 1;
long microsec;
float DISTANCE;



void setup() {
  Serial.begin(115200);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);

  xTaskCreatePinnedToCore(
    Task1code,   /* Task function. */
    "Task1",     /* name of task. */
    100000,       /* Stack size of task */
    NULL,        /* parameter of the task */
    1,           /* priority of the task */
    &Task1,      /* Task handle to keep track of created task */
    0);          /* pin task to core 0 */
}

void Task1code( void * pvParameters ) {

  delay(4000);
  digitalWrite(DIRECTION_PIN, HIGH);

  for (int x = 0; x < 1600; x++) { // 200 passos é uma volta, tá 1600 pq o passo está em 1/8
    pulso();
    contaPassos = contaPassos + 1;
  }

  delay(1000);


  digitalWrite(DIRECTION_PIN, LOW);
  for (int x = 0; x < 1600; x++) {
    pulso();
  }

  delay(1000);

  digitalWrite(DIRECTION_PIN, HIGH);
  posicao = 0;
  for (int x = 0; x < numerodejogadores; x++) {
    for (int x = 0; x < salvaposicao[posicao]; x++) {
      pulso();
    }
    posicao++;
    somadospassos = salvaposicao[x] + somadospassos;
    delay(1000);
  }

  for (int x = numerodejogadores; x < 8; x++) {
    salvaposicao[x] = 0;
  }
  for (int x = 0; x < (1600 - somadospassos); x++) {
    pulso();
  }


}


void loop() {

  microsec = ultrasonic.timing();
  DISTANCE = ultrasonic.convert(microsec, Ultrasonic::CM);
  //  Serial.print("CM: ");
  //  Serial.println(DISTANCE);
  delay(20);

  if (DISTANCE != 0 && DISTANCE <= 10.0 && IdentificaPessoa == 1) {
    salvaposicao[contador] = contaPassos;
    contaPassos = 1;
    Serial.println("Identificou");
    Serial.println(salvaposicao[contador]);
    contador++;
    IdentificaPessoa = 0;
    
  }

  if (DISTANCE != 0 && DISTANCE >= 10.0 && IdentificaPessoa == 0) {
    IdentificaPessoa = 1;
    Serial.println("Saiu");
  }
}



void pulso() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(1000);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(1000);
}
