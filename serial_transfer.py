import time
import string
from pySerialTransfer import pySerialTransfer as txfer
alphabet = '0123456789,-.'
# your code



def clean_str(stringy_boi:str) -> str:
    new = ''
    for x in stringy_boi:
        if x in alphabet:
            new+= x
    last_comma_idx = 0
    for idx,el in enumerate(reversed(new)):
        if el == ',':
            last_comma_idx = idx
            break
    return new[:len(new) - last_comma_idx + 2]

try:
    print("Connecting to ESP32")
    link = txfer.SerialTransfer('/dev/ttyACM1')
    print("Try to open link")
    link.open()
    print("Link opened")
    time.sleep(2) # allow some time for the Arduino to completely reset
    counter = 0
    while True:
        start_time = time.time()
        while not link.available():
            if link.status < 0:
                print("shits fucked")
        #print(f"RCVD: {counter}")
        #counter += 1
        res = ''
        for idx in range(link.bytesRead):
            res += chr(link.rxBuff[idx])
        clean = clean_str(res)
        elapsed_time = time.time() - start_time
        print(elapsed_time*1000)

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
