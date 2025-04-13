import sys
import time
from datetime import datetime
from socket import *
import sys
import random
import socket
import threading
import os

# Name: Tyler Mains #303849858
# Course CSC 138
# Section 01
# 3/27/25
# Description: Network project chatroom server

# Global
active_users = {}
log = []

def create_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    print('The server is listening on port ' + str(port))
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_thread = threading.Thread(target=handleClient,args=(client_address, client_socket))
        client_thread.start()


def handleClient(client_address, client_socket):
    global active_users
    username = None
    ip = client_address[0]

    try:
        while True:
            message = client_socket.recv(2048)
            if not message:
                break

            try:
                decoded = message.decode().strip()
            except UnicodeDecodeError:
                client_socket.send("ERROR: Invalid message encoding".encode())
                continue

            parts = decoded.split(maxsplit=1)
            if not parts:
                continue

            command = parts[0].upper()

            match command:
                case "JOIN":
                    if len(parts) < 2:
                        client_socket.send("ERROR: Usage: JOIN <username>".encode())
                        continue

                    username = parts[1]
                    if username in active_users:
                        client_socket.send(f"ERROR: Username '{username}' already exists".encode())
                    else:
                        active_users[username] = {"ip": client_address, "socket": client_socket}
                        client_socket.send(f"Welcome {username}! Type MESG <user> <message> to chat".encode())
                        with open(f"{ip}.txt)","a") as file:
                            pass
                case "MESG":
                    if len(parts) < 2:
                        client_socket.send("ERROR: Usage: MESG <user> <message>".encode())
                        continue

                    msg_parts = parts[1].split(maxsplit=1)
                    if len(msg_parts) < 2:
                        client_socket.send("ERROR: Missing message".encode())
                        continue

                    recipient, content = msg_parts
                    if recipient in active_users:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        try:
                            active_users[recipient]["socket"].send(f"{username}: {content}".encode())
                            client_socket.send("Message sent".encode())
                            with open(f"{client_address[0]}.txt", "a") as file:
                                file.write(timestamp + " " + username + " to " + recipient + ": " + content + '\n')
                        except:
                            client_socket.send("ERROR: Could not deliver message".encode())
                    else:
                        client_socket.send(f"ERROR: User '{recipient}' not found".encode())

                case "LIST":
                    users = "\n".join(active_users.keys()) if active_users else "No users online"
                    client_socket.send(f"Online users:\n{users}".encode())

                case "QUIT":
                    client_socket.send("Goodbye!".encode())
                    break

                case "LOG":
                    log = ""
                    with open(f"{client_address[0]}.txt", "r") as file:
                        client_socket.send(file.read().encode())
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        if username and username in active_users:
            del active_users[username]
        client_socket.close()
def main():
    if len(sys.argv) != 2:
        print("Useage: chatsvr.py <port>")
        sys.exit(1)
    else:
        port = int(sys.argv[1])
        print('The server is listening on port ' + str(port))
        create_server(port)


if __name__ == "__main__":
    main()
