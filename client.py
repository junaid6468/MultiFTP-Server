import socket
import os
import sys

class FTPclient:
    def __init__(self, address, port, data_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = int(port)
        self.data_port = int(data_port)

    def create_connection(self):
        print('Starting connection to', self.address, ':', self.port)

        try:
            server_address = (self.address, self.port)
            self.sock.connect(server_address)
            print('Connected to', self.address, ':', self.port)
        except KeyboardInterrupt:
            self.close_client()
        except Exception as e:
            print('Connection to', self.address, ':', self.port, 'failed:', str(e))
            self.close_client()

    def start(self):
        try:
            self.create_connection()
        except Exception as e:
            self.close_client()

        while True:
            try:
                command = input('Enter command: ')
                if not command:
                    print('Need a command.')
                    continue
            except KeyboardInterrupt:
                self.close_client()

            cmd = command[:4].strip().upper()
            path = command[4:].strip()

            try:
                self.sock.send(command.encode())
                data = self.sock.recv(1024).decode()
                print(data)

                if cmd == 'QUIT':
                    self.close_client()
                elif cmd in ['LIST', 'STOR', 'RETR']:
                    if data.startswith('125'):
                        func = getattr(self, cmd)
                        func(path)
                        data = self.sock.recv(1024).decode()
                        print(data)
            except Exception as e:
                print('Error:', str(e))
                self.close_client()

    def connect_datasock(self):
        self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.datasock.connect((self.address, self.data_port))

    def LIST(self, path):
        try:
            self.connect_datasock()

            while True:
                dirlist = self.datasock.recv(1024).decode()
                if not dirlist:
                    break
                sys.stdout.write(dirlist)
                sys.stdout.flush()
        except Exception as e:
            print('Error:', str(e))
        finally:
            self.datasock.close()

    def STOR(self, path):
        print('Storing', path, 'to the server')
        try:
            self.connect_datasock()

            with open(path, 'rb') as f:  # Open in binary mode
                upload = f.read(1024)
                while upload:
                    self.datasock.send(upload)
                    upload = f.read(1024)
        except Exception as e:
            print('Error:', str(e))
        finally:
            self.datasock.close()

    def RETR(self, path):
        print('Retrieving', path, 'from the server')
        try:
            self.connect_datasock()

            with open(path, 'wb') as f:  # Open in binary mode
                while True:
                    download = self.datasock.recv(1024)
                    if not download:
                        break
                    f.write(download)
        except Exception as e:
            print('Error:', str(e))
        finally:
            self.datasock.close()

    def close_client(self):
        print('Closing socket connection...')
        self.sock.close()
        print('FTP client terminating...')
        quit()

if __name__ == '__main__':
    address = input("Destination address - if left empty, default address is localhost: ")

    if not address:
        address = 'localhost'

    port = input("Port - if left empty, default port is 10021: ")

    if not port:
        port = 10021

    data_port = input("Data port - if left empty, default port is 10020: ")

    if not data_port:
        data_port = 10020

    ftpClient = FTPclient(address, port, data_port)
    ftpClient.start()
