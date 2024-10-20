import uuid
import time

def create_hash():
    timestamp = str(int(time.time()))
    uuid_unico = uuid.uuid4().hex[:7]
    string_para_hash = uuid_unico + timestamp
    return string_para_hash