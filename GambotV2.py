import RPi.GPIO as GPIO
import time
import RPi.GPIO as GPIO
import os
import threading
import cv2
import threading
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from keras.preprocessing.image import img_to_array 
from keras.models import load_model
import argparse
import imutils
from imutils import paths

            ########## CONSTANTES ##########

### MOTORES DC ###

emb_1       = 22     # Embaralhador Sentido Horário
emb_2       = 24    # Embaralhador Sentido Anti-Horário
dist        = 3    # Distribuidor/Lançador

### MOTORES DE PASSO ###

elev_ena    = 11    # Elevador Pino Enable
elev_stp    = 19    # Elevador Pino Step
elev_dir    = 21    # Elevador Pino Direction
base_ena    = 36    # Base/Rotacionador Pino Enable
base_stp    = 40    # Base/Rotacionador Pino Step
base_dir    = 38    # Base/Rotacionador Pino Direction
pos_ena     = 23    # Posicionador Pino Enable
pos_dir     = 31    # Posicionador Pino Direction
pos_stp     = 33    # Posicionador Pino Step

### SETUP DOS JOGADORES E PASSOS ###

NumerodeJogadores = 4
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
GPIO.setup(emb_1,  GPIO.OUT)
GPIO.setup(emb_2, GPIO.OUT) #CONFLITANTE
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

## SETUP DOS GPIOS 
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

##SETUP REDE NEURAL
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
GPIO.output(elev_ena, GPIO.LOW)
GPIO.output(elev_stp, GPIO.LOW)
GPIO.output(elev_dir, GPIO.LOW)
GPIO.output(base_ena, GPIO.LOW)
GPIO.output(base_stp, GPIO.LOW)
GPIO.output(base_dir, GPIO.LOW)
GPIO.output(pos_ena, GPIO.LOW)
GPIO.output(pos_stp, GPIO.LOW)
GPIO.output(pos_dir, GPIO.LOW)

            ########## FUNÇÕES ##########

def Embaralhador(): # 1º ESTÁGIO DE EMBARALHAMENTO

    
    GPIO.output(emb_1, GPIO.LOW)
    GPIO.output(emb_2, GPIO.LOW)
    
    time.sleep(3)

    GPIO.output(emb_1, GPIO.HIGH)
    GPIO.output(emb_2, GPIO.LOW)
    
    time.sleep(3)
    
    GPIO.output(emb_1, GPIO.LOW)
    GPIO.output(emb_2, GPIO.LOW)
    
    time.sleep(3)
    
    GPIO.output(emb_1, GPIO.LOW)
    GPIO.output(emb_2, GPIO.HIGH)
    
def Elevador(): # CONTROLE DO ELEVADOR E REDISTRIBUIDOR

    ### CÓDIGO MOTOR DE PASSOS SUBINDO
  
    ###
    
    time.sleep(1) #PLACEHOLDER
    
    ###  CÓDIGO MOTOR DE PASSOS DESCENDO

    ###  

def Posicionador():  # POSICIONADOR DA CARTA SOBRE A CÂMERA
  
    ### CÓDIGO MOTOR DE PASSOS GIRANDO
  
    ###

    time.sleep(1)   # PAUSA PRA FOTO

    ### CÓDIGO MOTOR DE PASSOS GIRANDO
    
    ###

def Distribuidor():  # LANÇADOR DE CARTAS

    GPIO.output(dist, GPIO.HIGH)
    
    time.sleep(1)
    
    GPIO.output(dist, GPIO.LOW)

def conectaNaRede():
    os.popen("sudo rfcomm watch hci0 1 getty rfcomm0 115200 vt100 -a pi")
    
def checaconexao():
    x = os.system("ping -c 3 google.com")
    if x == 512:
        return True
    else:
        return False
    
def pulso(pino):
    GPIO.output(pino,True)
    time.sleep(0.001)
    GPIO.output(pino,False)
    time.sleep(0.001)

