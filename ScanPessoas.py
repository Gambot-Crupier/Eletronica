import RPi.GPIO as GPIO
import os
import threading
import time
import cv2

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)


NumerodeJogadores = 2
NumerodePassos = 5400
seguraLooping = True
esperaCameraLigar = True

def pulso():
    GPIO.output(15,True)
    time.sleep(0.001)
    GPIO.output(15,False)
    time.sleep(0.001)
    
def GiraMotor():
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    p = 0
    if ret:
        GPIO.output(18,True)
        for i in range(NumerodePassos):
            pulso()
            if p == 160:
                crop_img = image[0:2000, 200:500]
                cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,crop_img)                   
                ret, image = cam.read()
                p=0
            p=p+1
    cam.release()
    
GiraMotor()

q =160
a=0

salvaPosicao = [0,0,0,0,0,0,0,0,0,0,0,0]
conta = 1
posicao = 0

for i in range(28):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    img = cv2.imread('/home/pi/Desktop/aa/' + str(q) +'.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        a=h
        if a>0 and posicao > 320:
            salvaPosicao[conta] = posicao
            conta = conta + 1
            cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,img)
            posicao = 0
    q = q+160
    posicao = posicao + 160

print(salvaPosicao)

GPIO.output(18,False)
for i in range(NumerodePassos):
    pulso() 
time.sleep(2)

GPIO.output(18,True)
for i in range(NumerodeJogadores):
    for p in range(salvaPosicao[i+1]):
        pulso()
    time.sleep(2)
        
somadospassos = 0

for i in range(3):
    somadospassos = somadospassos + salvaPosicao[i]
    
for i in range(NumerodePassos - somadospassos):        
    pulso();


print(salvaPosicao)
