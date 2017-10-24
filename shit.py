import socket,threading, hashlib
import itertools
import string


gen = itertools.product(string.ascii_lowercase, repeat=6)
FOUND=False

def checkPass(password,md5):
    m=hashlib.md5()
    m.update(password)
    if m.hexdigest()==md5:
        return True
    return False

def getRange(num_of_passwords):
    
    start = gen.next()
    stop = ''
    print start
    for i in range(num_of_passwords):
        gen.next()
    stop = gen.next()
    print stop
    return start, stop


def manageClient(client,md5):
    print 'help'
    while True:
        #get range
        start,stop=getRange(1000000)
        #send range
        client.send('START=%s,STOP=%s,MD5=%s'%(''.join(start),''.join(stop),md5))
        print 'sent:','START=%s,STOP=%s,MD5=%s'%(''.join(start),''.join(stop),md5)
        #listen to response
        data=client.recv(1024)
        if 'NOT FOUND' ==data:
            pass
        elif 'FOUND' in data:
            password=data.split('=')[1]
            if checkPass(password,md5):
                print 'found pass:',password
                break
        

md5=hashlib.md5()
md5.update('ababab')
print md5.hexdigest()
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port=4320
s.bind(('',port))
clients=[]
while True:
    s.listen(1)
    connection,clientAddr=s.accept()
    print 'connected:',clientAddr
    data=connection.recv(1024)
    print data
    if data=='HELLO':
        t=threading.Thread(target=manageClient,args=(connection,md5.hexdigest(),))
        t.start()
    else:
        connection.close()

if __name__=='__main__':
    pass
