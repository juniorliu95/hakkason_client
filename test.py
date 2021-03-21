# test the socket client

import time
import socket_client
import cv2
import numpy as np


received = []

def show_error(message):
    print(message)

def connect(image):

    # Get information for sockets client
    port = 6007
    # ip = '127.0.0.1'
    ip = '192.168.1.100'
    username = 'nq' 
    

    if not socket_client.connect(ip, port, username, show_error):
        return
    socket_client.send(image)

    socket_client.start_listening(incoming_message, show_error)


def incoming_message(username, message):
    # Update chat history with username and message, green color for username
    received.append(message)
    return username


if __name__ == "__main__":
    img = cv2.imread('./office.jpg')
    # encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    result, imgencode = cv2.imencode('.jpg', img)
    data = np.array(imgencode)
    stringData = data.tostring()

    connect(stringData)
    while not len(received):
        socket_client.send('hello')

    # deal with videos
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
    with open('videos/{}.mp4'.format(current_time), 'wb') as f:
        f.write(received[0])
    print('Done...')
    