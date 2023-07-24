import socket


HOST, PORT = '127.0.0.1', 65437

def client_program():
    client_socket = socket.socket()
    client_socket.connect((HOST, PORT))

    message = input(">> ")

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        if data is None:
            print('toto')
        print('Data received from server: ' + data)
        message = input(">> ")
    client_socket.close()


if __name__ == '__main__':
    client_program()