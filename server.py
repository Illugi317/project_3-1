import socket
import time
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 5000))
prev = 0
while True:
    recvSize = 1024
    start = time.time()
    message, address = server_socket.recvfrom(recvSize)
    message = str(message)
    el = time.time() - start
    fm = message[2:-1] + f",{round(el*1000,2)}"
    with open('csv/csv_new_throws/throw-demo.csv', 'a') as f:
        f.write("orix,oriy,oriz,gyrox,gyroy,gyroz,linerx,linery,linerz,accx,accy,accz,gravx,gravy,gravz,temp,ms\n")
        f.write(fm + "\n")