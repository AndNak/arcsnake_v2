import numpy as np
from matplotlib import pyplot as plt
from utils import *

# === CONFIGURATION ===
terrain = 'concrete'           # 'concrete', 'sand', 'gravel'
test_type = 'speed'            # 'speed' or 'torque'
pitch, depth, trial = 1, 2, 3
just_visualizing = False      # Set True to skip processing and just visualize output
index_set = [3000, 6000]       # Used in plotting only (optional quick view)

# === Construct Test ID and File Paths ===
test_id = f"{pitch}{depth}{trial}"
motor_csv = f"tests/Testbed/motor_data_files/motor_{terrain}_tests/{test_type}_test/test{test_id}.csv"
fts_csv = f"tests/Testbed/fts_data_files/{test_type}_test/test{test_id}.csv"

processed_dir = f"processed_data/processed_motor_fts/{terrain}/{test_type}/"
datafname = processed_dir + f"test{test_id}"
# === Data Loading ===
if just_visualizing:
    data = np.load(datafname + '.npz')
    filt_motor_data = data['filt_motor_data']
    filt_ft_data = data['filt_ft_data']
    segmented = data['segmented']
else:
    raw_motor_data = read_motor_csv(motor_csv)
    raw_ft_data = read_sensor_csv(fts_csv)

    # === Filtering ===
    filt_motor_data = filter_motor_data(raw_motor_data)
    filt_ft_data = filter_ft_data(raw_ft_data)

    # === Plotting for initial index selection ===
    plot_motor_data(filt_motor_data)
    plot_ft_data(filt_ft_data, *index_set, None)

    # === Manual Indexing for Segmentation ===
    print("Input data segmentation indices (time domain):")
    free_idx = int(input("Index for free hang: "))
    setdown_idx = int(input("Index for set down: "))
    trial_idx = int(input("Index for trial start: "))
    steady_idx = int(input("Index for steady state start: "))
    end_idx = int(input("Index for trial end: "))

    segmented = {
        'free': free_idx,
        'setdown': setdown_idx,
        'trial': trial_idx,
        'steady': steady_idx,
        'end': end_idx
    }

    # === Save Output ===
    np.savez(
        datafname + '.npz',
        filt_motor_data=filt_motor_data,
        filt_ft_data=filt_ft_data,
        segmented=segmented
    )

# === Final Visualization ===
plot_data(filt_motor_data, filt_ft_data, segmented)














if __name__ == "__main__":

	set_num = 1
	test_num = 1
	screw_num = 1

	ft_data = read_sensor_csv(
		'tests/ScrewTestScripts/data_files/const_torque_tests/set{0}/test{1}.csv'.format(set_num, test_num))
	motor_data = read_motor_csv(
		'tests/ScrewTestScripts/data_files/torque_tests/screw{0}/set{1}.csv'.format(screw_num, set_num))
	filt_motor_data = filter_motor_data(motor_data, cutoff=6, fs=125, order=2)
	filt_ft_data = filter_ft_data(ft_data, cutoff=6, fs=125, order=2)

	if just_visualizing == True:
		plot_motor_data(filt_motor_data, None)
		plot_ft_data(filt_ft_data, 3000, 6000, None)
		plt.show()

	elif just_visualizing == False:
		plot_ft_data(filt_ft_data, 0, None, None)

		# Almost always can put 200-300 for these
		free_hang_start = int(input('Enter free hang starting index: '))
		free_hang_end = int(input('Enter free hang ending index: '))

		set_down_start = int(input('Enter set down starting index: '))
		set_down_end = int(input('Enter set down ending index: '))

		ft_start = int(input('Enter trial starting index: '))
		ft_end = int(input('Enter trial ending index: '))

		ft_ss_start = int(input('Enter steady state starting index: '))
		ft_ss_end = int(input('Enter steady state ending index: '))

		plot_motor_data(filt_motor_data, None)

		motor_ss_start = int(input('Enter motor steady state starting index: '))
		motor_ss_end = int(input('Enter motor steady state ending index: '))

		figfname = 'figures/const_torque_tests/set{0}/test{1}'.format(
			set_num, test_num)
		datafname = 'processed_data_files/const_torque_tests/set{0}/testtest{1}'.format(
			set_num, test_num)

		plot_data(figfname, filt_ft_data, filt_motor_data, motor_ss_start,
		          motor_ss_end, ft_start, ft_end, ft_ss_start, ft_ss_end)

		np.savez(datafname, motor_data=motor_data, filt_motor_data=filt_motor_data,
                    ft_data=ft_data, filt_ft_data=filt_ft_data, ft_start=ft_start, ft_end=ft_end,
                    ft_ss_start=ft_ss_start, ft_ss_end=ft_ss_end,
                    motor_ss_start=motor_ss_start, motor_ss_end=motor_ss_end,
                    free_hang_start=free_hang_start, free_hang_end=free_hang_end,
                    set_down_start=set_down_start, set_down_end=set_down_end)

		plt.show()
		
        
