#define DIRECTION_PIN 32
#define STEP_PIN 33

int Passos = 1000;
int Direcao = 0;
void pulso() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(1000);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(1000);
}


void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
}

void loop() {
  digitalWrite(DIRECTION_PIN, Direcao);
  for (int x = 0; x < Passos; x++) {
      pulso();
  }
  delay(1000);
}
