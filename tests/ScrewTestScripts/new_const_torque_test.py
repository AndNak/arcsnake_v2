from tests.ScrewTestScripts.Test_Bench_Class import testBench
import time
myTestBench = testBench(1)
myTestBench.setGroundZero()

# myTestBench.changeScrewHeight(myTestBench.liftHeight)
# time.sleep(3)
# myTestBench.changeScrewHeight(myTestBench.groundZero)
myTestBench.startSensorLog()
myTestBench.runTorqueTest({.5, .75})
myTestBench.stopSensorLog()

# myTestBench.screwMotor1.speed_ctrl(8)
# time.sleep(2)
# myTestBench.zeroScrewMotor()


# myTestBench.runSingleSpeedTest({3,4})