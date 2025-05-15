#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
from datetime import datetime

class ChatServer:
    def __init__(self, host='', port=25565, buffer_size=1024):
        self.clients = {}  # {client_socket: name}
        self.lock = Lock()
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.running = False

    def start(self):
        try:
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5)
            self.running = True
            print(f"[{self._current_time()}] Сервер запущен на порту {self.port}")

            accept_thread = Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            self._admin_console()  # Блокирующий вызов
            
        except Exception as e:
            print(f"[{self._current_time()}] Ошибка: {e}")
        finally:
            self.stop()

    def _accept_connections(self):
        while self.running:
            try:
                client, address = self.server_socket.accept()
                Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except:
                if self.running:
                    print(f"[{self._current_time()}] Ошибка подключения")

    def _handle_client(self, client):
        try:
            # Получаем имя клиента
            name = client.recv(self.buffer_size).decode('utf8').strip()
            if not name:
                raise ValueError("Пустое имя")
                
            with self.lock:
                self.clients[client] = name
                
            welcome = f"Добро пожаловать, {name}! (Ваши сообщения тоже видны вам)"
            client.send(bytes(welcome, 'utf8'))
            
            # Уведомляем всех о новом участнике (включая самого клиента)
            self._broadcast(f"{name} присоединился к чату!")
            
            while self.running:
                msg = client.recv(self.buffer_size).decode('utf8').strip()
                if not msg or msg == "{quit}":
                    break
                    
                # Отправляем сообщение ВСЕМ (включая отправителя)
                self._broadcast(f"{name}: {msg}")
                
        except Exception as e:
            print(f"[{self._current_time()}] Ошибка клиента: {e}")
        finally:
            with self.lock:
                if client in self.clients:
                    name = self.clients.pop(client)
                    self._broadcast(f"{name} покинул чат!")
                client.close()

    def _broadcast(self, msg):
        with self.lock:
            for client in list(self.clients.keys()):
                try:
                    client.send(bytes(msg, 'utf8'))
                except:
                    pass

    def _admin_console(self):
        while self.running:
            cmd = input("Сервер> ").lower()
            if cmd in ('stop', 'exit', 'quit'):
                self.stop()
                break
            elif cmd == 'list':
                with self.lock:
                    print(f"Участники ({len(self.clients)}):")
                    for name in self.clients.values():
                        print(f"- {name}")

    def stop(self):
        self.running = False
        with self.lock:
            for client in list(self.clients.keys()):
                try:
                    client.send(bytes("{quit}", 'utf8'))
                    client.close()
                except:
                    pass
            self.clients.clear()
        self.server_socket.close()
        print(f"[{self._current_time()}] Сервер остановлен")

    @staticmethod
    def _current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    server = ChatServer(port=25565)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
