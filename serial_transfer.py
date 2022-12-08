import time
import string
from pySerialTransfer import pySerialTransfer as txfer
alphabet = '0123456789,-.'

def clean_str(stringy_boi:str) -> str:
    new = ''
    for x in stringy_boi:
        if x in alphabet:
            new+= x
    return new
try:
    print("Connecting to ESP32")
    link = txfer.SerialTransfer('/dev/ttyACM1')
    print("Try to open link")
    link.open()
    print("Link opened")
    time.sleep(2) # allow some time for the Arduino to completely reset
    while True: 
        while not link.available():
            if link.status < 0:
                print("shits fucked")
        print("Response recived")
        res = ''
        for idx in range(link.bytesRead):
            res += chr(link.rxBuff[idx])
        print(res)
        print(clean_str(res))
        #with open('esp_now_testing.csv', 'a') as f:
        #     f.write(clean_str(res) + "\n")
        

except KeyboardInterrupt:
    try:
        link.close()
    except:
        pass

except:
    import traceback
    traceback.print_exc()
    
    try:
        link.close()
    except:
        pass