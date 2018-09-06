import sys
import re
import json
import subprocess

# $node_conversion -i node0_3_CPU0
# sysmgr_show -o -p optics_ma -n 768

procs_list = {'coherent_driver': [],
                'fia_driver': [],
                'ifmgr' : [],
                'optics_ma' : [], 
                'optics_ea' : ['coh_aipc_client'], 
                'otn_ma' : [], 
                'otn_ea' : ['coh_aipc_client', 'icpe_local_ea'],
		'ttt' : ['ggg']
                }

class process_state:
    def __init__(self, proc_name_list, nodeid):
        self.proc_name_list = proc_name_list
        self.nodeid = nodeid
        self.proc_state = {}

    def get_process_jid (self, output_lines):
        jid = -1
        for line in output_lines:
            jid_line = line.find('Job Id') 
            if jid_line != -1:
                jid = line.split(':')
                if len(jid) == 2:
                    jid = jid[1].lstrip().rstrip()
                    break
        return jid

    def find_threads_running(self, proc_name, output_lines, threads):
        running = {}
        if len(threads) == 0:
            running[proc_name] = 1
            return running

        for thread in threads:
            running[thread] = 0

        for line in output_lines:
            for thread in threads:
                if line.find(thread) != -1:
                    running[thread] = 1
        return running

    
    def get_process_output (self, proc_name, nodeid):
        output = run_command('/pkg/sbin/sysmgr_show -o -p ' + proc_name + ' -n ' + str(nodeid))
        return output

    def check_proc_state (self):
        for process, threads in self.proc_name_list.items():
            proc = {}
            output = self.get_process_output(process, self.nodeid)
            output_lines = output.split('\n')
            jid = self.get_process_jid(output_lines)
            proc['jid'] = jid

            running =self.find_threads_running(process, output_lines, threads)
            proc['threads'] = running
            for run, val in running.items():
                if val == 0:
                    proc['good_state'] = 0
                    break
                else:
                    proc['good_state'] = 1

            self.proc_state[process] = proc

    def dump_proc_state(self):
        print json.dumps(self.proc_state, sort_keys=True, indent=4)



def run_command(command):
    try:
       output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
       output = ''

    return output


def get_node_id_from_node_name(node_name):
    node_id = 0
    name = 'node' + re.sub('/', '_', node_name)
    output = run_command('/pkg/bin/node_conversion' + ' -i ' + name)
    try:
        node_id = int(output)
    except ValueError:
        node_id = 0

    return node_id


if len(sys.argv) < 2:
    exit(-1)

node_id = get_node_id_from_node_name(sys.argv[1])

proc = process_state(procs_list, node_id)
proc.check_proc_state()
proc.dump_proc_state()



