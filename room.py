import os
import socket 
import threading
import time
import select
from user import User

class Room():
  def __init__(self, name, host, server, max_clients):
    self.name = name
    self.host = host
    self.server = server
    self.max_clients = max_clients
    self.connected_clients = []

  def run(self):
    try:
      # Checar se já tem uma room com o ip criado
      self.connectToServer()
      self.conexao_TCP()
    except:
      print("Ocorreu um erro com a sala")
      os._exit(1)
  
  def connectToServer(self):
    try:
      # Conecta com o servidor principal
      self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.server_socket.connect(self.server)

      host_ip, host_port = self.host

      # Manda a room criada com o ip para o servidor principal
      message = f"/add_room:{self.name}:{host_ip}:{host_port}:{self.max_clients}"
      self.server_socket.send(message.encode('utf-8'))
    except:
      print("Falha de conexão com o servidor")
      os._exit(1)

  def conexao_TCP(self):   
    self.socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket_host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
      self.socket_host.bind(self.host)
    except:
      print("Bind falhou")
      os._exit(1)
    self.socket_host.listen(self.max_clients)
    
    sockets_host = self.socket_host
    inputs = [sockets_host]
    outputs = []

    while True:
      readable, writable, exceptional = select.select(inputs, outputs, inputs)
      for r in readable:
        client, client_address = self.socket_host.accept()
        thread_client = threading.Thread(target = self.controla_conexao_client, args = (client, ))
        thread_client.start()
  
  def controla_conexao_client(self, client):

      user = self.create_nickname(client)
      self.connected_clients.append(user)

      client.send((f"Bem vindo ao bate papo {self.name}!").encode('utf-8'))
      self.no_tag_message(f"{user.nickname} entrou na sala!", user)
      self.receber_mensagem(user)

  def create_nickname(self, client): 
    message = f"Para entrar no bate papo deve primeiro digitar seu apelido: "

    client.send(message.encode('utf-8'))
    nickname = client.recv(1024).decode('utf-8')

    # Checar nickname
    has_nickname = self.checar_nickname(nickname)

    while has_nickname:
      client.send(("Já possui um usuário com esse nome. Por favor outro nome: ").encode('utf-8'))
      nickname = client.recv(1024).decode('utf-8')    
      has_nickname = self.checar_nickname(nickname)

    user = User(nickname, client)

    return user
  
  def controla_conexao(self, client):
    message = f"Para entrar no bate papo deve primeiro digitar seu apelido: "

    client.send(message.encode('utf-8'))
    nickname = client.recv(1024).decode('utf-8')

    # Checar nickname
    has_nickname = self.checar_nickname(nickname)

    while has_nickname:
      client.send(("Já possui um usuário com esse nome. Por favor outro nome: ").encode('utf-8'))
      nickname = client.recv(1024).decode('utf-8')    
      has_nickname = self.checar_nickname(nickname)

    user = User(nickname, client)
    self.connected_clients.append(user)

    self.no_tag_message(f"{user.nickname} entrou na sala!", user)
    self.receber_mensagem(user)

  def no_tag_message(self, message, user):
    for client in self.connected_clients:
      if user.client != client.client:
        try:
          client.client.send(message.encode('utf-8'))
        except:
          continue

  def checar_nickname(self, nickname):
    for user in self.connected_clients:
      if (user.nickname == nickname):
        return True
    
    return False

  def encerra_conexao(self):
    for user in self.connected_clients:
      user.client.close()

    self.socket_host.close()

  def enviar_mensagem(self, message, sender):
    for user in self.connected_clients:
      if sender.client != user.client:
        try:
          user.client.send(f"<{sender.nickname}>: {message}".encode('utf-8'))
        except:
          continue

  def receber_mensagem(self, user):
    while True:
      try:
        msg = user.client.recv(2048).decode('utf-8')

        if msg == '/exit':
          self.no_tag_message(f"{user.nickname} saiu do bate papo!", user)
          user.client.close()
          self.connected_clients.remove(user)

          if(len(self.connected_clients) == 0):
            host_ip, host_port = self.host
            message = f"/close_room:{self.name}:{host_ip}:{host_port}"
            self.server_socket.send(message.encode('utf-8'))
            return

        self.enviar_mensagem(msg, user)
      except:
        break
