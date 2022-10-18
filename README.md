# project_3-1

## How to run the code
Assuming that you have an ESP12-S arduino feather board with an BNO055 IMU connected via I2C. Then you have to install the required libraries, the ESP8266 arduino feather library and the BNO055 Library.

Then you need to find your macaddress to hardcode into the Feather so you only get the UDP packets and then you just need to upload the code to the ESP12-S Feather and then connect to the soft access point from your computer. When you are done connecting to the access point you can then run the server.py file to get the IMU data into a file called logfile.log
