import socket
import threading
import itertools
import re
import hashlib
import string

# Globals:
# Constants:
NUMBER_OF_PASSWORDS = 10000000

# real password is: 'ggbbaa'
HASHED_PASSWORD = '9286a271d4ab3ffa09727d9e18e3dee9'

# Not constants:
ranges=[]
gen = itertools.product(string.ascii_lowercase, repeat=6)
found = False
real_password = ''
connected_clients = []
is_connected = False
end_of_range=False

 # TODO: add watchdog

def getRanges():
    """
    try to read precalculated ranges from file
    if unable: calculate ranges save in a file and return
    otherwise: read from file and return"""

    with open('ranges.txt','w+') as f: #open file (automicly closes file)
        try:
            text=f.read() # try to read from file
        except: # unable to read, calculate ranges
            l=[]
            while not end_of_range:
                l.append(gen_pass(NUMBER_OF_PASSWORDS))

            fileText=''
            for i in l:
                fileText=fileText+','+i[0]+','+i[1] # create string that will be written to file

            fileText=fileText[1:-1] # remove the ',' in the beginning
            return l

        tempRanges=text.split(',') # able to read
        ranges=[]
        for i in range(len(tempRanges)-1): # create a list with all ranges
            ranges.append(tempRanges[i],tempRanges[i+1])
        return ranges



def gen_pass(num_of_passwords):
    """
    Generate passwords via global generator 'gen'.
    :params: num_of_passwords: number of passwords to be generated.
    :return: (start, stop): start password, stop password.
    """
    global end_of_range
    # start position.
    start = ''.join(gen.next())

    for i in range(num_of_passwords):
        try:
            gen.next()
        except:
            stop='zzzzzz'
            end_of_range=True
            return start,stop


    # stop position.
    stop = ''.join(gen.next())
    return start, stop


def stop_clients():
    """
    Stop all connected clients.
    :return: None.
    """

    global connected_clients

    # close each client in the 'connected clients' list.
    for client_socket in connected_clients:
        try:
            client_socket.send('STOP')
            client_socket.close()
        except:
            print 'Connection closed'

    # clear list.
    connected_clients = list()


def manage_client(client_socket):
    """
    Manage connected client (send password ranges, etc.).
    :params: client_socket: socket of the connected client.
    :return: None.
    """

    global connected_clients
    global found
    global real_password
    global ranges

    # handle the client while the password was not found.
    while not found:
        # assign job details (start password, stop password, hash).
        print ranges[-1]
        if len(ranges)!=0:
            temp=ranges.pop(0)
            client_start,client_stop = temp
            job_details = 'START={},STOP={},MD5={}'.format(client_start, client_stop, HASHED_PASSWORD)

            # send client job details and listen for an answer.
            client_socket.send(job_details)
            print str(job_details)
        try:
            answer = client_socket.recv(1024)
            # check client's answer with matchObject.
            answer_check = re.match('FOUND=(.*)', answer)
        except Exception as exc:
            ranges.append(temp)
            print type(exc)
            break


        if answer_check:

            # extract real password from client's answer.
            real_password = answer_check.group(1)

            # confirm the password is real.
            if hashlib.md5(real_password).hexdigest() == HASHED_PASSWORD:
                print 'found:',real_password
                found = True

        # check if client works according to protocol (close connection if not).
        elif answer != 'NOT FOUND':
            ranges.append(temp)
            # close connection since client is not genuine.
            client_socket.close()
            connected_clients.remove(client_socket)
            break

    # stop all clients when password is found.
    if found:
        stop_clients()

def main():
    # create manager socket.
    manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager_port = 4320
    manager_socket.bind(('', manager_port))
    ranges=getRanges() # retrieve ranges
    print 'got ranges'
    threads =[]

    while True:
        manager_socket.listen(1)
        client_socket, client_address = manager_socket.accept()

        data = client_socket.recv(1024)
        print 'Connected to client:', client_address,' recieved:',data
        if data == 'HELLO':


            connected_clients.append(client_socket)
            t = threading.Thread(target=manage_client, args=(client_socket, )) # open thread that will manage the client
            t.start()
            threads.append(t)
        else:

            client_socket.close()

        if len(connected_clients)==0 and len(ranges)==0: # if all connections closed and finished scanning all ranges
            for i in threads: # close all threads
                i.join()
            break
    manager_socket.close()
    print 'server closed'

if __name__=='__main__':
    main()
