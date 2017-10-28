import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 2345))

client.send('HELLO')

job = client.recv(1024)
print job

password = 'test'
client.send('FOUND={}'.format(password))

print client.recv(1024)

client.close()
