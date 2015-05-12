#!/usr/bin/env python

SEND_DELAY                      = 1
CID                             = "CID71"
SMOKE_BEFORE_SECOND_ALARM_TIME  = 120

import sys, json, time
from twisted.internet import task
from twisted.internet import reactor

from cbcommslib import CbApp
from cbconfig import *

from kitchenminder.cb import CbKitchenMinder

class Client():
    def __init__(self, aid):
        self.aid = aid
        self.count = 0
        self.messages = []

    def send(self, data):
        message = {
                   "source": self.aid,
                   "destination": CID,
                   "body": data
                  }
        message["body"]["n"] = self.count
        self.count += 1
        self.messages.append(message)
        self.sendMessage(message, "conc")
        self.cbLog("debug", "client sending: " + json.dumps(message, indent=4))

    def receive(self, message):
        #self.cbLog("debug", "Message from client: " + str(message))
        if "body" in message:
            if "n" in message["body"]:
                #self.cbLog("debug", "Received ack from client: " + str(message["body"]["n"]))
                for m in self.messages:
                    if m["body"]["n"] == m:
                        self.messages.remove(m)
                        self.cbLog("debug", "Removed message " + str(m) + " from queue")
        else:
            self.cbLog("warning", "Received message from client with no body")

class DataManager:
    """ Managers data storage for all sensors """
    def __init__(self, bridge_id):
        self.bridge_id = bridge_id
        self.baseAddress = bridge_id + "/"
        self.s = []
        self.waiting = False
        self.smokeTime = 0
        self.noSmokeTime = 0

    def sendValues(self):
        msg = {"m": "data",
               "d": self.s
               }
        self.cbLog("debug", "sendValues. Sending: " + str(msg))
        self.client.send(msg)
        self.s = []
        self.waiting = False

    def storeValues(self, values):
        self.s.append(values)
        if not self.waiting:
            self.waiting = True
            reactor.callLater(SEND_DELAY, self.sendValues)

    events = ['Boot', 'Smoke', 'NoSmoke', 'SwitchPressed',
              'Connected', 'NotConnected', 'Movement']

    def storeEvent(self, timeStamp, event):
        self.cbLog("debug", "storeEvent dbug 1: " + event)
        assert event in DataManager.events
        values = {"name": self.baseAddress + "km/" + event,
                  "points": [[int(timeStamp*1000), 1]]
                 }
        self.storeValues(values)
        now = time.time()
        if event == "Smoke":
            if now - self.smokeTime > SMOKE_BEFORE_SECOND_ALARM_TIME:
                self.smokeTime = now
                alarm = {"m": "alarm",
                         "a": "Smoke detected by Kitchen Minder " + self.bridge_id
                        }
                self.client.send(alarm)
        if event == "NoSmoke":
            if now - self.noSmokeTime > SMOKE_BEFORE_SECOND_ALARM_TIME:
                self.noSmokeTime = now
                alarm = {"m": "alarm",
                         "a": "Kitchen minder " + self.bridge_id + ". Smoke cleared"
                        }
                self.client.send(alarm)

    def storeBattery(self, timeStamp, v):
        values = {"name": self.baseAddress + "km/" + "battery",
                  "points": [[int(timeStamp*1000), v]]
                 }
        self.storeValues(values)

