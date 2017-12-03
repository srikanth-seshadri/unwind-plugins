import sys
import re
import json

string_map = {
        'Pluggable'                  : 'pluggable_type',
        'Controller optics admin up' : 'optics_admin_state',
        'Controller dsp admin up'    : 'dsp_admin_state',
        'Set Laser state'            : 'laser_state',
        'Laser On Response-Pending'  : 'is_laser_on_progress',
        'Set Laser Return Code'      : 'set_laser_code',
        'Frequency Configured'       : 'config_frequency',
        'Frequency Provisioned'      : 'actual_frequency',
        'Set Frequency Return Code'  : 'set_frequency_code',
        'Configured tx power'        : 'config_tx_power',
        'Provisioned tx power'       : 'actual_tx_power',
        'Set Tx Power Return Code'   : 'set_tx_code',
        'Configured cd min'          : 'config_cd_min',
        'Provisioned cd min'         : 'actual_cd_min',
        'Set CD Min Return Code'     : 'set_cd_min_code',
        'Configured cd max'          : 'config_cd_max',
        'Provisioned cd max'         : 'actual_cd_max',
        'Set CD Max Return Code'     : 'set_cd_max_code',
        'Traffic type Configured'    : 'config_traffic_type',
        'Traffic type Provisioned'   : 'actual_traffic_type',
        'Set traff type Return Code' : 'set_traffic_type_code',
        'Is Pending Provisioning'    : 'is_provision_pending',
        'No of ether intf created'   : 'num_ether_intf',
        'Is Created'                 : 'veth_intf_created',
        'Interface Name'             : 'veth_intf_name',
        'Interface Handle'           : 'veth_intf_handle',
        'Admin State'                : 'veth_admin_state',
        'Is PM Initialized (Optics)' : 'is_optics_pm_init',
        'RC for PM Init (Optics)'    : 'optics_pm_init_code', 
        'Is PM Initialized (DSP)'    : 'is_dsp_pm_init',
        'RC for PM Init (DSP)'       : 'dsp_pm_init_code',
        'Is Alarms Initialized (Optics)' : 'is_optics_alarm_init',
        'RC for Optics Alarms Init'  :  'optics_alarm_init_code',
        'Is Alarms Initialized (DSP)':  'is_dsp_alarm_init',
        'RC for DSP Alarms Init'     :  'dsp_alarm_init_code'
    }


class coherent_internal_parser:
    def __init__(self, input_str):
        self.input_str = input_str;
        self.internal_map = {}
        self.optics_map = {}
        self.veth_map = []

    def trim_line(self, line):
        res = []
        tmp = line.split(':')
        if len(tmp) == 2:
            res.append(tmp[0].rstrip())
            tright = re.sub(' +', ' ', tmp[1])
            right = tright.split(' ')
            if len(right) > 1:
                res.append(right[1])
            else:
                res.append('')
        return res

    def fix_key_values(self):
        if 'dsp_admin_state' in self.optics_map:
            if self.optics_map['dsp_admin_state'] == 'YES':
                self.optics_map['dsp_admin_state'] = 'Up'
            else:
                self.optics_map['dsp_admin_state'] = 'Down'

        if 'optics_admin_state' in self.optics_map:
            if self.optics_map['optics_admin_state'] == 'YES':
                self.optics_map['optics_admin_state'] = 'Up'
            else:
                self.optics_map['optics_admin_state'] = 'Down'

        if 'config_traffic_type' in self.optics_map:
            tmp = self.parse_traffic_type(self.optics_map['config_traffic_type'])
            self.optics_map['config_speed'] = tmp[0]
            self.optics_map['config_qam'] = tmp[1]
            self.optics_map['config_fec'] = tmp[2]
            self.optics_map['config_fec_type'] = tmp[3]

        if 'actual_traffic_type' in self.optics_map:
            tmp = self.parse_traffic_type(self.optics_map['actual_traffic_type'])
            self.optics_map['actual_speed'] = tmp[0]
            self.optics_map['actual_qam'] = tmp[1]
            self.optics_map['actual_fec'] = tmp[2]
            self.optics_map['actual_fec_type'] = tmp[3]
             

    def parse_traffic_type(self, tr_str):
        traffic = ['', '', '', '']
        tr = tr_str.split('_')
        for index in range(len(tr)): 
            if tr[index] == '100G':
                traffic[0] = 100
                traffic[1] = 'QPSK'
            elif tr[index] == '150G':
                traffic[0] = 150
                traffic[1] = '8QAM'
            elif tr[index] == '200G':
                traffic[0] = 200
                traffic[1] = '16QAM'
            elif tr[index] == 'FEC15':
                traffic[2] = 'FEC15'
            elif tr[index] == 'FEC25':
                traffic[2] = 'FEC25'
            elif tr[index] == 'DIFF':
                traffic[3] = 'DIFF'
            elif tr[index] == 'NODIFF':
                traffic[3] = 'NODIFF'
        return traffic

    def parse_str(self):
        veth_info = {}
        veth_intf = []
        veth_intf_num = 0

        lines = self.input_str.split('\n')

        for line in lines:
            res = self.trim_line(line)
            if len(res) == 2:
                if res[0] in string_map.keys():
                    m = string_map[res[0]]
                    if(m == 'veth_intf_name') or (m == 'veth_intf_handle') or \
                            (m == 'veth_admin_state') or (m == 'veth_intf_created'):
                        veth_info[m] = res[1]
                        if (m == 'veth_intf_created') and (res[1] == 'YES'):
                            veth_intf_num += 1
                        if(m == 'veth_admin_state'):
                            veth_intf.append(veth_info)
                            self.veth_map.append(veth_info)
                            veth_info = {}
                    else:
                        self.optics_map[string_map[res[0]]] = res[1]

        self.optics_map['num_ether_intf'] = str(veth_intf_num)
        self.fix_key_values()

    def merge_maps(self):
        length = len(self.veth_map)
        for index in range(length):
            self.internal_map[str(index)] = self.optics_map.copy()
            self.internal_map[str(index)].update({'veth_intf_name': self.veth_map[index]['veth_intf_name']})
            self.internal_map[str(index)].update({'veth_intf_handle': self.veth_map[index]['veth_intf_handle']})
            self.internal_map[str(index)].update({'veth_admin_state': self.veth_map[index]['veth_admin_state']})
            self.internal_map[str(index)].update({'veth_intf_created': self.veth_map[index]['veth_intf_created']})

    def get_dict(self):
        return self.internal_map

    def print_json(self):
        print json.dumps(self.internal_map, sort_keys=True, indent=4)

def parse_data(data):
    parser = coherent_internal_parser(data)
    parser.parse_str()
    parser.merge_maps()
    #parser.print_json()
    return parser.get_dict()

def get_keys():
    return string_map.values()


#if len(sys.argv) < 2:
#    exit(0)
#
#f = open(sys.argv[1], 'r')
#input_str = f.read() #sys.stdin.read()
#f.close()

#print parse_data(input_str)
#print get_keys()



