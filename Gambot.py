import RPi.GPIO as GPIO
import time

            ########## CONSTANTES ##########

### MOTORES DC ###

emb_1       = 3     # Embaralhador 1
emb_2       = 18    # Embaralhador 2
emb_c1      = 22    # Embaralhador Central Sentido Horário
emb_c2      = 24    # Embaralhador Central Sentido Anti-Horário
dist        = 16    # Distribuidor/Lançador

### MOTORES DE PASSO ###

elev_ena    = 11    # Elevador Pino Enable
elev_stp    = 19    # Elevador Pino Step
elev_dir    = 21    # Elevador Pino Direction
base_ena    = 23    # Base/Rotacionador Pino Enable
base_ms3    = 29    # Base/Rotacionador Pino Step Mode 3
base_stp    = 31    # Base/Rotacionador Pino Step
base_dir    = 33    # Base/Rotacionador Pino Direction
pos_ena     = 36    # Posicionador Pino Enable
pos_dir     = 38    # Posicionador Pino Direction
pos_stp     = 40    # Posicionador Pino Step



            ########## VARIAVEIS ##########

flag        = 0     # Flag de Software (Servidor)
players     = 0     # Número de Jogadores
counter     = 0     # Contador de Jogadores
pic         = 0     # Envia Mensagem para Raspberry Fotografar a Carta



            ########## SETUP ##########

GPIO.setmode(GPIO.BOARD) # Referência numérica dos pinos

### MOTORES DC ###
GPIO.setup(3,  GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

### MOTORES DE PASSO ###
GPIO.setup(11, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

    ### INICIALIZAÇÃO ###

GPIO.output(3,  GPIO.LOW)
GPIO.output(18, GPIO.LOW)
GPIO.output(22, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(11, GPIO.LOW)
GPIO.output(19, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
GPIO.output(23, GPIO.LOW)
GPIO.output(29, GPIO.LOW)
GPIO.output(31, GPIO.LOW)
GPIO.output(33, GPIO.LOW)
GPIO.output(36, GPIO.LOW)
GPIO.output(38, GPIO.LOW)
GPIO.output(40, GPIO.LOW)



            ########## FUNÇÕES ##########

def Embaralhador(): # 1º ESTÁGIO DE EMBARALHAMENTO

    GPIO.output(emb_1, GPIO.HIGH)
    
    time.sleep(3)

    GPIO.output(emb_1, GPIO.LOW)
    GPIO.output(emb_2, GPIO.HIGH)
    
    time.sleep(3)
    
    GPIO.output(emb_2, GPIO.LOW)
    
def Elevador(): # CONTROLE DO ELEVADOR E REDISTRIBUIDOR

    ### CÓDIGO MOTOR DE PASSOS SUBINDO
  
    ###

    GPIO.output(emb_c1, GPIO.HIGH)
    
    time.sleep(5)
    
    GPIO.output(emb_c1, GPIO.LOW)
    GPIO.output(emb_c2, GPIO.HIGH)
    
    time.sleep(5)
    
    GPIO.output(emb_c2, GPIO.LOW)

    ###  CÓDIGO MOTOR DE PASSOS DESCENDO

    ###  

def Rotacionador():

    ### CÓDIGO THÁSSIO
    
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

def FRT(): # FLOP, RIVER, TURN
 
    ### ROTACIONADOR, POSICIONADOR E DISTRIBUIDOR ESPECÍFICOS
  
    ###



            ########## FUNÇÃO PRINCIPAL ##########
while(1):
    
    while(flag == 0): # ESPERAR AUTORIZAÇÃO DO SERVIDOR
    
        Embaralhador()
        Elevador()
    
        for counter in range(players)
    
            Rotacionador()
            Posicionador()
            Distribuidor()    
    
        FRT()
        flag = 0
