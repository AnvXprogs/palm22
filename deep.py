#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
from tkinter import ttk
import os

def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tk.END, msg)
            msg_list.see(tk.END)  # Автопрокрутка к новому сообщению
        except OSError:
            break

def send(event=None):
    msg = my_msg.get()
    if msg.strip():  # Отправляем только непустые сообщения
        my_msg.set("")
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            client_socket.close()
            top.quit()

def on_closing(event=None):
    my_msg.set("{quit}")
    send()

# Создаем основное окно
top = tk.Tk()
top.title("TkMessenger")
top.geometry("800x600")  # Большое окно
top.minsize(600, 400)   # Минимальный размер

top.iconbitmap('logo.ico')


style = ttk.Style()
style.configure('TButton', font=('Arial', 12), padding=10)

main_container = ttk.Frame(top)
main_container.pack(fill="both", expand=True, padx=10, pady=10)


msg_frame = ttk.LabelFrame(main_container, text="Сообщения")
msg_frame.pack(fill="both", expand=True, pady=(0, 10))


msg_list = tk.Listbox(
    msg_frame,
    height=20,
    width=60,
    font=('Arial', 12),
    bg='white',
    fg='black',
    borderwidth=0,
    highlightthickness=0
)
scrollbar = ttk.Scrollbar(msg_frame, orient="vertical", command=msg_list.yview)
msg_list.configure(yscrollcommand=scrollbar.set)


scrollbar.pack(side="right", fill="y")
msg_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)


bottom_frame = ttk.Frame(main_container)
bottom_frame.pack(fill="x", pady=(5, 0))

my_msg = tk.StringVar()
entry_field = ttk.Entry(
    bottom_frame,
    textvariable=my_msg,
    font=('Arial', 12)
)
entry_field.pack(side="left", fill="x", expand=True, padx=(0, 10))

send_button = ttk.Button(
    bottom_frame,
    text="Отправить (Enter)",
    command=send,
    width=15
)
send_button.pack(side="right")


entry_field.bind("<Return>", send)

# Очистка placeholder-текста при фокусе
def clear_placeholder(e):
    if my_msg.get() == "Введите ваше сообщение здесь":
        my_msg.set("")
entry_field.bind("<FocusIn>", clear_placeholder)

# Возврат placeholder-текста если поле пустое
def return_placeholder(e):
    if not my_msg.get():
        my_msg.set("Введите ваше сообщение здесь")
entry_field.bind("<FocusOut>", return_placeholder)

top.protocol("WM_DELETE_WINDOW", on_closing)

# Подключение к серверу
HOST = input('Введите хост: ')
PORT = input('Введите порт: ')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()

tk.mainloop()