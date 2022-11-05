import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time

from os.path import dirname, realpath  
import sys
from core.CanMotor import CanMotor
import csv
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)

class testBench:
  def __init__(self, set): # Test relates to the medium that we are testing on 
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
    self.screwMotor1 = CanUJoint(can0, 0, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    self.screwMotor2 = CanUJoint(can0, 1, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    self.retractMotor = CanUJoint(can0, 3, 6)
    self.encoderMotor = CanUJoint(can0, 2, 1)
    self.sampling_rate = 200 # in Hz
    self.data_fname = "tests/ScrewTestScripts/data_files"
    self.set = set
    self.liftHeight = 180 # set in mm
    self.retractMotTorque = -.1
    self.reatractMotSpeed = 2

    self.retractMotor.torque_ctrl(self.retractMotTorque)
    print("Ensure TestBench screw are touching ground and cable is on pulley!!")
    input("Press enter to set Ground Zero Position")

    self.retractMotor.read_multiturn_position() # Have to read twice to actually get a good reading...
    self.groundZero = self.retractMotor.read_multiturn_position()


  def lowerScrews(self):
    self.retractMotor.pos_ctrl(self.groundZero, self.reatractMotSpeed)
    self.retractMotor.read_multiturn_position()
    self.retractMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading
    print("Lowering...")
    while(abs(self.retractMotor.read_multiturn_position() - self.groundZero) > .1):
      pass
    self.retractMotor.torque_ctrl(self.retractMotTorque)
    print("Done lowering!")

  def liftScrews(self):
    liftHeight = self.groundZero + -(self.liftHeight/180.55) * 2 * 3.14
    self.retractMotor.pos_ctrl(liftHeight,self.reatractMotSpeed)
    self.retractMotor.read_multiturn_position()
    self.retractMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading
    print("Raising...")
    while(abs(self.retractMotor.read_multiturn_position() - liftHeight) > .1):
      pass
    print("Done raising!")

  def runTorqueTest(self, torqueSettings):
    t0 = time.time() # Get start time
    trialNum = 5
    self.run_time = 2 # in second
    location = self.data_fname + "/const_torque_tests/set{0}.csv".format(self.set)
    
    try:
      with open(location, mode='w') as test_data: # Main testing loop
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['time', 'angular speed 1', 'angular speed 2', 'torque 1', 'torque 2', 'linear speed', 'linear position (meters)'])
        for torque in torqueSettings:
          for i in range(0,trialNum):
            self.screwMotor1.read_multiturn_position(); self.screwMotor1.read_multiturn_position()
            curPosition = self.screwMotor1.read_multiturn_position()
            print(int(curPosition/6.28)*6.28)
            print(curPosition)
            self.screwMotor1.pos_ctrl(int(curPosition/6.28)*6.28)
          
            self.liftScrews() # lift the screws up 
            print("Unbias the sensor!") # Unbias the sensor
            
            self.lowerScrews() # lower the screws down 
            print("Bias the sensor!") # Bias the sensor
            self.screwMotor1.torque_ctrl(torque)

            trialStart = time.time() # Get initial start time of trial
            lastTime = -1
            while (self.get_time(trialStart) < self.run_time):
              self.recordData(test_writer, t0)
              if (int(self.get_time(trialStart)) != lastTime):
                print(f"{self.run_time - int(self.get_time(trialStart))} seconds left")
                lastTime = int(self.get_time(trialStart))

    except(KeyboardInterrupt) as e:
      print(e)


    self.stopMotors()

  def get_time(self, t0):
    return time.time() - t0

  def stopMotors(self):
    self.screwMotor1.motor_stop()
    self.screwMotor2.motor_stop()
    self.retractMotor.motor_stop()
    self.encoderMotor.motor_stop()

  def recordData(self, writer, startTime):
    row = [self.get_time(startTime), self.screwMotor1.read_speed(), self.screwMotor2.read_speed(), self.screwMotor1.read_torque(), self.screwMotor2.read_torque(), self.encoderMotor.read_speed(), self.encoderMotor.read_multiturn_position() *-.09525/2]
    writer.writerow(row)      
    time.sleep(1/self.sampling_rate)