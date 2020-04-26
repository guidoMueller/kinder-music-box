import kivy
kivy.require('1.11.1') # replace with your current kivy version !

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import iconfonts

from os.path import join, dirname


import urllib
import urllib.request
import json
from time import sleep

import RPi.GPIO as GPIO
import sys
from mfrc522 import SimpleMFRC522


#Window.fullscreen = True
#for now, use a global for blink speed (better implementation TBD):
# Set up GPIO:
speed = 1.0
beepPin = 17
ledPin = 27
buttonPin = 22
flashLedPin = 10
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(beepPin, GPIO.OUT)
#GPIO.output(beepPin, GPIO.LOW)
#GPIO.setup(ledPin, GPIO.OUT)
#GPIO.output(ledPin, GPIO.LOW)
#GPIO.setup(flashLedPin, GPIO.OUT)
#GPIO.output(flashLedPin, GPIO.LOW)
#GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
iconfonts.register('default_font', join(dirname(__file__), 'fonts/fa-light-300.ttf'),
             join(dirname(__file__), 'font-awesome.fontd'))
# Define some helper functions:
defaultKeyCode = 0
reader = SimpleMFRC522()
trackImage = AsyncImage(source='https://dummyimage.com/300x400/000/fff.png&text=Track+image')
trackTitle = Label(text='')
trackAlbumTitle = Label(text='')
trackPlayPauseBtn = Button(size_hint=(None, None),size=(40,40),markup=True, text="%s"%(iconfonts.icon('fa-play', 32)))
currentTrackIsPlay=False
def updateImage():
    print("updateImage")
    global trackImage
    global trackTitle
    global trackAlbumTitle
    global trackPlayPauseBtn
    global currentTrackIsPlay
    url = 'https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/getCurrentSong/g.mueller@x-loco.de'
    result = json.load(urllib.request.urlopen(url))
    resultTrackImageUrl = result['item']['album']['images'][0]['url']
    print(resultTrackImageUrl)
    resultTrackTitle = result['item']['name']
    resultTrackAlbumTitle = result['item']['album']['name']
    resultTrackIsPlay = result['is_playing']
    trackImage.source = resultTrackImageUrl
    trackTitle.text = resultTrackTitle
    trackAlbumTitle.text = resultTrackAlbumTitle
    currentTrackIsPlay = resultTrackIsPlay
    if resultTrackIsPlay:
      trackPlayPauseBtn.unbind(on_press=playTrack)
      trackPlayPauseBtn.bind(on_press = pauseTrack)
      trackPlayPauseBtn.text="%s"%(iconfonts.icon('fa-pause', 32))
    else:
      trackPlayPauseBtn.unbind(on_press=pauseTrack)
      trackPlayPauseBtn.bind(on_press = playTrack)
      trackPlayPauseBtn.text="%s"%(iconfonts.icon('fa-play', 32))
def nextTrack(self):
    print("nextTrack")
    url = 'https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/nextTrack/g.mueller@x-loco.de'
    urllib.request.urlopen(url)
    sleep(1)
    updateImage()

def previousTrack(self):
    print("previousTrack")
    url = 'https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/previousTrack/g.mueller@x-loco.de'
    urllib.request.urlopen(url)
    sleep(0.5)
    updateImage()

def pauseTrack(self):
    print("pauseTrack")
    global trackPlayPauseBtn
    trackPlayPauseBtn.text="%s"%(iconfonts.icon('fa-play', 32))
    url = 'https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/pauseTrack/g.mueller@x-loco.de'
    urllib.request.urlopen(url)
    trackPlayPauseBtn.unbind(on_press=pauseTrack)
    trackPlayPauseBtn.bind(on_press=playTrack)
    sleep(1)
    updateImage()

def playTrack(self):
    print("playTrack")
    global trackPlayPauseBtn
    trackPlayPauseBtn.text="%s"%(iconfonts.icon('fa-pause', 32))
    url = 'https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/playTrack/g.mueller@x-loco.de'
    urllib.request.urlopen(url)
    trackPlayPauseBtn.unbind(on_press=playTrack)
    trackPlayPauseBtn.bind(on_press=pauseTrack)
    sleep(1)
    updateImage()

trackPlayPauseBtn.bind(on_press=playTrack)


class LabelKeyCode(Label):
    def update(self, dt):
        global defaultKeyCode
        id, text = reader.read_no_block()
        if id is not None and defaultKeyCode is not id:
            self.text = "ID: %s" % (id)
            defaultKeyCode = id
            req1 = urllib.request.Request('https://cf-baby-music-box.cfapps.eu10.hana.ondemand.com/playWithKey/g.mueller@x-loco.de/' + str(id))
            with urllib.request.urlopen(req1) as response1:
               the_page1 = response1.read()
               updateImage()
        #print("ID: %s\nText: %s" % (id,text))
        #self.text = "ID: %s" % (id)