def reconhecePessoas():
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    p = 0
    if ret:
        GPIO.output(18,True)
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
        pulso(base_stp) 
    time.sleep(1)

    ## onde entra o código de conexão com  galera de soft
    GPIO.output(18,True)
    for i in range(NumerodeJogadores):
        for p in range((salvaPosicao[i+1])):
            pulso(base_stp)

        time.sleep(2) #NO LUGAR DESSE TIME.SLEEP, TEM QUE FICAR UM LOOPING QUE TRAVA TUDO ATÉ A PESSOA SE IDENTIFICAR
    
    somadospassos = 0    

    for i in range(NumerodeJogadores+1):
        somadospassos = somadospassos + salvaPosicao[i]
        
    for i in range(NumerodePassos - somadospassos):        
        pulso(base_stp);
        
    time.sleep(1)    
    GPIO.output(18,False)
    for i in range(NumerodePassos):        
        pulso(base_stp);
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
            pulso(base_stp)
        for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO   
            pulso(pos_stp)
        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        ret, image = cam.read()
        nome =  reconheceCartas() #RECONHECE A CARTA
        for m in range(2):
            informacoesJogadores[j][k+m] =  nome[m]
        for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR 
            pulso(pos_stp)
            Distribuidor() #LANÇA CARTA

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
        pulso(base_stp);
    time.sleep(1)

    #ENTREGA 3 CARTAS NA MESA

    informacoesMesaRiver = []
    GPIO.output(18,True)
    for i in range(3):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso(base_stp)
        else:
            for p in range(200): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso(base_stp)

        for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
            pulso(pos_stp)

        cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
        ret, image = cam.read()           
        informacoesMesaRiver.append(reconheceCartas()) #RECONHECE A CARTA
            
        for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
            pulso(pos_stp)
            Distribuidor() #LANÇA CARTA

    #ENVIA DADOS PARA O SERVIDOR
        #A MATRIZ informacoesJogadores está da seguinte forma [id_jogador, naipe1,valor1,naipe2,valor2]
        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1,naipe2,valor2,naipe3,valor3]
    print(informacoesMesaRiver)

    #ENTREGA 1 CARTAS NA MESA

    informacoesMesaTurn = []
    for p in range(200):
        pulso(base_stp)

    for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
        pulso(pos_stp)

    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    ret, image = cam.read()           
    informacoesMesaTurn.append(reconheceCartas()) #RECONHECE A CARTA
        
    for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
        pulso(pos_stp)
        Distribuidor() #LANÇA CARTA

    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    print(informacoesMesaTurn)

    #ENTREGA 1 CARTAS NA MESA

    informacoesMesaFlop = []
    for p in range(200):
        pulso(base_stp)

    for q in range(NumerodePassosParaPosicionar):  #POSICIONA CARTA PARA FOTO 
        pulso(pos_stp)

    cv2.imwrite('/home/pi/Desktop/fotoCarta/carta.jpg' ,crop_img)  #TIRA FOTO                 
    ret, image = cam.read()           
    informacoesMesaFlop.append(reconheceCartas()) #RECONHECE A CARTA
        
    for q in range(NumerodePassosParaLancar):  #POSICIONA CARTA  PARA LANÇADOR
        pulso(pos_stp)
        Distribuidor() #LANÇA CARTA
        
    print(informacoesMesaFlop)
    #ENVIA DADOS PARA O SERVIDOR

        #O VETOR informacoesMesa está da seguinte forma [naipe1,valor1]
    
    #RETORNA PARA POSICAO ORIGINAL
    GPIO.output(18,False)
    for p in range(5):
        if i == 0:
            for p in range((salvaPosicao[0])): #GIRA MOTOR ATE A PRIMEIRA PESSOA
                pulso(base_stp)
        else:
            for p in range(200): #GIRA MOTOR PARA DISPOR CARTAS NA MESA
                pulso(base_stp)


#def jogoContinua():
#    #LE DADOS DO JSON
#    if FlagJogoContinua == 1:
#        return True
#    else:
#        return False

def embaralha():
    NumerodeEmbaralhadas = 0

    while NumerodeEmbaralhadas != 8:
        if GPIO.input(10) == GPIO.HIGH:
            NumerodeEmbaralhadas = NumerodeEmbaralhadas + 1


            ########## FUNÇÃO PRINCIPAL ##########
            
ConectaThread=threading.Thread(target=conectaNaRede)
ConectaThread.daemon = True
ConectaThread.start()

while checaconexao(): #TRAVA ATE SE CONECTAR A UMA REDE WIFI
    print(".")
        
while(1):
    
    #CONEXÃO RASP COM WIFI

    #O QUE DEVE SER ENVIADO PELA GALERA DE SOFT POR BT
        #sudo wpa_passphrase Nome_da_rede Senha_da_rede > /home/pi/Desktop/wpa.conf
        #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/home/pi/Desktop/wpa.conf
    
#    ConectaThread=threading.Thread(target=conectaNaRede)
#    ConectaThread.daemon = True
#    ConectaThread.start()
#
#    while checaconexao(): #TRAVA ATE SE CONECTAR A UMA REDE WIFI
#        print(".")
    
    #while(flag == 0): # ESPERAR AUTORIZAÇÃO DO SERVIDOR
        
        
    reconhecePessoas()

    salvaPosicao = salvaPosicaodasPessoas()

    PosicaoDosJogadores = identificaPessoascomApp(salvaPosicao)

    Embaralhador()
    Elevador()
    entregaCartas()    
        
    #flag = 0
