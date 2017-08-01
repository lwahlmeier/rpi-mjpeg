#!/usr/bin/env python
import argparse, sys
from time import sleep
import time
from picamera import PiCamera
import threadly
import litesockets
from io import BytesIO
import logging

if sys.version_info < (3,):
  def b(x):
    return x
else:
  import codecs
  def b(x):
    return codecs.latin_1_encode(x)[0]


GLOBALHEADER = "--IPCAMDATA\r\nContent-Type: image/jpeg\r\nContent-Length: {}\r\n\r\n"

HTML="""<html>
<head>
<title>Mjpeg camera</title>
</head>
<body>
<img src="stream/"/>
</body>
</html>
"""

class MjpegServer():

  def __init__(self, ip, port, hflip=False, vflip=False, delayMS=50):
    self.__camera = PiCamera(framerate=30)
    self.__delay = delayMS
#    self.__camera.resolution= (1920,1080)
#    self.__camera.resolution= (1280,720)
    self.__camera.resolution= (853,480)
    self.__camera.vflip = vflip
    self.__camera.hflip = hflip
    self.__camera.exposure_mode = 'auto'
    self.__pool = threadly.Scheduler(5)
    self.__SE = litesockets.SocketExecuter(scheduler=self.__pool)
    self.__server = self.__SE.createTCPServer(ip, port)
    self.__clients = {}
    self.__good = []
    self.__log = logging.getLogger("MjpegServer:{}:{}".format(ip, port))
    self.__server.setOnClient(self.__acceptor)
    self.__server.start()
    self.__log.info("New MjpegServer started! "+str(self.__delay))

  def __runit(self):
    if len(self.__good) == 0:
      return
    global GLOBALHEADER
    bio=BytesIO()
    self.__camera.capture(bio, 'jpeg', use_video_port=True, quality=35)
    h = b(GLOBALHEADER.format(len(bio.getvalue()))) + bio.getvalue()
    for c in self.__good:
      if not c.isClosed() and c.getWriteBufferSize() == 0:
        try:
          c.write(h)
        except:
          pass
      else:
        pass
        #print "skip"
    if len(self.__good) != 0:
      self.__pool.schedule(self.__runit, delay=self.__delay, key="CAMERA")
  
  def __acceptor(self, client):
    client.setReader(self.__reader)
    client.addCloseListener(self.__closer)
    self.__clients[client] = b""
    self.__log.info("New Client added:{}".format(client))

  def __reader(self, client):
    global HTML
    self.__clients[client]+=client.getRead()
    if self.__clients[client].find(b"\r\n\r\n") != -1:
      st = self.__clients[client].split(b"\r\n")
      r = st[0].split(b" ")
      if r[0].strip() == b"GET":
        if r[1].strip()[:7]==b"/stream":
          self.__log.info("Client sent http headers, starting stream:{}".format(client))
          client.write("HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace;boundary=--IPCAMDATA\r\nConnection: close\r\n\r\n")
          tmp = len(self.__good)
          self.__good.append(client)
          if tmp == 0:
            self.__pool.schedule(self.__runit, key="CAMERA")
        elif r[1].strip()[:7]==b"/right":
          rightIO()
          client.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\nContent-Length: {}\r\n\r\n{}".format(0, ""))
        elif r[1].strip()[:7]==b"/left":
          leftIO()
          client.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\nContent-Length: {}\r\n\r\n{}".format(0, ""))
        elif r[1].strip()[:7]==b"/center":
          centerIO()
          client.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\nContent-Length: {}\r\n\r\n{}".format(0, ""))
        elif r[1].strip() == b"/":
          self.__log.info("Client sent http headers, starting stream:{}".format(client))
          client.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\nContent-Length: {}\r\n\r\n{}".format(len(HTML), HTML))
        else:
          self.__log.info("Closing Client:{} {}".format(client, st[0]))
          client.close()
    elif len(self.__clients[client]) > 50000:
      self.__log.info("Closing Client:{} to much data!".format(client))
      client.close()

  def __closer(self, client):
    del self.__clients[client]
    try:
      self.__good.remove(client)
    except:
      pass

  def __scloser(self, server):
    for c in self.__clients:
      c.close()

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="port to use", type=int)
parser.add_argument("--ip", help="ip address to listen on", type=str, default="0.0.0.0")
parser.add_argument("--delay", help="delay in ms between frames", type=int, default=50)
parser.add_argument("--vflip", help="flip image vertically", action="store_true")
parser.add_argument("--hflip", help="flip image horizontally", action="store_true")

ag = parser.parse_args(sys.argv[1:])

mjs = MjpegServer(ag.ip, ag.port, vflip=ag.vflip, hflip=ag.hflip, delayMS=ag.delay)

while True:
  time.sleep(10)
