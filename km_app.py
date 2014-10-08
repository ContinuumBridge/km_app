#!/usr/bin/env python

ModuleName = "km_app"

import sys, logging, requests, json, time
from twisted.internet import task
from twisted.internet import reactor

from cbcommslib import CbApp
from cbconfig import *

from kitchenminder.cb import CbKitchenMinder

class DataManager:
    """ Managers data storage for all sensors """
    def __init__(self, bridgeId):
        self.baseurl = "http://geras.1248.io/series/" + bridgeId + "/"
        self.user = "ea2f0e06ff8123b7f46f77a3a451731a"
        self.delay = 20 # Time to gather values for a device before sending them
        self.s = {}
        self.waiting = []

    def sendValuesThread(self, values, deviceId):
        url = self.baseurl + deviceId
        status = 0
        logging.debug("===> Geras, device: %s : %s", deviceId, str(values))
        headers = {'Content-Type': 'application/json'}
        try:
            r = requests.post(url, auth=(self.user, ''),
                              data=json.dumps({"e": values}), headers=headers)
            status = r.status_code
            success = True
        except:
            success = False
        if status !=200 or not success:
            logging.debug("%s sendValues failed, status: %s", ModuleName, status)
            # On error, store the values that weren't sent ready to be sent again
            reactor.callFromThread(self.storeValues, values, deviceId)

    def sendValues(self, deviceId):
        values = self.s[deviceId]
        # Call in thread as it may take a second or two
        self.waiting.remove(deviceId)
        del self.s[deviceId]
        reactor.callInThread(self.sendValuesThread, values, deviceId)

    def storeValues(self, values, deviceId):
        if not deviceId in self.s:
            self.s[deviceId] = values
        else:
            self.s[deviceId].append(values)
        if not deviceId in self.waiting:
            reactor.callLater(self.delay, self.sendValues, deviceId)
            self.waiting.append(deviceId)

    events = ['Boot', 'Smoke', 'NoSmoke', 'SwitchPressed',
              'Connected', 'NotConnected', 'Movement']

    def storeEvent(self, timeStamp, event):
        logging.debug("--->Geras event: %s %s", timeStamp, event)
        assert event in DataManager.events
        values = [{"n":"event", "v":DataManager.events.index(event), "t":timeStamp}]
        self.storeValues(values, 'KM')

    def storeBattery(self, timeStamp, level):
        logging.debug("--->Geras battery: %s %s", timeStamp, level)
        values = [{"n":"level", "v":level, "t":timeStamp}]
        self.storeValues(values, 'Battery')

class App(CbApp):
    def __init__(self, argv):
        logging.basicConfig(filename=CB_LOGFILE,level=CB_LOGGING_LEVEL,format='%(asctime)s %(message)s')
        logging.debug("-------Started App---------")
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
            logging.debug("%s requestData, serviceid not set", ModuleName)
            return
        logging.debug("<----- %s requestData: %s @ %s", ModuleName, str(services),
                      str(intervals))
        sreqs = []
        assert len(services) == len(intervals)
        for s, i in zip(services, intervals):
            sreqs.append({'characteristic': s, 'interval': i})
        req = {'id': self.id, 'request': 'service', 'service': sreqs}
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
            logging.debug("%s sendData, serviceid not set", ModuleName)
            return
        logging.debug("-----> %s sendData: %s", ModuleName, data)
        cmd = {'id': self.id, 'request': 'command', 'data': data}
        self.sendMessage(cmd, serviceid)

    # Functions called automagically by CB framework
    def onAdaptorService(self, msg):
        logging.debug("%s Service msg: %s", ModuleName, msg)
        (services, serviceid) = self._parseServices(msg)
        logging.debug("Service Id:%s %s", str(serviceid), str(services))
        if services.has_key('binary_sensor'):
            if services.has_key('switch'):
                self.switchId = serviceid
                self._requestData(serviceid, ['connected'], [0])
                logging.debug("SWITCH FOUND %s", str(self.switchId))
            else:
                self.smokeId = serviceid
                self._requestData(serviceid, ['binary_sensor', 'battery', 'connected'], [0, 0, 0])
                logging.debug("SMOKE DETECTOR FOUND %s", str(self.smokeId))
        if services.has_key('gpio'):
            self.gpioId = serviceid
            self._requestData(serviceid, ['gpio'], [0])
            logging.debug("GPIO FOUND %s", str(self.gpioId))
        if self.smokeId != None and self.switchId != None and self.gpioId != None:
            self.km = CbKitchenMinder(self)
            t = task.LoopingCall(self.km.update)
            t.start(1.0)
            self._setState('running')
            logging.debug("-------Started KM---------")

    def onAdaptorData(self, msg):
        if self.km:
            logging.debug("%s Data %s message: %s", ModuleName, self.id, str(msg))
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
                logging.debug("Unhandled data:%s", str(msg))

    def onConfigureMessage(self, config):
        logging.debug("%s onConfigureMessage, config: %s", ModuleName, config)
        self.dm = DataManager(self.bridge_id)
        self.dm.storeEvent(str(time.time()), 'Boot')

App(sys.argv)
