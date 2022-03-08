import os
import can
import time
from CanArduinoSensors import CanArduinoSensors

# Open new terminal ctrl + alt + t
# run 'conda activate snake2'
# run 'cd ~/motorcontrol/arcsnake_v2'
# run 'python test_humidity_can.py'

def init():
  os.system('sudo ifconfig can0 down')
  os.system('sudo ip link set can0 type can bitrate 1000000')
  os.system('sudo ifconfig can0 up')

def cleanup():
  os.system('sudo ifconfig can0 down')

if __name__ == "__main__":
  init()

  canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  deviceId = 0x01
  sensor = CanArduinoSensors(canBus, deviceId)

  for _ in range(100):
    print(sensor.readHumidityAndTemperature())

  cleanup()