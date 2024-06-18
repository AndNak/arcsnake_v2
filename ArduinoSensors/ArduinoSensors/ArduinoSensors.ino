#include  <SPI.h>
#include <mcp_can.h>
#include "DHT.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/*
 * NOTE: THIS CODE REQUIRES AN EDITED VERSION OF ADAFRUIT_BNO055 CLASS WITH CUSTOM FUNCTION readRawBuffer
 */

#define DHTPIN 6
#define PRESSURESENSORPIN A3
#define DHTTYPE DHT11
#define BNO055_SAMPLERATE_DELAY_MS (100)

const int SPI_CS_PIN = 17;
MCP_CAN CAN(SPI_CS_PIN);
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BNO055 bno = Adafruit_BNO055(55,0x28,&Wire);

unsigned long this_address = 0x01; // Set CAN address for this arduino here

// data vars
float humidity = 0;
float temp = 0;
int pressure = 0;
sensors_event_t orientationData , angVelocityData , linearAccelData, magnetometerData, accelerometerData, gravityData;
int8_t imuTemp = 0;
uint8_t sys_calib, gyro_calib, accel_calib, mag_calib = 0;

void setup()
{
  Serial.begin(9600);
  while(!Serial);
  while (CAN_OK != CAN.begin(CAN_1000KBPS))    // init can bus : baudrate = 1000k
  {
    Serial.println("CAN BUS FAIL!");
    delay(100);
  }

  Serial.println("CAN BUS OK!");
  dht.begin();

  pinMode(PRESSURESENSORPIN, INPUT_PULLUP);

  if(!bno.begin())
  {
    Serial.print("No BNO sensor");
    while(1);
  }
  delay(1000);

//  displaySensorDetails();

  bno.setExtCrystalUse(true);
}


void loop()
{
  unsigned char len = 0;
  unsigned char recv_buf[8];

  while (CAN_MSGAVAIL == CAN.checkReceive())           // check if data coming
  {

    unsigned long canId;
    CAN.readMsgBufID(&canId, &len, recv_buf);    // read data,  len: data length, buf: data buf


    //        Serial.print(canId);
    //        for(int i = 0; i < len; i++){
    //          Serial.print(" ");
    //          Serial.print(buf[i]);
    //        }
    //        Serial.println();


    // send readings
    if (canId == this_address) {
      unsigned char send_buf[8] = {0, 0, 0, 0, 0, 0, 0, 0}; // For 8-byte CAN data
      uint8_t imu_buf[6]; // For 6-byte raw vector readings from IMU

      // read humidity, temp, pressure command
      if (recv_buf[0] == 0x00){
        humidity = dht.readHumidity();
        temp = dht.readTemperature();
        pressure = analogRead(PRESSURESENSORPIN);
        send_buf[0] = 0x00; // first buffer element matches read command
        send_buf[5] = char(pressure / 100);
        send_buf[6] = char(temp);
        send_buf[7] = char(humidity);
      }
      // read temp and calibration command
      else if(recv_buf[0] == 0x01){
        imuTemp = bno.getTemp();
        bno.getCalibration(&sys_calib, &gyro_calib, &accel_calib, &mag_calib);
        send_buf[0] = 0x01;
        send_buf[1] = char(sys_calib);
        send_buf[2] = char(gyro_calib);
        send_buf[3] = char(accel_calib);
        send_buf[4] = char(mag_calib);
        send_buf[5] = char(imuTemp);
//        Serial.println();
//        Serial.print(F("temperature: "));
//        Serial.println(imuTemp);
//        Serial.println();
//        Serial.print("Calibration: Sys=");
//        Serial.print(sys_calib);
//        Serial.print(" Gyro=");
//        Serial.print(gyro_calib);
//        Serial.print(" Accel=");
//        Serial.print(accel_calib);
//        Serial.print(" Mag=");
//        Serial.println(mag_calib);
//        Serial.println("--");
      }
      // read absolute orientation command
      else if(recv_buf[0] == 0x02){
//          bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
//          printEvent(&orientationData);
//          delay(10);
          send_buf[0] = 0x02;
          bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_EULER);
          memcpy(&send_buf[1], imu_buf, 6);
      } 
      // read accelerometer command
      else if(recv_buf[0] == 0x03){
//        bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
          send_buf[0] = 0x03;
          bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_ACCELEROMETER);
          memcpy(&send_buf[1], imu_buf, 6);
      }
      // read linear acceleration (without gravity)
      else if(recv_buf[0] == 0x04){
//        bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
          send_buf[0] = 0x04;
          bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_LINEARACCEL);
          memcpy(&send_buf[1], imu_buf, 6);
      }
      // read gyroscope command
      else if(recv_buf[0] == 0x05){
//        bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
          send_buf[0] = 0x05;
          bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_GYROSCOPE);
          memcpy(&send_buf[1], imu_buf, 6);
      }
      // read magnetometer command
      else if(recv_buf[0] == 0x06){
//        bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
          send_buf[0] = 0x06;
          bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_MAGNETOMETER);
          memcpy(&send_buf[1], imu_buf, 6);
      }
      // read orientation in quaternion
      else if(recv_buf[0] == 0x07){
        // populates all 8 bytes of send_buf with quaternion data
        bno.getRawQuat(send_buf);
      }
      // Read gravity vector
      else if(recv_buf[0] == 0x08){
        send_buf[0] = 0x08;
        bno.getRawBuffer(imu_buf, Adafruit_BNO055::VECTOR_GRAVITY);
        memcpy(&send_buf[1], imu_buf, 6);
      }
      
      
      Serial.print(F("Humidity: "));
      Serial.print(humidity);
      Serial.print(F("%  Temperature: "));
      Serial.print(temp);
      Serial.print(F("%  Pressure: "));
      Serial.print(pressure);
      Serial.println();

      if (CAN_FAIL == CAN.sendMsgBuf(this_address, CAN_STDID, 8, send_buf)) {
//        Serial.println("Failed to send message :(");
      }

    }

  }

}

void displaySensorDetails(void) // also need to make one for CAN
{
  sensor_t sensor;
  bno.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" xxx");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" xxx");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" xxx");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

char SignCarry(int val){ // output the sign and carry for the val
  char retVal = 0;
  if(val > 255){
    retVal = 1;
  }else if((val < 0) && (val > -255)){
    retVal = 16;
  } else if(val < -255){
    retVal = 17;
  }
  return retVal;
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
