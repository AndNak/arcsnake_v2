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

    self.retractMotor.torque_ctrl(self.retractMotTorque)
    print("Ensure TestBench screw are touching ground and cable is on pulley!!")
    input("Press enter to set Ground Zero Position")

    self.retractMotor.read_multiturn_position() # Have to read twice to actually get a good reading...
    self.groundZero = self.retractMotor.read_multiturn_position()


  def lowerScrews(self):
    self.retractMotor.pos_ctrl(self.groundZero, 1)
    self.retractMotor.read_multiturn_position()
    self.retractMotor.read_multiturn_position() # Make sure the encoder actually gives an accurate reading

    while(abs(self.retractMotor.read_multiturn_position() - self.groundZero) > .1):
      print("Lowering...")
    self.retractMotor.torque_ctrl(self.retractMotTorque)
    pass

  def liftScrews(self):
    self.retractMotor.pos_ctrl(self.groundZero + -(self.liftHeight/180.55) * 2 * 3.14 , 1)
    pass

  def runTorqueTest(self, startT, endT, increment):
    t0 = time.time() # Get start time
    self.run_time = 30 # in second
    self.screwMotor1.torque_ctrl(.25)

    self.recordData(self.data_fname + "/const_torque_tests/set{0}.csv".format(self.set))
    self.stopMotors()

  def get_time(self, t0):
    return time.time() - t0

  def stopMotors(self):
    self.screwMotor1.motor_stop()
    self.screwMotor2.motor_stop()
    self.retractMotor.motor_stop()
    self.encoderMotor.motor_stop()

  def recordData(self, location):
    try:
      t0 = time.time()
      with open(location, mode='w') as test_data:
        test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_writer.writerow(['time', 'angular speed 1', 'angular speed 2', 'torque 1', 'torque 2', 'linear speed', 'linear position (meters)'])
        t1 = time.time() # Get initial start time
        lastTime = int(self.get_time(t0))

        while True:
          row = [self.get_time(t0), self.screwMotor1.read_speed(), self.screwMotor2.read_speed(), self.screwMotor1.read_torque(), self.screwMotor2.read_torque(), self.encoderMotor.read_speed(), self.encoderMotor.read_multiturn_position() *-.09525/2]
          
          if (int(self.get_time(t0)) != lastTime):
            print(f"{self.run_time - int(self.get_time(t0))} seconds left")
            lastTime = int(self.get_time(t0))
          test_writer.writerow(row)
          time.sleep(1/self.sampling_rate)
          if self.get_time(t1) > self.run_time:
            break
    except(KeyboardInterrupt) as e:
      print(e)