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
                print("\n" + msg)  # Print server responses on new line
            except:
                print("\nConnection error")
                break

    threading.Thread(target=receive_messages, daemon=True).start()


    while True:
        message = input()
        if not message:
            continue

        clientSocket.send(message.encode())

        if message == "QUIT":
            break

        if message == "JOIN":
            # After JOIN, wait for acknowledgement
            response = clientSocket.recv(2048).decode()
            print(response)
            if "ERROR" in response:
                clientSocket.close()
                return

#Leave open channel to receive messages
def receive_messages(clientSocket):
    while True:
        try:
            message = clientSocket.recv(2048)
            if not message:
                break
            print(message.decode())
        except:
            break

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

