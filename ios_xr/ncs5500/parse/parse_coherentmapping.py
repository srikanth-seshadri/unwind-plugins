import sys
import re
import json

keys = [
        "dev_address",
        "ifhandle",
        "ifname",
        "intfname",
        "intftype",
        'frontpanelport',
        'denali_number'
        ]


class coherent_mapping_parser:
    def __init__(self, input_str):
        self.input_str = input_str
        self.mapping = {};

    def parse_map_str(self, map_str):
        map_info = {}
        map_info['intftype'] = None
        m = re.sub(' +', ' ', map_str).split(' ')
        if len(m) > 2:
            if m[0].find('0x') == -1:
                #print 'Not a valid str'
                return map_info

            optics = m[2].find('Optics')
            if optics == 0:
                map_info['intftype'] = 'Optics'
            else:
                map_info['intftype'] = 'CoherentDSP'

            map_info['dev_address'] = re.sub(' +', '', m[0])
            map_info['ifhandle'] = re.sub(' +', '', m[1])
            map_info['intfname'] = re.sub(' +', '', m[2])
            map_info['ifname'] = \
                    re.sub('_', '/', re.sub('[a-zA-Z]+', '', map_info['intfname']))
            front_panel = map_info['ifname'].split('/')
            if len(front_panel) == 4:
                map_info['frontpanelport'] = front_panel[3]
                try:
                    map_info['denali_number'] = int(front_panel[3])/2
                except ValueError:
                    map_info['denali_number'] = -1
            #print map_info
        return map_info

    def parse_str(self):
        map_info = {}
        intf_num = 0
        lines = self.input_str.split("\n")
        length = len(lines)
        for index in range(length):
            #print lines[index]
            map_info = self.parse_map_str(lines[index]);
            if map_info['intftype'] != None:
                self.mapping[str(intf_num)] = map_info
                intf_num += 1
                #self.mapping.append(map_info)

                #if map_info['intftype'] in self.mapping.keys():
                #    self.mapping[map_info['intftype']].append(map_info)
                #else:
                #    self.mapping[map_info['intftype']] = map_info

    def get_dict(self):
        return self.mapping

    def print_json(self):
        print json.dumps(self.mapping, sort_keys=True, indent=4)


def get_keys():
    return keys

def parse_data(input_str):
    parser = coherent_mapping_parser(input_str)
    parser.parse_str()
    return parser.get_dict()


#
#if len(sys.argv) < 2:
#    exit(0)
#
#f = open(sys.argv[1], 'r')
#input_str = f.read() #sys.stdin.read()
#f.close()
#print get_keys()
#print parse_data(input_str)
#
