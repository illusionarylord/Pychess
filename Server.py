import socket
import threading
#import chess

# Initialize global variables
host = '127.0.0.1'
port = 5559
WhitesMove = True
clients = []

# Create and bind the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(2)

def handle_client(Turn):
    global clients

    try:
        # Receive the move from the client
        move = clients[Turn].recv(1024).decode('utf-8')
        print("Move received!")

        # Broadcast the move to all clients
        BroadcastMove(move)
        print("Move sent!")

        # if theres an error, restart the server instead of crashing
    except Exception as e:
        print(f"Error handling client: {e}")
        print("Restarting server")
        clients = []
        accept_clients()

# sends the move to both clients to be made
def BroadcastMove(move):
    global clients
    for client in clients:
        try:
            client.send(move.encode('utf-8'))
        except:
            print("Error broadcasting move")
            print("Restarting server")
            clients = []
            accept_clients()

   # handles clients connecting to the server, and sending them their colours (1 or 0 depending on white or black respectively)
def accept_clients():
    while len(clients) < 2:
        print("Server is listening...")
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} established!")

        if len(clients) == 0:
            Colour = 1
        else:
            Colour = 0

        clients.append(client_socket)
        client_socket.send(str(Colour).encode('utf-8'))
                           
# Start accepting clients
accept_clients()

# Run main code

# count moves and repeat the client handling for the current player (decided by the move counter)
MoveCounter = 0
while True:

    Turn = MoveCounter % 2
    handle_client(Turn)
    MoveCounter += 1