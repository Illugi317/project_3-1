//IMU includes
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

//WiFi includes <CHANGE FOR BLUETOOTH LATER>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <LwipDhcpServer.h>
#include <WiFiUdp.h>


/* Set the delay between fresh samples */
uint16_t BNO055_SAMPLERATE_DELAY_MS = 2;

/* Set the WiFi ssid and password */
const char* ssid = "SpoonEnthusiast";
const char* password = "thereisnospoon";

/* Set fixed IP addr for AP */
IPAddress apIP(192, 168, 0, 1);

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup(void) {
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test");
  Serial.println("");

  /* Initialise the sensor */
  if (!bno.begin()) {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Oh no! no BNO055 detected!");
    while (1)
      ;
  }
  Serial.println("SENSOR DETECTED - CREATING WIFI AP");
  delay(1000);

  /* Mac address for the static lease */
  uint8 mac_LAP[6] = { 0xfc, 0x77, 0x74, 0x6a, 0xa9, 0x28 };

  /* Disable the WiFi persistence to avoid any re-configuration that may erase static lease when starting softAP */
  WiFi.persistent(false);

  WiFi.mode(WIFI_AP);
  /* Configure AP with IP = 192.168.0.1 / Gateway = 192.168.0.1 / Subnet = 255.255.255.0
     if you specify the ESP8266's IP-address with 192.168.0.1, the function softAPConfig() sets the DHCP-range as 192.168.0.100 - 192.168.0.200
  */
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  /* Setup your static leases.

     As it depend from your first address, and need to be done BEFORE any request from client,
     this need to be specified after WiFi.softAPConfig() and before WiFi.softAP().

     first call to wifi_softap_add_dhcps_lease() will setup first IP address of the range
     second call to wifi_softap_add_dhcps_lease() will setup second IP address of the range
     ...
     any client not listed will use next IP address available from the range (here 192.168.0.102 and more)
  */
  dhcpSoftAP.add_dhcps_lease(mac_LAP);  // always 192.168.0.100 website is there to double check
  /* Start Access Point. You can remove the password parameter if you want the AP to be open. */
  WiFi.softAP(ssid, password);
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
}

void transmit_data(sensors_event_t* ori,sensors_event_t* gyro, sensors_event_t* liner, sensors_event_t* accl, sensors_event_t* grav, int temp) {
  double x = -1000000, y = -1000000, z = -1000000;  //dumb values, easy to spot problem
  String reply;
  x = ori->orientation.x;
  y = ori->orientation.y;
  z = ori->orientation.z;
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  x = gyro->gyro.x;
  y = gyro->gyro.y;
  z = gyro->gyro.z;
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  x = liner->acceleration.x;
  y = liner->acceleration.y;
  z = liner->acceleration.z;
  
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  x = accl->acceleration.x;
  y = accl->acceleration.y;
  z = accl->acceleration.z;
  
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  x = grav->acceleration.x;
  y = grav->acceleration.y;
  z = grav->acceleration.z;
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  reply += String(temp);


  WiFiUDP UDP;
  Serial.println(reply);
  UDP.beginPacket("192.168.0.101", 5000);
  UDP.write(reply.c_str());
  UDP.endPacket();
}

void loop(void) {
  //could add VECTOR_ACCELEROMETER, VECTOR_MAGNETOMETER,VECTOR_GRAVITY...
  sensors_event_t orientationData, angVelocityData, linearAccelData, magnetometerData, accelerometerData, gravityData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
  bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gravityData, Adafruit_BNO055::VECTOR_GRAVITY);
  int8_t boardTemp = bno.getTemp();
  /*
  printEvent(&orientationData);
  printEvent(&angVelocityData);
  printEvent(&linearAccelData);
  printEvent(&magnetometerData);
  printEvent(&accelerometerData);
  printEvent(&gravityData);
  Serial.println();
  Serial.print(F("temperature: "));
  Serial.println(boardTemp);

  uint8_t system, gyro, accel, mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  Serial.println();
  Serial.print("Calibration: Sys=");
  Serial.print(system);
  Serial.print(" Gyro=");
  Serial.print(gyro);
  Serial.print(" Accel=");
  Serial.print(accel);
  Serial.print(" Mag=");
  Serial.println(mag);

  Serial.println("--");
  */
  int number_client;
  number_client = (int)wifi_softap_get_station_num();
  if (number_client == 1) {
    Serial.println("computer connected, Start transmitting data");
    transmit_data(&orientationData,&angVelocityData,&linearAccelData,&accelerometerData,&gravityData,boardTemp);
  }
}

void printEvent(sensors_event_t* event) {
  double x = -1000000, y = -1000000, z = -1000000;  //dumb values, easy to spot problem
  if (event->type == SENSOR_TYPE_ACCELEROMETER) {
    Serial.print("Accl:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  } else if (event->type == SENSOR_TYPE_ORIENTATION) {
    Serial.print("Orient:");
    x = event->orientation.x;
    y = event->orientation.y;
    z = event->orientation.z;
  } else if (event->type == SENSOR_TYPE_MAGNETIC_FIELD) {
    Serial.print("Mag:");
    x = event->magnetic.x;
    y = event->magnetic.y;
    z = event->magnetic.z;
  } else if (event->type == SENSOR_TYPE_GYROSCOPE) {
    Serial.print("Gyro:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  } else if (event->type == SENSOR_TYPE_ROTATION_VECTOR) {
    Serial.print("Rot:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  } else if (event->type == SENSOR_TYPE_LINEAR_ACCELERATION) {
    Serial.print("Linear:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  } else if (event->type == SENSOR_TYPE_GRAVITY) {
    Serial.print("Gravity:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  } else {
    Serial.print("Unk:");
  }

  Serial.print("\tx= ");
  Serial.print(x);
  Serial.print(" |\ty= ");
  Serial.print(y);
  Serial.print(" |\tz= ");
  Serial.println(z);
}