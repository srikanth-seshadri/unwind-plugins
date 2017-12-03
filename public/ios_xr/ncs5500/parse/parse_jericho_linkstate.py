import sys
import re
import json


string_map = {
        'Tx Local Fault'  : 'tx_local_fault',
        'Rx Status'       : 'rx_status',
        'Rx Hi BER'       : 'rx_hiber',
        'Rx Local Fault'  : 'rx_local_fault',
        'Rx Remote Fault' : 'rx_remote_fault'
    }


class macsec_link_parser:

    def __init__(self, input_str):
        self.input_str = input_str;
        self.link_map = {}

    def parse_line(self, line):
        vals = []
        strippled_line = re.sub(' +', ' ', line)
        fields = strippled_line.split(':')
        if len(fields) != 3:
            return vals
        # a bit awkward parsing :( 
        vals.append(fields[0].lstrip().rstrip())
        int_fields = fields[1].lstrip().rstrip().split(' ')
        vals.append(int_fields[0].lstrip().rstrip())
        vals.append(fields[1][len(int_fields[0])+2:-1])
        vals.append(fields[2].lstrip().rstrip())
        return vals

    def parse_str(self):
        link = {}
        system_side = {}
        lines = self.input_str.split('\n')
        for line in lines:
            res = self.parse_line(line)
            if len(res) == 4:
                if res[0] in string_map.keys():
                    link['network_' + string_map[res[0]]] = res[1]
                if res[2] in string_map.keys():
                    link['system_' + string_map[res[2]]] = res[3]

        self.link_map['0'] = link;

    def get_dict(self):
        return self.link_map

    def print_json(self):
        print json.dumps(self.link_map, sort_keys=True, indent=4)


def parse_data(data):
    parser = macsec_link_parser(data)
    parser.parse_str()
    #parser.print_json()
    return parser.get_dict()


def get_keys():
    new_keys = []
    for s in string_map.values():
        new_keys.append('network_' + s)
        new_keys.append('system_' + s)

    return new_keys

#
#if len(sys.argv) < 2:
#    exit(0)
#
#f = open(sys.argv[1], 'r')
#input_str = f.read() #sys.stdin.read()
#f.close()
#print parse_data(input_str)
#print get_keys()


