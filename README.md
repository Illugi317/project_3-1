# project_3-1

## How to run the code

### ESP8266 version (Only IMU data via WiFi)
Assuming that you have an ESP12-S arduino feather board with an BNO055 IMU connected via I2C. Then you have to install the required libraries, the ESP8266 arduino feather library and the BNO055 Library.

Then you need to find your macaddress to hardcode into the Feather so you only get the UDP packets and then you just need to upload the code to the ESP12-S Feather and then connect to the soft access point from your computer. When you are done connecting to the access point you can then run the server.py file to get the IMU data into a file called logfile.log

### ESP32 v2 version

Assuming that you have the ESP32v2 connected with the BNO055 IMU and the LoRa wing. You have to install the ESP32 arduino library, the BNO055 library, the Radiohead library for LoRa and lastly SerialTransfer python & arduino version.

We need two ESP32's to get the data from the dice. One will be called parent and one child, The child one is connected to the computer reciving the data and the parent is the one inside the dice. Upload the ```esp32v2_ESPNOW_SLAVE.ino``` code onto the child and keep it connected to the computer. Upload the ```esp32v2_IMU_LoRa_ESPNOW.ino``` to the parent, When you have powered up the parent and put it in the dice then you have to run the ```serial_transfer.py``` script to read the data. for debugging purposes you can look at the serial monitor of the parent and you will see if it's sending with success.
