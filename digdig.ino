#define DIRECTION_PIN 32
#define STEP_PIN 33

int Passos = 1000;

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
  for (int x = 0; x < Passos; x++) {
      pulso();
  }
}
