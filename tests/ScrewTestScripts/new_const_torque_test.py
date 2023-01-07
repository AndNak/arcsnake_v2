from tests.ScrewTestScripts.Test_Bench_Class import testBench
import time
myTestBench = testBench(1)
myTestBench.setGroundZero()

myTestBench.startSensorLog()
myTestBench.runSingleSpeedTest({2,3,4,5,6})
# myTestBench.runTorqueTest({1, 1.25, 1.5, 1.75, 2})
myTestBench.stopSensorLog()

# myTestBench.screwMotor1.speed_ctrl(8)
# time.sleep(2)
# myTestBench.zeroScrewMotor()


# myTestBench.runSingleSpeedTest({3,4})