import socket,threading
import itertools
import string


gen = itertools.product(string.ascii_lowercase, repeat=6)
FOUND=False

def gen_pass(num_of_passwords):
    
    start = gen.next()
    stop = ''
    for i in range(num_of_passwords):
        gen.next()
    stop = gen.next()

    return start, stop


def manageClient(client):
    while True:
        pass
        

         
s=socket.scoket(socket.AF_INET,socket.SOCK_STREAM)
port=2345
s.bind(('127.0.0.1',port))
clients=[]
while True:
    s.listen(1)
    connection,clientAddr=s.accept()
    data=connection.recv(1024)
    if data=='HELLO':
        t=threading.Thread(target=manageClient,args=(connection))
    else:
        connection.close()


