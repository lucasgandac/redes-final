import os
import threading
import time
from client import Client
from room import Room

class Application:
  def __init__(self, client_host, server_host):
    self.client_host = client_host
    self.server_host = server_host
  
  def run(self):
    while True:
      print("1 - Criar uma sala")
      print("2 - Listar salas")
      print("3 - Entrar em uma sala")
      print("0 - Sair do programa")

      resp = int(input("Selecione uma opção: "))

      if resp == 0:
        os._exit(0)

      if resp == 1:
        title = input("Escreva o nome da sua sala de bate papo: ")
        max_clients = input("Qual vai ser o limite máximo de participantes? ")
        self.create_room(title, max_clients)
      
      if resp == 2:
        print("========= Salas Disponíveis ==========")
        self.list_rooms()
        print("======================================")

      if resp == 3:
        print("========= Salas Disponíveis ==========")
        self.list_rooms()
        print("======================================")
        self.get_room_ip()

  def create_room(self, title, max_clients):
    # Cria sala com titulo, cliente, servidor, max_clientes
    room = Room(title, self.client_host, self.server_host, int(max_clients))

    # Roda a sala em uma outra thread
    thread = threading.Thread(target = room.run)
    thread.start()

    time.sleep(1)
    # Criando client com host para room
    host, port = self.client_host
    client = Client(host, port)

    # Conecta o client com a Room
    client.start_room()

  def list_rooms(self):
    # Criando client com host para server
    host, port = self.server_host
    client = Client(host, port)

    # Pede para o servidor listar as salas criadas
    client.send_to_server('/list_rooms')

  def get_room_ip(self):
    selected_room = int(input("Digite a sala que deseja entrar: "))
    # Criando client com host para server
    time.sleep(1)
    host, port = self.server_host
    client = Client(host, port)

    # Pede para o servidor pegar o ip de uma sala
    received_room = client.send_to_server(f"/get_room:{selected_room}")
    try: 
      room = received_room.split(':')
      self.join_room(room)
    except AttributeError:
      return

  def join_room(self, room):
    client = Client(room[0], int(room[1]))
    client.start_room()
