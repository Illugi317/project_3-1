//IMU imports
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>
//ESP now includes
#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h> // only for esp_wifi_set_channel()

//Bluetooth serial
//#include "BluetoothSerial.h"

//E8:9F:6D:26:A7:0E

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

// Mapping from WING to ESP32
#define RFM95_RST 27
#define RFM95_CS 33
#define RFM95_INT 15
#define RF95_FREQ 434.0

#define IMU_DATA_STRUCTURE_SIZE 120
// Singleton instance of the radio driver
RH_RF95 driver(RFM95_CS, RFM95_INT);

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, SERVER_ADDRESS);

uint16_t BNO055_SAMPLING_RATE_MS = 50;

Adafruit_BNO055 bno = Adafruit_BNO055(55);
                  ///fc:77:74:6a:a9:28'
//uint8_t addr[6] = {0xfc, 0x77, 0x74, 0x6a, 0xa9, 0x28};
//const char *pin = "1234";

//ESP NOW SECTION
esp_now_peer_info_t peerInfo = {};
#define CHANNEL 1
#define PRINTSCANRESULTS 0
#define DELETEBEFOREPAIR 0

// R E C I V E R  M A C  A D D R E S S
// gamer E8:9F:6D:26:A7:0D
uint8_t broadcastAddress[] = {0xE8,0x9F,0x6D,0x26,0xA7,0x0C};

//Structure to send data - F i x e d  v a l u e  m o m e n t
typedef struct message_struct
{
  char imu_data[IMU_DATA_STRUCTURE_SIZE];
  //char LoRa_gamers[];
} message_struct;

message_struct message;

void InitESPNow() {
  WiFi.disconnect();
  if (esp_now_init() == ESP_OK) {
    Serial.println("ESPNow Init Success");
  }
  else {
    Serial.println("ESPNow Init Failed");
    // Retry InitESPNow, add a counte and then restart?
    // InitESPNow();
    // or Simply Restart
    ESP.restart();
  }
}

// send data
void sendData(sensors_event_t* ori,sensors_event_t* gyro, sensors_event_t* liner, sensors_event_t* accl, sensors_event_t* grav, int temp) {
  // PeerInfo address to the esp32 connected to ESP32
  const uint8_t *peer_addr = peerInfo.peer_addr;
  double x = -1000000, y = -1000000, z = -1000000;  //dumb values, easy to spot problem
  // Dynamic string, Since the data is variable from 70 - 95 chars. 
  String reply;
  // Orientation data.
  x = ori->orientation.x;
  y = ori->orientation.y;
  z = ori->orientation.z;
  // Add to string
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  // Gyroscope data
  x = gyro->gyro.x;
  y = gyro->gyro.y;
  z = gyro->gyro.z;
  // Add to string
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  // Linear accelaration vector
  x = liner->acceleration.x;
  y = liner->acceleration.y;
  z = liner->acceleration.z;
  // Add to string
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  // Accelaration vector
  x = accl->acceleration.x;
  y = accl->acceleration.y;
  z = accl->acceleration.z;
  // Add to string
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  // Gravity data
  x = grav->acceleration.x;
  y = grav->acceleration.y;
  z = grav->acceleration.z;
  // Add to string
  reply += String(x);
  reply += ",";
  reply += String(y);
  reply += ",";
  reply += String(z);
  reply += ",";
  reply += String(temp);
  //Serial.print("Sending:(ONLY IMU_DATA)\n");
  //Serial.println(strlen(reply.c_str()));
  //Serial.print(reply);
  memset(message.imu_data, 0, IMU_DATA_STRUCTURE_SIZE);
  reply.toCharArray(message.imu_data, IMU_DATA_STRUCTURE_SIZE);
  esp_err_t result = esp_now_send(peer_addr, (uint8_t *) &message, sizeof(message));
  //Serial.print("Send Status: ");
  if (result == ESP_OK) {
    Serial.println("Send Success");
  } else if (result == ESP_ERR_ESPNOW_NOT_INIT) {
    // How did we get so far!!
    Serial.println("ESPNOW not Init.");
  } else if (result == ESP_ERR_ESPNOW_ARG) {
    Serial.println("Invalid Argument");
  } else if (result == ESP_ERR_ESPNOW_INTERNAL) {
    Serial.println("Internal Error");
  } else if (result == ESP_ERR_ESPNOW_NO_MEM) {
    Serial.println("ESP_ERR_ESPNOW_NO_MEM");
  } else if (result == ESP_ERR_ESPNOW_NOT_FOUND) {
    Serial.println("Peer not found.");
  } else {
    Serial.println("Error - Not sure what happened");
  }
}

