import numpy as np
import matplotlib.pyplot as plt
from utils import *
 
# ~~~ Configuration ~~~
terrain = 'concrete'           # [water, sand, concrete, gravel] *Could potentially change depending on testing!*
test_type = 'speed'            # [speed, torque]
pitch, depth, trial = 1, 2, 3
just_visualizing = False      # Set True to skip processing and just visualize output
index_set = [3000, 6000]       # Used in plotting only (optional quick view)

# ~~~ File Paths ~~~
test_id = f"{pitch}{depth}{trial}"
motor_csv = f"tests/Testbed/motor_data_files/motor_{terrain}_tests/{test_type}_test/test{test_id}.csv"
fts_csv = f"tests/Testbed/fts_data_files/fts_{terrain}_tests/{test_type}_test/test{test_id}.csv"

processed_dir = f"tests/Testbed/processed_data/{terrain}/{test_type}/"
datafname = processed_dir + f"test{test_id}"

# ~~~ Data Loading ~~~
if just_visualizing:
    data = np.load(datafname + '.npz')
    filt_motor_data = data['filt_motor_data']
    filt_ft_data = data['filt_ft_data']
    segmented = data['segmented']
else:
    raw_motor_data = read_motor_csv(motor_csv)
    raw_ft_data = read_sensor_csv(fts_csv)

    # ~~~ Filtering ~~~
    filt_motor_data = filter_motor_data(raw_motor_data)
    filt_ft_data = filter_ft_data(raw_ft_data)

    # ~~~ Plotting for initial index selection ~~~
    plot_motor_data(filt_motor_data)
    plot_ft_data(filt_ft_data, *index_set, None)

    # ~~~ Manual Indexing for Segmentation ~~~
    print("Input data segmentation indices (time domain):")
    free_start = int(input("Enter free hang start index: "))
    free_end = int(input("Enter free hang end index: "))
    setdown_start = int(input("Enter set down start index: "))
    setdown_end = int(input("Enter set down end index: "))
    trial_start = int(input("Enter trial start index: "))
    trial_end = int(input("Enter trial end index: "))
    steady_start = int(input("Enter steady state start index: "))
    steady_end = int(input("Enter steady state end index: "))

    segmented = {
        'free': (free_start, free_end),
        'setdown': (setdown_start, setdown_end),
        'trial': (trial_start, trial_end),
        'steady': (steady_start, steady_end)
    }

    # ~~~ Save Output ~~~
    np.savez(
        datafname + '.npz',
        filt_motor_data=filt_motor_data,
        filt_ft_data=filt_ft_data,
        segmented=segmented
    )

# ~~~ Final Visualization ~~~
plot_data(filt_motor_data, filt_ft_data, segmented)
