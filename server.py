import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 5000))
while True:
    recvSize = 1024
    message, address = server_socket.recvfrom(recvSize)
    message = str(message)
    with open('logfile.log','a') as f:
        f.write(message[2:-1] + "\n")