class App(CbApp):
    def __init__(self, argv):
        self.smokeId = None
        self.switchId = None
        self.gpioId = None
        self.smokeConnected = True
        self.switchConnected = True
        self.km = None
        self.dm = None
        CbApp.__init__(self, argv)

    # Local helper functions
    def _setState(self, action):
        self.state = action
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def _parseServices(self, msg):
        services = {}
        for s in msg['service']:
            services[s['characteristic']] = s
        return (services, self._getId(msg))

    def _requestData(self, serviceid, services, intervals):
        if serviceid == None:
            self.cbLog("debug", "requestData, serviceid not set")
            return
        self.cbLog("debug", "<----- requestData: " + str(services) + " @ " + str(intervals))
        sreqs = []
        assert len(services) == len(intervals)
        for s, i in zip(services, intervals):
            sreqs.append({'characteristic': s, 'interval': i})
        req = {'id': self.id, 'request': 'service', 'service': sreqs}
        self.cbLog("debug", "requestData sending: " + json.dumps(req, indent=4))
        self.sendMessage(req, serviceid)

    def _getId(self, msg):
        return msg['id']

    def _getTS(self, msg):
        return msg['timeStamp']

    def _getData(self, msg, characteristic):
        if msg['characteristic'] == characteristic:
            return msg['data']
        else:
            return None

    def _sendData(self, serviceid, data):
        if serviceid == None:
            self.cbLog("debug", "sendData, serviceid not set")
            return
        self.cbLog("debug", "-----> sendData: " + str(data))
        cmd = {'id': self.id, 'request': 'command', 'data': data}
        self.sendMessage(cmd, serviceid)

    # Functions called automagically by CB framework
    def onAdaptorService(self, msg):
        self.cbLog("debug", "Service msg: " + str(msg))
        (services, serviceid) = self._parseServices(msg)
        self.cbLog("debug", "Service Id: " + str(serviceid) + " " + str(services))
        if services.has_key('binary_sensor'):
            if services.has_key('switch'):
                self.switchId = serviceid
                self._requestData(serviceid, ['connected'], [0])
                self.cbLog("debug", "SWITCH FOUND: " + str(self.switchId))
            elif not services.has_key("gpio"):
                self.smokeId = serviceid
                self._requestData(serviceid, ['binary_sensor', 'battery', 'connected'], [0, 0, 0])
                self.cbLog("debug", "SMOKE DETECTOR FOUND: " + str(self.smokeId))
        if services.has_key('gpio'):
            self.gpioId = serviceid
            self._requestData(serviceid, ['gpio'], [0])
            self.cbLog("debug", "GPIO FOUND: " + str(self.gpioId))
        #if self.smokeId != None and self.switchId != None and self.gpioId != None:
        if True:
            self.km = CbKitchenMinder(self)
            t = task.LoopingCall(self.km.update)
            t.start(1.0)
            self._setState('running')
            self.cbLog("debug", " -------Started KM---------")

    def onAdaptorData(self, msg):
        self.cbLog("debug", "onAdaptorData,  message: " + str(msg))
        event = "Smoke"
        if self.km:
            event = None
            if self._getId(msg) == self.smokeId:
                timeStamp = self._getTS(msg)
                sensor = self._getData(msg, 'binary_sensor')
                if sensor != None:
                    if sensor == 'on':
                        event = 'Smoke'
                    else:
                        event = 'NoSmoke'
                    self.km.addEvent(event)
                    self.dm.storeEvent(timeStamp, event)
                level = self._getData(msg, 'battery')
                if level != None:
                    self.dm.storeBattery(timeStamp, level)
                connected = self._getData(msg, 'connected')
                if connected != None:
                    changed = (self.smokeConnected != connected)
                    self.smokeConnected = connected
                    if changed:
                        if self.smokeConnected and self.switchConnected:
                            event = 'Connected'
                        else:
                            event = 'NotConnected'
                        self.km.addEvent(event)
                        self.dm.storeEvent(timeStamp, event)
            elif self._getId(msg) == self.switchId:
                timeStamp = self._getTS(msg)
                connected = self._getData(msg, 'connected')
                if connected != None:
                    changed = (self.switchConnected != connected)
                    self.switchConnected = connected
                    if changed:
                        if self.smokeConnected and self.switchConnected:
                            event = 'Connected'
                        else:
                            event = 'NotConnected'
                        self.km.addEvent(event)
                        self.dm.storeEvent(timeStamp, event)
            elif self._getId(msg) == self.gpioId:
                timeStamp = self._getTS(msg)
                gpio = self._getData(msg, 'gpio')
                if gpio != None:
                    if gpio == 'button':
                        event = 'SwitchPressed'
                    elif self._getData(msg, 'gpio') == 'movement':
                        event = 'Movement'
                    assert event != None
                    self.km.addEvent(event)
                    self.dm.storeEvent(timeStamp, event)
            else:
                self.cbLog("debug", "Unhandled data: " + str(msg))

    def onConfigureMessage(self, config):
        self.cbLog("debug", "onConfigureMessage, config: " + str(config))
        self.client = Client(self.id)
        self.client.sendMessage = self.sendMessage
        self.client.cbLog = self.cbLog
        self.dm = DataManager(self.bridge_id)
        self.dm.cbLog = self.cbLog
        self.dm.client = self.client
        self.dm.storeEvent(time.time(), 'Boot')

App(sys.argv)
