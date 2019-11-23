import RPi.GPIO as GPIO
import os
import threading
import time
import cv2
import threading
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from keras.preprocessing.image import img_to_array 
from keras.models import load_model
import numpy as np
import argparse
import imutils
from imutils import paths


## SETUP DOS GPIOS
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

## SETUP DOS JOGADORES E PASSOS
NumerodeJogadores = 4
NumerodePassos = 9520

##SETUP REDE NEURAL
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
modelNaipe = load_model('/home/pi/Desktop/fotoCarta/Naipe.model')
modelNumero = load_model('/home/pi/Desktop/fotoCarta/Numeros.model')


## FUNÇÕES
def conectaNaRede():
    os.popen("sudo rfcomm watch hci0 1 getty rfcomm0 115200 vt100 -a pi")
    
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
    
def reconhecePessoas():
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    p = 0
    if ret:
        GPIO.output(18,True)
        for i in range(NumerodePassos):
            pulso()
            time.sleep(0.001)
            if p == 160:
                crop_img = image[0:2000, 200:500]
                cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,crop_img)                   
                ret, image = cam.read()
                p=0
            p=p+1
    cam.release()

def salvaPosicaodasPessoas():
    q =160
    a=0

    salvaPosicao = []
    conta = 1
    posicao = -800

    for i in range(59):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        img = cv2.imread('/home/pi/Desktop/aa/' + str(q) +'.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.25, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            a=h
            if a>0 and posicao > 320:
                salvaPosicao.append(posicao)
                conta = conta + 1
                cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,img)
                posicao = 0
        q = q+160
        posicao = posicao + 160

    return salvaPosicao


def identificaPessoascomApp(salvaPosicao):
    GPIO.output(18,False)
    for i in range(NumerodePassos):
        pulso() 
    time.sleep(1)

    ## onde entra o código de conexão com  galera de soft
    GPIO.output(18,True)
    for i in range(NumerodeJogadores):
        for p in range((salvaPosicao[i+1])):
            pulso()

        time.sleep(2) #NO LUGAR DESSE TIME.SLEEP, TEM QUE FICAR UM LOOPING QUE TRAVA TUDO ATÉ A PESSOA SE IDENTIFICAR
    

    somadospassos = 0    

    for i in range(NumerodeJogadores+1):
        somadospassos = somadospassos + salvaPosicao[i]
        
    for i in range(NumerodePassos - somadospassos):        
        pulso();
        
    time.sleep(1)    
    GPIO.output(18,False)
    for i in range(NumerodePassos):        
        pulso();
    time.sleep(1)


    return PosicaoDosJogadores

def reconheceCartas():
    nome = []
    image = cv2.imread('/home/pi/Desktop/fotoCarta/carta.jpg')
    orig = image.copy()
    image = cv2.resize(image, (56, 56))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    
    predicao = modelNaipe.predict(image)[0]
    #IDENTIFICA NAIPE    
    if np.argmax(predicao) == 1:
        nome.append("c")
    if np.argmax(predicao) == 2:
        nome.append("d")
    if np.argmax(predicao) == 3:
        nome.append("h")
    if np.argmax(predicao) == 4:
        nome.append("s")
    predicao = modelNumero.predict(image)[0]
    #IDENTIFICA NUMERO
    if np.argmax(predicao) == 1:
        nome.append("a")
    if np.argmax(predicao) == 2:
        nome.append("2")
    if np.argmax(predicao) == 3:
        nome.append("3")
    if np.argmax(predicao) == 4:
        nome.append("4")
    if np.argmax(predicao) == 5:
        nome.append("5")
    if np.argmax(predicao) == 6:
        nome.append("6")
    if np.argmax(predicao) == 7:
        nome.append("7")
    if np.argmax(predicao) == 8:
        nome.append("8")
    if np.argmax(predicao) == 9:
        nome.append("9")
    if np.argmax(predicao) == 10:
        nome.append("10")
    if np.argmax(predicao) == 11:
        nome.append("j")
    if np.argmax(predicao) == 12:
        nome.append("q")
    if np.argmax(predicao) == 13:
        nome.append("k")
    return nome

