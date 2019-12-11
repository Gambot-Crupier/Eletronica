import RPi.GPIO as GPIO
import time
import os
import threading
import requests
import json
import sys
import cv2
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from keras.preprocessing.image import img_to_array 
from keras.models import load_model
import numpy as np
import argparse
import imutils
from imutils import paths

frente = False
tras = True
desce = False
sobe = True

botao = 37
            ########## CONSTANTES ##########
### MOTORES DC ###

StepPinForward=13
StepPinBackward=15
sleeptime=1
dist = 35    # Distribuidor/Lançador

### MOTORES DE PASSO ###

elev_ena    = 11    # Elevador Pino Enable
elev_stp    = 19    # Elevador Pino Step
elev_dir    = 21    # Elevador Pino Direction

base_ms3    = 29   # Base/Rotacionador Pino Enable
base_ena    = 23   # Base/Rotacionador Pino Enable
base_stp    = 31   # Base/Rotacionador Pino Step
base_dir    = 32  # Base/Rotacionador Pino Direction

pos_ena     = 40    # Posicionador Pino Enable
pos_dir     = 36    # Posicionador Pino Direction
pos_stp     = 38    # Posicionador Pino Step

### SETUP DOS JOGADORES E PASSOS ###


NumerodePassos = 9520

            ########## VARIAVEIS ##########

flag        = 0     # Flag de Software (Servidor)
players     = 0     # Número de Jogadores
counter     = 0     # Contador de Jogadores
pic         = 0     # Envia Mensagem para Raspberry Fotografar a Carta



            ########## SETUP ########## 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # Referência numérica dos pinos #CONFLITANTE

### MOTORES DC ###
GPIO.setup(dist, GPIO.OUT)

### MOTORES DE PASSO ###
GPIO.setup(StepPinForward, GPIO.OUT)
pwmForward = GPIO.PWM(StepPinForward,2)
GPIO.setup(StepPinBackward, GPIO.OUT)
pwmBackward = GPIO.PWM(StepPinBackward,2)
GPIO.setup(elev_ena, GPIO.OUT)
GPIO.setup(elev_stp, GPIO.OUT)
GPIO.setup(elev_dir, GPIO.OUT)
GPIO.setup(base_ena, GPIO.OUT)
GPIO.setup(base_stp, GPIO.OUT)
GPIO.setup(base_dir, GPIO.OUT)
GPIO.setup(pos_ena, GPIO.OUT)
GPIO.setup(pos_stp, GPIO.OUT)
GPIO.setup(pos_dir, GPIO.OUT)
GPIO.setup(base_ms3, GPIO.OUT)


## SETUP DOS GPIOS 
GPIO.setup(botao, GPIO.IN, pull_up_down=GPIO.PUD_UP) #PUSHBUTTON RELHAR
GPIO.setup(10, GPIO.OUT) #LED DE INFORMAÇÃO
# 
# ##SETUP REDE NEURAL
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
modelNaipe = load_model('/home/pi/Desktop/fotoCarta/Naipe.model')
modelNumero = load_model('/home/pi/Desktop/fotoCarta/Numeros.model')

    ### INICIALIZAÇÃO ###

# REMOVER ALGUNS, ADICIONAR OUTROS
GPIO.output(dist, GPIO.LOW)
GPIO.output(elev_ena, GPIO.HIGH)
GPIO.output(elev_stp, GPIO.LOW)
GPIO.output(elev_dir, GPIO.LOW)
GPIO.output(base_ena, GPIO.HIGH)
GPIO.output(base_stp, GPIO.LOW)
GPIO.output(base_dir, GPIO.LOW)
GPIO.output(pos_ena, GPIO.HIGH)
GPIO.output(pos_stp, GPIO.LOW)
GPIO.output(pos_dir, GPIO.LOW)
GPIO.output(base_dir, GPIO.HIGH)

            ########## FUNÇÕES ##########

