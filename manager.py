import socket
import threading
import re
import hashlib
import password_handler

# Globals:
MANAGER_PORT = 4320
KEEP_ALIVE_PORT = 4321
HASHED_PASSWORD = '62318aca2ef2e809a13623715a8aaff4'  # testme

found = False
password = ''

connected_clients = list()
keep_alive_counter = dict()


def keep_alive(ka_client):

    global keep_alive_counter

    try:

        ka_message = ka_client.recv(1024)

        if ka_message == 'ALIVE':

            keep_alive_counter[ka_client] = 0

        else:

            keep_alive_counter[ka_client] = 3
            ka_client.close()

    except socket.timeout:

        keep_alive_counter[ka_client] += 1


def stop_self():
    """
    stop_self stop_self() -> None

    Stop manager socket.
    """

    stop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stop_socket.connect(('127.0.0.1', MANAGER_PORT))
    stop_socket.send('')
    stop_socket.close()


def stop_clients():
    """
    stop_clients stop_clients() -> None

    Stop all connected clients.
    """

    global connected_clients

    # close each client in the 'connected clients' list
    for client_socket in connected_clients:

        try:

            client_socket.send('STOP')
            client_socket.close()

        except Exception as e:

            print type(e)

    # clear connected clients list
    connected_clients = list()


def manage_client(client_socket, keep_alive_socket):
    """
    manage_client manage_client(client_socket) -> None

    Manage a connected client socket according to known
    protocol.
    """

    global found
    global password
    global connected_clients
    global keep_alive_counter

    k = threading.Timer(4.5, keep_alive, args=keep_alive_socket)
    k.start()

    temp = tuple()

    # handle the client while the password was not found
    while not found:

        if keep_alive_counter[keep_alive_socket] == 3:

            k.close()
            client_socket.close()
            connected_clients.remove(client_socket)
            keep_alive_counter.pop(keep_alive_socket, None)
            break

        # assign job details (start password, stop password, hash)
        # only assign job when password queue is not empty
        if not password_handler.password_generator_empty and password_handler.password_queue.empty():

            password_handler.generate_chunk()
            print 'New chunk generated. Ready to work!'

        if not password_handler.password_queue.empty():

            temp = password_handler.password_queue.get()
            client_start, client_stop = temp
            job_details = 'START={},STOP={},MD5={}'.format(client_start, client_stop, HASHED_PASSWORD)

            # send job details to client and listen for an answer
            try:

                client_socket.send(job_details)

            # if something went wrong with the connection,
            # return range back to queue and stop managing
            # this client.
            except Exception as e:

                password_handler.password_queue.put(temp)
                print type(e)
                break

        try:

            answer = client_socket.recv(1024)

        except Exception as e:

            password_handler.password_queue.put(temp)
            print type(e)
            break

        else:

            # check client's answer with matchObject
            answer_check = re.match('FOUND=(.*)', answer)

            if answer_check:

                # extract real password from client's answer
                password = answer_check.group(1)

                # confirm the password is real
                if hashlib.md5(password).hexdigest() == HASHED_PASSWORD:

                    found = True

                else:

                    password = ''
                    password_handler.password_queue.put(temp)

                # if client sent found, we assume it closed the
                # connection, so we stop listening to him.
                break

            # check if client works according to protocol (close connection if not)
            elif answer != 'NOT FOUND':

                password_handler.password_queue.put(temp)
                # close connection since client is not genuine
                client_socket.close()
                connected_clients.remove(client_socket)
                break

    # stop all clients when password is found
    if found:
        print 'WE FOUND IT! Stopping clients.'
        stop_clients()
        stop_self()


def main():

    global KEEP_ALIVE_PORT
    global MANAGER_PORT
    global connected_clients

    # initialize password ranges queue
    password_handler.generate_chunk()
    print 'Chunk generated. Ready to work!'

    # create manager socket
    manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager_socket.bind(('', MANAGER_PORT))

    # create keep-alive socket
    ka_manager = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ka_manager.bind(('', KEEP_ALIVE_PORT))

    while not found:

        manager_socket.listen(1)
        client_socket, client_address = manager_socket.accept()

        data = client_socket.recv(1024)

        if data == 'HELLO':

            connected_clients.append(client_socket)

            client_socket.send('KA={}'.format(KEEP_ALIVE_PORT))

            ka_client, ka_address = ka_manager.accept()
            ka_client.settimeout(1)

            keep_alive_counter[ka_client] = 0

            t = threading.Thread(target=manage_client, args=(client_socket, ka_client))
            t.start()

        else:

            client_socket.close()

    manager_socket.close()
    print 'Password found! {}'.format(password)


if __name__ == '__main__':
    main()
