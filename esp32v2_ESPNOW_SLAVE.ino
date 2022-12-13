#include <esp_now.h>
#include <WiFi.h>

#include "SerialTransfer.h"

#define CHANNEL 1
#define IMU_DATA_STRUCTURE_SIZE 120


typedef struct message_struct
{
  char imu_data[IMU_DATA_STRUCTURE_SIZE];
  //char lora_data[100];
} message_struct;

message_struct the_data;
SerialTransfer data_transfer;

// Init ESP Now with fallback
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

// config AP SSID
//void configDeviceAP() {
//  const char *SSID = "Slave_1";
//  bool result = WiFi.softAP(SSID, "Slave_1_Password", CHANNEL, 0);
//  if (!result) {
//    Serial.println("AP Config failed.");
//  } else {
//    Serial.println("AP Config Success. Broadcasting with AP: " + String(SSID));
//    Serial.print("AP CHANNEL "); Serial.println(WiFi.channel());
//  }
//}

void setup() {
  Serial.begin(115200);
  data_transfer.begin(Serial);
  //Serial.println("ESPNow/Basic/Slave Example");
  //Set device in AP mode to begin with
  WiFi.mode(WIFI_STA);
  // configure device AP mode
  //configDeviceAP();
  // This is the mac address of the Slave in AP Mode
  //Serial.print("STA MAC: "); Serial.println(WiFi.macAddress());
  //Serial.print("STA CHANNEL: "); Serial.println(WiFi.channel());
  // Init ESPNow with a fallback logic
  InitESPNow();
  // Once ESPNow is successfully Init, we will register for recv CB to
  // get recv packer info.
  esp_now_register_recv_cb(OnDataRecv);
}

// callback when data is recv from Master
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
  memset(the_data.imu_data,0,IMU_DATA_STRUCTURE_SIZE);
  memcpy(&the_data, data, sizeof(the_data));
  //Serial.println("INCOMING DATA:");
  //Serial.println(the_data.imu_data);
  //if(data_transfer.available())
  //{
  for(int i=0; i<IMU_DATA_STRUCTURE_SIZE; i++)
  {
    data_transfer.packet.txBuff[i] = the_data.imu_data[i];
  }
  data_transfer.sendData(IMU_DATA_STRUCTURE_SIZE);
  data_transfer.reset();
  //}
  //Serial Transfer Time.
}

void loop() {
  // Chill
}
