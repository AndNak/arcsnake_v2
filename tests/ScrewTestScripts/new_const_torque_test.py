from tests.ScrewTestScripts.Test_Bench_Class import testBench
import time
myTestBench = testBench(1)


# myTestBench.liftScrews()

# time.sleep(10)

# myTestBench.lowerScrews()
myTestBench.runTorqueTest({.25, .5, .75, 1})

 