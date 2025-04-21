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

            # Separates the command from other parts of message
            parts = decoded.split(maxsplit=1)

            # If user sends nothing
            if not parts:
                continue

            command = parts[0].upper()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            match command:
                case "JOIN":

                    if len(parts) < 2:
                        client_socket.send("ERROR: Usage: JOIN <username>".encode())
                        continue

                    if len(active_users) >= 10:
                        client_socket.send("ERROR: Too many users".encode())
                        return
                    username = parts[1]
                    already_registered = False
                    for reg_user, data in active_users.items():
                        if data["socket"] == client_socket:
                            client_socket.send(f"ERROR: You're already registered as '{reg_user}'".encode())
                            already_registered = True
                            break

                    # Forces next iteration throwing request away if user attempts to login as multiple users
                    if already_registered:
                        continue

                    if username in active_users:
                        client_socket.send(f"ERROR: Username '{username}' already exists".encode())
                    else:
                        active_users[username] = {"ip": client_address, "socket": client_socket}
                        print(f"{username} has joined the chatroom\n")

                        # Broadcast someone new joining server
                        for user in active_users:
                            active_users[user]["socket"].send(f"{username} has joined the chat".encode())

                        #Start log file if none present
                        with open(f"{ip}.txt)", "a") as file:
                            pass


                case "MESG":
                    # Checks for missing useage components
                    if len(parts) < 2:
                        client_socket.send("ERROR: Usage: MESG <user> <message>".encode())
                        continue

                    #Take recipient from message
                    msg_parts = parts[1].split(maxsplit=1)

                    if len(msg_parts) < 2:
                        client_socket.send("ERROR: Missing message. Usage: MESG <user> <message>".encode())
                        continue

                    recipient, content = msg_parts

                    #Check that user is registered then send and log message
                    if recipient in active_users:
                        try:
                            active_users[recipient]["socket"].send(f"{username}: {content}".encode())
                            client_socket.send(f"To {recipient}: {content}".encode())
                            with open(f"{client_address[0]}.txt", "a") as file:
                                file.write(timestamp + " " + username + " to " + recipient + ": " + content + '\n')
                        except:
                            client_socket.send("ERROR: Could not deliver message".encode())
                    else:
                        client_socket.send(f"ERROR: User '{recipient}' not found".encode())

                # Check that user is registered then return list of current users
                case "LIST":
                    if username in active_users:
                        users = "\n".join(active_users.keys())
                        client_socket.send(f"Online users:\n{users}".encode())
                    else:
                        client_socket.send(f"ERROR: Must be logged in to do this".encode())

                # Check that user is registered, then alert server and users that user has left, socket closed on client
                case "QUIT":
                    if username in active_users:
                        active_users.pop(username)
                        for user in active_users:
                            active_users[user]["socket"].send(f"{username} has left the chat.".encode())
                    print(f"{username} has left the chat")

                # View chat log
                case "LOG":
                    if username in active_users:
                        with open(f"{client_address[0]}.txt", "r") as file:
                            client_socket.send(file.read().encode())

                # Broadcast
                case "BCST":
                    if len(parts) < 2:
                        client_socket.send("ERROR: Missing message. Usage: BCST <message>".encode())
                        continue

                    # Check that user is registered then loop through all users sending broadcast
                    for user in active_users:
                        try:
                            active_users[user]["socket"].send(f"{username} is sending a broadcast\n".encode())
                            active_users[user]["socket"].send(f"{username}: {parts[1]}".encode())
                            with open(f"{client_address[0]}.txt", "a") as file:
                                file.write(timestamp + " " + username + " broadcasts to " + user + ": " + parts[1] + '\n')
                        except:
                            client_socket.send("ERROR: Could not deliver message".encode())


    except Exception as e:
        print(f"Client error: {e}")


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
