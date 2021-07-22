import machine
from machine import I2C, ADC, Pin
from dht import DHT

import pycom
import time
import json
import sys
from bmp085 import BMP180
from network import WLAN
import os

from umqtt import MQTTClient


def connect_to_wlan():
    print("Connect to WLAN")

    wlan = WLAN(mode=WLAN.STA)
    #print(wlan.scan())
    nets = wlan.scan()
    for net in nets:
        if net.ssid == '<your-SSID>':
            print('Network found!')
            wlan.connect(ssid='<your-SSID>', auth=(WLAN.WPA2, '<your-wifi-key>'))
            while not wlan.isconnected():
                machine.idle()

            print(wlan.ifconfig())
            print("WiFi connected succesfully")

def setRTCLocalTime():
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")
    time.sleep_ms(1500)
    print('RTC Set from NTP to UTC:', rtc.now())
    time.timezone(7200)
    print('Adjusted from UTC to EST timezone', time.localtime(), '\n')

def connect_to_mqtt():

    try:
        client = MQTTClient("<your-lopy4-devicename>", "<your-mqtt-IP-address>",user="<your-mqtt-userid>", password="<your-mqtt-password>", port=1883)
        #client.set_callback(mqtt_cb)
        client.connect()
    except:
        print("Unexpected error:", sys.exc_info()[0])
    #client.subscribe(topic="youraccount/feeds/lights")
    return client

def mqtt_cb(topic, msg):
   print(topic, msg)


def humid_temp_sensor():
    th = DHT('P11', 0)
    time.sleep(5)
    #while read:
    x = 0
    result = th.read()

    # Try 50 times. Quit if not successful.
    while not result.is_valid():
        x += 1
        print(result.is_valid())
        time.sleep(.5)
        if x > 50:
            break
        result = th.read()
    temperature = result.temperature
    humidity = result.humidity

    return (temperature, humidity)

def get_pressure():
    i2c=I2C(0)
    i2c.init(I2C.MASTER, pins=('P6','P7'),baudrate=48000)

    bmp180 = BMP180(i2c)
    bmp180.baseline = 101325

    temp = bmp180.temperature
    p = bmp180.pressure
    altitude = bmp180.altitude
    #print(temp, p, altitude)
    return(temp, p, altitude)


pycom.heartbeat(True)
print("Temp, pressure and humidity check, v0.9, 2021-07-22 By: Mats Pettersson")

connect_to_wlan()
setRTCLocalTime()

while True:
    t1 = time.localtime()
    sensortime = str(t1[0]) + " " + str(t1[1]) + " " + str(t1[2]) + " " + str(t1[3]) + " " + str(t1[4]) + " " + str(t1[5])

    temperature, humidity = humid_temp_sensor()
    bmp180_t, bmp180_p, bmp180_a = get_pressure()
    soilhumidity = getsoilhumidity()

    jsondict = {}
    jsondict['outsidetemp'] = temperature  #strtemp
    jsondict['outsidehumidity'] = humidity #strhumidity
    jsondict['airpressure'] = bmp180_p
    jsondict['sensortime'] = sensortime
    jsondict['device'] = "MatsLopy4"
    js = str(json.dumps(jsondict))

    print(js)
    client = connect_to_mqtt()
    client.publish(topic = "mats/test", msg = js )
    client.disconnect()

    time.sleep(5)

wlan.disconnect()
print("Finished...")
