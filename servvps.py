# server.py
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}

def accept_connections():
    while True:
        client, client_address = SERVER.accept()
        print(f"{client_address} подключился.")
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8")
    clients[client] = name
    broadcast(f"{name} присоединился к чату!")

    while True:
        try:
            msg = client.recv(BUFSIZ).decode("utf8")
            if msg != "{quit}":
                broadcast(f"{name}: {msg}")
            else:
                client.close()
                del clients[client]
                broadcast(f"{name} покинул чат.")
                break
        except:
            break

def broadcast(msg):
    for sock in clients:
        try:
            sock.send(bytes(msg, "utf8"))
        except:
            pass

HOST = ''  # Пустая строка означает все доступные интерфейсы
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)
SERVER.listen(5)

print("Сервер запущен и ожидает подключений...")
ACCEPT_THREAD = Thread(target=accept_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
SERVER.close()
