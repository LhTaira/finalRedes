#!/usr/bin/env python3
import threading
import socket
import argparse
import os
import sys
import tkinter as tk
import queue

class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]
            if message == 'QUIT':
                break
                    
        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

arrayQ = queue.Queue()
roomsQ = queue.Queue()
class Receive(threading.Thread):
    def __init__(self, sock, name, rooms, rooms_array):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None
        self.rooms = rooms
        self.rooms_array = rooms_array

    def run(self):
        while True:
            message = self.sock.recv(1024).decode('ascii')

            json = eval(message)

            if(json["header"] == 'room'):
                self.rooms_array.clear()

                for index, roomNumber in enumerate(json['message']):
                    self.rooms_array.append(roomNumber)
                self.rooms_array.append(69)
                print('thisis', self.rooms_array)
                self.rooms.delete(0, 'end')

                list_rooms(self.rooms_array, self.rooms)

            if json["header"] == 'message':
                print(eval(message)["header"])

                print(eval(message))
                if self.messages:
                    self.messages.insert(tk.END, eval(message)["name"] +': ' + eval(message)["message"])
                    print('\r{}\n{}: '.format(message, self.name), end = '')
                
                else:

                    print('\r{}\n{}: '.format(message, self.name), end = '')

class Client:
    def __init__(self, host, port, rooms, rooms_array):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None
        self.rooms = rooms
        self.rooms_array = rooms_array
    
    def start(self):
        print('Trying to connect to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Successfully connected to {}:{}'.format(self.host, self.port))
        
        print()
        self.name = input('Your name: ')

        print()
        print('Welcome, {}! Getting ready to send and receive messages...'.format(self.name))

        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name, self.rooms, self.rooms_array)

        send.start()
        receive.start()

        print("\rAll set! Leave the chatroom anytime by typing 'QUIT'\n")
        print('{}: '.format(self.name), end = '')

        return receive

    def send(self, header, message):
        message = f'{{"header":  "{header}","message":  "{message}", "name": "{self.name}"}}'
        if message == 'QUIT':
            
            print('\nQuitting...')
            self.sock.close()
            os._exit(0)
        else:
            print('send: ', message)
            self.sock.sendall(message.encode('ascii'))

def list_rooms_t():

    for index, room in enumerate(rooms_array):
        print(room, index)
        if(room == 69):
            rooms.insert(tk.END, 'Criar nova sala')
        else:
            rooms.insert(tk.END, '{} {}'.format('Sala', index))


def list_rooms(rooms_array, rooms):
    for index, room in enumerate(rooms_array):
        print(room, index)
        if(room == 69):
            rooms.insert(tk.END, 'Criar nova sala')
        else:
            rooms.insert(tk.END, '{} {}'.format('Sala', room))
    
def room_selected(rooms_array, frm_messages, rooms, frm_rooms, t, client, receive):

    selected_room = rooms.curselection()
    if(len(selected_room) > 0):
        if(selected_room[0] < 68):
            if(selected_room[0] == len(client.rooms_array) - 1):

                client.send('room', len(client.rooms_array))

            else: 
                client.send('connect', "sala"+str(selected_room[0] + 1))
                t.config(text = 'Sala ' + str(selected_room[0] + 1))
                frm_messages.tkraise()
                receive.messages.delete(0, tk.END)


def main(host, port):
    rooms = []
    rooms_array = []

    window = tk.Tk()
    window.title('Fonk Chat')

    frm_messages = tk.Frame(master=window)
    frm_rooms = tk.Frame(master=window)

    scrollbar = tk.Scrollbar(master=frm_messages)
    messages = tk.Listbox(
        master=frm_messages, 
        yscrollcommand=scrollbar.set
    )
    rooms = tk.Listbox(
        master=frm_rooms, 

    )
    client = Client(host, port, rooms, rooms_array)
    receive = client.start() 
    rooms.bind('<<ListboxSelect>>', lambda event: room_selected(rooms_array, frm_messages, rooms, frm_rooms, t, client, receive))


    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    rooms.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    rooms_array = []
    rooms_array.append(69)
    
    list_rooms(rooms_array, rooms)
    frm_rooms.grid(row=1, column=0, columnspan=3, sticky="nsew")


    client.messages = messages
    receive.messages = messages

    frm_messages.grid(row=1, column=0, columnspan=3, sticky="nsew")
    frm_rooms.tkraise()

    frm_entry = tk.Frame(master=window)
    text_input = tk.Entry(master=frm_entry)
    text_input.pack(fill=tk.BOTH, expand=True)

    text_input.insert(0, "Your message here.")

    btn_send = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send('null', text_input.get()) or text_input.delete(0, tk.END)
            
    )

    btn_fonk = tk.Button(
        master=window,
        text='X',
        command= lambda: frm_rooms.tkraise() or t.config(text = 'Entre em uma sala') or client.send('disconnect', 'null') or text_input.delete(0, tk.END)
            
    )

    t = tk.Label(window, text='imgay')
    t.grid(row=0, column=1, columnspan=2)
    t.config(text = 'Entre em uma sala')
    frm_entry.grid(row=2, column=0, padx=10, sticky="ew", columnspan=2)
    btn_send.grid(row=2, column=2, pady=10, sticky="ew")    
    btn_fonk.grid(row=0, column=0, pady=10, sticky="ew")

    window.rowconfigure(0, minsize=10, weight=0)
    window.rowconfigure(1, minsize=500, weight=1)
    window.rowconfigure(2, minsize=50, weight=0)
    window.columnconfigure(0, minsize=5, weight=0)
    window.columnconfigure(1, minsize=500, weight=1)
    window.columnconfigure(2, minsize=200, weight=0)

    window.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    main(args.host, args.p)