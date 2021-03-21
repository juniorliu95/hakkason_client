import socket
import errno
from threading import Thread


class socket_client:
    def __init__(self):
        self.HEADER_LENGTH = 10
        self.client_socket = None
        self.received = []


    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf


    # Connects to the server
    def connect(self, ip, port, my_username, error_callback):
        # Create a socket
        # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to a given ip and port
            self.client_socket.connect((ip, port))
        except Exception as e:
            # Connection error
            error_callback('Connection error: {}'.format(str(e)))
            return False

        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
        username = my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username)

        return True

    # Sends a message to the server
    def send(self, message):
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        if type(message) != bytes:
            message = message.encode('utf-8')
        message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(message_header + message)

    # Starts listening function in a thread
    # incoming_message_callback - callback to be called when new message arrives
    # error_callback - callback to be called on error
    def start_listening(self, incoming_message_callback, error_callback):
        thread = Thread(target=self.listen, args=(incoming_message_callback, error_callback), daemon=True)
        thread.start()
        return thread

    # Listens for incomming messages
    def listen(self, incoming_message_callback, error_callback):
        while True:

            try:
                # Now we want to loop over received messages (there might be more than one) and print them
                while True:

                    # Receive our "header" containing username length, it's size is defined and constant
                    username_header = self.client_socket.recv(self.HEADER_LENGTH)

                    # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not len(username_header):
                        error_callback('Connection closed by the server')
                        
                    if self.received:
                        break

                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = self.client_socket.recv(username_length).decode('utf-8')

                    # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                    message_header = self.client_socket.recv(self.HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    if message_length < 100:
                        message = self.client_socket.recv(message_length).decode('utf-8')
                    else: # videos
                        message = self.recvall(self.client_socket, message_length)
                        # from datetime import datetime
                        # now = datetime.now()
                        # current_time = now.strftime("%d_%m_%Y_%H_%M_%S")

                    # Print message
                    incoming_message_callback(username, message)

                    # send message
                    self.send('hell0!')
                break

            except Exception as e:
                # Any other exception - something happened, exit
                error_callback('Reading error: {}'.format(str(e)))