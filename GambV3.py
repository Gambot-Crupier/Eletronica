import RPi.GPIO as GPIO
import time
import os
import threading
import requests
import json
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
desce = True
sobe = False

            ########## CONSTANTES ##########
NumerodeJogadores = 2
### MOTORES DC ###

emb_1       = 26     # Embaralhador Sentido Horário
emb_2       = 24    # Embaralhador Sentido Anti-Horário
dist        = 3    # Distribuidor/Lançador

### MOTORES DE PASSO ###

elev_ena    = 11    # Elevador Pino Enable
elev_stp    = 19    # Elevador Pino Step
elev_dir    = 21    # Elevador Pino Direction

base_ms3    = 29   # Base/Rotacionador Pino Enable
base_ena    = 23   # Base/Rotacionador Pino Enable
base_stp    = 31   # Base/Rotacionador Pino Step
base_dir    = 33  # Base/Rotacionador Pino Direction

pos_ena     = 40    # Posicionador Pino Enable
pos_dir     = 36    # Posicionador Pino Direction
pos_stp     = 38    # Posicionador Pino Step

### SETUP DOS JOGADORES E PASSOS ###


NumerodePassos = 9520
#NumerodePassosElevador = 2800

            ########## VARIAVEIS ##########

flag        = 0     # Flag de Software (Servidor)
players     = 0     # Número de Jogadores
counter     = 0     # Contador de Jogadores
pic         = 0     # Envia Mensagem para Raspberry Fotografar a Carta



            ########## SETUP ########## 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # Referência numérica dos pinos #CONFLITANTE

### MOTORES DC ###
GPIO.setup(emb_1,  GPIO.OUT)
GPIO.setup(emb_2, GPIO.OUT)
GPIO.setup(dist, GPIO.OUT)

### MOTORES DE PASSO ###
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
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP) #PUSHBUTTON REEMBARALHAR
GPIO.setup(13, GPIO.OUT) #LED DE INFORMAÇÃO
# 
# ##SETUP REDE NEURAL
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
modelNaipe = load_model('/home/pi/Desktop/fotoCarta/Naipe.model')
modelNumero = load_model('/home/pi/Desktop/fotoCarta/Numeros.model')

    ### INICIALIZAÇÃO ###

# REMOVER ALGUNS, ADICIONAR OUTROS
GPIO.output(emb_1,  GPIO.LOW)
GPIO.output(emb_2, GPIO.LOW)
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

            ########## FUNÇÕES ##########

