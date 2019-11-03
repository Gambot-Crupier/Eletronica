import RPi.GPIO as GPIO
import os
import threading
import time

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

ConectaThread=threading.Thread(target=conectaNaRede)
ConectaThread.daemon = True
ConectaThread.start()


while checaconexao():
    print(".")
