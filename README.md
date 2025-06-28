# Getting Started with USB CAN bus
After USB-Can Adapter is connected to the computer, check if CAN bus is online, run

```
ifconfig -a
```

and verify that `can0` appears in the list.

## Cloning Repo4

```
sudo apt-get install git          // If Git is not installed, install it
git clone https://github.com/ucsdarclab/arcsnake_v2.git       // Clone the repo into your local machine
```

# Run installation script to install required dependencies / system tools

'''
bash installation.sh
'''

# Test Bed:
Things to Keep in Mind:

Things to keep in mind while setting up:
- Plug FT sensor into computer at least 30 min. before testing to let it warm up
- ALWAYS have the sensor display open and reading during set up so you can make sure you don't overload sensor accidentally!
- Keep a written log of the tests you are performing. Change set #, test #, terrain, etc.
  (set describes current media, test describes current input params)

Status codes to watch out for:
0xC0000000 -- Warning! Out of calibration range. You are close to overloading the sensor.
0x88000000 -- Super Warning! Out of gage range. You are close to damaging the sensor.
If you see these on the event log you are straining the sensor too much, try to ease the load being put on it.

## For Single Screw Tests
### Constant Speed Test:
1) Configuration should be in free hang. HIT UNBIAS SENSOR BUTTON!
2) Ensure that media is smoothed and uniform as possible
3) Write down current set(material)/test(current trial that you're doing) info in notebook. 
4) Ensure proper set/test number is set on motor script AND sensor log
  Tools -> Sensor log  -> (three dots) -> Name it -> Click on New File
5) Start motor script and sensor log (I try to start them at the same time but it doesn't have to be exact)
6) synchronization procedure will start, after 3 screw spins to set position.
7) After synchronization procedure, you have 20 seconds to set the screw down. Firmly push it into media to sink it in.
8) AFTER SETTING DOWN, BIAS THE SENSOR
9) 20 seconds after sync procedure, actual trial will start. Be prepared to stop motor script just in case.
10) Ensure that the proper data files (with the correct set/test number) were saved.


## Constant Torque Test:
### Steps 1-6 exactly the same as constant speed test.
7) During this step, make sure someone pushes the configuration forward agianst the "brake" on  while setting down.
8) This time the screw may or may not spin during trial. Watch to make sure the test bed itself doesn't move.
Steps 9-10 same

# Sidenote:
## Add Python to ubuntu path

- type sudo gedit ~/.bashrc in /home directory
- Insert this command near end of text file: 
  '''
    export PATH="$HOME/myeoh/Documents/GitHub/arcsnake_v2:$PATH"
  '''
- Run source ~/.bashrc
- save and verify by running echo $PATH in terminal 

## Otherwise, if issues with Path stuff insert this into top of code

from os.path import dirname, realpath  
import sys  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)