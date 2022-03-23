# TODO:
- Export conda environment so all the python dependencies can be easily imported
- Torque control / torque plotting

# Arduino TODO
- Update README in ArduionoHumidity to explain how the set up is
- Get Arduino humidity sensor thingy working 

# Getting Started with USB CAN bus
To check if USB CAN bus is working, run
```
ifconfig -a
```
and verify that `can0` appears in the list.

# Install Code base
Do this by running the installation.sh file alternatively, you can manually run the below commands yourself


## Installing Anaconda
Install anaconda from official website   
Verify anaconda installed with conda -V  
Create a new virtual environment  
```
conda create -n arcsnake python=3.9.7 anaconda
```
### Activating virtual environment 
```
conda activate arcsnake 
```
### For deactivating virtual environment 
```
conda decativate arcsnake
```

## Cloning Repo
```
sudo apt-get install git
git clone https://github.com/ucsdarclab/arcsnake_v2.git
```

## Installing Packages 
Install can utils:
```
sudo apt-get install can-utils
```

Install pip packages:
```
pip install pyinstrument
pip install numpy
pip install matplotlib
pip install python-can
```

# Running test programs
cd inside of arcsnake directory 
run 
'''
python3 tests/test_sanity.py
'''


# Notes: 

## Add Python to ubuntu path 
- type sudo gedit ~/.bashrc in /home directory 
- Insert this command near end of text file: 
'''
    export PYTHONPATH="${PYTHONPATH}:/home/myeoh/Documents/Github"
'''
- save and verify by running echo $PYTHONPATH in terminal 

## Otherwise, if issues with Path stuff insert this into top of code
from os.path import dirname, realpath  
import sys  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  