import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time
import serial

from os.path import dirname, realpath  
import sys
from core.CanMotor import CanMotor
import csv
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)

class testBench:
  def __init__(self, set): # Set relates to the medium that we are testing on 
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
    self.screwMotor1 = CanUJoint(can0, 0, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    # self.screwMotor2 = CanUJoint(can0, 1, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    self.retractMotor = CanUJoint(can0, 3, 6)
    self.encoderMotor = CanUJoint(can0, 2, 1)
    self.sampling_rate = 200 # in Hz
    self.data_fname = "tests/ScrewTestScripts/data_files"
    self.set = set
    self.liftHeight = 100 # set in mm
    self.retractMotTorque = -.1
    self.retractMotSpeed = 3
    self.seeeduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=.1)
    self.groundZero = None
    self.liftHeight = None
    self.retractMotor.torque_ctrl(self.retractMotTorque)
    self.railLength = 1.25
    
  def __del__(self):
    self.stopMotors()

  def setGroundZero(self):
    print("Ensure TestBench screw are touching ground and cable is on pulley!!")
    input("Press enter to set Ground Zero Position")

    self.retractMotor.read_multiturn_position() # Have to read twice to actually get a good reading...
    self.groundZero = self.retractMotor.read_multiturn_position()
    self.liftHeight = self.groundZero + -(self.liftHeight/180.55) * 2 * 3.14

  def changeScrewHeight(self, height):
    if (self.groundZero is None):
      self.stopMotors()
      raise Exception("Ground zero not set yet!")
    self.retractMotor.pos_ctrl(height, self.retractMotSpeed)
    self.retractMotor.read_multiturn_position(); self.retractMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading
    print("Moving...")
    while(abs(self.retractMotor.read_multiturn_position() - height) > .1):
      pass
    self.retractMotor.torque_ctrl(self.retractMotTorque)
    print("Done moving!")

  def lowerScrews(self):
    self.changeScrewHeight(self.groundZero)

  def liftScrews(self):
    self.changeScrewHeight(self.liftHeight)

  def resetLinPosition(self, pos):
    self.encoderMotor.pos_ctrl(pos, 3)
    self.encoderMotor.read_multiturn_position()
    self.encoderMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading
    print("Moving...")
    while(abs(self.encoderMotor.read_multiturn_position() - pos) > .1):
      pass
    print("Done moving!")
    self.encoderMotor.torque_ctrl(0)

  def runTorqueTest(self, torqueSettings):
    numTrials = 5
    run_time = 15 # in second
    location = self.data_fname + "/const_torque_tests/set{0}.csv".format(self.set)
    self.encoderMotor.speed_ctrl(0)

    t0 = time.time() # Get start time
    # self.startSensorLog()

    try:
      with open(location, mode='w') as test_data: # Main testing loop
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['time', 'angular speed 1', 'torque 1', f'Torques: {torqueSettings}', f'numTrials: {numTrials}'])
        for torque in torqueSettings:
          for i in range(0,numTrials):
            self.liftScrews() # lift the screws up 
            self.unBiasSensor()
            print("Unbias the sensor!") # Unbias the sensor
            # self.zeroScrewMotor()
            self.lowerScrews() # lower the screws down 
            self.biasSensor()
            print("Bias the sensor!") # Bias the sensor
            self.screwMotor1.torque_ctrl(torque)

            trialStart = time.time() # Get initial start time of trial
            lastTime = -1
            self.screwMotor1.read_multiturn_position; initialpos = self.screwMotor1.read_multiturn_position

            while (self.get_time(trialStart) < run_time and abs(self.screwMotor1.read_multiturn_position - initialpos) < 3.14*2):
              row = [self.get_time(t0), self.screwMotor1.read_speed(), self.screwMotor1.read_torque()]
              test_writer.writerow(row)      
              time.sleep(1/self.sampling_rate)
              if (int(self.get_time(trialStart)) != lastTime):
                print(f"{run_time - int(self.get_time(trialStart))} seconds left")
                lastTime = int(self.get_time(trialStart))

    except(KeyboardInterrupt) as e:
      print(e)
    self.stopMotors()
    # self.stopSensorLog()

  def runSingleSpeedTest(self, speedSettings):
    self.liftScrews()
    input("Move testbed to the beginning of the rail")
    linEncZero = self.encoderMotor.read_multiturn_position()
    run_time = 30 # in seconds
    location = self.data_fname + "/const_speed_tests/set{0}.csv".format(self.set)

    t0 = time.time() # Get start time
    # self.startSensorLog()

    try:
      with open(location, mode='w') as test_data: # Main testing loop
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['time', 'angular speed 1', 'torque 1', 'linear speed', 'linear position (meters)', f'Speeds: {speedSettings}'])
        for speed in speedSettings:
          self.screwMotor1.torque_ctrl(0)
          self.liftScrews() # lift the screws up 
          self.unBiasSensor()
          print("Unbias the sensor!") # Unbias the sensor
          self.resetLinPosition(linEncZero)

          self.lowerScrews() # lower the screws down 
          self.biasSensor()
          print("Bias the sensor!") # Bias the sensor
          self.screwMotor1.speed_ctrl(-speed)

          trialStart = time.time() # Get initial start time of trial
          lastTime = -1
          while (self.get_time(trialStart) < run_time):
            linPos = (linEncZero - self.encoderMotor.read_multiturn_position()) *.09525/2
            if (linPos > self.railLength):
              print("Hit end of the rail!")
              break
            row = [self.get_time(t0), self.screwMotor1.read_speed(), self.screwMotor1.read_torque(), self.encoderMotor.read_speed(), linPos]
            test_writer.writerow(row)      
            time.sleep(1/self.sampling_rate)
            if (int(self.get_time(trialStart)) != lastTime):
              print(f"{run_time - int(self.get_time(trialStart))} seconds left")
              lastTime = int(self.get_time(trialStart))

    except(KeyboardInterrupt) as e:
      print(e)
    # self.stopSensorLog()
    self.stopMotors()

  def zeroScrewMotor(self):
    self.screwMotor1.torque_ctrl(0)
    time.sleep(1)
    for i in range(10):
      self.screwMotor1.read_multiturn_position(); 
    curPosition = self.screwMotor1.read_multiturn_position()
    newPosition = int(curPosition/6.28)*6.28
    print(f"Curposition: {curPosition}")
    print(f"Newposition: {newPosition}")
    self.screwMotor1.pos_ctrl(newPosition)
    time.sleep(5)
    for i in range(10):
      self.screwMotor1.read_multiturn_position(); 
    print(f"Final position:{self.screwMotor1.read_multiturn_position()}")
      
  def get_time(self, t0):
    return time.time() - t0

  def stopMotors(self):
    self.screwMotor1.motor_stop()
    # self.screwMotor2.motor_stop()
    self.retractMotor.motor_stop()
    self.encoderMotor.motor_stop()

  def biasSensor(self):
    time.sleep(.5)
    self.sendBluetoothCommand('a')
    time.sleep(.5)

  def unBiasSensor(self):
    time.sleep(.5)
    self.sendBluetoothCommand('b')
    time.sleep(.5)

  def stopSensorLog(self):
    self.sendBluetoothCommand('c')

  def startSensorLog(self):
    self.sendBluetoothCommand('d')

  def sendBluetoothCommand(self, letter): # Presses LCTRL + SHIFT + letter
    self.seeeduino.write(bytes(letter, 'utf-8'))
    time.sleep(.1) # Delay 100 ms for Autohotkey