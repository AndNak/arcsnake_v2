import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

for i in [1, 4]:
    folder = 'tests/System Tests/ScrewShellSpinTests'
    filename = f"{folder}/assembled_screwblock{i}_v30_Kp255_Ki50.csv"
    data = pd.read_csv(filename)
    print(data['torque'].mean())
    # with open(filename, 'r') as f:
    #     reader = csv.reader(f)
    #     print(next(reader))
