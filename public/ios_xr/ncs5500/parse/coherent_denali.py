import sys
import re

string_map_denali = {
        'Module State'   : 'module_state',
        'Module General Status' : 'module_general_status',
        'TX_SIGNALS'     : 'tx_signal',
        'RX_SIGNALS'     : 'rx_signal',
        'TX_IC_LOCK'     : 'tx_lock',
        'RX_IC_LOCK'     : 'rx_lock',
        'TX_CMU'         : 'tx_cmu',
        'HOST_LANE_SKEW' : 'host_lane_skew'
    }

string_map_network = {
        'TX_REF_CLOCK'   : 'tx_ref_clock',
        'TX_JITTER_PLL'  : 'tx_jitter_pll',
        'DAC READY'      : 'dac_ready',
        'ASIC_TX_READY'  : 'asic_tx_ready',
        'TX_CLOCKS'      : 'tx_clocks',
        'DEMOD LOCK'     : 'demod_lock',
        'DISPER LOCK'    : 'disper_lock', 
        'ADC OUTPUT'     : 'adc_output',
        'ADC READY'      : 'adc_ready',
        'ASIC_RX_READY'  : 'asic_rx_ready',
        'RX_CLOCKS'      : 'rx_clocks',
        'LASER'          : 'laser_state',
        'TRAFFIC TYPE'   : 'traffic_type',
        'TX-CHN'         : 'tx_chan',
        'RX-CHN'         : 'rx_chan',
        'PWD'            : 'pwr',
        'LED'            : 'led_state'
    }


class denali_state_parser:

    def __init__(self, input_str):
        self.input_str = input_str;
        self.denali_map = {}
        self.network_lines = []
        self.denali = {}

    def parse_line(self, line):
        ret = []
        bisect = line.lstrip().rstrip().split(':')
        if len(bisect) != 2:
            return ret
        left = bisect[0].lstrip()
        pos = left.find('(')
        if pos != -1:
            ret.insert(0, left[:pos-1])
        else:
            ret.insert(0, left.rstrip())
        ret.insert(1, bisect[1].lstrip().rstrip())
        return ret

    def insert_map(self, val, network_line):
        if len(val) != 2:
            return
        if val[0] in string_map_denali.keys():
            self.denali_map[string_map_denali[val[0]]] = val[1]
        elif val[0] in string_map_network.keys():
            net = {}
            net[string_map_network[val[0]]] = val[1]
            try:
                self.network_lines[network_line].update(net)
            except IndexError:
                #self.network_lines[network_line] = {}
                self.network_lines.insert(network_line, net)

    def merge_dict(self):
        length = len(self.network_lines)
        for i in range(length):
            self.denali[str(i)] = self.denali_map.copy()
            for key in self.network_lines[i].keys():
                self.denali[str(i)][key] = self.network_lines[i][key]


    def parse_str(self):
        network_line = 0
        lines = self.input_str.split('\n')
        for index in range(len(lines)):
            if lines[index].find('NW Lane ') != -1:
                tnetwork = lines[index].lstrip().split(' ')
                network_line = int(tnetwork[2]) # do some error checks!
                continue
            if lines[index].find('Configuration Information') != -1:
                continue
            ret = self.parse_line(lines[index])
            self.insert_map(ret, network_line)
        self.merge_dict()


    def get_dict(self):
        return self.denali


def parse_data(data):
    parser = denali_state_parser(data)
    parser.parse_str()
    return parser.get_dict()


def get_keys():
    return string_map_denali.values() + string_map_network.values()

