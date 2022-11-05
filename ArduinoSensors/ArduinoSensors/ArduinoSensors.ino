#include  <SPI.h>
#include <mcp_can.h>
#include "DHT.h"

#define DHTPIN 6
#define PRESSURESENSORPIN A3

float h = 0;
float t = 0;
int p = 0;

#define DHTTYPE DHT11

unsigned long address = 0x01;
const int SPI_CS_PIN = 17;

MCP_CAN CAN(SPI_CS_PIN);

DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  Serial.begin(9600);
  //while(!Serial);
  while (CAN_OK != CAN.begin(CAN_1000KBPS))    // init can bus : baudrate = 1000k
  {
    Serial.println("CAN BUS FAIL!");
    delay(100);
  }

  Serial.println("CAN BUS OK!");
  dht.begin();

  pinMode(PRESSURESENSORPIN, INPUT_PULLUP);
}


void loop()
{

  h = dht.readHumidity();
  t = dht.readTemperature();
  p = analogRead(PRESSURESENSORPIN);

  unsigned char len = 0;
  unsigned char buf[8];

  while (CAN_MSGAVAIL == CAN.checkReceive())           // check if data coming
  {

    unsigned long canId;
    CAN.readMsgBufID(&canId, &len, buf);    // read data,  len: data length, buf: data buf


    //        Serial.print(canId);
    //        for(int i = 0; i < len; i++){
    //          Serial.print(" ");
    //          Serial.print(buf[i]);
    //        }
    //        Serial.println();


    if (canId == address) {
      Serial.print(F("Humidity: "));
      Serial.print(h);
      Serial.print(F("%  Temperature: "));
      Serial.print(t);
      Serial.print(F("%  Pressure: "));
      Serial.print(p);
      Serial.println();

      unsigned char stmp[8] = {0, 0, 0, 0, 0, char(p / 100), char(t), char(h)};


      if (CAN_FAIL == CAN.sendMsgBuf(address, CAN_STDID, 8, stmp)) {
        Serial.println("Failed to send message :(");
      }

    }

  }

}
