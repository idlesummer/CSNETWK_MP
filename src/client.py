from socket import *

client = socket(AF_INET, SOCK_STREAM)

client.connect(('localhost', 12345))

print(client.recv(4096).decode())

client.send('/register User1'.encode())

print(client.recv(4096).decode())