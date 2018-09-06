import sys
import re
import json

class alarms_parser:
    def __init__(self, input_str):
        self.input_str = input_str
        self.alarms = {};

    def parse_alarm_str(self, alarm_str):
        severe_alarms = {};
        alarm_str_stripped = re.sub(' +', '', alarm_str)
        alarms = alarm_str_stripped.split(',')
        for alarm in alarms:
            if (alarm == 'LOS') or (alarm == 'LOS-P'):
                severe_alarms['LOS'] = 1
            if alarm == 'LOF':
                severe_alarms['LOF'] = 1
            if alarm == 'LOM':
                severe_alarms['LOM'] = 1
            if alarm == 'IMPROPER-REM':
                severe_alarms['IMPROPER-REM'] = 1
        return severe_alarms;


    def parse_str(self):
        lines = self.input_str.split("\n")
        length = len(lines)
        for index in range(length):
            found = lines[index].find("Detected Alarms")
            if found == 0:
                none = lines[index].find('None')
                if none == -1:
                    coherent_alarms = lines[index].split(":") 
                    if(len(coherent_alarms) > 1):
                        self.alarms = self.parse_alarm_str(coherent_alarms[1])
                    self.alarms.update(self.parse_alarm_str(lines[index+1]))
                    break

    def print_json(self):
        print json.dumps(self.alarms, sort_keys=True, indent=4)


#if len(sys.argv) < 2:
#    exit(0)
#
#f = open(sys.argv[1], 'r')
#input_str = f.read() #sys.stdin.read()
#f.close()
#parser = alarms_parser(input_str)
#parser.parse_str()
#parser.print_json()