def entregaCartas(salvaPosicao,PosicaoDosJogadores):
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    NumerodePassosParaPosicionar = 200
    NumerodePassosParaLancar = 100
    GPIO.output(18,True)
    trocadeJogador = 0
    j = 0
    k = 1
    informacoesJogadores = []

    for x in range (NumerodeJogadores): #Cria matriz para enviar dados
        informacoesJogadores.append(['','','','',''])

    for x in range (NumerodeJogadores): #Cria matriz para enviar dados
        informacoesJogadores[x][0] = PosicaoDosJogadores[x]
    nome = ['','']
    for i in range(NumerodeJogadores*2):
        print(j)
        for p in range(0,salvaPosicao[j]): #GIRA MOTOR ATE A PESSOA
            pulso()
        for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO   
            pulso()
        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        ret, image = cam.read()
        nome =  reconheceCartas() #RECONHECE A CARTA
        for m in range(2):
            informacoesJogadores[j][k+m] =  nome[m]
        for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR 
            pulso()

        trocadeJogador = trocadeJogador + 1
        k = k + 2
        if trocadeJogador == 2:
            trocadeJogador = 0
            j = j + 1
            k = 1
            
    print(informacoesJogadores)
   #RETORNA PARA POSICAO ORIGINAL 
    somadospassos = 0    

    for i in range(NumerodeJogadores):
        somadospassos = somadospassos + salvaPosicao[i]
    GPIO.output(18,False)
    for i in range(somadospassos):        
        pulso();
    time.sleep(1)

    #ENTREGA 3 CARTAS NA MESA

    informacoesMesaRiver = []
    GPIO.output(18,True)
    for i in range(3):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso()
        else:
            for p in range(200): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso()

        for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
            pulso()

        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        ret, image = cam.read()           
        informacoesMesaRiver.append(reconheceCartas()) #RECONHECE A CARTA
            
        for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
            pulso()

    #ENVIA DADOS PARA O SERVIDOR
        #A MATRIZ informacoesJogadores está da seguinte forma [id_jogador, naipe1,valor1,naipe2,valor2]
        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1,naipe2,valor2,naipe3,valor3]
    print(informacoesMesaRiver)

    #ENTREGA 1 CARTAS NA MESA

    informacoesMesaTurn = []
    for p in range(200):
        pulso()

    for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
        pulso()

    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    ret, image = cam.read()           
    informacoesMesaTurn.append(reconheceCartas()) #RECONHECE A CARTA
        
    for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
        pulso()

    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    print(informacoesMesaTurn)

    #ENTREGA 1 CARTAS NA MESA

    informacoesMesaFlop = []
    for p in range(200):
        pulso()

    for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
        pulso()

    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    ret, image = cam.read()           
    informacoesMesaFlop.append(reconheceCartas()) #RECONHECE A CARTA
        
    for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
        pulso()
    print(informacoesMesaFlop)
    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    
    #RETORNA PARA POSICAO ORIGINAL
    GPIO.output(18,False)
    for p in range(5):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso()
        else:
            for p in range(200): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso()


def jogoContinua():
    #LE DADOS DO JSON
    if FlagJogoContinua == 1:
        return True
    else:
        return False

def embaralha():
    NumerodeEmbaralhadas = 0

    while NumerodeEmbaralhadas != 8:
        if GPIO.input(10) == GPIO.HIGH:
            NumerodeEmbaralhadas = NumerodeEmbaralhadas + 1

def checaconexao():
    x = os.system("ping -c 3 google.com")
    if x == 512:
        return True
    else:
        return False

## MAIN

#CONEXÃO RASP COM WIFI

#O QUE DEVE SER ENVIADO PELA GALERA DE SOFT POR BT
    #sudo wpa_passphrase Nome_da_rede Senha_da_rede > /home/pi/Desktop/wpa.conf
    #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/home/pi/Desktop/wpa.conf

ConectaThread=threading.Thread(target=conectaNaRede)
ConectaThread.daemon = True
ConectaThread.start()

while checaconexao(): #TRAVA ATE SE CONECTAR A UMA REDE WIFI
    print(".")

#RECONHECIMENTO DA GALERA NA MESA

reconhecePessoas()

salvaPosicao = salvaPosicaodasPessoas()

PosicaoDosJogadores = identificaPessoascomApp(salvaPosicao)

#ENTREGA CARTAS PARA OS JOGADORES

while jogoContinua(): #ENQUANTO O JOGO CONTINUAR
    
    embaralha(): #ESPERA EMBARALHAR
    entregaCartas(salvaPosicao,PosicaoDosJogadores) #ENTREGA AS CARTAS
