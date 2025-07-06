import socket
import os
import sys
import threading
import time

class FTPThreadServer(threading.Thread):
    def __init__(self, client_tuple, local_ip, data_port):
        self.client, self.client_address = client_tuple
        self.cwd = os.getcwd()
        self.data_address = (local_ip, data_port)

        threading.Thread.__init__(self)

    def start_datasock(self):
        try:
            print('Creating data socket on ' + str(self.data_address) + '...')
            # create TCP for data socket
            self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.datasock.bind(self.data_address)
            self.datasock.listen(5)

            print('Data socket is started. Listening to ' + str(self.data_address) + '...')
            self.client.send(b'125 Data connection already open; transfer starting.\r\n')

            return self.datasock.accept()
        except Exception as e:
            print('ERROR: test ' + str(self.client_address) + ': ' + str(e))
            self.close_datasock()
            self.client.send(b'425 Cannot open data connection.\r\n')

    def close_datasock(self):
        print('Closing data socket connection...')
        try:
            self.datasock.close()
        except:
            pass

    def run(self):
        try:
            print('Client connected: ' + str(self.client_address) + '\n')

            while True:
                cmd = self.client.recv(1024).decode()
                if not cmd:
                    break
                print('Commands from ' + str(self.client_address) + ': ' + cmd)
                try:
                    func = getattr(self, cmd[:4].strip().upper())
                    func(cmd)
                except AttributeError:
                    print('ERROR: ' + str(self.client_address) + ': Invalid Command.')
                    self.client.send(b'550 Invalid Command\r\n')
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            self.QUIT('')

    def QUIT(self, cmd):
        try:
            self.client.send(b'221 Goodbye.\r\n')
        except:
            pass
        finally:
            print('Closing connection from ' + str(self.client_address) + '...')
            self.close_datasock()
            self.client.close()
            quit()

    def LIST(self, cmd):
        print('LIST', self.cwd)
        (client_data, client_address) = self.start_datasock()

        try:
            listdir = os.listdir(self.cwd)
            if not len(listdir):
                max_length = 0
            else:
                max_length = len(max(listdir, key=len))

            header = '| %*s | %9s | %12s | %20s | %11s | %12s |' % (max_length, 'Name', 'Filetype', 'Filesize', 'Last Modified', 'Permission', 'User /Group')
            table = '%s\n%s\n%s\n' % ('-' * len(header), header, '-' * len(header))
            client_data.sendall(table.encode())
            
            for i in listdir:
                path = os.path.join(self.cwd, i)
                stat = os.stat(path)
                data = '| %*s | %9s | %12s | %20s | %11s | %12s |\n' % (max_length, i, 'Directory' if os.path.isdir(path) else 'File', str(stat.st_size) + 'B', time.strftime('%b %d, %Y %H:%M', time.localtime(stat.st_mtime)),
                    oct(stat.st_mode)[-4:], str(stat.st_uid) + '/' + str(stat.st_gid)) 
                client_data.sendall(data.encode())
            
            table = '%s\n' % ('-' * len(header))
            client_data.sendall(table.encode())
            
            self.client.send(b'\r\n226 Directory send OK.\r\n')
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            self.client.send(b'426 Connection closed; transfer aborted.\r\n')
        finally: 
            client_data.close()
            self.close_datasock()

    def PWD(self, cmd):
        self.client.send(f'257 "{self.cwd}".\r\n'.encode())

    def CWD(self, cmd):
        dest = os.path.join(self.cwd, cmd[4:].strip())
        if os.path.isdir(dest):
            self.cwd = dest
            self.client.send(f'250 OK "{self.cwd}".\r\n'.encode())
        else:
            print('ERROR: ' + str(self.client_address) + ': No such file or directory.')
            self.client.send(b'550 No such file or directory.\r\n')

    def CDUP(self, cmd):
        parent_dir = os.path.dirname(self.cwd)
        if os.path.isdir(parent_dir):
            self.cwd = parent_dir
            self.client.send(f'250 OK "{self.cwd}".\r\n'.encode())
        else:
            print('ERROR: ' + str(self.client_address) + ': No parent directory.')
            self.client.send(b'550 No parent directory.\r\n')

    def RETR(self, cmd):
        filename = cmd[5:].strip()
        filepath = os.path.join(self.cwd, filename)
        if os.path.isfile(filepath):
            (client_data, client_address) = self.start_datasock()
            try:
                with open(filepath, 'rb') as f:
                    self.client.send(b'150 Opening data connection.\r\n')
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        client_data.sendall(data)
                self.client.send(b'226 Transfer complete.\r\n')
            except Exception as e:
                print('ERROR: ' + str(self.client_address) + ': ' + str(e))
                self.client.send(b'426 Connection closed; transfer aborted.\r\n')
            finally:
                client_data.close()
                self.close_datasock()
        else:
            print('ERROR: ' + str(self.client_address) + ': File not found.')
            self.client.send(b'550 File not found.\r\n')

    def STOR(self, cmd):
        filename = cmd[5:].strip()
        filepath = os.path.join(self.cwd, filename)
        (client_data, client_address) = self.start_datasock()
        try:
            self.client.send(b'150 Opening data connection for upload.\r\n')
            with open(filepath, 'wb') as f:
                while True:
                    data = client_data.recv(1024)
                    if not data:
                        break
                    f.write(data)
            self.client.send(b'226 Transfer complete.\r\n')
        except Exception as e:
            print('ERROR: ' + str(self.client_address) + ': ' + str(e))
            self.client.send(b'426 Connection closed; transfer aborted.\r\n')
        finally:
            client_data.close()
            self.close_datasock()

class FTPserver:
    def __init__(self, port=10021, data_port=10020):
        self.address = '0.0.0.0'
        self.port = port
        self.data_port = data_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.address, self.port))
        self.sock.listen(5)
        print(f'Server is up. Listening on {self.address}:{self.port}')

    def start(self):
        try:
            while True:
                client, client_address = self.sock.accept()
                print(f'Connection from {client_address} has been established.')
                ftp_thread = FTPThreadServer((client, client_address), self.address, self.data_port)
                ftp_thread.start()
        except KeyboardInterrupt:
            print('Server is shutting down...')
        finally:
            self.sock.close()

if __name__ == '__main__':
    port = input("Port - if left empty, default port is 10021: ")
    if not port:
        port = 10021

    data_port = input("Data port - if left empty, default port is 10020: ")
    if not data_port:
        data_port = 10020

    server = FTPserver(int(port), int(data_port))
    server.start()
