#include  <SPI.h>
#include <mcp_can.h>
#include "DHT.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

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
//  Serial.begin(9600);
  //while(!Serial);
  while (CAN_OK != CAN.begin(CAN_1000KBPS))    // init can bus : baudrate = 1000k
  {
//    Serial.println("CAN BUS FAIL!");
    delay(100);
  }

//  Serial.println("CAN BUS OK!");
  dht.begin();

  pinMode(PRESSURESENSORPIN, INPUT_PULLUP);

  if(!bno.begin())
  {
//    Serial.print("No BNO sensor");
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
      unsigned char send_buf[8] = {0, 0, 0, 0, 0, 0, 0, 0};

      // read humidity, temp, pressure command
      if (recv_buf[0] == 0x00){
        humidity = dht.readHumidity();
        temp = dht.readTemperature();
        pressure = analogRead(PRESSURESENSORPIN);
        send_buf[0] = 0; // first buffer element matches read command
        send_buf[5] = char(pressure / 100);
        send_buf[6] = char(temp);
        send_buf[7] = char(humidity);
      }
      // read absolute orientation command
      else if(recv_buf[0] == 0x01){
        bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
        send_buf[0] = 1;
        send_buf[1] = SignCarry(orientationData.orientation.x);
        send_buf[2] = abs(orientationData.orientation.x);
        send_buf[3] = SignCarry(orientationData.orientation.y);
        send_buf[4] = abs(orientationData.orientation.y);
        send_buf[5] = SignCarry(orientationData.orientation.z);
        send_buf[6] = abs(orientationData.orientation.z);
      } 
      // read accelerometer command
      else if(recv_buf[0] == 0x02){
        bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
        send_buf[0] = 2;
      }
      // read gyroscope command
      else if(recv_buf[0] == 0x03){
        bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
        send_buf[0] = 3;
      }
      // read magnetometer command
      else if(recv_buf[0] == 0x04){
        bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
        send_buf[0] = 4;
      }
      // read temp and calibration command
      else if(recv_buf[0] == 0x05){
        imuTemp = bno.getTemp();
        bno.getCalibration(&sys_calib, &gyro_calib, &accel_calib, &mag_calib);
        send_buf[0] = 5;
      }
      
//      Serial.print(F("Humidity: "));
//      Serial.print(h);
//      Serial.print(F("%  Temperature: "));
//      Serial.print(t);
//      Serial.print(F("%  Pressure: "));
//      Serial.print(p);
//      Serial.println();

      if (CAN_FAIL == CAN.sendMsgBuf(this_address, CAN_STDID, 8, send_buf)) {
        Serial.println("Failed to send message :(");
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
