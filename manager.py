import socket
import threading
import itertools
import re
import hashlib
import string

# Globals:
# Constants:
NUMBER_OF_PASSWORDS = 1000

# real password is: 'xtestme'
HASHED_PASSWORD = '0087c33019e2efcc8a4e9e881a1f33e2'

# Not constants:
gen = itertools.product(string.ascii_lowercase, repeat=6)
found = False
real_password = ''
connected_clients = []
is_connected = False


def gen_pass(num_of_passwords):
    """
    Generate passwords via global generator 'gen'.

    :params: num_of_passwords: number of passwords to be generated.
    :return: (start, stop): start password, stop password.
    """

    # start position.
    start = ''.join(gen.next())

    for i in range(num_of_passwords):
        gen.next()

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

        client_socket.send('STOP')
        client_socket.close()

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

    # handle the client while the password was not found.
    while not found:

        # assign job details (start password, stop password, hash).
        client_start, client_stop = gen_pass(NUMBER_OF_PASSWORDS)
        job_details = 'START={},STOP={},MD5={}'.format(client_start, client_stop, HASHED_PASSWORD)

        # send client job details and listen for an answer.
        client_socket.send(job_details)
        answer = client_socket.recv(1024)

        # check client's answer with matchObject.
        answer_check = re.match('FOUND=(.*)', answer)

        if answer_check:

            # extract real password from client's answer.
            real_password = answer_check.group(1)

            # confirm the password is real.
            if hashlib.md5(real_password).hexdigest() == HASHED_PASSWORD:

                found = True

        # check if client works according to protocol (close connection if not).
        elif answer != 'NOT FOUND':

            # close connection since client is not genuine.
            client_socket.close()
            connected_clients.remove(client_socket)
            break

    # stop all clients when password is found.
    if found:
        stop_clients()


# create manager socket.
manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
manager_port = 2345
manager_socket.bind(('127.0.0.1', manager_port))
manager_socket.listen(1)


while True:

    client_socket, client_address = manager_socket.accept()

    data = client_socket.recv(1024)
    if data == 'HELLO':

        connected_clients.append(client_socket)
        t = threading.Thread(target=manage_client, args=(client_socket, ))
    else:

        client_socket.close()

manager_socket.close()
