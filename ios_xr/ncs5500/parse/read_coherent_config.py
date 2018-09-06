import json;
import re;

#Do not change func signatures.
def get_keys():
    return ["diff","fec", "state", "speed", 'frequency'];

def parse_data(data): 
    data1=data.split("\n");
    data1="NEWLINE".join(data1);
    data1 = re.sub(".*{", "{", data1)
    data1 = re.sub("NEWLINE","",data1)
    data1 = re.sub("}RP.*","",data1)
    print data1;
    dict={};
    dict['0']=json.loads(data1)
    return dict;
