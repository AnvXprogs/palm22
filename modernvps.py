#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
import time
from datetime import datetime

class ChatServer:
    def __init__(self, host='', port=33000, buffer_size=1024):
        self.clients = {}
        self.lock = Lock()
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.running = False

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            print(f"[{self._current_time()}] Сервер запущен на порту {self.port}. Ожидание подключений...")
            
            accept_thread = Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Поток для обработки команд администратора
            admin_thread = Thread(target=self._admin_console)
            admin_thread.daemon = True
            admin_thread.start()
            
            accept_thread.join()
            
        except Exception as e:
            print(f"[{self._current_time()}] Ошибка запуска сервера: {e}")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        with self.lock:
            for client in list(self.clients.keys()):
                try:
                    client.send(bytes("{quit}", "utf8"))
                    client.close()
                except:
                    pass
            self.clients.clear()
        
        try:
            self.server_socket.close()
        except:
            pass
        print(f"[{self._current_time()}] Сервер остановлен.")

    def _accept_connections(self):
        while self.running:
            try:
                client, client_address = self.server_socket.accept()
                print(f"[{self._current_time()}] Подключение от {client_address}")
                
                Thread(target=self._handle_client, args=(client,)).start()
                
            except Exception as e:
                if self.running:
                    print(f"[{self._current_time()}] Ошибка приема подключения: {e}")

    def _handle_client(self, client):
        try:
            # Получаем имя клиента
            name = client.recv(self.buffer_size).decode("utf8").strip()
            if not name:
                raise ValueError("Пустое имя клиента")
                
            with self.lock:
                self.clients[client] = name
                
            self._broadcast(f"{name} присоединился к чату!", exclude=client)
            print(f"[{self._current_time()}] {name} ({client.getpeername()}) вошел в чат")
            
            # Основной цикл обработки сообщений
            while self.running:
                msg = client.recv(self.buffer_size).decode("utf8").strip()
                if not msg:
                    break
                    
                if msg == "{quit}":
                    break
                    
                print(f"[{self._current_time()}] {name}: {msg}")
                self._broadcast(f"{name}: {msg}", exclude=client)
                
        except Exception as e:
            print(f"[{self._current_time()}] Ошибка клиента: {e}")
            
        finally:
            with self.lock:
                if client in self.clients:
                    name = self.clients[client]
                    del self.clients[client]
                    self._broadcast(f"{name} покинул чат!")
                    print(f"[{self._current_time()}] {name} вышел из чата")
                try:
                    client.close()
                except:
                    pass

    def _broadcast(self, msg, exclude=None):
        with self.lock:
            for client in list(self.clients.keys()):
                if client != exclude:
                    try:
                        client.send(bytes(msg, "utf8"))
                    except:
                        pass

    def _admin_console(self):
        """Консоль администратора для управления сервером"""
        while self.running:
            cmd = input("Введите команду (stop/quit - остановка сервера): ").lower()
            if cmd in ('stop', 'quit', 'exit'):
                self.stop()
                break
            elif cmd == 'list':
                with self.lock:
                    print(f"Подключенные клиенты ({len(self.clients)}):")
                    for name in self.clients.values():
                        print(f"- {name}")
            else:
                print("Доступные команды: stop, list")

    @staticmethod
    def _current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    server = ChatServer(port=33000)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
