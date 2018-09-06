import subprocess
import sys
import re
import json


def runCmd(cmd):
    #print "cmd: ", cmd
    output = subprocess.check_output(cmd, shell=True)
    #print "output: ", output
    return output

def getNextLine(text, startPos):
    # seek the end of this line
    endPos= text.find('\n', startPos)
    # get a line of config
    nextLine = text[startPos:endPos]
    return nextLine, endPos + 1

class readOpticsConfig:
    def __init__(self, card, numPorts):
        self.numPorts = numPorts
        self.card = card
        self.CtrlOpticsState = []
        self.CtrlOpticsSpeed = []
        self.CtrlOpticsFec   = []
        self.CtrlOpticsDiff  = []
        self.CtrlOpticsFreq = []

    def readConfigCtrlOptics(self):
        cmd = "nvgen -c -q if/act/Optics" + self.card.replace('/', '_') + \
                "_0_.*/"
        result = runCmd(cmd)

        for port in xrange(0, self.numPorts):
            searchStr = "controller Optics" + self.card + "/0/" + str(port)
            found = result.find(searchStr)
            # shouldn't occur, but seems to be occuring for both the
            # controllers. int hundredGE seems to behave differently
            # where the item itself isn't removed from config.
            # when we have a port-mode config though, it shows up.
            # Therefore, in this situation, assume the speed to be 100G 
            # and the controller to be "no shut".
            if found == -1:
                self.CtrlOpticsState.append('NOSHUT')
                self.CtrlOpticsSpeed.append(100)
                self.CtrlOpticsFec.append(15)
                self.CtrlOpticsDiff.append(0)
                self.CtrlOpticsFreq.append(1937000)
                #print searchStr + " State, speed: True, 100"
                continue

            # Populate with Defaults
            speed = 100
            state = 'NOSHUT'    # assume no shut
            fec   = 15
            diff  = 0
            frequency = 1937000

            # need to glean port-mode and ! (end of this config block)
            gleanedTwo = 0

            # gets the current line.
            config, nextPos = getNextLine(result, found)
            # another read gets the "next" line
            config, nextPos = getNextLine(result, nextPos)
            # print "config line, next: ", config, nextPos

            # end of config.
            while config != '!' and gleanedTwo < 2:
                if 'shutdown' in config:
                    state = 'SHUT'
                    gleanedTwo += 1
                    config, nextPos = getNextLine(result, nextPos)
                    # print "1. config line, len: ", config, nextPos
                    continue

                # if none of these three speeds, assume 100.
                if 'port-mode' in config:
                    if '100G' in config:
                        speed = 100
                    elif '150G' in config:
                        speed = 150
                    elif '200G' in config:
                        speed = 200

                    if '15percent' in config:
                        fec = 15
                    elif '25percent' in config:
                        fec = 25

                    if 'diff enable' in config:
                        diff = 1
                    elif 'diff disable' in config:
                        diff = 0

                    if 'dwdm-carrier' in config:
                        freq = config.lstrip().rstrip().split(' ')
                        frequency = int(freq[3])
                    gleanedTwo += 1

                # print "2. config line, len: ", config, nextPos
                config, nextPos = getNextLine(result, nextPos)

            self.CtrlOpticsState.append(state)
            self.CtrlOpticsSpeed.append(speed)
            self.CtrlOpticsFec.append(fec)
            self.CtrlOpticsDiff.append(diff)
            self.CtrlOpticsFreq.append(frequency)
            #print searchStr + " State, speed: ", state, speed

    def get_dict_port(self, port):
        ctrl_map = {}
        ctrl_map['state'] = self.CtrlOpticsState[port]
        ctrl_map['speed'] = self.CtrlOpticsSpeed[port]
        ctrl_map['fec'] = self.CtrlOpticsFec[port]
        ctrl_map['diff'] = self.CtrlOpticsDiff[port]
        ctrl_map['frequency'] = self.CtrlOpticsFreq[port]
        return ctrl_map

    def get_dict(self, port):
        config_map = {}
        port_num = -1
        tport = port.split('/')
        if(len(tport) > 3):
            port_num = int(tport[3])
        if port_num != -1:
            config_map['0'] = self.get_dict_port(port_num)
            return config_map

        for index in range(len(self.CtrlOpticsState)):
            config_map[str(index)] = self.get_dict_port(index)
        return config_map

