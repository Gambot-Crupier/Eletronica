import requests
import json


def enviarmao(num_jogadores, id_jogador, naipe1, valor1, naipe2, valor2):

	payload = {'num_players' : num_jogadores}
	payload = [dict() for x in range(num_jogadores)]
	for x in range(num_jogadores): payload[x] = {'player_id': id_jogador[x], 'cartas': [{ 'value' : valor1[x], 'suit' : naipe1[x]}, {'value' : valor2[x], 'suit' : naipe2[x]}] }

	r = requests.post("http://httpbin.org/post", data=json.dumps(payload)) #Colocar o URL da galera de software aqui
	print r.text #pode apagar esse print


def enviarmesa(rodada, naipe1, valor1, naipe2, valor2, naipe3, valor3):

	payload = dict()

	if (rodada == 1):
		payload = {'player_id': 'mesa', 'cartas': [{ 'value' : valor1, 'suit' : naipe1}, {'value' : valor2, 'suit' : naipe2}, { 'value' : valor3, 'suit' : naipe3}] }


	if (rodada > 1):
		payload = {'player_id': 'mesa', 'cartas': [{ 'value' : valor1, 'suit' : naipe1}] }


	r = requests.post("http://httpbin.org/post", data=json.dumps(payload)) #Colocar o URL da galera de software aqui
	print r.text #pode apagar esse print



def ler():

	r = requests.get('http://echo.jsontest.com/id_jogador/-1') #Colocar o URL da galera de software aqui

	d = r.json()

	x = d['id_jogador']


	return(x)



#flag = ler()

#print(flag)

id_jogadores = ['1','2','3']
naipes1 = ['copas','espadas','paus']
naipes2 = ['paus','ouros','copas']
valores1 = ['Q','2','6']
valores2 = ['K','A','10']



enviarmao(3, id_jogadores, naipes1, valores1, naipes2, valores2)


enviarmesa(1, 'ouro', 'paus', 'copas', 'A', '2', '3')


enviarmesa(3, 'copas', 'espadas', 'ouro', 'A', '2', '3')


