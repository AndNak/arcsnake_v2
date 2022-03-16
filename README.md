# Getting Started with USB CAN bus
To check if USB CAN bus is working, run
```
ifconfig -a
```
and verify that `can0` appears in the list.

# Install Code base


# Installing Packages 
Install can utils
```
sudo apt-get install can-utils
```

Install pip packages:
```
pip install numpy
pip install matplotlib
pip install python-can
```


# TODO:
- Add steps for git cloning, creating new conda environment to run stuff from etc.
- Go through each python file in tests/* and get them to run (also learn about what they do or attempt to do)
- Add explaination for how to run code in tests/* (do this to the level of running from a terminal)
- Update README in ArduionoHumidity to explain how the set up is
- Export conda environment so all the python dependencies can be easily imported

# Notes: 

## Add Python to ubuntu path 
- type sudo gedit ~/.bashrc in /home directory 
- Insert this command near end of text file: 
    export PYTHONPATH="${PYTHONPATH}:/home/myeoh/Documents/Github"
- save and verify by running echo $PYTHONPATH in terminal 

## Otherwise, if issues with Path stuff insert this into top of code
from os.path import dirname, realpath
import sys
arcsnake_v2_path = dirname(dirname(realpath(__file__)))
sys.path.append(arcsnake_v2_path)