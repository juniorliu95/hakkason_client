'''
Shuffled Camera Feed Puzzle
===========================

This demonstrates using Scatter widgets with a live camera.
You should see a shuffled grid of rectangles that make up the
camera feed. You can drag the squares around to see the
unscrambled camera feed or double click to scramble the grid
again.
'''

import time
import os
from random import randint, random
from functools import partial

from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

import cv2
import numpy as np

import socket_client

class socket_client_module:
    def __init__(self):
        self.received = []
        # Get information for sockets client
        self.port = 6007
        # ip = '127.0.0.1'
        self.ip = '192.168.1.100'
        self.username = 'ljy'

    def show_error(self, message):
        print(message)

    def connect(self, image):
        if not socket_client.connect(self.ip, self.port, self.username, self.show_error):
            return
        socket_client.send(image)
        socket_client.start_listening(self.incoming_message, self.show_error)

    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username
        self.received.append(message)
        return username


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.


# Declare both screens
class ImageScreen(Screen):
    def __init__(self, name):
        self.screen = Screen(name=name)
        self.root = BoxLayout(orientation='vertical')
        self.img = Camera(resolution=(1000, 1000), play=True, size_hint=(1, 1))
        self.root.add_widget(self.img)

        w1 = Widget(size_hint=(.3, 1))
        w2 = Widget(size_hint=(.3, 1))
        self.btn = Button(text='Caption!', size_hint=(.4, 1))
        r2 = BoxLayout(size_hint=(1, .1))
        r2.add_widget(w1)
        r2.add_widget(self.btn)
        r2.add_widget(w2)
        self.root.add_widget(r2)
        self.screen.add_widget(self.root)

    
class VideoScreen(Screen):
    def __init__(self, name):
        self.screen = Screen(name=name)
        self.root = BoxLayout(orientation='vertical')
        self.video = Video(source='./nq.mp4',  state='play', options={'allow_stretch': True, 'eos':'loop'}, size_hint=(1, 1))
        self.root.add_widget(self.video)

        w1 = Widget(size_hint=(.3, 1))
        w2 = Widget(size_hint=(.3, 1))
        self.btn = Button(text='Close', size_hint=(.4, 1))

        r2 = BoxLayout(size_hint=(1, .1))
        r2.add_widget(w1)
        r2.add_widget(self.btn)
        r2.add_widget(w2)
        self.root.add_widget(r2)
        self.screen.add_widget(self.root)

    
class CoolApp(App):
    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
        self.im_sc = ImageScreen(name='image')
        self.vi_sc = VideoScreen(name='video')
        self.sm.add_widget(self.im_sc.screen)
        self.sm.add_widget(self.vi_sc.screen)

        self.video = self.vi_sc.video

        self.capturebutton = self.im_sc.btn
        self.capturebutton.bind(on_press=self.im_callback)

        self.videobutton = self.vi_sc.btn
        self.videobutton.bind(on_press=self.vi_callback)

        return self.sm

    def vi_callback(self, instance):
        self.im_sc.btn.text = 'Capture!'
        # self.video.source = 'nq2.mp4'
        # self.video.unload()
        self.sm.current = 'image'

    def im_callback(self, instance):
        self.capturebutton.text = 'Loading...'
        scm = socket_client_module()
        timestr = time.strftime("%Y%m%d_%H%M%S")
        if not os.path.exists('./images'):
            os.makedirs('./images')
        if not os.path.exists('./videos'):
            os.makedirs('./videos')
        image_path = "./images/IMG_{}.png".format(timestr)
        video_path = "./videos/V_{}.mp4".format(timestr)
        self.im_sc.img.export_to_png(image_path)
        print("Captured!")

        img = cv2.imread(image_path)
        result, imgencode = cv2.imencode('.jpg', img)
        data = np.array(imgencode)
        stringData = data.tostring()

        scm.connect(stringData)
        while not len(scm.received):
            socket_client.send('hello')

        # deal with videos
        with open(video_path, 'wb') as f:
            f.write(scm.received[0])
        scm.received = []
        
        socket_client.client_socket.close()

        print('**********')
        self.sm.current = 'video'
        self.video.source = video_path
        print(self.video.source)
        


if __name__ == '__main__':
    cool_app = CoolApp()
    cool_app.run()


# class take_pic:
#     def __init__(self, resolution=(1000, 1000), play=True, size_hint=(1, 1)):
#         # root = Widget()
#         self.root = BoxLayout(orientation='vertical')
#         img = Camera(resolution=resolution, play=play, size_hint=size_hint)
#         self.root.add_widget(img)

#         def callback(instance):
#             timestr = time.strftime("%Y%m%d_%H%M%S")
#             # img.export_to_png("IMG_{}.png".format(timestr))
#             self.root.clear_widgets()
#             print("Captured!")
#             show_video('./nq.mp4').get_widget()

#         w1 = Widget(size_hint=(.3, 1))
#         w2 = Widget(size_hint=(.3, 1))
#         btn = Button(text='Caption!', size_hint=(.4, 1))
#         btn.bind(on_press=callback)
#         r2 = BoxLayout(size_hint=(1, .1))
#         r2.add_widget(w1)
#         r2.add_widget(btn)
#         r2.add_widget(w2)
#         self.root.add_widget(r2)

#     def get_widget(self):
#         return self.root


# class show_video:
#     def __init__(self, source):
#         self.root = BoxLayout(orientation='vertical')

#         video = Video(source=source,  state='play', options={'allow_stretch': True}, size_hint=(1, 1))
        
#         self.root.add_widget(video)

#         def callback(instance):
#             self.root.clear_widgets()

#         w1 = Widget(size_hint=(.3, 1))
#         w2 = Widget(size_hint=(.3, 1))
#         btn = Button(text='Close', size_hint=(.4, 1))
#         btn.bind(on_press=callback)
#         r2 = BoxLayout(size_hint=(1, .1))
#         r2.add_widget(w1)
#         r2.add_widget(btn)
#         r2.add_widget(w2)
#         self.root.add_widget(r2)
    
#     def get_widget(self):
#         return self.root

# class CoolApp(App):
#     def build(self):
#         # root = Widget()
#         root = BoxLayout(orientation='vertical')
#         img = take_pic(resolution=(1000, 1000), play=True, size_hint=(1, 1)).get_widget()
#         root.add_widget(img)

#         # root.add_widget(slider)
#         return root

    # def on_value(self, puzzle, instance, value):
    #     value = int((value + 5) / 10) * 10
    #     puzzle.blocksize = value
    #     instance.value = value


CoolApp().run()
