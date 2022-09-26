import random
from app import Application

class Main:
  def start(self):
    port = random.randint(1000, 9999)

    server = ('127.0.0.1', 5000)
    client = ('127.0.0.1', port)

    app = Application(client, server)

    app.run()


main = Main()
main.start()