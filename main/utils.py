from datetime import datetime
import requests
from PIL import Image
import io

def log(msg):
    timestamp = datetime.now().strftime('[%d/%m/%Y::%H:%M:%S]')
    
    with open(f'main/DatabaseLogs.log', "a") as log:
        log.write(f"{timestamp} {msg}\n")