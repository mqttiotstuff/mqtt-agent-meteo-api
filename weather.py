#
# Mqttagent that grab the current weather, every 3 hours, with wind, humidity
#

import paho.mqtt.client as mqtt
import time
import configparser
import os.path

import traceback

config = configparser.RawConfigParser()

import socket
hostname = socket.gethostname()

METRICS_WEATHER="home/agents/weather"


#############################################################
## MAIN

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")
api_key = config.get("weather","api_key")

client2 = mqtt.Client()

# client2 is used to send events to wifi connection in the house 
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)

client = mqtt.Client();
client.username_pw_set(username, password)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected")

latesttime = None
cpt = 0

def on_message(client, userdata, msg):
   try:
      pass 
   except:
      traceback.print_exc();
 
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttbroker, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()
client.loop_start()

lastvalue = None

import shutil
import psutil

from pyowm import OWM

while True:
   try:


      owm = OWM(api_key)
      mgr = owm.weather_manager()


      observation = mgr.weather_at_place('Lyon,FR')
      w = observation.weather

      #w.detailed_status         # 'clouds'
      #w.wind()                  # {'speed': 4.6, 'deg': 330}
      #w.humidity                # 87
      #w.temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
      #w.rain                    # {}
      #w.heat_index              # None
      #w.clouds                  # 75
    
      wind = w.wind()
      temperature = w.temperature("celsius")
      client2.publish(METRICS_WEATHER + "/observation_time", "" + time.strftime("%a, %d %b %Y %H:%M:%S ", time.localtime()), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/wind/speed", str(wind["speed"]), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/wind/deg", str(wind["deg"]), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/wind/gust", str(wind["gust"]), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/humidity", str(w.humidity), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/temperature", str(temperature['temp']), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/temperature/min", str(temperature['temp_min']), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/temperature/max", str(temperature['temp_max']), qos=1,retain=True)
      client2.publish(METRICS_WEATHER + "/temperature/feeds_like", str(temperature['feels_like']), qos=1,retain=True)



   except Exception:
        traceback.print_exc()


   # every 2 hours
   time.sleep(2 * 60 * 60)

