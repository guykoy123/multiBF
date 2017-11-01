import socket
import threading
import re
import hashlib
import password_handler

# Globals:
MANAGER_PORT = 4320
HASHED_PASSWORD = '62318aca2ef2e809a13623715a8aaff4'  # testme

found = False
password = ''

connected_clients = list()


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


def manage_client(client_socket):
    """
    manage_client manage_client(client_socket) -> None

    Manage a connected client socket according to known
    protocol.
    """

    global found
    global password
    global connected_clients

    temp = tuple()

    # handle the client while the password was not found
    while not found:

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

    global connected_clients

    # initialize password ranges queue
    password_handler.generate_chunk()
    print 'Chunk generated. Ready to work!'

    # create manager socket
    manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager_socket.bind(('127.0.0.1', MANAGER_PORT))
    manager_socket.listen(1)

    while not found:

        client_socket, client_address = manager_socket.accept()

        data = client_socket.recv(1024)

        if data == 'HELLO':

            connected_clients.append(client_socket)

            t = threading.Thread(target=manage_client, args=(client_socket,))
            t.start()

        else:

            client_socket.close()

    manager_socket.close()
    print 'Password found! {}'.format(password)


if __name__ == '__main__':
    main()