def Lancador():
    GPIO.output(dist, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(dist, GPIO.LOW)

def ligaLED():
    GPIO.output(22, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(24, GPIO.LOW)


        
def getContinueStart():
    r = requests.get('https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/get_continue') #Colocar o URL da galera de software aqui
    while r.status_code != 200:
        print('Não foi 200, foi ' + str(r.status_code))
        r = requests.get('https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/get_continue')
    json = r.json()
    x = json['continue']
    return(x)



def postContinueStop():
    
    payload = {"continue": 2}
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_continue", json = payload,headers = {'Accept': 'application/json', 'content-type' : 'application/json'}) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print


def postplayerid():
    
    payload = {"player_id": -1}
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_player_id", json = payload,headers = {'Accept': 'application/json', 'content-type' : 'application/json'}) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print

def enviarmesaFlop(matriz):
    
    payload = dict()
    payload = {'cards': [{ 'value' : str(matriz[0][1]), 'suit' : str(matriz[0][0])}, {'value' : str(matriz[1][1]), 'suit' : str(matriz[1][0])}, { 'value' : str(matriz[2][1]), 'suit' : str(matriz[2][0])}] }
    print(payload)
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_table_cards", json = payload,headers = {'Accept': 'application/json', 'content-type' : 'application/json'}) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print

    
def enviarmesaRT(matriz):
    
    payload = dict()
    payload = {'cards': [{ 'value' : str(matriz[0][1]), 'suit' : str(matriz[0][0])}] }
    print(payload)
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_table_cards", json = payload,headers = {'Accept': 'application/json', 'content-type' : 'application/json'}) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print
    
def enviarmao(matriz,Num):
    payload = []
    for x in range(Num):
        payload.append({'player_id': int(matriz[x][0]), 'cards': [{ 'value' : str(matriz[x][2]), 'suit' : str(matriz[x][1])}, {'value' : str(matriz[x][4]), 'suit' : str(matriz[x][3])}] })
    print(payload)
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_hands", json = payload,headers = {'Accept': 'application/json', 'content-type' : 'application/json'}) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print

def lerNumerodeJogadores():
    r = requests.get('https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/get_total_players_in_game') #Colocar o URL da galera de software aqui
    d = r.json()
    x = d['qtd_players']
    return(x)

def lerIdJogador():
    r = requests.get('https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/get_player_id') #Colocar o URL da galera de software aqui
    d = r.json()
    x = d['player_id']
    return(x)
        
    
def pulso(pino):
    GPIO.output(pino,GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(pino,GPIO.LOW)
    time.sleep(0.001)
    
def forward(x):
    GPIO.output(StepPinForward, GPIO.HIGH)
    time.sleep(x)
    GPIO.output(StepPinForward, GPIO.LOW)

def reverse(x):
    GPIO.output(StepPinBackward, GPIO.HIGH)
    time.sleep(x)
    GPIO.output(StepPinBackward, GPIO.LOW)

def Embaralhador(): # 1º ESTÁGIO DE EMBARALHAMENTO

    for i in range(8):
        for j in range(12):
            GPIO.output(StepPinForward, GPIO.LOW)
            GPIO.output(StepPinBackward, GPIO.LOW)
            
            time.sleep(0.02)
        
            GPIO.output(StepPinForward, GPIO.HIGH)
            GPIO.output(StepPinBackward, GPIO.LOW)
            
            time.sleep(0.04)
            
        time.sleep(0.005)
            
        for k in range(12):
            GPIO.output(StepPinForward, GPIO.LOW)
            GPIO.output(StepPinBackward, GPIO.LOW)
            
            time.sleep(0.02)
            
            GPIO.output(StepPinForward, GPIO.LOW)
            GPIO.output(StepPinBackward, GPIO.HIGH)
            
            time.sleep(0.04)
        
        time.sleep(0.1)
        
    GPIO.output(StepPinForward, GPIO.LOW)
    GPIO.output(StepPinBackward, GPIO.LOW)
    
def Elevador(direcao,NumerodePassosElevador): # CONTROLE DO ELEVADOR E REDISTRIBUIDOR

    GPIO.output(elev_ena, GPIO.LOW)  
    GPIO.output(elev_dir, direcao)
        
    for i in range(NumerodePassosElevador):        
        GPIO.output(elev_stp,GPIO.HIGH)
        time.sleep(0.002)
        GPIO.output(elev_stp,GPIO.LOW)
        time.sleep(0.0005)
        
    GPIO.output(elev_ena, GPIO.HIGH)
    
def Posicionador(direcao):  # POSICIONADOR DA CARTA SOBRE A CÂMERA
    
    GPIO.output(pos_ena, GPIO.LOW)
    GPIO.output(pos_dir, direcao)
    for i in range(2048):  #1340 #2048 #708      
        pulso(pos_stp);
    GPIO.output(pos_ena, GPIO.HIGH)

def Pescocinho():  # POSICIONADOR DA CARTA SOBRE A CÂMERA
    GPIO.output(base_ms3, GPIO.HIGH)
    GPIO.output(base_ena, GPIO.LOW)
    GPIO.output(base_dir, GPIO.LOW)
    for i in range(500):  #1340 #2048 #708      
        pulso(base_stp);
    GPIO.output(base_dir, GPIO.HIGH)
    for i in range(500):  #1340 #2048 #708      
        pulso(base_stp);
    GPIO.output(base_ena, GPIO.HIGH)
    
    
def Distribuidor():  # LANÇADOR DE CARTAS

    GPIO.output(dist, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(dist, GPIO.LOW)
    time.sleep(0.002)
        
def conectaNaRede():
    os.popen('bluetoothctl discoverable on')
    os.popen('bluetoothctl agent NoInputNoOutput')
    os.popen('bluetoothctl default-agent')
    os.popen("sudo rfcomm watch hci0 1 getty rfcomm0 115200 vt100 -a pi")
    
def checaconexao():
    x = os.system("ping -c 3 google.com")
    if x == 512:
        return True
    else:
        return False
    

def reconhecePessoas():
    GPIO.output(base_ena, GPIO.LOW)
    GPIO.output(base_ms3, GPIO.HIGH)
    cam = cv2.VideoCapture(1)
    ret, image = cam.read()
    p = 0
    GPIO.output(base_dir, GPIO.HIGH)
    if ret:
        for i in range(NumerodePassos):
            pulso(base_stp)
           # time.sleep(0.001)
            if p == 160:
                crop_img = image[0:2000, 200:500]
                cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,crop_img)                   
                ret, image = cam.read()
                p=0
            p=p+1
    cam.release()
    GPIO.output(base_ena, GPIO.LOW)
    
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

    print(salvaPosicao)
    return salvaPosicao

def identificaPessoascomApp(salvaPosicao):
    print("Dentro do app ja")
    GPIO.output(base_ena, GPIO.LOW)
    PosicaoDosJogadores = []
    PosicaoDosJogadores.append([])
    PosicaoDosJogadores.append([])
    print("ESTA IDENTIFICANDO AS PESSOAS")
    postplayerid()
    GPIO.output(base_dir,GPIO.LOW)
    for i in range(NumerodePassos):
        pulso(base_stp) 
    NumPassos = 0
    lejson = ""
    ## onde entra o código de conexão com  galera de soft
    GPIO.output(base_dir,GPIO.HIGH)
    for i in range(len(salvaPosicao)):
        for p in range((salvaPosicao[i])):
            pulso(base_stp)
            NumPassos = NumPassos + 1
        print("GIROU ATE O JOGADOR")
        lejson = lerIdJogador()
        while lejson == "-1":
            GPIO.output(10, GPIO.HIGH)
            print("fica parado")
            lejson = lerIdJogador()
        if lejson == "-5":
            postplayerid()
            print("faz nada")
            GPIO.output(10, GPIO.LOW)
        elif lejson == "-10":
            postplayerid()
            print("break")
            GPIO.output(10, GPIO.LOW)
            break
        else:
            PosicaoDosJogadores[0].append(lejson)
            PosicaoDosJogadores[1].append(NumPassos)
            print(lejson)
            print(PosicaoDosJogadores[0])
            print(PosicaoDosJogadores[1])
            NumPassos = 0
            postplayerid()  #ENVIA PARA SERVIDOR QUE FOI LIDO
            print("caiu aqui")

    
    somadospassos = 0    

    for i in range(len(salvaPosicao)):
        somadospassos = somadospassos + salvaPosicao[i]
        print(somadospassos)
    for i in range(NumerodePassos - somadospassos):        
        pulso(base_stp);
    print("1")       
    GPIO.output(base_dir,GPIO.LOW)
    while lejson != "-10": #ESPERA FINALIZAR O RECONHECIMENTO DA GALERA
        print("Esperando resposta do servidor")
        lejson = lerIdJogador()
    print("cabou")
    
    for i in range(NumerodePassos):
        pulso(base_stp) 
    print(PosicaoDosJogadores[0])
    print(PosicaoDosJogadores[1])
    GPIO.output(base_ena, GPIO.HIGH)
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
        nome.append("A")
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
        nome.append("J")
    if np.argmax(predicao) == 12:
        nome.append("Q")
    if np.argmax(predicao) == 13:
        nome.append("K")
    
    print(nome)
    return nome

def mostrquereconhece():
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
    caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
    imagem = cv2.imread(caminhoImagem)
    corte = imagem[80:324,346:534]
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte)
    reconheceCartas()
    
def entregaCartas(PosicaoDosJogadoresMatriz):
    GPIO.output(base_ena, GPIO.LOW)
    salvaPosicao = []
    PosicaoDosJogadores = []  
    salvaPosicao = PosicaoDosJogadoresMatriz[1]
    PosicaoDosJogadores = PosicaoDosJogadoresMatriz[0]
    
    print("Dentro do entrega cartas")
    print(salvaPosicao)
    print(PosicaoDosJogadores)
    GPIO.output(base_dir,GPIO.LOW)
    NumPassos = 0

    cam = cv2.VideoCapture(0)
    
    ret, image = cam.read()
    GPIO.output(base_dir,GPIO.HIGH)
    trocadeJogador = 0
    j = 0
    k = 1
    flaggiro = 0
    informacoesJogadores = []

    for x in range (len(PosicaoDosJogadores)): #Cria matriz para enviar dados
        informacoesJogadores.append(['','','','',''])

    for x in range (len(PosicaoDosJogadores)): #Cria matriz para enviar dados
        informacoesJogadores[x][0] = PosicaoDosJogadores[x]
    nome = ['','']
    
    for i in range(len(PosicaoDosJogadores)*2):
        if(flaggiro == 0):
            for p in range(salvaPosicao[j]): #GIRA MOTOR ATE A PESSOA
                print(salvaPosicao[j])
                pulso(base_stp)
            flaggiro = 1
        Posicionador(frente)
        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
        caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
        imagem = cv2.imread(caminhoImagem)
        corte = imagem[80:324,346:534]
        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte)
        ret, image = cam.read()
        Distribuidor()
        nome =  reconheceCartas()
        for m in range(2):
            informacoesJogadores[j][k+m] =  nome[m]
        print(j)
        trocadeJogador = trocadeJogador + 1
        k = k + 2
        if trocadeJogador == 2:
            flaggiro = 0
            trocadeJogador = 0
            j = j + 1
            k = 1
            
    enviarmao(informacoesJogadores,len(PosicaoDosJogadores))
    postContinueStop()
    print(informacoesJogadores)
   #RETORNA PARA POSICAO ORIGINAL 
    somadospassos = 0    
    for i in range(len(PosicaoDosJogadores)):
        somadospassos = somadospassos + salvaPosicao[i]
    GPIO.output(base_dir,GPIO.LOW)
    for i in range(somadospassos):        
        pulso(base_stp);
    
    lejson = ""
    lejson = getContinueStart()
    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
    if lejson == "3":
        print("entrou aqui")
        lejson = getContinueStart()
        postContinueStop()
    if lejson == "4":
        lejson = getContinueStart()
        postContinueStop()
        return()
        
    
    #ENTREGA 3 CARTAS NA MESA
    i = 0
    informacoesMesaFlop = []
    GPIO.output(base_dir,GPIO.HIGH)
    for i in range(3):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso(base_stp)
            Posicionador(frente)
            cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
            caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
            imagem = cv2.imread(caminhoImagem)
            corte = imagem[80:324,346:534]
            cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte) 
            ret, image = cam.read()
            Distribuidor()
        else:
            for p in range(500): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso(base_stp)
            Posicionador(frente)
            cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
            caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
            imagem = cv2.imread(caminhoImagem)
            corte = imagem[80:324,346:534]
            cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte)
            ret, image = cam.read()
            Distribuidor()
        informacoesMesaFlop.append(reconheceCartas())
        enviarmesaRT(informacoesMesaFlop) #RECONHECE A CARTA
        informacoesMesaFlop = []
    #ENTREGA 1 CARTAS NA MESA

    lejson = getContinueStart()
    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
        print(lejson)
    if lejson == "3":
        lejson = getContinueStart()
        postContinueStop()
        print(lejson)
    if lejson == "4":
        lejson = getContinueStart()
        postContinueStop()
        print(lejson)
        GPIO.output(base_dir,GPIO.LOW)
        for i in range(3):
            if i == 0:
                for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                    pulso(base_stp)
            else:
                for p in range(500): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                    pulso(base_stp)            
        return()
    informacoesMesaTurn = []
    for p in range(500):
        pulso(base_stp)

    Posicionador(frente)
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
    caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
    imagem = cv2.imread(caminhoImagem)
    corte = imagem[80:324,346:534]
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte)
    ret, image = cam.read()           
    informacoesMesaTurn.append(reconheceCartas()) #RECONHECE A CARTA
            
    Distribuidor()
    print(informacoesMesaTurn)
    enviarmesaRT(informacoesMesaTurn)

    #ENVIA DADOS PARA O SERVIDOR
    lejson = getContinueStart()
    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
        print(lejson)
    if lejson == "3":
        lejson = getContinueStart()
        postContinueStop()
        print(lejson)
    if lejson == "4":
        lejson = getContinueStart()
        postContinueStop()
        print(lejson)
        GPIO.output(base_dir,GPIO.LOW)
        for i in range(4):
            if i == 0:
                for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                    pulso(base_stp)
            else:
                for p in range(500): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                    pulso(base_stp)  
        return()
    print(lejson)
    #ENTREGA 1 CARTAS NA MESA
    
    informacoesMesaRiver = []
    
    for p in range(500):
        pulso(base_stp)

    Posicionador(frente)
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,image)  #TIRA FOTO
    caminhoImagem = '/home/pi/Desktop/fotoCarta/carta.jpg'
    imagem = cv2.imread(caminhoImagem)
    corte = imagem[80:324,346:534]
    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg', corte)
    ret, image = cam.read()
    informacoesMesaRiver.append(reconheceCartas()) #RECONHECE A CARTA
    Distribuidor()        
    print(informacoesMesaRiver)
    enviarmesaRT(informacoesMesaRiver)

    #ENVIA DADOS PARA O SERVIDOR

    GPIO.output(base_dir,GPIO.LOW)
    for p in range(5):
        if i == 0:
            for p in range((salvaPosicao[0])):
                pulso(base_stp)
        else:
            for p in range(500):
                pulso(base_stp)

