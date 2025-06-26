# Getting Started with USB CAN bus
After USB-Can Adapter is connected to the computer, check if CAN bus is online, run

```
ifconfig -a
```

and verify that `can0` appears in the list.

## Cloning Repo

```
sudo apt-get install git          // If Git is not installed, install it
git clone https://github.com/ucsdarclab/arcsnake_v2.git       // Clone the repo into your local machine
```

# Run installation script to install required dependencies / system tools

'''
bash installation.sh
'''

# Installing Ros (fix up)

# TODO

# Notes:

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