"""
interface HundredGigE0/3/0/0/0 State:  False
interface HundredGigE0/3/0/1/0 State:  False
interface HundredGigE0/3/0/2/0 State:  False
interface HundredGigE0/3/0/3/0 State:  False
interface HundredGigE0/3/0/4/0 State:  False
interface HundredGigE0/3/0/5/0 State:  False
interface HundredGigE0/3/0/0/1 State:  False
interface HundredGigE0/3/0/1/1 State:  False
interface HundredGigE0/3/0/2/1 State:  False
interface HundredGigE0/3/0/3/1 State:  False
interface HundredGigE0/3/0/4/1 State:  False
interface HundredGigE0/3/0/5/1 State:  False
"""

class readGigEConfig:
    def __init__(self, card, numPorts):
        self.numPorts = 6
        self.card = card
        self.intfGEState = {}

    def readConfigIntfGE(self):
        cmd = "nvgen -c -q if/act/HundredGigE" + self.card.replace('/', '_') + \
                "_0_.*/"
        result = runCmd(cmd)

        for subport in [0, 1]:
            for port in xrange(0, self.numPorts):
                portStr = str(port) + "/" + str(subport)
                searchStr = "interface HundredGigE" + self.card + "/0/" + portStr
                found = result.find(searchStr)
                if found == -1:  # can occur depending on the traffic type
                    self.intfGEState[portStr] = 'SHUT'
                    #print searchStr + " State: ", False
                    continue

                # Populate with Defaults
                state = 'NOSHUT'    # assume no shut

                gleanedOne = 0
                config, nextPos = getNextLine(result, found)
                config, nextPos = getNextLine(result, nextPos)
                # print "1. config line, len, next: ", config, len(config), nextPos

                # end of config.
                while config != '!' and gleanedOne < 1:
                    if 'shutdown' in config:
                        state = 'SHUT'
                        gleanedOne += 1

                    config, nextPos = getNextLine(result, nextPos)
                    # print "2. config line, len, next: ", config, len(config), nextPos

                self.intfGEState[portStr] = state
                #print self.intfGEState
                #print searchStr + " State: ", state

    def get_dict_port(self, port_num):
        controller_map = {}
        port1 = str(port_num) + '/0'
        port1 = str(port_num) + '/1'
        controller_map['0'] = self.intfGEState[port1]
        controller_map['1'] = self.intfGEState[port1]
        return controller_map

    def get_dict(self, port):
        config_map = {}
        port_num = -1
        tport = port.split('/')
        if(len(tport) > 3):
            port_num = int(tport[3])

        if port_num != -1:
            config_map['0'] = self.get_dict_port(port_num)
            return config_map

        for index in range(self.numPorts):
            config_map[str(index)] = self.get_dict_port(index)
        return config_map

if len(sys.argv) < 3:
    exit(-1)

arg_card_name = sys.argv[2]
port = ''

if(len(sys.argv)) > 3:
    port = sys.argv[3]

card_name = arg_card_name.lower()
tcard = card_name.split('/cpu0')
card = tcard[0]
numPorts = 6

if(sys.argv[1].find('Optics')) != -1:
    optics = readOpticsConfig(card, numPorts)
    optics.readConfigCtrlOptics()
    print json.dumps(optics.get_dict(port))

if(sys.argv[1].find('HundredGigE')) != -1:
    gige = readGigEConfig(card, numPorts)
    gige.readConfigIntfGE()
    print json.dumps(gige.get_dict(port))

