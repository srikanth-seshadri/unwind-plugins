import sys
import re
import json

keys = [
    "chip",
    "host-link1",
    "host-link2",
    "host-link3",
    "host-link4",
    "network-link1",
    "network-link2",
    "network-link3",
    "network-link4"
    ]

class msfpga_linkstate:
    def __init__(self, input_str):
        self.num_msfpga = 0
        self.num_ports = 0
        self.input_str = input_str
        self.link_state = {};
        self.keys = []

    def parse_status_array(self, status_str, source):
        link_state_t = {}
        status_found = status_str.find("Status");
        if status_found == -1:
            return link_state_t;
        bisect = status_str[6:].lstrip().rstrip().split('|')
        host_side_str = re.sub(' +', ' ', bisect[0])
        network_side_str = re.sub(' +', ' ', bisect[1])
        host_side = host_side_str[0:-1].split(' ')
        network_side = network_side_str[1:].split(' ')

        #link_state_t['network'] = network_side;
        #link_state_t['host'] = host_side;
        for index in range(len(network_side)):
            link_state_t['chip'] = source
            key = 'network-link' + str(index+1)
            self.keys.append(key)
            link_state_t[key] = network_side[index]
            key = 'host-link' + str(index+1)
            self.keys.append(key)
            link_state_t[key] = host_side[index]
        #print self.link_state;
        return link_state_t;

    def parse_linkstate(self):
        lines = self.input_str.split("\n")
        length_lines = len(lines)
        for index in range(length_lines):
            found_fpga = lines[index].find('XILINX FPGA')
            if found_fpga == 0:
                # Status of that link is 5th line from here
                if (index + 6 < length_lines):
                    status_array_str = lines[index+5]
                    key = 'Xilinx-MSFPGA-' + str(self.num_msfpga)
                    self.link_state[str(self.num_msfpga)] = \
                            self.parse_status_array(status_array_str, key)
                    self.keys.append(key)
                    self.num_msfpga += 1
                    #print status_array_str

    def get_dict(self):
        return self.link_state

    def print_json(self):
        print json.dumps(self.link_state, sort_keys=True, indent=4)
        print list(set(self.keys))

def parse_data(input_str):
    parser = msfpga_linkstate(input_str)
    parser.parse_linkstate()
    return parser.get_dict()
    parser.print_json()

def get_keys():
    return keys

if len(sys.argv) < 2:
    exit(0)

f = open(sys.argv[1], 'r')
input_str = f.read() #sys.stdin.read()
f.close()
print parse_data(input_str)
print get_keys()