// callback when data is sent from Master to
// This is essentially useless but is nice for debugging purposes.
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
           mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
  Serial.print("Last Packet Sent to: "); Serial.println(macStr);
  Serial.print("Last Packet Send Status: "); Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}




void setup() {
  Serial.begin(115200);

  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  Serial.println("Orientation Sensor Test"); Serial.println("");

  if (!bno.begin())
  {
    Serial.print("BNO055 not detected!");
    while(1);
  }
  Serial.println("BNO055 detected!");
  delay(100);
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  if (!manager.init())
    Serial.println("init failed");

  Serial.println("Feather LoRa init worked!");
  driver.setTxPower(23, false);

  //Set device in STA mode to begin with
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
  Serial.println("ESPNow/Basic/Master Example");
  // This is the mac address of the Master in Station Mode
  Serial.print("STA MAC: "); Serial.println(WiFi.macAddress());
  Serial.print("STA CHANNEL "); Serial.println(WiFi.channel());
  // Init ESPNow with a fallback logic
  InitESPNow();
  // Once ESPNow is successfully Init, we will register for Send CB to
  // get the status of Trasnmitted packet
  esp_now_register_send_cb(OnDataSent);

  //Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, sizeof(broadcastAddress));
  //peerInfo.ifidx = WIFI_IF_AP;
  peerInfo.channel = CHANNEL;
  peerInfo.encrypt = false;

  //Add peer
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer!");
    ESP.restart();
  }
}

uint8_t lora_data[] = "And hello back to you";
// Dont put this on the stack:
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];

void loop() {
  //Get all the data from the IMU
  sensors_event_t orientationData , angVelocityData , linearAccelData, magnetometerData, accelerometerData, gravityData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
  bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gravityData, Adafruit_BNO055::VECTOR_GRAVITY);
  //Temperture of IMU 
  int8_t boardTemp = bno.getTemp();


  // Debug messages, See all the data from the IMU
  /*
  printEvent(&orientationData);
  printEvent(&angVelocityData);
  printEvent(&linearAccelData);
  printEvent(&magnetometerData);
  printEvent(&accelerometerData);
  printEvent(&gravityData);

  int8_t boardTemp = bno.getTemp();
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
    
  //Lora fuckery
  uint8_t len = sizeof(buf);
  uint8_t from;
  if (manager.recvfromAck(buf, &len, &from))
  {
    Serial.print("got request from : 0x");
    Serial.print(from, HEX);
    Serial.print(": ");
    Serial.println((char*)buf);
    Serial.println(driver.lastRssi());
    // Send a reply back to the originator client
    if (!manager.sendtoWait(lora_data, sizeof(lora_data), from))
      Serial.println("LoRa out of range - sendtoWait failed");
  }
  sendData(&orientationData,&angVelocityData,&linearAccelData,&accelerometerData,&gravityData,boardTemp);
}

void printEvent(sensors_event_t* event) {
  double x = -1000000, y = -1000000 , z = -1000000; //dumb values, easy to spot problem
  if (event->type == SENSOR_TYPE_ACCELEROMETER) {
    Serial.print("Accl:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_ORIENTATION) {
    Serial.print("Orient:");
    x = event->orientation.x;
    y = event->orientation.y;
    z = event->orientation.z;
  }
  else if (event->type == SENSOR_TYPE_MAGNETIC_FIELD) {
    Serial.print("Mag:");
    x = event->magnetic.x;
    y = event->magnetic.y;
    z = event->magnetic.z;
  }
  else if (event->type == SENSOR_TYPE_GYROSCOPE) {
    Serial.print("Gyro:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else if (event->type == SENSOR_TYPE_ROTATION_VECTOR) {
    Serial.print("Rot:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else if (event->type == SENSOR_TYPE_LINEAR_ACCELERATION) {
    Serial.print("Linear:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_GRAVITY) {
    Serial.print("Gravity:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else {
    Serial.print("Unk:");
  }

  Serial.print("\tx= ");
  Serial.print(x);
  Serial.print(" |\ty= ");
  Serial.print(y);
  Serial.print(" |\tz= ");
  Serial.println(z);
}
