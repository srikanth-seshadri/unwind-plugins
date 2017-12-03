#Do not change func signatures.
def get_keys():
    return ["diff","fec", "state", "speed"];

def parse_data(data):
    dict=json.loads(data)[0]
    return dict;