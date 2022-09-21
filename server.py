#!/usr/bin/env python3

from http import client
import threading
import socket
import argparse
import os
import json

def findClient(target):

    for client in clients:

        if client.socket_name == target:
            return client

clients = []
rooms = []

class Client():
    def __init__(self):
        self.socket_name = None
        self.room = None
    

class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
    


    def run(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print('Listening at', sock.getsockname())

        while True:


            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))
            
            
            server_socket = ServerSocket(sc, sockname, self)
            

            server_socket.start()
            print(sockname, server_socket.sockname)
            client = Client()
            client.socket_name = sockname
            client.room = 'sala1'

            clients.append(client)
            self.connections.append(server_socket)
            print(clients)
            print('Ready to receive messages from', sc.getpeername())
            roomsObj = {
                "header": "room",
                "message": rooms
            }
            roomsJson = json.dumps(roomsObj)
            server_socket.send(roomsJson)

    def broadcast(self, message, source, name, isroom):
        client = findClient(source)
        print(source)
        jsonObj = {
            "header": "message",
            "message": message,
            "name": name
        }
        jsonString = json.dumps(jsonObj)

        for connection in self.connections:
            connClient = findClient(connection.sockname)

            if connClient.room == client.room:
                if(isroom == 'false'):
                    connection.send(jsonString)
                else:
                    connection.send(message)
    
    def remove_connection(self, connection):
        client = findClient(connection.sockname)

        self.connections.remove(connection)
        clients.pop(clients.index(client))


class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
    


    def run(self):

        while True:
            message = self.sc.recv(1024).decode('ascii')
            print('message: ', message)
            if message:
                print(message)
                jsonMessage = json.loads(message)
                if jsonMessage["header"] == "connect":
                    newClient = Client()
                    newClient.socket_name = self.sockname
                    newClient.room = jsonMessage["message"]

                    clientRoom = findClient(self.sockname)
                    clients[clients.index(clientRoom)] = newClient
                    

                elif jsonMessage["header"] == "disconnect":
                    message = '{} has left the chat.'.format(jsonMessage["name"])
                    self.server.broadcast(message, self.sockname, 'Server', 'false')
                    roomsObj = {
                        "header": "room",
                        "message": rooms
                        }
                    roomsJson = json.dumps(roomsObj)
                    self.server.broadcast(roomsJson, self.sockname,'','true')

                elif jsonMessage["header"] == "room":
                    rooms.append(jsonMessage["message"])
                    roomsObj = {
                        "header": "room",
                        "message": rooms
                        }
                    roomsJson = json.dumps(roomsObj)
                    self.server.broadcast(roomsJson, self.sockname,'','true')

                else:
                    self.server.broadcast(jsonMessage["message"], self.sockname,jsonMessage["name"],'false')
            else:

                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                server.remove_connection(self)
                return

    
    def send(self, message):

        self.sc.sendall(message.encode('ascii'))


def exit(server):

    while True:
        ipt = input('')
        if ipt == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()


    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target = exit, args = (server,))
    exit.start()