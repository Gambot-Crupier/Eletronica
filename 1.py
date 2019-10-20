import RPi.GPIO as GPIO
import os
import threading



import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)



NumerodePassos = 800


def conectaNaRede():
    os.popen("sudo rfcomm watch hci0 1 getty rfcomm0 115200 vt100 -a pi")
    
    #sudo wpa_passphrase NomeDaRede SenhaDaRede > /home/pi/Desktop/wpa.conf o que tem que ser mandado por BT
    #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/home/pi/Desktop/wpa.conf o que tem que ser mandado por BT
    
def checaconexao():
    x = os.system("ping -c 3 google.com")
    if x == 512:
        return True
    else:
        return False

def pulso():
    GPIO.output(15,True)
    time.sleep(0.001)
    GPIO.output(15,False)
    time.sleep(0.001)

def GiraMotor():
    for i in range(2):
        GPIO.output(18,True)
        for i in range(NumerodePassos):
            pulso()
        time.sleep(2)
        GPIO.output(18,False)
        for i in range(NumerodePassos):
            pulso()        
        time.sleep(2)



ConectaThread=threading.Thread(target=conectaNaRede)
ConectaThread.daemon = True
ConectaThread.start()


while checaconexao():
    print(".")
GiraMotor()


GPIO.cleanup()
