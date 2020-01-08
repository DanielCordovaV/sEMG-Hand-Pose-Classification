from EmgCollector import EmgCollector
from myo import init, Hub
from itertools import cycle
from collections import deque
import pandas as pd
import numpy as np
import sys, os
from time import sleep


'''Constants'''

LABELS = ['Flexion', 'Extension', 'Fist', 'Neutral']
NB_LABELS = len(LABELS)
NB_CHANNELS = 8
CHANNELS = [f'ch{n}' for n in range(1, NB_CHANNELS + 1)]
INTERVAL = 15 # Total time each label stays on screen
RECORDING_TIME = 10 # Seconds to record of each label
DEAD_TIME = INTERVAL - RECORDING_TIME
EXAMPLE_SIZE = 50 # Number of data points to be stored in the csvs
SAMPLE_RATE = 200
SAMPLES_PER_INTERVAL = INTERVAL * SAMPLE_RATE
CHECKPOINTS = list(range((DEAD_TIME*SAMPLE_RATE+EXAMPLE_SIZE-1), SAMPLES_PER_INTERVAL, EXAMPLE_SIZE))

'''Setting workspace'''

os.chdir('..')
ROOT = os.getcwd()
DIR_PATH = os.path.join(ROOT, 'datasets/myo_data')
try:
    os.mkdir(DIR_PATH)
except FileExistsError:
    pass
for label in LABELS:
    try:
        os.mkdir(os.path.join(DIR_PATH, label))
    except FileExistsError:
            pass

'''Globals'''

g_index = 0
g_label_iter = cycle(range(NB_LABELS))
g_label_index = -1
g_label_count = { label: len(os.listdir(f'datasets/myo_data/{label}')) for label in LABELS }
g_file_index = np.sum(list(g_label_count.values())) + 1
g_ch_data = {ch: deque() for ch in CHANNELS}

def output_command(label):
    dots = "·" * 42 + "\n"
    print(f'Producing {label}\'s csv no.: {g_label_count[label]}, sample no.: {g_file_index}', end='\n\n')
    print(dots * 2 + f"    {label} \n" + dots * 2, end='')

def clear_window():
    for _ in range(7):
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[F")

def save_example(csv_path, label):
    global g_label_count
    
    df = pd.DataFrame(g_ch_data)
    df.to_csv(f'{csv_path}/{label}{g_label_count[label]}.csv', index=False)
    
    g_label_count[label] += 1 

def collect_data(collector):
    global g_index, g_file_index, g_label_index, g_ch_data

    emg = collector.get_EMG()
    if emg == []:
        return

    if g_index % SAMPLES_PER_INTERVAL == 0:
        if g_index == 0:
            print('')
        g_label_index = next(g_label_iter)
        if g_index != 0:
            clear_window()
        output_command(LABELS[g_label_index])

    for n in range(1, NB_CHANNELS + 1):
        ch = f'ch{n}'
        if g_index >= 50:
            g_ch_data[ch].popleft()
        g_ch_data[ch].append(emg[n - 1])

    g_index += 1
    if g_index % SAMPLES_PER_INTERVAL in CHECKPOINTS:
        label = LABELS[g_label_index]
        save_example(os.path.join(DIR_PATH, label), label)
        g_file_index += 1

if __name__ == "__main__":
    if sys.version_info.major == 3:
        print('--------------------')
        print("-- MYO  Collector --")
        print('--------------------')
        print('--------------------')

        init()
        hub = Hub()
        collector = EmgCollector()

        while hub.run(collector.on_event, 5):
            collect_data(collector)
    else:
        print("Make sure python is version 3 and up")