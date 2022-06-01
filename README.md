# TODO:

- get version control down!!! PETER!!!!!!!!
- Fix multiturn code get it solved figure out what's wrong 
- get the differential pressure sensor and the humidity sensor to communicate via CAN line
- Document how to upload code to the longan can board

## Ros

- find how to make ini file
- Document installation for ros 
- test python time vs ros time 

# Getting Started with USB CAN bus

To check if USB CAN bus is working, run

```
ifconfig -a
```

and verify that `can0` appears in the list.

# Install Code base

Do this by running the installation.sh file alternatively, you can manually run the below commands yourself

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

# Installing Ros (fix up)

Use the installation script made by Ace Bhatia (Thanks)

git clone https://github.com/ankbhatia19/ROS2-Containerized.git

Follow instructions in Ace's git??

# Notes:

## Add Python to ubuntu path

- type sudo gedit ~/.bashrc in /home directory 
- Insert this command near end of text file: 
  '''
    export PYTHONPATH="${PYTHONPATH}:/home/myeoh/Documents/Github"
  '''
- **RESTART COMPUTER TO SAVE CHANGES**
- save and verify by running echo $PYTHONPATH in terminal 

## Otherwise, if issues with Path stuff insert this into top of code

from os.path import dirname, realpath  
import sys  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  
