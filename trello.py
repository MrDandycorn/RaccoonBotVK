import socket


def trello_socket():
    while True:
        try:
            s = socket.socket()
            s.bind(('', 9083))
            print('Trello socket running!')
            s.listen(5)
            while True:
                try:
                    c, (client_host, client_port) = s.accept()
                    if client_host.startswith('107.23') or client_host.startswith('54.152'):
                        request = c.recv(1000)
                        c.send(b'HTTP/1.1 200 OK\n')
                        c.send(b'Content-Type: text/html\n')
                        c.send(b'\n')
                        print(f'New request from Trello: {request}')
                    c.close()
                except Exception as e:
                    print(f'Произошла ошибка: {e}')
        except Exception as e:
            print(f'Произошла ошибка: {e}')

