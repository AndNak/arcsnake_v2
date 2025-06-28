from tests.ScrewTestScripts.Test_Bench_Class import testBench

#terrain = [water, sand, concrete, gravel]
#pitch = 1 #[ , , , , ]
#depth = 1 #[ , , , , ]
#test_num = 1 # Trial [1 2 3]

# Instantiate TestBench Object
myTestBench = testBench("water", 1, 1, 1) # terrain, pitch, depth, test_num

# For Running Constant Speed Test:
myTestBench.runSingleSpeedTest({2,3,4,5,6})

#For Running Constant Torque test:
# myTestBench.runTorqueTest({.25, .5, .75, 1, 1.25})
