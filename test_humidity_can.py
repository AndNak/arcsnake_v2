import os
import can
import time

# Open new terminal ctrl + alt + t
# run 'conda activate snake2'
# run 'cd ~/motorcontrol/arcsnake_v2'
# run 'python test_humidity_can.py'



def init():
  os.system('sudo ifconfig can2 down')
  os.system('sudo ip link set can2 type can bitrate 1000000')
  os.system('sudo ifconfig can2 up')

def cleanup():
  os.system('sudo ifconfig can2 down')

if __name__ == "__main__":
  init()

  canBus = can.ThreadSafeBus(channel='can2', bustype='socketcan_ctypes')

  data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  msg = can.Message(arbitration_id=0x0, data=data, extended_id=False)
  canBus.send(msg)

  # Make sure return send from the arudion is the SAME ID as the send from this computer

  # Uncomment when the arduino is ready to send back!
  msg = canBus.recv()
  print(msg)



  cleanup()