class InputButton(Button):
    def update(self, dt):
        if GPIO.input(buttonPin) == True:
            self.state = 'normal'
        else:
            self.state = 'down'
            
class MyApp(App):
    def build(self):
        global trackImage
        global trackTitle
        global trackAlbumTitle
        global trackPlayPauseBtn
        # Set up the layout:
        layout = GridLayout(cols=1, spacing=0, padding=0, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        header = GridLayout(cols=1, spacing=0, padding=0)
        headerTitle = Label(text="Kinder Musik Box")
        
        header.add_widget(headerTitle)
        headerBar = BoxLayout()
        headerBarRight = RelativeLayout()
        headerBarRightIcons = BoxLayout(size_hint=(None, None),
                                        size=(100, 15),
                                        spacing=10,
                         pos_hint ={'right':1, 'top':1})
        volumeIcon = Label(size_hint=(None, None),
                         size=(20, 25),
                         markup=True,
                         text="%s"%(iconfonts.icon('fa-volume', 15)))
        wlanIcon = Label(size_hint=(None, None),
                        size=(20, 25),
                         markup=True,
                         text="%s"%(iconfonts.icon('fa-wifi', 15)))
        akkuIcon = Label(size_hint=(None, None),
                         size=(20, 25),
                         markup=True,
                         text="%s"%(iconfonts.icon('fa-battery-half', 15)))

        headerBarRightIcons.add_widget(volumeIcon)
        headerBarRightIcons.add_widget(wlanIcon)
        headerBarRightIcons.add_widget(akkuIcon)
        headerBarRight.add_widget(headerBarRightIcons)
        
        
        headerBar.add_widget(headerBarRight)
        header.add_widget(headerBar)
            
            
        
        
        layout.add_widget(header)
        
        layoutTagInfo = GridLayout(cols=2, spacing=0, padding=0, row_default_height=50)
    
        tagInfos = GridLayout(cols=2, spacing=0, padding=0, row_default_height=100)
        tagLabel = Label(text="Kinder Musik Box")
        
        layoutTagInfo.add_widget(tagLabel)
        tagCode = LabelKeyCode(text="")
        Clock.schedule_interval(tagCode.update, 0.0)
        layoutTagInfo.add_widget(tagCode)
        
        layout.add_widget(tagInfos)
        
        layoutMain = GridLayout(cols=2, spacing=30, padding=30, row_default_height=200)
        layoutMain.add_widget(trackImage)
        
        layoutMainRight = GridLayout(cols=1, spacing=30, padding=30)
        
        layoutMainRightSongInfos = GridLayout(cols=2, spacing=30, padding=30)
        layoutMainRightSongInfos.add_widget(Label(text="Songtitle"))
        layoutMainRightSongInfos.add_widget(trackTitle)
        layoutMainRightSongInfos.add_widget(Label(text="Albumname"))
        layoutMainRightSongInfos.add_widget(trackAlbumTitle)
        
        layoutMainRight.add_widget(layoutMainRightSongInfos)
        
        
        layoutMainRightSongControl = GridLayout(cols=3, spacing=30, padding=30)
        
        nextTrackBtn = Button(size_hint=(None, None),size=(40,40),markup=True, text="%s"%(iconfonts.icon('fa-forward', 32)))
        nextTrackBtn.bind(on_press=nextTrack)
        
        previousTrackBtn = Button(size_hint=(None, None),size=(40,40),markup=True, text="%s"%(iconfonts.icon('fa-backward', 32)))
        previousTrackBtn.bind(on_press=previousTrack)
        
        layoutMainRightSongControl.add_widget(previousTrackBtn)
        layoutMainRightSongControl.add_widget(trackPlayPauseBtn)
        layoutMainRightSongControl.add_widget(nextTrackBtn)
        
        layoutMainRight.add_widget(layoutMainRightSongControl)
        
        layoutMainRightSongControlVol = GridLayout(cols=1)
        
        speedSlider = Slider(min=1, max=30, value=speed)
        #speedSlider.bind(on_touch_down=update_speed, on_touch_move=update_speed)
        layoutMainRightSongControlVol.add_widget(speedSlider)
        #layoutMainRight.add_widget(layoutMainRightSongControlVol)
        
        
        layoutMain.add_widget(layoutMainRight)
        layout.add_widget(layoutTagInfo)
        layout.add_widget(layoutMain)
        # Start flashing the LED
        #Clock.schedule_once(flash, 1.0/speed)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        # Make the background gray:
        with root.canvas.before:
            Color(.2,.2,.2,1)
        root.add_widget(layout)
        
        updateImage()
        return root
         

if __name__ == '__main__':
    MyApp().run()