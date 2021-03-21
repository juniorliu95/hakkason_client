import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.video import Video
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        self.box = BoxLayout(orientation='vertical')

        self.video = Video(source='nq.mp4')
        self.video.state='play'
        self.video.options = {'eos': 'loop'}
        self.video.allow_stretch=True
        self.box.add_widget(self.video)

        but = Button(text='Caption!', size_hint=(.4, 1))
        but.bind(on_press=self.callback)
        self.box.add_widget(but)

        return self.box

    def callback(self, instance):
        self.video.source = 'nq2.mp4'

if __name__ == '__main__':
    MyApp().run()