def embaralha():
    Elevador(sobe,2000)
    print("EMBARALHA 1")
    Embaralhador()
    pushbutton = GPIO.input(botao)
    Elevador(sobe,1500)
    while pushbutton == 1:
        GPIO.output(10, GPIO.HIGH)
        time.sleep(0.2)
        pushbutton = GPIO.input(botao)
        print("travado")
    GPIO.output(10, GPIO.LOW)
    print("EMBARALHA 2")
    Elevador(desce,1500)
    Embaralhador()
    Elevador(sobe,1500)
    pushbutton = GPIO.input(botao)
    while pushbutton == 1:
        GPIO.output(10, GPIO.HIGH)
        time.sleep(0.2)
        pushbutton = GPIO.input(botao)
        print("travado")
    GPIO.output(10, GPIO.LOW)
    print("EMBARALHA 3")
    Elevador(desce,1500)
    Embaralhador()
    Elevador(desce,2500)


            ########## FUNÇÃO PRINCIPAL ##########       
#ConectaThread=threading.Thread(target=conectaNaRede)
#ConectaThread.daemon = True
#ConectaThread.start()  
    #CONEXÃO RASP COM WIFI
            
    #O QUE DEVE SER ENVIADO PELA GALERA DE SOFT POR BT
        #sudo wpa_passphrase Nome_da_rede Senha_da_rede > /home/pi/Desktop/wpa.conf
        #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/home/pi/Desktop/wpa.conf


# #######################     CODIGO RECONHECE GALERA ###############################
while checaconexao(): #TRAVA ATE SE CONECTAR A UMA REDE WIFI
    print(".")
getContinueStart()
NumerodeJogadores = lerNumerodeJogadores()
postContinueStop()
reconhecePessoas()
SalvaPosicao = salvaPosicaodasPessoas()
PosicaoDosJogadores = identificaPessoascomApp(SalvaPosicao)
# 
# #######################      CODIGO DA RODADA    ###################################
while(1):
    embaralha()
    entregaCartas(PosicaoDosJogadores)     
