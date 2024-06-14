#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <mcp_can.h>
#include <SPI.h>
#define BNO055_SAMPLERATE_DELAY_MS (100)
const int SPI_CS_PIN = 17;
MCP_CAN CAN(SPI_CS_PIN);
Adafruit_BNO055 bno = Adafruit_BNO055(55,0x28,&Wire);

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

void setup() {
  // put your setup code here, to run once:
//  Serial.begin(115200);

//  while(!Serial) delay(10);

  if(!bno.begin())
  {
//    Serial.print("No BNO sensor");
    while(1);
  }
  delay(1000);

//  displaySensorDetails();

  bno.setExtCrystalUse(true);

  while (CAN_OK != CAN.begin(CAN_1000KBPS)) 
  {
//    Serial.println("CAN BUS FAIL!");
    delay(100);
  }
//  Serial.println("CAN BUS OK!");
}
unsigned char sensor0[8] = {136,136,136,136,136,136,136,136};
void loop() {
  // put your main code here, to run repeatedly:
  sensors_event_t event;
  bno.getEvent(&event);
//  Serial.print("X: ");
//  Serial.print(event.orientation.x, 4);
//  Serial.print("\tY: ");
//  Serial.print(event.orientation.y, 4);
//  Serial.print("\tZ: ");
//  Serial.print(event.orientation.z, 4);
//  Serial.println("");
  delay(BNO055_SAMPLERATE_DELAY_MS);
  sensor0[0] = SignCarry(event.orientation.x);
  sensor0[1] = abs(event.orientation.x);
  sensor0[2] = SignCarry(event.orientation.y);
  sensor0[3] = abs(event.orientation.y);
  sensor0[4] = SignCarry(event.orientation.z);
  sensor0[5] = abs(event.orientation.z);
  CAN.sendMsgBuf(0x00,0,8,sensor0);
}
// dont do this here, do in python
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
