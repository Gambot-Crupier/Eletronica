import RPi.GPIO as GPIO
import RPi.GPIO as GPIO2

import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

GPIO.setwarnings(False)

NumerodePassos = 800

def pulso():
    GPIO.output(15,True)
    time.sleep(0.001)
    GPIO.output(15,False)
    time.sleep(0.001)



for i in range(2):
    GPIO.output(18,True)
    for i in range(NumerodePassos):
        pulso()
    time.sleep(2)
    GPIO.output(18,False)
    for i in range(NumerodePassos):
        pulso()
        
time.sleep(2)  
  
GPIO.cleanup()