def Lancador():
    GPIO.output(dist, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(dist, GPIO.LOW)

def ligaLED():
    GPIO.output(13, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(13, GPIO.LOW)


        
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
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_table_cards", json = payload) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print

    
def enviarmesaRT(matriz):
    
    payload = dict()
    payload = {'cards': [{ 'value' : str(matriz[0][1]), 'suit' : str(matriz[0][0])}] }
    r = requests.post("https://6wiv4418b6.execute-api.sa-east-1.amazonaws.com/production/post_table_cards", json = payload) #Colocar o URL da galera de software aqui
    print(r.text) #pode apagar esse print
    
def enviarmao(matriz):
    payload = []
    for x in range(NumerodeJogadores):
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
    
def Embaralhador(): # 1º ESTÁGIO DE EMBARALHAMENTO
    for i in range(5):
        for i in range(150):
            GPIO.output(emb_1, True)
            GPIO.output(emb_2, False)
            time.sleep(0.002)
            GPIO.output(emb_1, False)
            GPIO.output(emb_2, False)
            time.sleep(0.004)
            
        time.sleep(0.1)
        
        for i in range(150):
            GPIO.output(emb_1, False)
            GPIO.output(emb_2, True)
            time.sleep(0.002)
            GPIO.output(emb_1, False)
            GPIO.output(emb_2, False)
            time.sleep(0.004)
        
    GPIO.output(emb_1, False)
    GPIO.output(emb_2, False)
    
    
def Elevador(direcao,NumerodePassosElevador): # CONTROLE DO ELEVADOR E REDISTRIBUIDOR

    GPIO.output(elev_ena, GPIO.LOW)  
    GPIO.output(elev_dir, direcao)
        
    for i in range(NumerodePassosElevador):        
        GPIO.output(elev_stp,GPIO.HIGH)
        time.sleep(0.0005)
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
    
    time.sleep(1)
    
    GPIO.output(dist, GPIO.LOW)

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
    cam = cv2.VideoCapture(1)
    ret, image = cam.read()
    p = 0
    GPIO.output(13, GPIO.HIGH)
    if ret:
        GPIO.output(base_dir,GPIO.HIGH)
        for i in range(NumerodePassos):
            pulso(base_stp)
            time.sleep(0.001)
            if p == 160:
                crop_img = image[0:2000, 200:500]
                cv2.imwrite('/home/pi/Desktop/aa/' + str(i) +'.jpg' ,crop_img)                   
                ret, image = cam.read()
                p=0
            p=p+1
    cam.release()
    GPIO.output(13, GPIO.LOw)
    
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
    PosicaoDosJogadores = []
    print("ESTA IDENTIFICANDO AS PESSOAS")
    GPIO.output(base_dir,GPIO.LOW)
    for i in range(10):
        pulso(base_stp) 
    lejson = ""
    ## onde entra o código de conexão com  galera de soft
    GPIO.output(base_dir,GPIO.HIGH)
    for i in range(len(salvaPosicao)):
        for p in range((salvaPosicao[i])):
            pulso(base_stp)
        print("GIROU ATE O PRIMEIRO JOGADOR")
        lejson = lerIdJogador()
        while lejson == "-1":
            GPIO.output(13, GPIO.HIGH)
            print("fica parado")
            lejson = lerIdJogador()
        if lejson == "-5":
            postplayerid()
            print("faz nada")
            GPIO.output(13, GPIO.LOW)
        elif lejson == "-10":
            postplayerid()
            print("break")
            GPIO.output(13, GPIO.LOW)
            break
        else:
            PosicaoDosJogadores.append(lejson)
            print(lejson)
            print(PosicaoDosJogadores)
            postplayerid()  #ENVIA PARA SERVIDOR QUE FOI LIDO
            print("caiu aqui")

    
    somadospassos = 0    

    for i in range(1):
        somadospassos = somadospassos + salvaPosicao[i]
        print(somadospassos)
    for i in range(400 - somadospassos):        
        pulso(base_stp);
    print("1")       
    GPIO.output(base_dir,GPIO.LOW)
    for i in range(1):        
        pulso(base_stp);
    print("2") 
    while lejson != "-10": #ESPERA FINALIZAR O RECONHECIMENTO DA GALERA
        print("Esperando resposta do servidor")
        lejson = lerIdJogador()
    print("cabou") 
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
    return nome

def entregaCartas(salvaPosicao,PosicaoDosJogadores):
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
            for p in range(0,salvaPosicao[j]): #GIRA MOTOR ATE A PESSOA
                pulso(base_stp)
            flaggiro = 1
        Posicionador(frente)
        #cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        #ret, image = cam.read()
        nome =  reconheceCartas()
        for m in range(2):
            informacoesJogadores[j][k+m] =  nome[m]
#        for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR 
#            pulso(pos_stp)
        trocadeJogador = trocadeJogador + 1
        k = k + 2
        if trocadeJogador == 2:
            flaggiro = 0
            trocadeJogador = 0
            j = j + 1
            k = 1
            
    enviarmao(informacoesJogadores)
    
    print(informacoesJogadores)
   #RETORNA PARA POSICAO ORIGINAL 
    somadospassos = 0    
    for i in range(len(PosicaoDosJogadores)):
        somadospassos = somadospassos + salvaPosicao[i]
    GPIO.output(base_dir,GPIO.LOW)
    for i in range(somadospassos):        
        pulso(base_stp);
    
    lejson = ""
    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
    if lejson == "3":
        print("entrou aqui")
        lejson = getContinueStart()
    if lejson == "4":
        lejson = getContinueStart()
        return()
        

    #ENTREGA 3 CARTAS NA MESA

    informacoesMesaFlop = []
    GPIO.output(base_dir,GPIO.HIGH)
    for i in range(3):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso(base_stp)
        else:
            for p in range(200): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso(base_stp)

        Posicionador(frente)

        #cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        #ret, image = cam.read()           
        informacoesMesaFlop.append(reconheceCartas()) #RECONHECE A CARTA

    print(informacoesMesaFlop)
    enviarmesaFlop(informacoesMesaFlop)
    #ENTREGA 1 CARTAS NA MESA

    informacoesMesaTurn = []
    for p in range(200):
        pulso(base_stp)

    Posicionador(frente)

    #cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    #ret, image = cam.read()           
    informacoesMesaTurn.append(reconheceCartas()) #RECONHECE A CARTA
        
#     for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
#         pulso(pos_stp)

    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    print(informacoesMesaTurn)
    enviarmesaRT(informacoesMesaTurn)
    #ENTREGA 1 CARTAS NA MESA


    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
    if lejson == "3":
        lejson = getContinueStart()
    if lejson == "4":
        lejson = getContinueStart()
        return()
    
    
    informacoesMesaRiver = []
    for p in range(200):
        pulso(base_stp)

    Posicionador(frente)

    #cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    #ret, image = cam.read()           
    informacoesMesaRiver.append(reconheceCartas()) #RECONHECE A CARTA
        
#     for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
#         pulso(pos_stp)
    print(informacoesMesaRiver)
    enviarmesaRT(informacoesMesaRiver)

    while lejson == "2":
        print("fica parado")
        lejson = getContinueStart()
    if lejson == "3":
        lejson = getContinueStart()
    if lejson == "4":
        lejson = getContinueStart()
        return()
    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    
    #RETORNA PARA POSICAO ORIGINAL
    GPIO.output(base_dir,GPIO.LOW)
    for p in range(5):
        if i == 0:
            for p in range((salvaPosicao[0])):
                pulso(base_stp)
        else:
            for p in range(200):
                pulso(base_stp)


def embaralha():
    print("EMBARALHA 1")
    Embaralhador()
    pushbutton = GPIO.input(12)
    Elevador(sobe,1500)
    while pushbutton == 1:
        GPIO.output(13, GPIO.HIGH)
        time.sleep(0.2)
        pushbutton = GPIO.input(12)
        print("travado")
    GPIO.output(13, GPIO.LOW)
    print("EMBARALHA 2")
    Elevador(desce,1500)
    Embaralhador()
    Elevador(sobe,1500)
    time.sleep(2)
    pushbutton = GPIO.input(12)
    while pushbutton == 1:
        GPIO.output(13, GPIO.HIGH)
        time.sleep(0.2)
        pushbutton = GPIO.input(12)
        print("travado")
    GPIO.output(13, GPIO.LOW)
    print("EMBARALHA 3")
    Elevador(desce,1500)
    Embaralhador()
    Elevador(desce,1800)
    
    
    
            ########## FUNÇÃO PRINCIPAL ##########
            
#ConectaThread=threading.Thread(target=conectaNaRede)
#ConectaThread.daemon = True
#ConectaThread.start()

#embaralha()    
    #CONEXÃO RASP COM WIFI

    #O QUE DEVE SER ENVIADO PELA GALERA DE SOFT POR BT
        #sudo wpa_passphrase Nome_da_rede Senha_da_rede > /home/pi/Desktop/wpa.conf
        #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/home/pi/Desktop/wpa.conf
    

#######################     CODIGO RECONHECE GALERA ###############################
while checaconexao(): #TRAVA ATE SE CONECTAR A UMA REDE WIFI
    print(".")
getContinueStart()
NumerodeJogadores = lerNumerodeJogadores()
print(NumerodeJogadores)
# reconhecePessoas()
#salvaPosicao = salvaPosicaodasPessoas()
SalvaPosicao = [1,2,3]
PosicaoDosJogadores = identificaPessoascomApp(SalvaPosicao)

#######################      CODIGO DA RODADA    ###################################
while(1):
    #Elevador(sobe,2500)
    #embaralha()
    entregaCartas(SalvaPosicao,PosicaoDosJogadores)


##FUNCAO QUE ESPERA FLAG DOS MALUCO DE SOFT INFORMANDO QUE A RODADA ACABOU

#Elevador(desce,2800)    
################################################################################
    
    
###ROTINA FUNCIONA SEPARADO###

# Elevador(sobe,1500)
# Pescocinho()
# embaralha()
# Elevador(sobe,2200) 
# Posicionador(frente)


