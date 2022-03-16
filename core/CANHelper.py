import os

def init(CANBUSID):
  os.system(f'sudo ifconfig {CANBUSID} down')
  os.system(f'sudo ip link set {CANBUSID} type can bitrate 1000000')
  os.system(f'sudo ifconfig {CANBUSID} up')

def cleanup(CANBUSID):
  os.system(f'sudo ifconfig {CANBUSID} down')