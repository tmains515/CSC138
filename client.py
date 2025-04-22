import os
import sys
import time
from socket import *
import threading
# Name: Tyler Mains #303849858
# Course CSC 138
# Section 01
# 3/27/25
# Description: Network project chatroom client

def client(server_name, server_port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((server_name, server_port))
    print("Connected to server")


    def receive_messages():
        while True:
            try:
                msg = clientSocket.recv(2048).decode()
                if not msg:
                    print("\nServer disconnected")
                    break
                print("\n" + msg)
            except:
                print("\nConnection error")
                break

    # Start individual thread
    threading.Thread(target=receive_messages, daemon=True).start()
    print(f"Enter JOIN followed by your username: ")

    # Loop waiting for message
    while True:
        message = input()
        message = message
        if not message:
            continue

        clientSocket.send(message.encode())

        if message.upper().startswith("QUIT"):
            clientSocket.close()
            sys.exit(0)


        if message.upper().startswith("JOIN"):
            response = clientSocket.recv(2048).decode()
            print(response)



def main():
    if len(sys.argv) != 3:
        print('Useage: chatcli.py <server name> <port>')
        sys.exit(1)
    else:
        server = sys.argv[1]
        port = int(sys.argv[2])
        client(server, port)



if __name__ == "__main__":
    main()

