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
  def __init__(self, terrain, pitch, depth, test_num): # Set relates to the medium that we are testing on 
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
    self.screwMotor = CanUJoint(can0, 0, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    self.encoderMotor = CanUJoint(can0, 2, 1)
    self.terrain = terrain
    self.pitch = pitch
    self.depth = depth
    self.test_num = test_num
    self.sampling_rate = 200 # in Hz
    self.data_fname = f"tests/ScrewTestScripts/motor_data_files/motor_{terrain}_tests"
    self.railLength = 1.25
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def __del__(self):
    self.stopMotors()
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def resetLinPosition(self, pos):
    self.encoderMotor.pos_ctrl(pos, 3)
    self.encoderMotor.read_multiturn_position()
    self.encoderMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading
    print("Moving...")
    while(abs(self.encoderMotor.read_multiturn_position() - pos) > .1):
      pass
    print("Done moving!")
    self.encoderMotor.torque_ctrl(0)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def runTorqueTest(self, torqueSettings):
    numTrials = 5
    run_time = 5 # in second

    location = self.data_fname + "motor_{0}_tests/torque_test/test{1}{2}{3}.csv".format(self.terrain, self.pitch, self.depth, self.test_num)
    self.encoderMotor.speed_ctrl(0)
    
    try:
      t0 = time.time() # Get start time
      with open(location, mode='w') as test_data: # Main testing loop
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['Time', 'Angular Speed', 'Torque', f'Torques: {torqueSettings}', f'Trials: {numTrials}'])
        for torque in torqueSettings:
          for i in range(0, numTrials):
            self.screwMotor.torque_ctrl(0)

            input('Sensor should be in free hang, unbias sensor then press enter.')
            test_writer.writerow([self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque()])
            input("Lower screw into water, then press enter.")
            test_writer.writerow([self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque()])
            input("Bias sensor, then press enter to start trial. Hit log at the same time you press enter.")
            
            self.screwMotor.torque_ctrl(-torque)

            trialStart = time.time() # Get initial start time of trial
            lastTime = -1

            print(f"Trial: {i}, Torque: {torque}")
            
            while (self.get_time(trialStart) < run_time):
              
              row = [self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque()]
              test_writer.writerow(row)      
              time.sleep(1/self.sampling_rate)
              if (int(self.get_time(trialStart)) != lastTime):
                print(f"{run_time - int(self.get_time(trialStart))} seconds left")
                lastTime = int(self.get_time(trialStart))

    except(KeyboardInterrupt) as e:
      print(e)
    self.stopMotors()
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def runSingleSpeedTest(self, speedSettings):
    input("Move testbed to the beginning of the rail")
    linEncZero = self.encoderMotor.read_multiturn_position()
    run_time = 30 # in seconds
    location = self.data_fname + "motor_{0}_tests/speed_test/test{1}{2}{3}.csv".format(self.terrain, self.pitch, self.depth, self.test_num)

    try:
      t0 = time.time() # Get start time
      with open(location, mode='w') as test_data: # Main testing loop
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['Time', 'Angular Speed', 'Torque', 'Linear Speed', 'Linear Position (meters)', f'Speeds: {speedSettings}'])
        for speed in speedSettings:
          self.screwMotor.torque_ctrl(0)

          input('Sensor should be in free hang, unbias sensor then press enter.')
          test_writer.writerow([self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque()])
          input("Lower screw into water, then press enter.")
          test_writer.writerow([self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque()])
          input("Bias sensor, then press enter to start trial. Hit log at the same time you press enter.")
          self.resetLinPosition(linEncZero)
          self.screwMotor.speed_ctrl(-speed)

          trialStart = time.time() # Get initial start time of trial
          lastTime = -1
          print(f"Speed: {speed}")

          while (self.get_time(trialStart) < run_time):
            linPos = (linEncZero - self.encoderMotor.read_multiturn_position()) *.09525/2
            if (linPos > self.railLength):
              print("Hit end of rail!")
              break
            row = [self.get_time(t0), self.screwMotor.read_speed(), self.screwMotor.read_torque(), self.encoderMotor.read_speed(), linPos]
            test_writer.writerow(row)      
            time.sleep(1/self.sampling_rate)
            if (int(self.get_time(trialStart)) != lastTime):
              print(f"{run_time - int(self.get_time(trialStart))} seconds left")
              lastTime = int(self.get_time(trialStart))

    except(KeyboardInterrupt) as e:
      print(e)
    # self.stopSensorLog()
    self.stopMotors()
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def zeroScrewMotor(self):
    self.screwMotor.torque_ctrl(0)
    time.sleep(1)
    for i in range(10):
      self.screwMotor.read_multiturn_position(); 
    curPosition = self.screwMotor.read_multiturn_position()
    newPosition = int(curPosition/6.28)*6.28
    print(f"Curposition: {curPosition}")
    print(f"Newposition: {newPosition}")
    self.screwMotor.pos_ctrl(newPosition)
    time.sleep(5)
    for i in range(10):
      self.screwMotor.read_multiturn_position(); 
    print(f"Final position:{self.screwMotor.read_multiturn_position()}")
 # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////     
  def get_time(self, t0):
    return time.time() - t0
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  def stopMotors(self):
    self.screwMotor.motor_stop()
    self.encoderMotor.motor_stop()
