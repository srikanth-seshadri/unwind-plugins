import sys
import re
import json

optics_map = {
        'Controller State'      : 'oper_state',
        'Transport Admin State' : 'transport_state',
        'Laser State'           : 'laser_state',
        'Optics Type'           : 'optics_type',
        'Frequency'             : 'frequency',
        'Detected Alarms'       : 'alarms',
        'Laser Bias Current'    : 'lbc',
        'Actual TX Power'       : 'tx_power',
        'RX Power'              : 'rx_power',
        'Performance Monitoring': 'pm',
        }



class optics_controller:
    def __init__(self, intput_str):
        self.input_str = input_str
        self.optics_controller = {}

    def trim_line(self, line):
        res = []
        tmp = line.split(':')
        if len(tmp) == 2:
            res.append(tmp[0].rstrip())
            #tright = re.sub(' +', ' ', tmp[1])
            #right = tright.split(' ')
            res.append(tmp[1].lstrip().rstrip())
        return res

    def parse_alarm(self, alarm_str):
        severe_alarms = ''
        alarm_str_stripped = re.sub(' +', '', alarm_str)
        alarms = alarm_str_stripped.split(',')
        for alarm in alarms:
            if (alarm == 'LOS') or (alarm == 'LOS-P'):
                severe_alarms = alarm
            if alarm == 'LOF':
                severe_alarms = alarm
            if alarm == 'LOM':
                severe_alarms = alarm
            if alarm == 'IMPROPER-REM':
                severe_alarms = alarm
        return severe_alarms;

    def get_frequency(self, line):
        frequency = ''
        index = line.find('Frequency=')
        if index != -1:
            freq = line[index+len('Frequency='):-1]
            frequency = re.sub('[a-zA-Z]+', '', freq)
        return frequency

    def parse_output(self):
        lines = self.input_str.split('\n')
        length = len(lines)
        for index in range(length):
            if lines[index].find('Detected Alarms') != -1:
                self.optics_controller['alarms'] = self.parse_alarm(lines[index+1])
            elif lines[index].find('DWDM carrier Info') != -1:
                self.optics_controller['frequency'] = self.get_frequency(lines[index])
            else:
                res = self.trim_line(lines[index])
                if len(res) == 2:
                    if res[0] in optics_map.keys():
                        self.optics_controller[optics_map[res[0]]]  = res[1]

    def get_dict(self):
        return self.optics_controller

    def print_json(self):
        print json.dumps(self.optics_controller, sort_keys=True, indent=4)


def get_keys():
    return optics_map.values()

def parse_data(data):
    parser = optics_controller(data)
    parser.parse_output()
    return parser.get_dict()


#
#if len(sys.argv) < 2:
#    exit(0)
#
#f = open(sys.argv[1], 'r')
#input_str = f.read() #sys.stdin.read()
#f.close()
#print parse_data(input_str)
#print get_keys()
