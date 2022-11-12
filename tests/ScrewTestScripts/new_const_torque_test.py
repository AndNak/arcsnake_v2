from tests.ScrewTestScripts.Test_Bench_Class import testBench
import time
myTestBench = testBench(1)
myTestBench.setGroundZero()

# time.sleep(10)

# myTestBench.lowerScrews()

# myTestBench.runTorqueTest({.25, .5, .75, 1})

# myTestBench.screwMotor1.speed_ctrl(8)
# time.sleep(2)
# myTestBench.zeroScrewMotor()


myTestBench.runSingleSpeedTest({3,4})